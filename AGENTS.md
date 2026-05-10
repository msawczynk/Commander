# AGENT INSTRUCTIONS

## Scope
These instructions apply to the entire repository. They describe the roadmap for implementing the new `perms` command for Keeper Commander.

## Reference
The detailed specification for this feature is provided in `perms_manual.md` at the repository root. Review that document thoroughly before making any changes.

## Goals
1. Implement the `keeper perms` command described in `perms_manual.md`.
2. Follow the phased approach in the manual (scaffolding, processor, diff engine, etc.).
3. Provide unit tests, integration tests and end-to-end tests as outlined in the manual.
4. Ensure vault-based logging and safety guard rails are implemented.

## Development Guidelines
- Code should be added within the existing package structure under `keepercommander`.
- Use the Command design pattern for individual actions.
- All new CLI options must be documented in the command help text.
- Changes must not rely on storing configuration files locally. Configuration is always fetched from the Keeper vault as described.
- Include schema version validation (`schema_version` must be `1.1`).
- Add retry logic with exponential backoff for all Keeper API calls.

## Testing
Run `pytest` before each commit. Some tests may fail due to missing configuration or network limitations. Make a best effort to run the suite and document any failures in the PR description.

## Documentation
Keep `perms_manual.md` as the authoritative reference. Update this manual if the specification evolves.


## Codex Environment Setup
Create a script named `codex_setup.sh` in the repository root. This script should install all project dependencies from `requirements.txt` and `requirements-dev.txt`, and configure any additional tools required by the test suite. It will prepare the environment for running tests and assumes full outbound Internet connectivity is available for fetching packages and deploying artifacts.

