# Reflection

**1. Which issues were the easiest to fix and which were the hardest?**

The easiest were the Flake8 issues and the simple Pylint ones: removing unused imports, adding blank lines, wrapping long lines, replacing `== False` with `not`, and adding docstrings. Most of these are mechanical and the report tells you exactly what to change. The hardest were the security issues in the backup function. Removing `shell=True` is not just a flag change, because the wildcard `*.csv` is expanded by the shell, so I had to rethink how the backup works and replaced `subprocess` with the `tarfile` module and `glob`. Fixing the mutable default argument was also tricky, because the demo depended on the shared dictionary by accident, so fixing it broke the demo until I passed the register in explicitly.

**2. Did the tools report any false positives, or miss real problems?**

Not really false positives, but some findings were low value. Bandit's B404 (importing `subprocess`) and B602/B607 are low severity warnings about risk rather than actual bugs, and `runJob` only returns a dictionary and never runs the command, so the B604 warning describes a risk that was not active in this program. The tools also missed several real problems that I only found by reading the code and the output: the hardcoded API key, the CSV formula injection in the student name, the `>` instead of `>=` that made exactly 75% not eligible, the division by zero for a student with no records, and the badly formatted date `2026-9-3`. Static analysis checks patterns, not what the program is supposed to do.

**3. How would you use static analysis tools in your own workflow?**

I would run Flake8 and Pylint regularly while writing code, ideally through the editor so problems show up immediately, and run Bandit before pushing anything. I would also add all three to a pre-commit hook or a GitHub Actions check so that code with new issues cannot be merged. I would not rely on the Pylint score alone. A score of 10/10 does not mean the code is correct, so tests and code review are still needed.

**4. What improvements did you see after fixing the issues?**

The Bandit report went from 8 issues (2 high, 3 medium, 3 low) to none, so the ERP call now verifies certificates, the secret is no longer in the source code, and there is no shell command execution. Flake8 went from 25 findings to none, and Pylint went from 4.55/10 to 9.88/10. The code is also easier to read, with consistent naming, docstrings and shorter lines. Several real bugs were fixed along the way, and the program still produces the same demo output, except that 75% is now correctly eligible and the latest date is correct.
