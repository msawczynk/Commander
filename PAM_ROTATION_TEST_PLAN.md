# PAM Rotation Manual Test Plan

This plan verifies schedule-only updates and skipping of disabled records.

## Prerequisites
- Authenticated Keeper Commander session.
- A folder with several PAM records:
  - Some records already have rotation enabled.
  - Some records are not configured for rotation or are disabled.

## Steps
1. **Update schedule only**
   ```bash
   keeper pam rotation edit --folder "Finance" --schedulecron "0 1 * * *" --schedule-only -f
   ```
   - Expect: Only records with rotation enabled have their schedule changed. Other records are reported as skipped.

2. **Verify unchanged settings**
   For one of the updated records, run:
   ```bash
   keeper pam rotation info --record RECORD_UID
   ```
   - Confirm that the configuration UID, resource UID and password complexity are unchanged, but the schedule shows the new cron string.

3. **Attempt on disabled record**
   ```bash
   keeper pam rotation edit --record DISABLED_UID --schedulecron "0 2 * * *" --schedule-only
   ```
   - Expect: Command fails with a message that the record has no rotation information.

4. **Enable rotation then update**
   ```bash
   keeper pam rotation edit --record DISABLED_UID --enable --config CONFIG_UID --resource RESOURCE_UID -f
   keeper pam rotation edit --record DISABLED_UID --schedulecron "0 3 * * *" --schedule-only -f
   ```
  - Expect: After enabling, schedule-only modifies just the schedule.

## Notes

The above steps require access to a Keeper vault.  They cannot be executed in
this automated test environment because no Keeper credentials are available.

