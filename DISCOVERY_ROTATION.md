# Discovery Rotation Module Overview

`keepercommander.commands.discoveryrotation` defines the majority of Keeper's
PAM related CLI commands.  The module registers the top level `pam` group and
implements subcommands for gateway management, configuration management and
password rotation.  This document focuses on the `pam rotation edit` command and
provides an overview of how the module orchestrates PAM rotation updates.

## Purpose

The command configures password rotation settings for PAM records. It can target a single record via `--record` or all records in a folder via `--folder`. The settings include enabling or disabling rotation, selecting a PAM Configuration, defining password complexity, linking the record to a resource, and setting rotation schedules.

The command is mapped to the `pam rotation edit` CLI verb in `PAMRotationCommand` within `discoveryrotation.py`.

## Key Steps

1. **Resolve record or folder** – The command resolves record UIDs or folder UIDs from CLI arguments. When a folder is specified, it traverses the folder tree and gathers records matching the provided title pattern.
2. **Validate record types** – Only PAM record types (`pamDatabase`, `pamDirectory`, `pamMachine`, `pamUser`, `pamRemoteBrowser`) are processed. Other records are skipped with an error message.
3. **Load PAM Configuration** – If `--config` points to a PAM Configuration record, it is loaded and used as the source of default schedule and resource information.
4. **Parse schedule** – The command accepts schedule definitions either as JSON (`--schedulejson`) or cron strings (`--schedulecron`). Cron values must contain exactly five components: minute, hour, day of month, month, and day of week. Invalid cron strings raise `CommandError`.
5. **Determine password complexity** – Complexity rules are parsed from the `--complexity` flag. They are validated and then encrypted before being sent to the router service.
6. **Build router requests** – For each target record, a `RouterRecordRotationRequest` protobuf is created containing schedule, complexity and resource linkage information. These requests are submitted to the PAM Router service via `router_set_record_rotation_information`.
7. **Confirmation prompts** – When multiple records will be modified, the command prints a summary table and prompts the user before performing the operation unless `--force` is used.

## Module Structure

`discoveryrotation.py` groups related PAM commands under several classes:

- **`PAMControllerCommand`** – registers the `pam` top level command and
  subcommands for gateways, configurations, rotation and other helper actions.
- **`PAMCreateRecordRotationCommand`** – implements `pam rotation edit`.  This is
  the most complex command and performs schedule parsing, validation and request
  submission described above.
- **`PAMListRecordRotationCommand`** – displays existing rotation settings for
  PAM user records.
- **`PAMGatewayListCommand`** – lists available PAM gateways.  Other helper
  classes handle discovery jobs, debugging and service configuration.

Rotation editing uses helper functions such as `TunnelDAG` to ensure records are
linked to the correct configuration and resource, and `router_set_record_rotation_information`
to persist the changes via Keeper's router service.

## Schedule Only Mode

The `--schedule-only` flag updates the rotation schedule without modifying the
resource link, password complexity, or enable/disable status. When used with
`--folder`, records that do not currently have rotation enabled are skipped to
avoid accidental configuration changes.

Example:

```bash
keeper pam rotation edit --folder Finance --schedulecron "0 1 * * *" --schedule-only -f
```

This updates the cron schedule on all PAM records in the *Finance* folder that
already have rotation enabled.

## Additional Edge Cases

- Records representing user credentials may be stored in folders separate from
  their associated resources. When scheduling rotations for a folder, ensure
  that each record is still linked to the correct resource. The command now
  skips records that have rotation disabled when `--schedule-only` is used on a
  folder.

## Edge Cases

- Supplying both `--record` and `--folder` results in a `CommandError`.
- Specifying a cron expression with fewer or more than five fields triggers a `CommandError` (see unit test `TestCronScheduleParsing`).
- If a target record has no associated resource and none is provided via `--resource`, the command aborts with a message instructing how to associate a resource.
- Attempting to enable rotation when the resource lacks admin credentials also results in an error.
- Using `--schedule-only` on a folder skips records that either have rotation
  disabled or have never been configured for rotation.  Re-enable or configure
  the record first if schedule-only is desired.

## Live Testing

The command requires an authenticated session with a Keeper vault and appropriate PAM records. Attempting to run the command without valid credentials will fail during login. In this environment no Keeper vault configuration is available, so a live test cannot be performed. Running:

```bash
keeper pam rotation edit --record RECORD_UID --enable
```

results in an authentication error because no config or login is present.

