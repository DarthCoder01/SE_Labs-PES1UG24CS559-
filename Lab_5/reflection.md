# Lab 5 – Reflection

**Name:** Ashith Rao K  **SRN:** PES1UG24CS559

**1. Which issues were the easiest and which were the hardest to fix?**
Style issues (Flake8 E302/E501, docstrings, snake_case) were easiest: mechanical and clearly described. The hardest was the expired-permit bug. No tool flagged it directly; I found it by running the program and noticing `KA01AB1234` (set to an expired date) wasn't flagged. The root cause was a date-format mismatch hidden by a bare `except`, so fixing it meant changing the design (validation + fail-closed behaviour), not just silencing a warning.

**2. Did the tools report any false positives, or issues you chose not to fix?**
Bandit B311 (`random`) is arguably low-risk for a demo, but permit numbers should not be guessable, so I fixed it with `secrets`. I didn't find real false positives; Pylint's `global-statement` and `consider-using-with` were valid. I did choose to fix more than the required four because several were connected (e.g. the bare excepts).

**3. How could static analysis be integrated into a real development workflow?**
Run Flake8/Pylint/Bandit as a pre-commit hook locally and as a required CI check (e.g. GitHub Actions) on every pull request, with a minimum Pylint score and "no Bandit medium/high" as merge gates. This catches problems before code review, so reviewers can focus on logic and design.

**4. What tangible improvements did you see in code quality, readability and robustness?**
Pylint went from 6.32 to 10.00, Bandit from 2 issues to 0, Flake8 from 16 to 0. Beyond the numbers: invalid input is now rejected with clear messages, resources are closed properly, exceptions are specific so failures are visible, the module is importable without side effects, and the expired-permit logic now actually works. Static analysis is not enough on its own, though: the most serious bug needed running the program and reading its output.
