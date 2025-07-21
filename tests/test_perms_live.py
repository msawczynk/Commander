import os
import tempfile
from unittest import TestCase

import pytest

from data_config import read_config_file
from keepercommander.params import KeeperParams
from keepercommander import api, cli
from keepercommander.commands.perms_command import KeeperPerms


@pytest.mark.integration
class TestPermsLive(TestCase):
    params = None

    @classmethod
    def setUpClass(cls):
        cls.params = KeeperParams()
        # use the sandbox's persistent config; no vault.json required
        keeper_config = os.path.join(os.path.expanduser('~'), '.keeper', 'config.json')
        read_config_file(cls.params, keeper_config)
        api.login(cls.params)

    @classmethod
    def tearDownClass(cls):
        cli.do_command(cls.params, 'logout')

    def test_generate_and_validate_template(self):
        params = TestPermsLive.params
        keeper = KeeperPerms(params)
        with tempfile.NamedTemporaryFile('w+', delete=False) as tmp:
            path = tmp.name
        try:
            keeper.generate_template(path)
            self.assertTrue(os.path.isfile(path))
            valid = keeper.validate_csv(path)
            self.assertTrue(valid)
        finally:
            os.unlink(path)

    def test_permission_flags(self):
        keeper = KeeperPerms(TestPermsLive.params)
        flags = keeper.permission_level_to_flags('rw')
        expected = {
            'manage_records': False,
            'manage_users': False,
            'can_edit': True,
            'can_share': False,
        }
        self.assertEqual(flags, expected)
