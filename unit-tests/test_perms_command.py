import csv
import os
from unittest import TestCase, mock
from collections import OrderedDict

from keepercommander.commands import base
from keepercommander.cli import do_command
from keepercommander.commands.perms_command import KeeperPerms
from data_vault import get_connected_params


class TestPermsCommand(TestCase):
    def setUp(self):
        base.commands.clear()
        base.aliases.clear()
        base.command_info.clear()
        base.register_commands(base.commands, base.aliases, base.command_info)

    def test_template_vault_only(self):
        params = get_connected_params()
        with mock.patch.object(KeeperPerms, 'generate_template') as mock_gen, \
             mock.patch.object(KeeperPerms, 'store_in_vault_bytes') as mock_store, \
             mock.patch('keepercommander.api.sync_down'):
            do_command(params, 'perms template --vault-only')
            self.assertTrue(mock_gen.called)
            self.assertTrue(mock_store.called)

    def test_template_file(self):
        params = get_connected_params()
        with mock.patch.object(KeeperPerms, 'generate_template') as mock_gen, \
             mock.patch.object(KeeperPerms, 'store_in_vault') as mock_store, \
             mock.patch('keepercommander.api.sync_down'):
            with open('tmp.csv', 'w') as tmp:
                path = tmp.name
            do_command(params, f'perms template {path}')
            mock_gen.assert_called_with(path)
            self.assertTrue(mock_store.called)
            os.unlink(path)

    def test_validate_vault_csv(self):
        params = get_connected_params()
        with mock.patch.object(KeeperPerms, 'download_from_vault', return_value='file.csv') as mock_download, \
             mock.patch.object(KeeperPerms, 'validate_csv', return_value=True) as mock_validate, \
             mock.patch('builtins.print') as mock_print, \
             mock.patch('os.unlink') as mock_unlink, \
             mock.patch('keepercommander.api.sync_down'):
            do_command(params, 'perms validate --vault-csv sample.csv')
            mock_download.assert_called_with('sample.csv')
            mock_validate.assert_called_with('file.csv')
            mock_print.assert_called_with('Valid')

    def test_apply_permissions_called(self):
        params = get_connected_params()
        with open('apply.csv', 'w', newline='') as tmp:
            writer = csv.writer(tmp)
            writer.writerow(['Record UID', 'Title', 'Folder Path', 'Team1'])
            writer.writerow(['UID', 'Record', '/folder', 'ro'])
            path = tmp.name
        with mock.patch.object(KeeperPerms, 'apply_permissions') as mock_apply, \
             mock.patch('keepercommander.api.sync_down'):
            do_command(params, f'perms apply {path} --dry-run')
            mock_apply.assert_called_with(path, dry_run=True, root_name='[Perms]')
        os.unlink(path)
