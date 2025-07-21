# Helper Function Guidelines

This document summarizes how helper functions are typically added in the project.

* Place new helpers near related code, either in `keepercommander/api.py` or within `keepercommander/commands/helpers`.
* Use a `# type:` comment after the function declaration to indicate parameter and return types.
* A short docstring is optional but recommended when the function performs non-trivial logic.
* Separate helper definitions with a blank line for readability.
* Standalone helper functions usually do not require an entry in `__init__.py`.
