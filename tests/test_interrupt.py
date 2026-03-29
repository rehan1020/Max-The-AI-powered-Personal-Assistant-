"""Tests for interrupt handling."""

import pytest
import threading
import time
from core.execution.interrupt import InterruptHandler, INTERRUPT


class TestInterruptHandler:
    """Tests for the interrupt handler."""

    def test_initial_state(self):
        """Test interrupt is initially not set."""
        handler = InterruptHandler()
        assert not handler.is_interrupted()

    def test_interrupt_set(self):
        """Test setting interrupt."""
        handler = InterruptHandler()
        handler.interrupt()
        assert handler.is_interrupted()

    def test_interrupt_clear(self):
        """Test clearing interrupt."""
        handler = InterruptHandler()
        handler.interrupt()
        handler.clear()
        assert not handler.is_interrupted()

    def test_interrupt_check_raises(self):
        """Test check raises InterruptedError when interrupted."""
        handler = InterruptHandler()
        handler.interrupt()
        
        with pytest.raises(InterruptedError):
            handler.check()

    def test_interrupt_check_no_raise(self):
        """Test check does not raise when not interrupted."""
        handler = InterruptHandler()
        handler.check()

    def test_global_interrupt(self):
        """Test global INTERRUPT instance."""
        INTERRUPT.clear()
        assert not INTERRUPT.is_interrupted()
        
        INTERRUPT.interrupt()
        assert INTERRUPT.is_interrupted()
        
        INTERRUPT.clear()
        assert not INTERRUPT.is_interrupted()

    def test_thread_safety(self):
        """Test interrupt works across threads."""
        handler = InterruptHandler()
        results = []
        
        def set_interrupt():
            time.sleep(0.1)
            handler.interrupt()
        
        def check_interrupt():
            while not handler.is_interrupted():
                time.sleep(0.01)
            results.append(True)
        
        t1 = threading.Thread(target=set_interrupt)
        t2 = threading.Thread(target=check_interrupt)
        
        t2.start()
        t1.start()
        
        t1.join()
        t2.join()
        
        assert len(results) == 1
