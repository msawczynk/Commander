# Testing Guide

Follow these steps to run the project tests.

1. Activate the preconfigured virtual environment in the repository root:
   ```bash
   . .venv/bin/activate
   ```
   If `.venv` does not exist, create it:
   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -U pip
   ```
2. Install dependencies and dev requirements:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   pip install pytest
   pip install -e .
   ```
3. Run the tests from the repository root:
   ```bash
   pytest -q
   ```

4. Run integration tests (these modify a live Keeper account) with:
   ```bash
   pytest -m integration
   ```
   Check the Keeper Vault used for testing to confirm records and folders were created or removed as expected.


Tests may require additional configuration files found under `tests/`. Some integration tests rely on external Keeper accounts and will fail without proper credentials.
