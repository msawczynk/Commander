from __future__ import annotations
import argparse
from . import get_meta_info, get_meta_data, show_meta_menu
from ..discover import PAMGatewayActionDiscoverCommandBase, GatewayContext
from keepercommander.discovery_common.rm_types import (RmAwsRoleAddMeta, RmAzureRoleAddMeta, RmMySQLRoleAddMeta,
                                                       RmRole)
from ..pam.pam_dto import GatewayAction
from ..pam.router_helper import router_send_action_to_gateway
from ...proto import pam_pb2
from ...display import bcolors
from ... import vault
import json
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...params import KeeperParams
    from ...vault import TypedRecord


class GatewayActionRmCreateRoleCommandInputs:

    def __init__(self,
                 configuration_uid: str,
                 role: str,
                 resource_uid: Optional[str] = None,
                 meta: Optional[str] = None,
                 database: Optional[str] = None):

        self.configurationUid = configuration_uid
        self.role = role
        self.resourceUid = resource_uid
        self.meta = meta
        self.database = database

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class GatewayActionRmCreateRoleCommand(GatewayAction):

    def __init__(self, inputs: GatewayActionRmCreateRoleCommandInputs, conversation_id=None):
        super().__init__('rm-create-role', inputs=inputs, conversation_id=conversation_id, is_scheduled=True)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class RmCreateRoleCommand(PAMGatewayActionDiscoverCommandBase):
    parser = argparse.ArgumentParser(prog='pam-rm-role-create')

    # The record to base everything on.
    parser.add_argument('--gateway', '-g', required=True, dest='gateway', action='store',
                        help='Gateway name or UID.')
    parser.add_argument('--role', required=True, dest='role', action='store', help='Role Name')
    parser.add_argument('--resource-uid', '-r', required=False, dest='resource_uid', action='store',
                        help='Resource UID')
    parser.add_argument('--database', required=False, dest='database', action='store',
                        help='Override the connect database')

    @staticmethod
    def get_meta_role_class(params: KeeperParams,
                            configuration_record_uid: str,
                            resource_record_uid: Optional[str] = None):
        record_uid = configuration_record_uid
        if resource_record_uid is not None:
            record_uid = resource_record_uid

        record = vault.TypedRecord.load(params, record_uid)  # type: Optional[TypedRecord]

        meta_provider_map = {
            "pamAwsConfiguration": RmAwsRoleAddMeta,
            "pamAzureConfiguration": RmAzureRoleAddMeta,
        }

        meta_class = meta_provider_map.get(record.record_type)
        if meta_class is not None:
            return meta_class

        lookup = {}
        for field in record.fields:
            key = field.label
            if key is None or key == "":
                key = field.type
            value = field.value
            if len(value) > 0:
                value = value[0]
            lookup[key] = value

        if record.record_type == "pamDatabase":
            database_type = lookup.get("databaseType")
            if database_type == "mysql":
                return RmMySQLRoleAddMeta
            # elif database_type == "mariadb":
            #     return RmMySQLUserAddMeta
            raise Exception("Database type was not set on the database record.")
        # elif record.record_type == "pamMachine":
        #     operating_system = lookup.get("operatingSystem")
        #     if operating_system == "linux":
        #         return RmLinuxUserAddMeta
        #     raise Exception("Operating system was not set on the machine record.")
        # elif record.record_type == "pamDirectory":
        #     directory_type = lookup.get("directoryType")
        #     if directory_type == "openldap":
        #         return RmOpenLdapUserAddMeta
        #     elif directory_type == "active_directory":
        #         return RmAdUserAddMeta
        #     raise Exception("Directory type was not set on the directory record.")

        return None

    def get_parser(self):
        return RmCreateRoleCommand.parser

    def execute(self, params: KeeperParams, **kwargs):

        gateway = kwargs.get("gateway")

        gateway_context = GatewayContext.from_gateway(params, gateway)
        if gateway_context is None:
            print(f"{bcolors.FAIL}Could not find the gateway configuration for {gateway}.")
            return

        configuration_record = vault.TypedRecord.load(params, gateway_context.configuration_uid)

        try:
            meta_class = self.get_meta_role_class(
                params=params,
                configuration_record_uid=configuration_record.record_uid,
                resource_record_uid=kwargs.get('resource_uid')
            )
        except Exception as err:
            print(f"{bcolors.FAIL}{err}{bcolors.ENDC}")
            return

        meta_data = None
        if meta_class is not None:

            meta_info = get_meta_info(meta_class)
            show_meta_menu(meta_info)
            meta_data = get_meta_data(meta_info, meta_class, configuration_record.record_key)

        action_inputs = GatewayActionRmCreateRoleCommandInputs(
            configuration_uid=gateway_context.configuration_uid,
            resource_uid=kwargs.get('resource_uid'),
            role=kwargs.get('role'),
            meta=meta_data,
            database=kwargs.get('database')
        )

        conversation_id = GatewayAction.generate_conversation_id()
        router_response = router_send_action_to_gateway(
            params=params,
            gateway_action=GatewayActionRmCreateRoleCommand(
                inputs=action_inputs,
                conversation_id=conversation_id),
            message_type=pam_pb2.CMT_GENERAL,
            is_streaming=False,
            destination_gateway_uid_str=gateway_context.gateway_uid
        )

        print("")

        data = self.get_response_data(router_response)
        if data is None:
            raise Exception("The router returned a failure.")
        elif data.get("success") is False:
            error = data.get("error")
            print(f"{bcolors.FAIL}Could not create role: {error}{bcolors.ENDC}")
            return

        role_json = gateway_context.decrypt(data.get("data"))
        role = RmRole.model_validate(role_json)

        print(f"{bcolors.OKGREEN}Role created successfully{bcolors.ENDC}")
        print("")
        print(f"{bcolors.BOLD}Id{bcolors.ENDC}: {role.id}")
        print(f"{bcolors.BOLD}Name{bcolors.ENDC}: {role.name}")
        print("")
