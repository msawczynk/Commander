from __future__ import annotations
from ...utils import value_to_boolean
import os
import base64
import json
from ...crypto import encrypt_aes_v2, decrypt_aes_v2
from ...display import bcolors
from typing import Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...params import KeeperParams
    from keeper_dag.connection import ConnectionBase


def get_connection(params: KeeperParams) -> ConnectionBase:
    if value_to_boolean(os.environ.get("USE_LOCAL_DAG", False)) is False:
        from keeper_dag.connection.commander import Connection as CommanderConnection
        return CommanderConnection(params=params)
    else:
        from keeper_dag.connection.local import Connection as LocalConnection
        return LocalConnection()


# def decrypt(self, cipher_base64: bytes, key: bytes) -> dict:
#     ciphertext = base64.b64decode(cipher_base64)
#     return json.loads(decrypt_aes_v2(ciphertext, key))
#
#
# def encrypt(self, data: dict, key: bytes) -> str:
#     json_data = json.dumps(data)
#     ciphertext = encrypt_aes_v2(json_data.encode(), key)
#     return base64.b64encode(ciphertext).decode()
#
#
# def encrypt_str(self, data: Union[bytes, str], key: bytes) -> str:
#     if isinstance(data, str):
#         data = data.encode()
#     ciphertext = encrypt_aes_v2(data, key)
#     return base64.b64encode(ciphertext).decode()


def get_meta_info(meta_class) -> List[dict]:

    data = []
    for attr_name in meta_class.model_fields:
        default = meta_class.model_fields[attr_name].default
        if str(default) == "PydanticUndefined":
            default = None
        data_type = "str"
        is_array = meta_class.model_fields[attr_name].annotation.__name__ == "List"
        required = meta_class.model_fields[attr_name].annotation.__name__ == "Optional"
        if meta_class.model_fields[attr_name].annotation == bool:
            data_type = "bool"
        elif meta_class.model_fields[attr_name].annotation == str:
            data_type = "str"
        else:
            for item in list(meta_class.model_fields[attr_name].annotation.__args__):

                data_type_name = item.__name__
                if data_type_name != "NoneType":
                    data_type = data_type_name
        data.append({
            "name": attr_name,
            "data_type": data_type,
            "required": required,
            "is_array": is_array,
            "value": default
        })

    return sorted(data, key=lambda x: x["name"])


def show_meta_menu(meta_info_data) -> List[dict]:
    print("")
    print(f"{bcolors.HEADER}Meta data is available for this record type.{bcolors.ENDC}")
    while True:
        for item in meta_info_data:
            value = item['value']
            if value is not None and len(value) > 40:
                value = value[:40] + "..."
            print(f" {bcolors.BOLD}*{bcolors.ENDC} {item['name']} = {value} ")
        print("")
        action = input("[A]ccept, [E]dit > ").lower()
        if action == "a":
            return meta_info_data
        if action == "e":
            attr_name = input("Attribute >")
            value = input("Value >")
            for item in meta_info_data:
                if item["name"] == attr_name:
                    if item["is_array"] is True:
                        new_value = []
                        for v in value.split(","):
                            new_value.append(v.strip())
                        value = new_value
                    elif item["data_type"] == "bool":
                        value = value_to_boolean(value)
                    elif item["data_type"] == "str":
                        if os.path.exists(value) is True:
                            with open(value, "r") as fh:
                                value = fh.read()
                                fh.close()
                    item["value"] = value
            print("")


def get_meta_data(meta_info: List[dict], meta_class, key: bytes):
    kwargs = {}
    for item in meta_info:
        kwargs[item['name']] = item['value']
    meta = meta_class(**kwargs)
    meta_json = meta.model_dump_json()
    meta_json_enc = encrypt_aes_v2(meta_json.encode(), key)
    return base64.b64encode(meta_json_enc).decode()