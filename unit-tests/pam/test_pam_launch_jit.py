"""Unit tests for just-in-time (JIT) support in `pam launch`.

Covers the pure helpers introduced for JIT — payload builders in
`terminal_connection.py` and the launch-time derivation/validation helpers in
`launch.py`. The full offer-building path is exercised by the live acme-lab
smoke test (see notes/acme-lab-reconciliation.md); these unit tests pin the
bits that can change without a gateway.
"""

import sys
import unittest
from types import SimpleNamespace
from unittest import mock

from keepercommander.error import CommandError

# launch.py / terminal_connection.py both pull in large transitive dep trees
# (WebRTC / router / Guacamole). The import guard matches the pattern in
# test_pam_tunnel.py: only run when the optional deps are available.
JIT_TESTS_ENABLED = sys.version_info >= (3, 8)

if JIT_TESTS_ENABLED:
    from keepercommander.commands.pam_launch.terminal_connection import (
        _build_jit_ephemeral_payload,
        _build_jit_elevation_payload,
        _JIT_EPHEMERAL_KEYS,
        _JIT_ELEVATION_KEYS,
    )
    from keepercommander.commands.pam_launch.launch import (
        _derive_jit_mode,
        _get_jit_settings,
    )
else:
    # Keep module importable on 3.7 and skip test classes explicitly.
    _build_jit_ephemeral_payload = None
    _build_jit_elevation_payload = None
    _JIT_EPHEMERAL_KEYS = ()
    _JIT_ELEVATION_KEYS = ()
    _derive_jit_mode = None
    _get_jit_settings = None


def _typed_field_stub(value):
    """Minimal stand-in for keepercommander.vault.TypedField.get_default_value(dict)."""
    return SimpleNamespace(get_default_value=lambda _t=dict: value)


def _record_with_pam_settings(pam_settings_value):
    """Build a record-like object exposing get_typed_field('pamSettings')."""
    field = _typed_field_stub(pam_settings_value)

    def _get(name):
        return field if name == 'pamSettings' else None

    return SimpleNamespace(get_typed_field=_get)


@unittest.skipUnless(JIT_TESTS_ENABLED, "Requires Python >= 3.8")
class TestBuildJitEphemeralPayload(unittest.TestCase):
    def test_returns_empty_for_none(self):
        self.assertEqual(_build_jit_ephemeral_payload(None), {})

    def test_returns_empty_for_non_dict(self):
        self.assertEqual(_build_jit_ephemeral_payload('not-a-dict'), {})

    def test_keeps_only_ephemeral_keys(self):
        payload = _build_jit_ephemeral_payload({
            'create_ephemeral': True,
            'ephemeral_account_type': 'linux',
            'base_distinguished_name': 'OU=JIT,DC=acme,DC=corp',
            'pam_directory_uid_ref': 'ref-uid',
            # Elevation keys must not leak into the ephemeral payload:
            'elevate': True,
            'elevation_method': 'group',
            'elevation_string': 'wheel',
        })
        self.assertEqual(set(payload.keys()), set(_JIT_EPHEMERAL_KEYS))
        self.assertEqual(payload['ephemeral_account_type'], 'linux')

    def test_drops_empty_and_none_values(self):
        payload = _build_jit_ephemeral_payload({
            'create_ephemeral': True,
            'ephemeral_account_type': 'linux',
            'base_distinguished_name': '',
            'pam_directory_uid_ref': None,
        })
        self.assertIn('create_ephemeral', payload)
        self.assertIn('ephemeral_account_type', payload)
        self.assertNotIn('base_distinguished_name', payload)
        self.assertNotIn('pam_directory_uid_ref', payload)


@unittest.skipUnless(JIT_TESTS_ENABLED, "Requires Python >= 3.8")
class TestBuildJitElevationPayload(unittest.TestCase):
    def test_returns_empty_for_none(self):
        self.assertEqual(_build_jit_elevation_payload(None), {})

    def test_returns_empty_for_non_dict(self):
        self.assertEqual(_build_jit_elevation_payload(42), {})

    def test_keeps_only_elevation_keys(self):
        payload = _build_jit_elevation_payload({
            'elevate': True,
            'elevation_method': 'group',
            'elevation_string': 'wheel,sudo',
            # Ephemeral keys must not leak into the elevation payload:
            'create_ephemeral': True,
            'ephemeral_account_type': 'linux',
        })
        self.assertEqual(set(payload.keys()), set(_JIT_ELEVATION_KEYS))
        self.assertEqual(payload['elevation_method'], 'group')
        self.assertEqual(payload['elevation_string'], 'wheel,sudo')

    def test_drops_empty_strings(self):
        payload = _build_jit_elevation_payload({
            'elevate': True,
            'elevation_method': 'role',
            'elevation_string': '',
        })
        self.assertIn('elevate', payload)
        self.assertIn('elevation_method', payload)
        self.assertNotIn('elevation_string', payload)


@unittest.skipUnless(JIT_TESTS_ENABLED, "Requires Python >= 3.8")
class TestDeriveJitMode(unittest.TestCase):
    def test_none_for_non_dict(self):
        self.assertIsNone(_derive_jit_mode(None))
        self.assertIsNone(_derive_jit_mode('nope'))

    def test_none_when_no_flags(self):
        self.assertIsNone(_derive_jit_mode({'elevation_method': 'group'}))
        self.assertIsNone(_derive_jit_mode({
            'create_ephemeral': False,
            'elevate': False,
        }))

    def test_ephemeral_only(self):
        self.assertEqual(_derive_jit_mode({'create_ephemeral': True}), 'ephemeral')

    def test_elevation_only(self):
        self.assertEqual(_derive_jit_mode({'elevate': True}), 'elevation')

    def test_both(self):
        self.assertEqual(_derive_jit_mode({
            'create_ephemeral': True,
            'elevate': True,
        }), 'both')


@unittest.skipUnless(JIT_TESTS_ENABLED, "Requires Python >= 3.8")
class TestGetJitSettings(unittest.TestCase):
    def test_none_record(self):
        self.assertIsNone(_get_jit_settings(None))

    def test_no_pam_settings(self):
        record = SimpleNamespace(get_typed_field=lambda _n: None)
        self.assertIsNone(_get_jit_settings(record))

    def test_no_options_block(self):
        record = _record_with_pam_settings({'connection': {'protocol': 'ssh'}})
        self.assertIsNone(_get_jit_settings(record))

    def test_no_jit_settings(self):
        record = _record_with_pam_settings({'options': {'connections': 'on'}})
        self.assertIsNone(_get_jit_settings(record))

    def test_happy_path(self):
        jit = {'create_ephemeral': True, 'ephemeral_account_type': 'linux'}
        record = _record_with_pam_settings({'options': {'jit_settings': jit}})
        self.assertEqual(_get_jit_settings(record), jit)

    def test_non_dict_jit_settings_ignored(self):
        record = _record_with_pam_settings({'options': {'jit_settings': 'bogus'}})
        self.assertIsNone(_get_jit_settings(record))


@unittest.skipUnless(JIT_TESTS_ENABLED, "Requires Python >= 3.8")
class TestDispatchIntegration(unittest.TestCase):
    """
    The dispatch (credential_type_for_gateway selection) is inlined in
    _open_terminal_webrtc_tunnel which is hard to unit-test. Instead we verify
    the builder helpers produce the shape the dispatch consumes when fed the
    three JIT modes, which is the invariant callers care about.
    """

    def test_ephemeral_and_elevation_payloads_disjoint(self):
        combined = {
            'create_ephemeral': True,
            'ephemeral_account_type': 'linux',
            'elevate': True,
            'elevation_method': 'group',
            'elevation_string': 'wheel',
        }
        eph = _build_jit_ephemeral_payload(combined)
        elev = _build_jit_elevation_payload(combined)
        # No cross-contamination: every key is in exactly one payload
        self.assertEqual(set(eph.keys()) & set(elev.keys()), set())
        # Together they reconstruct the interesting parts of the input
        self.assertEqual(
            set(eph.keys()) | set(elev.keys()),
            set(_JIT_EPHEMERAL_KEYS[:2]) | set(_JIT_ELEVATION_KEYS),
        )


if __name__ == '__main__':
    unittest.main()
