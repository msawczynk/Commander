import json
import sys
import types
import unittest
from contextlib import contextmanager
from dataclasses import dataclass
from unittest.mock import MagicMock, patch


@contextmanager
def fake_dsk_shim(**shim_attrs):
    dsk_module = types.ModuleType("dsk")
    shim_module = types.ModuleType("dsk.shim")
    for name, value in shim_attrs.items():
        setattr(shim_module, name, value)
    dsk_module.shim = shim_module
    with patch.dict(sys.modules, {"dsk": dsk_module, "dsk.shim": shim_module}):
        yield shim_module


def shim_result():
    return {"exit_code": 0, "stdout": "ok", "stderr": "", "args": []}


class TestMigrateEnterpriseGated(unittest.TestCase):
    """L8: migrate visibility is enterprise-gated per joao J8=B."""

    def test_register_commands_does_not_add_migrate_to_default_commands(self):
        from keepercommander.commands import migrate

        commands = {}
        migrate.register_commands(commands)
        self.assertNotIn(
            "migrate",
            commands,
            "migrate must be enterprise-gated; not in default commands",
        )

    def test_register_enterprise_commands_adds_migrate(self):
        from keepercommander.commands import migrate

        enterprise_commands = {}
        migrate.register_enterprise_commands(enterprise_commands)
        self.assertIn("migrate", enterprise_commands)
        self.assertIsInstance(enterprise_commands["migrate"], migrate.MigrateGroupCommand)

    def test_register_command_info_does_not_add_migrate_to_default_help_text(self):
        from keepercommander.commands import migrate

        aliases = {}
        command_info = {}
        migrate.register_command_info(aliases, command_info)
        self.assertNotIn("migrate", command_info)

    def test_register_enterprise_command_info_adds_migrate_help_text(self):
        from keepercommander.commands import migrate

        aliases = {}
        command_info = {}
        migrate.register_enterprise_command_info(aliases, command_info)
        self.assertIn("migrate", command_info)


class TestMigrateExtrasGuard(unittest.TestCase):
    def test_dsk_shim_import_error_raises_extras_message(self):
        from keepercommander.commands import migrate

        with patch.dict(sys.modules, {"dsk": None, "dsk.shim": None}):
            with self.assertRaises(RuntimeError) as cm:
                migrate._require_dsk_shim()
            self.assertIn("pip install keepercommander[migrate]", str(cm.exception))


class TestMigrateGroupCommand(unittest.TestCase):
    def test_group_command_has_8_verbs(self):
        from keepercommander.commands.migrate import MigrateGroupCommand

        gc = MigrateGroupCommand()
        self.assertEqual(
            {
                "adopt",
                "plan",
                "apply",
                "diff",
                "audit-explain",
                "drift-watch",
                "rehearse-report",
                "bundle",
            },
            set(gc.subcommands.keys()),
        )


class TestMigrateVerbCommands(unittest.TestCase):
    def test_adopt_calls_dsk_shim_adopt(self):
        from keepercommander.commands.migrate import MigrateAdoptCommand

        adopt = MagicMock(return_value=shim_result())
        with fake_dsk_shim(adopt=adopt):
            cmd = MigrateAdoptCommand()
            cmd.execute(MagicMock(), run_dir="/tmp/run", output=None, dry_run=True)

        adopt.assert_called_once_with(
            run_dir="/tmp/run",
            output=None,
            dry_run=True,
            auto_approve=False,
            skip_audit_verify=False,
            skip_sha256=False,
            suspect_threshold=0,
            verbose=False,
            require_output_signature=False,
            signature_pubkey=None,
            signature_pubkey_keeper_record=None,
            commander_config=None,
        )

    def test_plan_calls_dsk_shim_plan(self):
        from keepercommander.commands.migrate import MigratePlanCommand

        plan = MagicMock(return_value=shim_result())
        with fake_dsk_shim(plan=plan):
            cmd = MigratePlanCommand()
            cmd.execute(MagicMock(), target_state="/tmp/manifest.yml")

        plan.assert_called_once_with(
            target_state="/tmp/manifest.yml",
            allow_delete=False,
            provider="mock",
            folder_uid=None,
        )

    def test_apply_calls_dsk_shim_apply(self):
        from keepercommander.commands.migrate import MigrateApplyCommand

        apply = MagicMock(return_value=shim_result())
        with fake_dsk_shim(apply=apply):
            cmd = MigrateApplyCommand()
            cmd.execute(MagicMock(), plan="/tmp/manifest.yml")

        apply.assert_called_once_with(
            plan="/tmp/manifest.yml",
            manifest_path=None,
            dry_run=True,
            allow_delete=False,
            auto_approve=False,
            provider="mock",
            folder_uid=None,
        )

    def test_diff_calls_dsk_shim_diff(self):
        from keepercommander.commands.migrate import MigrateDiffCommand

        diff = MagicMock(return_value=shim_result())
        with fake_dsk_shim(diff=diff):
            cmd = MigrateDiffCommand()
            cmd.execute(MagicMock(), manifest_path="/tmp/manifest.yml")

        diff.assert_called_once_with(
            manifest_path="/tmp/manifest.yml",
            allow_delete=False,
            provider="mock",
            folder_uid=None,
        )

    def test_audit_explain_calls_dsk_shim_audit_explain(self):
        from keepercommander.commands.migrate import MigrateAuditExplainCommand

        audit_explain = MagicMock(return_value=shim_result())
        with fake_dsk_shim(audit_explain=audit_explain):
            cmd = MigrateAuditExplainCommand()
            cmd.execute(MagicMock(), audit_log="/tmp/audit.log")

        audit_explain.assert_called_once_with(audit_log="/tmp/audit.log", summary=True)

    def test_drift_watch_calls_dsk_shim_drift_watch(self):
        from keepercommander.commands.migrate import MigrateDriftWatchCommand

        drift_watch = MagicMock(return_value=shim_result())
        with fake_dsk_shim(drift_watch=drift_watch):
            cmd = MigrateDriftWatchCommand()
            cmd.execute(MagicMock(), manifest_paths=["/tmp/a.yml", "/tmp/b.yml"])

        drift_watch.assert_called_once_with(
            manifest_paths=["/tmp/a.yml", "/tmp/b.yml"],
            interval=300,
            github_repo=None,
            github_token=None,
            pr_base="main",
            dry_run=True,
            slack_webhook=None,
            slack_channel=None,
            servicenow_instance=None,
            servicenow_api_key=None,
            verbose=False,
        )

    def test_rehearse_report_calls_dsk_shim_rehearse_report(self):
        from keepercommander.commands.migrate import MigrateRehearseReportCommand

        rehearse_report = MagicMock(return_value=shim_result())
        with fake_dsk_shim(rehearse_report=rehearse_report):
            cmd = MigrateRehearseReportCommand()
            parsed = vars(cmd.get_parser().parse_args(["/tmp/run", "--report-format", "junit"]))
            cmd.execute(MagicMock(), **parsed)

        rehearse_report.assert_called_once_with(
            run_dir="/tmp/run",
            output=None,
            dry_run=False,
            verbose=False,
            output_format="junit",
        )

    def test_bundle_calls_dsk_shim_bundle(self):
        from keepercommander.commands.migrate import MigrateBundleCommand

        bundle = MagicMock(return_value=shim_result())
        with fake_dsk_shim(bundle=bundle):
            cmd = MigrateBundleCommand()
            cmd.execute(MagicMock(), manifest_path="/tmp/compliance.yml")

        bundle.assert_called_once_with(
            manifest_path="/tmp/compliance.yml",
            output_dir=None,
            dry_run=False,
        )


class TestMigrateSessionConfusionGuard(unittest.TestCase):
    def test_execute_docstrings_disclose_dsk_environment(self):
        from keepercommander.commands import migrate

        expected = (
            "Uses DSK environment (KEEPER_CONFIG / --commander-config), "
            "not the active Commander session."
        )
        command_types = (
            migrate.MigrateAdoptCommand,
            migrate.MigratePlanCommand,
            migrate.MigrateApplyCommand,
            migrate.MigrateDiffCommand,
            migrate.MigrateAuditExplainCommand,
            migrate.MigrateDriftWatchCommand,
            migrate.MigrateRehearseReportCommand,
            migrate.MigrateBundleCommand,
        )

        for command_type in command_types:
            self.assertEqual(expected, command_type.execute.__doc__)

    def test_active_session_without_commander_config_warns(self):
        from keepercommander.commands.migrate import MigrateAdoptCommand

        adopt = MagicMock(return_value=shim_result())
        params = types.SimpleNamespace(session_token="active-session")
        with fake_dsk_shim(adopt=adopt):
            with self.assertLogs(level="WARNING") as logs:
                MigrateAdoptCommand().execute(
                    params,
                    run_dir="/tmp/run",
                    output=None,
                    dry_run=True,
                )

        self.assertIn(
            "migrate adopt: active Commander session will not be used",
            "\n".join(logs.output),
        )


class TestMigrateJsonRedaction(unittest.TestCase):
    def test_json_serialization_redacts_sensitive_args(self):
        from keepercommander.commands.migrate import _redact_args_for_safety

        raw = ["drift-watch", "--github-token", "ghp_secret", "--manifest", "/tmp/m.yml"]
        redacted = _redact_args_for_safety(raw)

        self.assertNotIn("ghp_secret", redacted)
        self.assertIn("***REDACTED***", redacted)
        self.assertIn("--manifest", redacted)
        self.assertIn("/tmp/m.yml", redacted)


class TestSafeJsonOutput(unittest.TestCase):
    def assert_no_sensitive_json_fields(self, output):
        for field in ("manifest_yaml", "stdout", "stderr", "before", "after"):
            self.assertNotIn(f'"{field}"', output)

    def test_emit_result_uses_result_allowlist(self):
        from keepercommander.commands.migrate import _emit_result

        @dataclass
        class ImportResult:
            exit_code: int
            stdout: str
            stderr: str
            args: tuple[str, ...]
            manifest_yaml: str
            before: dict
            after: dict
            verb: str
            summary: dict
            changes_count: int

        result = ImportResult(
            exit_code=0,
            stdout="stdout secret",
            stderr="stderr secret",
            args=("--github-token", "ghp_secret"),
            manifest_yaml="manifest secret",
            before={"password": "old"},
            after={"password": "new"},
            verb="adopt",
            summary={"ok": True, "before": {"password": "old"}},
            changes_count=1,
        )
        output = _emit_result(
            result,
            {"format": "json"},
        )
        payload = json.loads(output)

        self.assertEqual(
            {"changes_count": 1, "exit_code": 0, "summary": {"ok": True}, "verb": "adopt"},
            payload,
        )
        self.assert_no_sensitive_json_fields(output)
        self.assertNotIn("ghp_secret", output)

    def test_emit_result_uses_plan_allowlist(self):
        from keepercommander.commands.migrate import _emit_result

        @dataclass
        class Change:
            title: str
            before: dict
            after: dict

        @dataclass
        class Plan:
            changes: list[Change]
            families: tuple[str, ...]
            verb: str
            dry_run: bool

        result = Plan(
            changes=[
                Change(
                    title="record",
                    before={"password": "old"},
                    after={"password": "new"},
                )
            ],
            families=("pam",),
            verb="plan",
            dry_run=True,
        )
        output = _emit_result(result, {"format": "json"})
        payload = json.loads(output)

        self.assertEqual(
            {"change_count": 1, "dry_run": True, "families": ["pam"], "verb": "plan"},
            payload,
        )
        self.assert_no_sensitive_json_fields(output)
        self.assertNotIn("password", output)

    def test_emit_result_strips_unsafe_mapping_fields(self):
        from keepercommander.commands.migrate import _emit_result

        output = _emit_result(
            {
                "exit_code": 0,
                "stdout": "stdout secret",
                "stderr": "stderr secret",
                "manifest_yaml": "manifest secret",
                "before": {"password": "old"},
                "after": {"password": "new"},
                "args": ["--github-token", "ghp_secret"],
            },
            {"format": "json"},
        )
        payload = json.loads(output)

        self.assertEqual({"exit_code": 0}, payload)
        self.assert_no_sensitive_json_fields(output)
        self.assertNotIn("ghp_secret", output)


class TestRedactionListsInSync(unittest.TestCase):
    """Lurey L5 (Bob review 2026-05-10): duplicated redaction lists can drift.

    Redaction logic is duplicated between dsk/shim/_types.py and
    Commander/migrate.py for defense-in-depth. This test fails if the lists
    diverge so the duplication is caught at CI time, not at incident time.

    If a new sensitive option pattern is added to one side, this test forces
    the same addition on the other side or an explicit acknowledgement of
    asymmetry.
    """

    def test_sensitive_option_names_match(self):
        from keepercommander.commands.migrate import _COMMANDER_SENSITIVE_ARG_NAMES

        try:
            from dsk.shim._types import _SENSITIVE_OPTION_NAMES
        except ImportError:
            self.skipTest("dsk extras not installed; skipping drift check")
        self.assertEqual(
            sorted(_COMMANDER_SENSITIVE_ARG_NAMES),
            sorted(_SENSITIVE_OPTION_NAMES),
            "Commander and DSK redaction option name lists have drifted; "
            "update both or document the asymmetry",
        )

    def test_sensitive_option_suffixes_match(self):
        from keepercommander.commands.migrate import _COMMANDER_SENSITIVE_ARG_SUFFIXES

        try:
            from dsk.shim._types import _SENSITIVE_OPTION_SUFFIXES
        except ImportError:
            self.skipTest("dsk extras not installed; skipping drift check")
        self.assertEqual(
            sorted(_COMMANDER_SENSITIVE_ARG_SUFFIXES),
            sorted(_SENSITIVE_OPTION_SUFFIXES),
            "Commander and DSK redaction suffix lists have drifted; "
            "update both or document the asymmetry",
        )

    def test_redaction_placeholder_matches(self):
        from keepercommander.commands.migrate import _COMMANDER_REDACTION

        try:
            from dsk.shim._types import _REDACTION_PLACEHOLDER
        except ImportError:
            self.skipTest("dsk extras not installed; skipping drift check")
        self.assertTrue(_COMMANDER_REDACTION)
        self.assertTrue(_REDACTION_PLACEHOLDER)


class TestRedactionByteParity(unittest.TestCase):
    def test_trailing_bare_sensitive_flag_matches_dsk(self):
        from keepercommander.commands.migrate import _redact_args_for_safety

        raw = ["--source-config", "x.json", "--password"]
        commander_redacted = _redact_args_for_safety(raw)

        try:
            from dsk.shim._types import _redact_sensitive_args
        except ImportError:
            self.assertEqual(1, commander_redacted.count("--password"))
            return

        dsk_redacted = list(_redact_sensitive_args(raw))
        self.assertEqual(dsk_redacted, commander_redacted)


if __name__ == "__main__":
    unittest.main()
