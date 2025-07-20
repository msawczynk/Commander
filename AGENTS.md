# Agent Instructions

This file provides guidance for AI agents contributing to this repository.

## Testing

1. Activate the provided Python virtual environment (located at `.venv`).
   ```bash
   . .venv/bin/activate
   ```
   If the `.venv` directory does not exist, create it first:
   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -U pip
   ```
2. Install project dependencies and development tools.
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   pip install pytest
   pip install -e .
   ```
3. Run the test suite.
   ```bash
   pytest -q
   ```
   Some tests require configuration files (for example `tests/config.json`) and may fail if those files or external services are unavailable.


4. To execute integration ("live") tests, run `pytest -m integration`. These tests interact with real Keeper accounts defined in the `tests/` configuration files and modify Vault records.
   After they complete, sign in to the Keeper Vault used for testing and verify the expected changes (such as new or deleted records and folders).
   Document any observations or issues in the `codex` directory so future contributors can review the results.


## Documentation Notes

Repository documentation references the [official Keeper Commander documentation](https://docs.keeper.io/secrets-manager/commander-cli/overview). Review that site for detailed usage instructions.


All additional documentation, test results and notes should be stored in the `codex` directory so they remain versioned with the project.

