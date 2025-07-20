# `perms` Command Improvements

The previous version of `perms_command.py` had several shortcomings. These have now been addressed as follows:

1. **CSV Validation**
   - `validate_csv` now checks column headers, verifies team names against the vault and ensures permission levels are within the allowed set.
2. **Error Handling**
   - Network failures during permission application are caught and logged. Errors no longer silently fail.
3. **Config Record**
   - The configuration record title is configurable and will be recreated automatically if missing.
4. **Team Lookup**
   - Team names are matched case-insensitively to reduce errors from typos.
5. **Scalability**
   - Team information is cached and API calls are grouped, improving performance on large CSV files.
6. **Unit Tests**
   - New tests cover validation and application logic to ensure the command works end-to-end.
7. **Interactive Mode**
   - Interactive prompts remain optional and are disabled by default for non-interactive use cases.
