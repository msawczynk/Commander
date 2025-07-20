# Keeper Commander with Permissions Automation Integration

## Features
- **template**: Generate a CSV template based on your vault's records and teams.
- **validate**: Validate a CSV file before applying permissions.
- **apply**: Apply permissions from a CSV file (with optional --dry-run for simulation).

All data (CSVs, logs) is stored securely in the Keeper vault.

## Usage
The `perms` command has three subcommands:

### Generate Template
```
python keeper.py perms template <output_csv> [--vault-only]
```
- Creates a CSV with columns for Record UID, Title, Folder Path, and one column per team.
- Stores the template as an attachment in the vault's "Perms Config" record.
- With --vault-only, generates and stores directly in vault without local file.

### Validate CSV
```
python keeper.py perms validate <csv_path> [--vault-csv <attachment_title>]
```
- Checks if the CSV file exists and is valid (basic validation; expand as needed).
- With --vault-csv, downloads attachment from Perms Config by title to temp, validates, deletes temp.

### Apply Permissions
```
python keeper.py perms apply <csv_path> [--dry-run] [--interactive] [--root <root_folder>] [--vault-csv <attachment_title>]
```
- Applies permissions from the CSV to records in the vault.
- Creates folder structure under "[Perms]" root (customizable with --root).
- Shares records to team folders with specified permissions (e.g., "ro" for read-only).
- --dry-run simulates without changes.
- --interactive enables prompts for config folder/record names (default: non-interactive with defaults).
- With --vault-csv, downloads attachment from Perms Config by title to temp, applies, deletes temp.
- Logs applied to vault if not dry-run.

## Example CSV
```
Record UID,Title,Folder Path,Admin Team
p4aON3q0kckkPAbRsJQTjw,Client4 DigitalOcean,/Test,ro
```
- Applies read-only permissions for "Admin Team" to the record in /Test path.

## Testing
- Use --dry-run for safe testing.
- Run in the activated venv with `python keeper.py`.
- Example test sequence:
  ```
  python keeper.py perms template test_template.csv
  python keeper.py perms validate test.csv
  python keeper.py perms apply test.csv --dry-run
  ```

## Notes
- Requires a Keeper account with teams and records.
- Permissions levels: ro (read-only), rw (edit), rws (edit+share), mgr (manage records), admin (full).




