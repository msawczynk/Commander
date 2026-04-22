# `pam launch`

Launch a terminal connection to a PAM resource (`pamMachine`, `pamDirectory`, `pamDatabase`)
over SSH, Telnet, Kubernetes, MySQL, PostgreSQL, or SQL Server. The Gateway brokers
the connection via WebRTC + Guacamole; Commander only drives the client side.

```
pam launch <record>
  [-cr|--credential RECORD]
  [-H|--host HOST:PORT]
  [-hr|--host-record RECORD]
  [-j|--jit]
  [-nti|--no-trickle-ice]
```

## Credential modes

Commander negotiates one of four credential modes with the Gateway:

| Mode | When | How the credential is obtained |
|---|---|---|
| `linked` | Record has a DAG-linked `pamUser` | Gateway looks up the credential via DAG |
| `userSupplied` | `allowSupplyUser`/`allowSupplyHost` + `-cr` | Commander encrypts a `ConnectAs` payload to the Gateway's public key |
| `ephemeral` | `-j/--jit` + `pamSettings.options.jit_settings.create_ephemeral: true` | Gateway creates a short-lived account for the session, tears it down afterwards |
| *(unset)* | Fallback | Gateway reads login/password directly off the `pamMachine` record |

## Just-in-time (JIT) access — `-j / --jit`

Commander supports the two JIT flavors defined by the declarative schema
(`keeper-pam-declarative/manifests/pam-environment.v1.schema.json` → `$defs.jit_settings`):

- **Ephemeral account** (`create_ephemeral: true`) — Gateway creates a fresh account on the
  target, optionally joining a domain, and deletes it on disconnect.
- **Privilege elevation** (`elevate: true`) — Gateway adds the launch credential to an
  elevated group/role for the session and reverts afterwards. Commander still emits the
  linked credential so the Gateway knows who to elevate.
- **Both** (`create_ephemeral: true` + `elevate: true`) — ephemeral account is provisioned
  *and* immediately elevated.

Minimal record shape:

```yaml
pam_settings:
  options:
    jit_settings:
      create_ephemeral: true
      ephemeral_account_type: linux      # linux | mac | windows | domain
  connection:
    protocol: ssh
    administrative_credentials_uid_ref: <admin-record-uid>
```

For `ephemeral_account_type: domain` the record **must** also carry
`pam_directory_uid_ref`; Commander rejects the launch otherwise, matching the
declarative validator.

### CLI examples

```bash
# Ephemeral Linux SSH account
keeper pam launch my-linux-host -j

# Ephemeral domain account (Windows host joined to AD)
keeper pam launch prod/win-rdp -j

# Privilege elevation against an existing linked account
keeper pam launch db01 -j
```

### Precedence rules (match Web Vault)

1. `allowSupplyHost` wins over JIT. `pam launch -j` on a record with
   `allowSupplyHost: true` is rejected with a clear error — supply host+credential
   manually via `-H` / `-hr` / `-cr` instead.
2. `-j` is mutually exclusive with `-cr`, `-H`, and `-hr`. JIT provisions the
   credential itself, so overriding credential or host alongside `-j` is rejected.
3. A record that has `jit_settings` but is launched **without** `-j` behaves exactly
   as before — JIT is strictly opt-in.

### Gateway compatibility

JIT uses the Gateway's existing `credentialType` protocol extended with the `ephemeral`
value plus two optional payload blocks: `jitSettings` (ephemeral metadata) and
`jitElevation` (elevation deltas). Keys mirror the declarative schema verbatim and are
built by `_build_jit_ephemeral_payload` / `_build_jit_elevation_payload` in
`terminal_connection.py`, so adapting to any future camelCase-vs-snake_case change
is a one-function edit.
