# Manual Testing Strategy for `perms` Command

This guide outlines how to manually test the `perms` command without relying on automated tests.

## Prerequisites
- A Keeper account with vault access and at least one team.
- Commander configured and logged in (`keeper shell` or via config file).
- Sample records and folders in the vault to work with.

## Steps
1. **Generate Template**
   - Run `perms template perms.csv` to create a CSV locally.
   - Confirm the file lists existing records and teams.
   - Run `perms template --vault-only` to store a template attachment in the vault. Verify the attachment exists in the "Perms Config" record.

2. **Populate CSV**
   - Edit `perms.csv` and set permission levels (`ro`, `rw`, `rws`, `mgr`, `admin`) for various teams.

3. **Validate CSV**
   - Execute `perms validate perms.csv` to ensure the file structure is correct.
   - Upload the CSV as an attachment and run `perms validate --vault-csv perms.csv` to validate it from the vault.

4. **Dry‑Run Apply**
   - Run `perms apply perms.csv --dry-run` to preview changes. Check the output log for expected folder paths and team names.

5. **Apply Permissions**
   - Execute `perms apply perms.csv` to apply permissions.
   - After completion, verify:
     - A root folder named `[Perms]` (or custom name) was created with team subfolders.
     - Records are shared into the appropriate team folders.
     - A log file attachment was uploaded to the "Perms Config" record.

6. **Vault Verification**
   - Browse the vault UI to confirm teams have the specified permissions on records.
   - Remove the created folders and attachments after testing if desired.

This sequence exercises the template, validation and apply workflows while confirming results directly in the vault.
