from typing import Any

from ... import api, crypto, utils
from ...params import KeeperParams
from ...error import KeeperApiError
from ...proto import folder_pb2


def add_team_to_shared_folder(params, folder_uid, team_uid, **permissions):
    # type: (KeeperParams, str, str, ...) -> None
    """Share a folder with a team using specified permission flags."""
    api.load_team_keys(params, [team_uid])
    team_keys = params.key_cache.get(team_uid)
    if not team_keys:
        raise KeeperApiError('team_key_not_found', f'Team key unavailable: {team_uid}')

    sf = params.shared_folder_cache.get(folder_uid)
    if not sf:
        raise KeeperApiError('sf_not_found', f'Shared folder not found: {folder_uid}')

    sf_key = sf.get('shared_folder_key_unencrypted')
    if not sf_key:
        raise KeeperApiError('sf_key_not_found', 'Shared folder key not found')

    rq = folder_pb2.SharedFolderUpdateV3Request()
    rq.sharedFolderUid = utils.base64_url_decode(folder_uid)
    rq.forceUpdate = True

    tq = folder_pb2.SharedFolderUpdateTeam()
    tq.teamUid = utils.base64_url_decode(team_uid)
    if 'manage_records' in permissions:
        tq.manageRecords = folder_pb2.BOOLEAN_TRUE if permissions['manage_records'] else folder_pb2.BOOLEAN_FALSE
    if 'manage_users' in permissions:
        tq.manageUsers = folder_pb2.BOOLEAN_TRUE if permissions['manage_users'] else folder_pb2.BOOLEAN_FALSE
    if 'can_edit' in permissions:
        tq.canEdit = folder_pb2.BOOLEAN_TRUE if permissions['can_edit'] else folder_pb2.BOOLEAN_FALSE
    if 'can_share' in permissions:
        tq.canShare = folder_pb2.BOOLEAN_TRUE if permissions['can_share'] else folder_pb2.BOOLEAN_FALSE

    if team_keys.aes:
        tq.typedSharedFolderKey.encryptedKey = crypto.encrypt_aes_v2(sf_key, team_keys.aes)
        tq.typedSharedFolderKey.encryptedKeyType = folder_pb2.encrypted_by_data_key_gcm
    elif team_keys.ec:
        ec_key = crypto.load_ec_public_key(team_keys.ec)
        tq.typedSharedFolderKey.encryptedKey = crypto.encrypt_ec(sf_key, ec_key)
        tq.typedSharedFolderKey.encryptedKeyType = folder_pb2.encrypted_by_public_key_ecc
    elif team_keys.rsa and not params.forbid_rsa:
        rsa_key = crypto.load_rsa_public_key(team_keys.rsa)
        tq.typedSharedFolderKey.encryptedKey = crypto.encrypt_rsa(sf_key, rsa_key)
        tq.typedSharedFolderKey.encryptedKeyType = folder_pb2.encrypted_by_public_key
    else:
        raise KeeperApiError('team_public_key_missing', f'Team public key missing: {team_uid}')

    rq.sharedFolderAddTeam.append(tq)
    api.communicate_rest(params, rq, 'vault/shared_folder_update_v3',
                         rs_type=folder_pb2.SharedFolderUpdateV3Response)
