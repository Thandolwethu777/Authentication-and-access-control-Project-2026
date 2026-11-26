-- This file is safe to open as an administrator. No restricted probe runs here.
-- From PowerShell run: .\.venv\Scripts\python.exe test_deny.py
-- Each case opens a new TLS session and checks CURRENT_USER() and CURRENT_ROLE().
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Run test_deny.py for authenticated per-account assertions';
