# `perms` Command Test Summary

Automated tests were added in `unit-tests/test_perms_command.py` to ensure the CLI integrates correctly with the `perms` subcommands. The tests mock API interactions and verify that high-level methods are invoked:

- **Template generation**
  - `perms template --vault-only` calls `generate_template` and `store_in_vault_bytes`.
  - `perms template <file>` writes to a local file and stores it in the vault.
- **Validation**
  - `perms validate --vault-csv TITLE` downloads the attachment, validates it, and prints `Valid`.
  - Invalid CSV columns or permission values cause validation to fail.
- **Apply**
  - `perms apply <file> --dry-run` invokes `apply_permissions` with the correct arguments.

All tests run with `pytest unit-tests/test_perms_command.py` and pass after patching network calls.

