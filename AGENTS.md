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

## Documentation Notes

Repository documentation references the [official Keeper Commander documentation](https://docs.keeper.io/secrets-manager/commander-cli/overview). Review that site for detailed usage instructions.

Additional documentation and notes are stored in the `codex` directory.

## Helper Function Guidelines

Helper functions are typically added to existing modules near related logic
(for example `keepercommander/api.py` or the modules under
`keepercommander/commands/helpers`).
They use type hint comments and may include a short docstring.

```python
def example_helper(params, uid):  # type: (KeeperParams, str) -> None
    """Describe the helper purpose."""
    ...
```

Place new helpers below existing ones with a blank line separation.
No updates to `__init__.py` files are required when adding standalone helpers.
