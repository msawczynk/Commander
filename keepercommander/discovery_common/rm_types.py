from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List


class RmResponse(BaseModel):
    notes: List[str] = []


class RmScriptResponse(BaseModel):
    script: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None


class RmKeyValue(BaseModel):
    key: str
    value: str


class RmInformation(BaseModel):
    name: str
    record_type: str
    version: Optional[str] = None
    version_number: Optional[str] = None
    supports_groups: bool = False
    supports_roles: bool = False
    can_create_users: bool = False
    can_delete_users: bool = False
    can_run_scripts: bool = False
    settings: List[RmKeyValue] = []


class RmUser(BaseModel):
    id: str
    name: str
    desc: Optional[str] = None
    password: Optional[str] = None
    private_key: Optional[str] = None
    connect_database: Optional[str] = None
    dn: Optional[str] = None


class RmNewUser(BaseModel):
    id: str
    name: str
    desc: Optional[str] = None
    password: Optional[str] = None
    private_key: Optional[str] = None
    connect_database: Optional[str] = None
    dn: Optional[str] = None


class RmRole(BaseModel):
    id: str
    name: Optional[str] = None
    desc: Optional[str] = None
    users: List[RmUser] = []


class RmGroup(BaseModel):
    id: str
    name: Optional[str] = None
    desc: Optional[str] = None
    users: List[RmUser] = []


class RmStubMeta(BaseModel):
    pass


class RmAwsUserAddMeta(BaseModel):
    console_access:  Optional[bool] = True
    path: Optional[str] = "/"
    permission_boundary_arn: Optional[str] = None
    password_reset_required: Optional[bool] = False
    tags: List[RmKeyValue] = []
    roles: List[str] = []
    groups: List[str] = []
    policies: List[str] = []


class RmAwsRoleAddMeta(BaseModel):
    policy_json: str
    description: Optional[str] = None


class RmAwsGroupAddMeta(BaseModel):
    path: Optional[str] = None


class RmAzureUserAddMeta(BaseModel):
    account_enabled: Optional[bool] = True
    display_name: Optional[str] = None
    on_premise_immutable_id: Optional[str] = None
    password_reset_required: Optional[bool] = False
    password_reset_required_with_mfa: Optional[bool] = False
    roles: List[str] = []
    groups: List[str] = []


class RmAzureRoleAddMeta(BaseModel):
    policy_json: str
    description: Optional[str] = None


class RmAzureGroupAddMeta(BaseModel):
    mail_enabled: bool = False
    mail_nickname: Optional[str] = None
    security_enabled: bool = True
    group_types: List[str] = []


class RmDomainUserAddMeta(BaseModel):
    roles: List[str] = []
    groups: List[str] = []


class RmMySQLUserAddMeta(BaseModel):
    authentication_plugin: Optional[str] = None
    authentication_value: Optional[str] = None
    roles: List[str] = []


class RmMySQLRoleAddMeta(BaseModel):
    # The str is database.table.column
    grant_select: List[str] = []
    grant_insert: List[str] = []
    grant_update: List[str] = []
    grant_delete: List[str] = []
    grant_create: List[str] = []
    grant_drop: List[str] = []
    grant_alter: List[str] = []
    grant_index: List[str] = []
    grant_execute: List[str] = []
    grant_create_view: List[str] = []
    grant_show_view: List[str] = []
    all_privileges: List[str] = []

    # This is select, insert, update, delete, create, drop, alter, index, execute
    grant_option: List[str] = []

    # Roles can use other roles
    roles: List[str] = []


class RmPostgreSqlUserAddMeta(BaseModel):
    superuser: Optional[bool] = False
    create_db: Optional[bool] = False
    create_role: Optional[bool] = False
    inherit: Optional[bool] = False
    login: Optional[bool] = True
    replication: Optional[bool] = False
    bypass_rls: Optional[bool] = False
    connection_limit: Optional[int] = None
    valid_until: Optional[str] = None
    roles: List[str] = []
    inc_in_roles: List[str] = []
    inc_in_roles_as_admin: List[str] = []
    sysid: Optional[str] = None


class RmSqlServerUserAddMeta(BaseModel):
    allow_login: bool = True
    use_windows_auth: bool = False
    is_reader: bool = True
    is_writer: bool = True
    roles: List[str] = []


class RmOracleUserAddMeta(BaseModel):
    allow_login: bool = True
    allow_resource: bool = True
    roles: List[str] = []


class RmMongoDbUserAddMeta(BaseModel):
    roles: List[str] = []


# MACHINE

class RmMachineMeta(BaseModel):
    pass


class RmLinuxUserAddMeta(RmMachineMeta):
    system_user: Optional[bool] = False
    shell: Optional[str] = None
    no_login:  Optional[bool] = False
    home_dir: Optional[str] = None
    do_not_create_home_dir: Optional[bool] = False
    allow_bad_names: Optional[bool] = False
    gecos_full_name: Optional[str] = None
    gecos_room_number: Optional[str] = None
    gecos_work_phone: Optional[str] = None
    gecos_home_phone: Optional[str] = None
    gecos_other: Optional[str] = None
    group: Optional[str] = None
    groups: List[str] = []
    create_group: Optional[bool] = False
    validate_group: Optional[bool] = True
    uid: Optional[str] = None
    selinux_user_context:  Optional[str] = None
    btrfs_subvolume: Optional[bool] = False
    system_dir_mode: Optional[str] = None
    non_system_dir_mode: Optional[str] = None
    use_password: Optional[bool] = True
    use_private_key: Optional[bool] = False
    use_private_key_type: Optional[str] = "ecdsa_sha2_nistp521"
    private_key: Optional[str] = None
    authorized_keys: List[str] = []


class RmLinuxUserDeleteMeta(RmMachineMeta):
    remove_home_dir: Optional[bool] = False
    remove_user_group: Optional[bool] = True


class RmWindowsUserAddMeta(RmMachineMeta):
    display_name: Optional[str] = None
    description: Optional[str] = None
    disabled: bool = False
    expire_days: int = 0
    groups: List[str] = []


class RmMacOsUserAddMeta(RmMachineMeta):
    display_name: Optional[str] = None
    uid: Optional[str] = None
    gid: Optional[str] = None
    shell: Optional[str] = None
    home_dir: Optional[str] = None
    is_admin: bool = False
    is_role_account: bool = False
    groups: List[str] = []


# DIRECTORY


class RmBaseLdapUserAddMeta(BaseModel):
    object_class: List[str] = []
    dn: Optional[str] = None
    base_dn: Optional[str] = None
    auto_uid_number: bool = True
    gid_number_match_uid: bool = True
    home_dir_base: Optional[str] = "/home"
    first_rdn_component: Optional[str] = None
    attributes: Optional[dict] = {}
    groups: List[str] = []


class RmOpenLdapUserAddMeta(RmBaseLdapUserAddMeta):
    object_class: List[str] = ["top", "inetOrgPerson", "posixAccount"]


class RmAdUserAddMeta(RmBaseLdapUserAddMeta):
    object_class: List[str] = ["top", "person", "organizationalPerson", "user"]
    user_account_control: Optional[int] = 512


class RmBaseLdapUserDeleteMeta(BaseModel):
    orphan_check: Optional[bool] = False
    delete_orphans: Optional[bool] = True


class RmOpenLdapUserDeleteMeta(RmBaseLdapUserDeleteMeta):
    pass


class RmAdUserDeleteMeta(RmBaseLdapUserDeleteMeta):
    pass
