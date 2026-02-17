"""Orchestrator — the main pipeline connecting all modules.

Flow:
  [Hotword Engine] → [STT] → [AI Planner] → [Safety Validator]
  → [Confirmation (if needed)] → [Execution Engine] → [TTS Response]
  → [Memory Storage]
"""

import json
import logging
import threading
import time
from typing import Optional

import numpy as np

import config
from core.voice.audio_capture import AudioCapture
from core.voice.hotword import HotwordDetector
from core.voice.stt import SpeechToText
from core.voice.tts import TextToSpeech
from core.ai.provider_factory import create_llm_provider
from core.ai.schema import plan_to_json
from core.safety.validator import SafetyValidator
from core.execution.dispatcher import ActionDispatcher
from core.memory.database import MemoryDatabase

logger = logging.getLogger(__name__)


class Orchestrator:
    """Main pipeline coordinator connecting all Max subsystems."""

    def __init__(self, gui=None):
        self.gui = gui
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Initialize subsystems
        logger.info("Initializing Max subsystems...")
        self.audio = AudioCapture()
        self.hotword = HotwordDetector()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.ai = create_llm_provider()
        logger.info(f"LLM provider: {self.ai.provider_name}")
        self.safety = SafetyValidator()
        self.dispatcher = ActionDispatcher()
        self.memory = MemoryDatabase()

        logger.info("All subsystems initialized")

        # Update GUI with memory count
        if self.gui:
            count = self.memory.get_conversation_count()
            self.gui.set_memory_count(count)

    def start(self):
        """Start the voice listening loop."""
        if self._running:
            return

        self._running = True
        self.audio.start_stream()
        self._log("Max is listening. Say 'Max' to activate.", "system")
        self.tts.speak_async("Max is ready.")

        self._main_loop()

    def stop(self):
        """Stop the voice listening loop."""
        self._running = False
        self.audio.stop_stream()
        self._log("Max stopped.", "system")

    def _main_loop(self):
        """Main listening and processing loop."""
        while self._running:
            try:
                # Phase 1: Listen for hotword
                self._set_status("idle")
                audio_buffer = self.audio.get_short_buffer(duration_ms=3000)
                
                if audio_buffer is None or len(audio_buffer) == 0:
                    time.sleep(0.1)
                    continue

                # Check for wake word
                if not self.hotword.check_audio(audio_buffer):
                    continue

                # Wake word detected!
                self._set_status("listening")
                self._log("Wake word detected! Listening...", "system")
                self.tts.speak_async("Yes?")

                # Phase 2: Record the full command
                self.audio.clear_queue()
                time.sleep(0.3)  # Small pause for "Yes?" to play

                command_audio = self.audio.record_utterance()
                if command_audio is None:
                    self._log("No speech detected after wake word.", "system")
                    self._set_status("idle")
                    continue

                # Phase 3: Transcribe
                self._set_status("processing")
                self._log("Transcribing...", "system")
                
                text = self.stt.transcribe(command_audio)
                if not text:
                    self._log("Could not transcribe audio.", "system")
                    self.tts.speak_async("I didn't catch that. Please try again.")
                    continue

                # Extract command (remove wake word prefix if present)
                command = self.hotword.extract_command(text)
                self._log(command, "user")

                # Phase 4: Get AI plan
                self._set_status("processing", "Thinking...")
                recent = self.memory.get_recent_conversations(limit=5)
                plan = self.ai.plan(command, recent)

                if plan is None:
                    self._log("Failed to generate action plan.", "system")
                    self.tts.speak_async("Sorry, I couldn't understand that command.")
                    self.memory.save_conversation(command, None, "Plan generation failed", False)
                    continue

                plan_json = json.dumps(plan, indent=2)
                self._log_plan(plan_json)

                # Handle clarification requests
                if plan["task_type"] == "clarify":
                    message = plan["actions"][0]["parameters"].get("message", "Could you clarify?")
                    self._log(message, "max")
                    self.tts.speak_async(message)
                    self.memory.save_conversation(command, plan_json, "Clarification requested", True)
                    continue

                # Phase 5: Safety validation
                validation = self.safety.validate_plan(plan)

                if not validation["approved"]:
                    msg = "Action blocked by safety policy."
                    self._log(msg, "system")
                    self.tts.speak_async("Sorry, that action is blocked for safety reasons.")
                    self.memory.save_conversation(command, plan_json, msg, False)
                    continue

                # Phase 6: Confirmation (if needed)
                if validation["needs_confirmation"]:
                    confirm_msg = self.safety.format_confirmation_message(plan, validation)
                    self._log("Waiting for confirmation...", "system")
                    self.tts.speak_async("This action requires your approval. Please check the screen.")

                    approved = False
                    if self.gui:
                        approved = self.gui.request_confirmation(confirm_msg)
                    else:
                        # CLI fallback
                        print(f"\n{confirm_msg}")
                        response = input("Approve? (y/n): ").strip().lower()
                        approved = response in ("y", "yes")

                    if not approved:
                        self._log("Action denied by user.", "system")
                        self.tts.speak_async("Action cancelled.")
                        self.memory.save_conversation(command, plan_json, "User denied", False)
                        continue

                # Phase 7: Execute
                self._set_status("executing")
                self._log("Executing plan...", "system")

                skip_indices = set(validation.get("blocked_actions", []))
                results = self.dispatcher.execute_plan(plan, skip_indices)

                # Log results
                all_success = True
                for result in results:
                    success = result.get("success", False)
                    if not success:
                        all_success = False
                    self._log_result(
                        result.get("action_type", "unknown"),
                        success,
                        result.get("message", ""),
                    )

                # Phase 8: Respond with intelligent feedback
                if all_success:
                    self._log("All actions completed successfully.", "max")
                    # Provide specific feedback based on action types
                    action_types = [r.get("action_type") for r in results]
                    feedback = self._generate_feedback(action_types)
                    self.tts.speak_async(feedback)
                else:
                    failed = [r for r in results if not r.get("success")]
                    msg = f"Completed with {len(failed)} error(s)."
                    self._log(msg, "max")
                    self.tts.speak_async(msg)

                # Phase 9: Save to memory
                result_json = json.dumps(results, default=str)
                self.memory.save_conversation(command, plan_json, result_json, all_success)

                if self.gui:
                    self.gui.set_memory_count(self.memory.get_conversation_count())

            except Exception as e:
                logger.error(f"Pipeline error: {e}", exc_info=True)
                self._log(f"Error: {e}", "system")
                self._set_status("error")
                time.sleep(1)

    # ── GUI/Logging Helpers ──

    def _generate_feedback(self, action_types: list) -> str:
        """Generate intelligent voice feedback based on action types."""
        if not action_types:
            return "Done."
        
        # Remove None values and duplicates
        actions = [a for a in set(action_types) if a]
        
        feedback_map = {
            "open_app": "Opened.",
            "close_app": "Closed.",
            "open_browser": "Opened browser.",
            "navigate": "Navigated.",
            "single_step": "Done.",
            "multi_step": "Completed steps.",
            "system_volume": "Volume adjusted.",
            "system_brightness": "Brightness adjusted.",
            "system_sleep": "System sleeping.",
            "system_lock": "Screen locked.",
            "system_shutdown": "Shutdown scheduled.",
            "system_restart": "Restart scheduled.",
            "system_wifi": "WiFi toggled.",
            "system_bluetooth": "Bluetooth toggled.",
            "system_screensaver": "Screensaver toggled.",
            "system_mute": "Audio muted.",
            "system_unmute": "Audio unmuted.",
            "file_operation": "File operation completed.",
            "file_create": "File created.",
            "file_delete": "File deleted.",
            "file_move": "File moved.",
            "install_software": "Installation completed.",
        }
        
        # If single action, use specific message
        if len(actions) == 1:
            return feedback_map.get(actions[0], "Done.")
        
        # Multiple actions - build summary
        responses = []
        for action in sorted(actions):
            if action in feedback_map:
                msg = feedback_map[action]
                if msg not in responses:
                    responses.append(msg)
        
        if len(responses) == 1:
            return responses[0]
        elif len(responses) > 1:
            return " ".join(responses)
        
        return "Done."

    def _log(self, text: str, source: str = "system"):
        """Log a message to GUI and logger."""
        if source == "user":
            logger.info(f"[USER] {text}")
            if self.gui:
                self.gui.add_user_message(text)
        elif source == "max":
            logger.info(f"[MAX] {text}")
            if self.gui:
                self.gui.add_max_message(text)
        else:
            logger.info(f"[SYS] {text}")
            if self.gui:
                self.gui.add_system_message(text)

    def _log_plan(self, plan_json: str):
        """Log an action plan."""
        logger.info(f"[PLAN] {plan_json}")
        if self.gui:
            self.gui.add_plan(plan_json)

    def _log_result(self, action_type: str, success: bool, message: str):
        """Log an action result."""
        status = "OK" if success else "FAIL"
        logger.info(f"[RESULT] {action_type}: {status} — {message}")
        if self.gui:
            self.gui.add_result(action_type, success, message)

    def _set_status(self, status: str, text: str = ""):
        """Update status display."""
        if self.gui:
            self.gui.set_status(status, text)

    def cleanup(self):
        """Clean up all resources."""
        self.stop()
        self.ai.close()
        self.memory.close()
        logger.info("Orchestrator cleaned up")
