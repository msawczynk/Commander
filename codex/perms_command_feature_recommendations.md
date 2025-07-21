# `perms` Command Feature Suggestions

Based on manual testing and review, the following enhancements could improve usability:

1. **Permission Summary Report**
   - After applying permissions, generate a concise report listing records, teams and effective permission levels.
   - Store this report alongside the log attachment for auditing.

2. **CSV Export of Current Permissions**
   - Provide a flag to export existing team permissions for records, enabling a full round‑trip workflow.

3. **Granular Error Messages**
   - Include record titles and folder paths when reporting failures to apply a permission.

4. **Dry‑Run Diff Mode**
   - When `--dry-run` is specified, show the difference between current and desired permissions to help with change reviews.

5. **Configurable Log Retention**
   - Allow setting how many log attachments to keep in the vault to avoid clutter.
