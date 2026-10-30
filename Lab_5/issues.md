# Lab 5 – Issues Found (parking_system.py)

**Name:** Ashith Rao K  **SRN:** PES1UG24CS559
Line numbers refer to the ORIGINAL file. Ordered high → low severity.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Expired permit never flagged (date-format mismatch + bare except) | Bug (High) | 25-30, 51-52, 60 | `setExpiry` stores `"01/01/2020"` but `is_expired` parses `%Y-%m-%d`. The `ValueError` is swallowed by `except:` which returns `False`, so an expired permit is treated as valid and `scan_zone` doesn't flag it (seen in program output). | Validate date format in `set_expiry`; in `is_expired` catch only `(KeyError, ValueError)` and fail closed (return `True`). |
| Mutable default argument `zone_records=[]` | Bug (Medium) – Pylint W0102 | 9 | The list is created once and shared across all calls, so records leak between calls. | Default to `None`, create a new list inside the function. |
| Bare `except:` (×4) | Bug / Style (Medium) – Pylint W0702, Flake8 E722 | 16, 22, 29, 43 | Catches everything incl. `KeyboardInterrupt`; hides real errors (this is what masked the date bug). | Catch specific exceptions (`ValueError`, `KeyError`, `FileNotFoundError`, `json.JSONDecodeError`, `OSError`). |
| Try/except/pass in `revoke_permit` | Security (Low) – Bandit B110 | 22-23 | Failure is silently ignored; caller can't tell if anything was revoked. | Use `permits.pop(plate, None)` and return a bool; report in `main`. |
| No input validation on `register_permit` | Bug (Medium) | 9-17, 58-60 | Accepts zone `"Z"`, empty plate `""` and `None` plate; garbage permits get saved (`None` becomes key `"null"` in JSON). | Validate plate is non-empty string and zone is in `ZONES`; raise `ValueError`; `main` catches and prints "Rejected". |
| "Enter to skip" actually revokes `""` | Bug (Medium) | 62-63 | Pressing Enter calls `revoke_permit("")`, deleting the bogus empty-plate permit instead of skipping. | `.strip()` the input and only call revoke if non-empty. |
| `random` used for permit numbers | Security (Low) – Bandit B311 | 11 | `random` is predictable; permit numbers can be guessed. | Use `secrets.randbelow(90000) + 10000`. |
| Files opened without `with` / encoding | Quality (Medium) – Pylint R1732, W1514 | 42, 47 | `json.load(open(file))` never closes the handle; platform-dependent encoding. | `with open(file, encoding="utf-8") as handle:`. |
| `global` statement | Style – Pylint W0603 | 40 | Rebinds module global. | Mutate in place: `permits.clear()` + `permits.update(loaded)`. |
| Corrupt DB silently becomes empty | Bug (Medium) | 42-45 | Bad/missing file → `{}` silently, next save overwrites the old data. | Ignore only `FileNotFoundError`; warn on `OSError`/`JSONDecodeError`. |
| Expiry compared as datetime, not date | Bug (Low) | 28 | Permit expiring "today" counts as expired from 00:00 onward. | Compare `.date()` with `date.today()`. |
| `setExpiry` crashes on unknown plate | Bug (Low) | 52 | `KeyError` if plate has no permit. | Check membership, raise clear `KeyError`; handled in `main`. |
| `setExpiry` not snake_case | Style – Pylint C0103 | 51 | Violates PEP 8 naming. | Rename to `set_expiry`. |
| Missing docstrings | Style – Pylint C0114/C0116 | 1, 9, 19, 25, 32, 39, 46, 51, 54 | Module and 8 functions undocumented. | Add module and function docstrings. |
| Line too long / blank lines | Style – Flake8 E501, E302, E305; Pylint C0301 | 13, 27, 62, many | Lines > 79 chars; 1 blank line between functions instead of 2. | Reformat to PEP 8. |
| `main()` runs on import | Quality | 68 | Importing the module executes the program. | `if __name__ == "__main__":` guard. |

## Before vs After

| Tool | Before | After |
|------|--------|-------|
| Pylint | 6.32/10 (21 messages) | **10.00/10** |
| Bandit | 2 issues (B311, B110) | **0 issues** |
| Flake8 | 16 violations | **0 violations** |
