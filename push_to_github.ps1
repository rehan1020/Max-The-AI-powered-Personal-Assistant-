#!/usr/bin/env pwsh
# Git push script to bypass pager issues

$env:GIT_PAGER = 'cat'
$env:GIT_EDITOR = 'cat'

cd C:\Users\30reh\Downloads\voice

# Get current status
Write-Host "Current status:"
git status --short

# Fetch from remote
Write-Host "`nFetching from remote..."
git fetch --all

# Try to rebase and then push
Write-Host "`nRebasing with remote..."
git rebase origin/main --no-edit

# Push
Write-Host "`nPushing to GitHub..."
git push origin main

Write-Host "`nDone!"
