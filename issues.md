# Issues found in attendance_tracker.py

Line numbers refer to the original file. Severity is from the Bandit report; Pylint and Flake8 do not rate severity, so I ranked those myself. Results: Bandit 8 issues to 0, Flake8 25 to 0, Pylint 4.55/10 to 9.88/10.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| SSL certificate check disabled (B501, High) | Security | 60 | `requests.post(..., verify=False)` turns off certificate validation, so the ERP connection can be intercepted (man-in-the-middle). | Removed `verify=False` so certificates are verified by default. |
| Shell command with wildcard (B609 High, B602 Low, B607 Low) | Security | 64 | `subprocess.Popen("tar -czf reports_backup.tgz *.csv", shell=True)` runs through the shell with a wildcard and a partial executable path, which allows command or argument injection through file names. | Removed subprocess completely. Backup now uses the `tarfile` module with `glob.glob("*.csv")`. |
| Hardcoded API key | Security | 12 | The live ERP key was written in the source code and would be pushed to GitHub. Not flagged by the tools; found by reading the code. | Read the key from the `ERP_API_KEY` environment variable. |
| Request without timeout (B113, Medium; Pylint W3101) | Security / Bug | 60 | `requests.post` has no timeout, so the program can hang forever if the server does not answer. | Added `timeout=10`. |
| Function call with `shell=True` (B604, Medium) | Security | 73 | `scheduleReminders` passes `shell=True` to `runJob`. | Changed it to `shell=False`. |
| Outdated TLS 1.0 default (Bandit, Medium) | Security | 66 | `legacyChannel(version=ssl.PROTOCOL_TLSv1)` defaults to the deprecated, insecure TLS 1.0 protocol. | Replaced with `ssl.create_default_context()`. |
| `subprocess` import (B404, Low) | Security | 5 | Importing subprocess is flagged because of the risks of running external commands. | Import removed after the tarfile change. |
| CSV formula injection | Security / Bug | 54, 77 | Student name `=HYPERLINK(...)` is written to the CSV as-is, and Excel would run it as a formula. Not flagged by the tools; found by reading the demo output. | Added `safe_cell()`, which puts a `'` before values starting with `=`, `+`, `-` or `@`. |
| Mutable default argument (Pylint W0102) | Bug | 18 | `register={}` is created once and shared between all calls, so data leaks between calls. | Default is now `None`; a new dict is created inside the function. The demo passes its own register. |
| Eligibility off-by-one | Bug | 30 | `percentage > 75` means exactly 75% is not eligible, but the demo printed `False` for "Is 75% eligible?". | Changed to `percentage >= MIN_ATTENDANCE`. |
| Division by zero | Bug | 27 | `attendancePercentage` crashes with `ZeroDivisionError` for a student with no records. | Return 0 when there are no records. |
| `shortageList` returns `None` | Bug | 37-39 | Returns `None` instead of an empty list when nobody has a shortage, which breaks callers that loop over it. | Always return a list (list comprehension). |
| Unnormalised dates | Bug | 82 | Date `2026-9-3` does not match the `YYYY-MM-DD` format, so `latestDate` compared strings and returned a wrong "latest" date. | `mark_attendance` now parses and reformats every date to `YYYY-MM-DD`. |
| File not closed safely (Pylint R1732, W1514) | Code quality | 50 | `open()` without `with` and without an encoding; the file stays open if an error occurs. | Used `with open(path, "w", encoding="utf-8", newline="")`. |
| Unused imports (Flake8 F401, Pylint W0611) | Style | 1, 4, 6 | `os`, `json` and `datetime` were imported but not used. | Removed them (`os` is used again for the API key; `datetime` is used for date parsing). |
| Comparison to False (E712, Pylint C0121, R1719) | Style | 30, 35 | `== False` and `True if ... else False` are not Pythonic. | Used `not ...` and returned the comparison directly. |
| Missing blank lines and long lines (E302, E305, E501) | Style | many | 25 Flake8 findings: missing blank lines between functions and lines over 79 characters. | Added blank lines and wrapped long lines. |
| Naming and docstrings (Pylint C0103, C0114, C0116) | Code quality | 1, 15-75 | camelCase function names and no docstrings anywhere. | Renamed functions to snake_case and added a module docstring and function docstrings. |
| Generator and comprehension simplifications (R1729, R1721, C0206) | Code quality | 43, 46, 53 | List built inside `any()`, an unneeded comprehension, and looping over dict keys. | Used a generator, `max()` directly, and `.items()`. |
| `main()` runs on import | Code quality | 96 | `main()` was called at module level, so importing the file runs the demo. | Wrapped it in `if __name__ == "__main__":`. |
