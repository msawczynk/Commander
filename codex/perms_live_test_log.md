# `perms` Live Test Attempt

Attempted to run `keeper whoami` and the `perms` integration tests using the
default configuration at `~/.keeper/config.json`. Commander prompted for an SSO
login URL, indicating that automatic login details were not present. As a
result, the tests could not proceed and no changes were made to the Keeper
Vault.

## July 21, 2025

Tried running `pytest -q tests/test_perms_live.py -m integration` with the
updated credentials. Commander still prompted for an SSO login URL and the tests
were unable to proceed automatically.
