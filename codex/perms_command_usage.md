# `perms` Command Usage

The `perms` command automates record permissions inside Keeper. It provides three subcommands:

- `perms template [OUTPUT] [--vault-only]`
- `perms validate [CSV_PATH] [--vault-csv TITLE]`
- `perms apply [CSV_PATH] [--dry-run] [--interactive] [--root NAME] [--vault-csv TITLE]`

## `template`
Generates a CSV template listing available records and teams. The CSV contains `Record UID`, `Title`, `Folder Path`, followed by a column for each team. Use it to specify permission levels per team.

Options:
- `OUTPUT`: Path to save the CSV locally.
- `--vault-only`: Write the template directly to a vault record attachment rather than a local file.

## `validate`
Validates a permissions CSV file before applying changes. Validation checks the required columns, verifies team names in the vault and ensures permission values are valid.

Options:
- `CSV_PATH`: Path to the CSV file.
- `--vault-csv TITLE`: Download the specified attachment from the "Perms Config" record in the vault and validate it.

## `apply`
Applies permissions from a CSV file. Each row specifies a record and permission levels for teams. Folders are automatically created under a root folder (default `[Perms]`). Team lookups are case-insensitive and the configuration record is recreated automatically if missing.

Options:
- `CSV_PATH`: Path to the CSV file with permissions.
- `--dry-run`: Parse the CSV and display actions without making changes.
- `--interactive`: Prompt for folder and record names when creating configuration entries.
- `--root NAME`: Custom root folder for created folder structure.
- `--vault-csv TITLE`: Use a CSV attachment from the "Perms Config" record.

### Permission Levels
The following values map to specific permission flags:

| Level | Can Edit | Can Share | Manage Records | Manage Users |
|-------|---------|-----------|----------------|--------------|
| `ro`  | ✗       | ✗         | ✗              | ✗            |
| `rw`  | ✓       | ✗         | ✗              | ✗            |
| `rws` | ✓       | ✓         | ✗              | ✗            |
| `mgr` | ✓       | ✓         | ✓              | ✗            |
| `admin` | ✓     | ✓         | ✓              | ✓            |

### Example Workflow
1. Generate a template: `perms template perms.csv`
2. Fill in permission levels per team.
3. Validate the file: `perms validate perms.csv`
4. Apply permissions: `perms apply perms.csv`

### Recent Improvements
The command now validates CSV content thoroughly, matches team names case-insensitively and automatically recreates the configuration record if it is missing.

