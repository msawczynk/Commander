import argparse
import csv
import logging
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

from keepercommander import api
from .helpers.shared_folder import add_team_to_shared_folder
from keepercommander.commands.base import GroupCommand, Command
from keepercommander.params import KeeperParams
from keepercommander.commands.folder import FolderMakeCommand
from keepercommander.commands.utils import SyncDownCommand
from keepercommander.subfolder import find_folders
from keepercommander.record_management import add_record_to_folder
from keepercommander.vault import KeeperRecord
from keepercommander import utils
from keepercommander.proto import record_pb2
from keepercommander.attachment import (
    FileUploadTask,
    prepare_attachment_download,
    AttachmentDownloadRequest,
    BytesUploadTask,
    upload_attachments,
)
from keepercommander.record_management import update_record
from io import StringIO
import io

# Setup logging (Commander may have its own, but for now)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PermsCommand(GroupCommand):
    def __init__(self):
        super(PermsCommand, self).__init__()
        self.register_command('template', TemplateCommand(), 'Generate CSV template with vault data')
        self.register_command('validate', ValidateCommand(), 'Validate CSV file before applying')
        self.register_command('apply', ApplyCommand(), 'Apply permissions from CSV file')

    def get_parser(self):
        return perms_parser

perms_parser = argparse.ArgumentParser(prog='perms', description='Keeper Permissions Automation')

class TemplateCommand(Command):
    def get_parser(self):
        parser = argparse.ArgumentParser(description='Generate CSV template')
        parser.add_argument('output', nargs='?', type=str, help='Output CSV path')
        parser.add_argument('--vault-only', action='store_true', help='Store template directly in vault without local file')
        return parser

    def execute(self, params: KeeperParams, **kwargs):
        output_path = kwargs.get('output')
        vault_only = kwargs.get('vault_only', False)
        if not vault_only and not output_path:
            raise ValueError('Output path is required unless --vault-only is used')
        keeper_perms = KeeperPerms(params)
        if vault_only:
            with io.StringIO() as csv_io:
                keeper_perms.generate_template(csv_io)
                csv_data = csv_io.getvalue().encode('utf-8')
            title = f"Template_{datetime.now().isoformat()}.csv"
            keeper_perms.store_in_vault_bytes(csv_data, title)
        else:
            keeper_perms.generate_template(output_path)
            keeper_perms.store_in_vault(output_path, f"Template_{datetime.now().isoformat()}")

template_parser = argparse.ArgumentParser(prog='perms template', description='Generate CSV template')
template_parser.add_argument('output', help='Output CSV path')

class ValidateCommand(Command):
    def get_parser(self):
        parser = argparse.ArgumentParser(description='Validate CSV file before applying')
        parser.add_argument('csv_path', nargs='?', type=str, help='Path to CSV file')
        parser.add_argument('--vault-csv', type=str, help='Attachment title in vault to validate instead of local path')
        return parser

    def execute(self, params, **kwargs):
        csv_path = kwargs.get('csv_path')
        vault_csv = kwargs.get('vault_csv')
        if not csv_path and not vault_csv:
            raise ValueError('CSV path or vault CSV title is required')
        keeper_perms = KeeperPerms(params)
        if vault_csv:
            csv_path = keeper_perms.download_from_vault(vault_csv)
        valid = keeper_perms.validate_csv(csv_path)
        if vault_csv:
            os.unlink(csv_path)
        print("Valid" if valid else "Invalid")

validate_parser = argparse.ArgumentParser(prog='perms validate', description='Validate CSV')
validate_parser.add_argument('csv', help='CSV path')

class ApplyCommand(Command):
    def get_parser(self):
        parser = argparse.ArgumentParser(description='Apply permissions from CSV')
        parser.add_argument('csv_path', nargs='?', type=str, help='Path to CSV file')
        parser.add_argument('--dry-run', action='store_true', help='Simulate application without changes')
        parser.add_argument('--interactive', action='store_true', help='Enable interactive prompts for folder/record names')
        parser.add_argument('--root', type=str, default='[Perms]', help='Root folder for permissions structure')
        parser.add_argument('--vault-csv', type=str, help='Attachment title in vault to apply instead of local path')
        return parser

    def execute(self, params, **kwargs):
        csv_path = kwargs.get('csv_path')
        vault_csv = kwargs.get('vault_csv')
        if not csv_path and not vault_csv:
            raise ValueError('CSV path or vault CSV title is required')
        dry_run = kwargs.get('dry_run', False)
        interactive = kwargs.get('interactive', False)
        root_name = kwargs.get('root', '[Perms]')
        logging.info('Applying permissions from %s (dry-run: %s, interactive: %s, root: %s)', csv_path or vault_csv, dry_run, interactive, root_name)
        keeper_perms = KeeperPerms(params, interactive=interactive)
        if vault_csv:
            csv_path = keeper_perms.download_from_vault(vault_csv)
        keeper_perms.apply_permissions(csv_path, dry_run=dry_run, root_name=root_name)
        if vault_csv:
            os.unlink(csv_path)
        if not dry_run:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.log') as temp_log:
                log_path = temp_log.name
                temp_log.write(b'Sample log: Permissions applied successfully.')
            keeper_perms.store_in_vault(log_path, f"Apply_Log_{datetime.now().isoformat()}")
            os.unlink(log_path)
        else:
            logging.info('Dry-run complete, no changes applied or logged to vault.')

apply_parser = argparse.ArgumentParser(prog='perms apply', description='Apply permissions from CSV')
apply_parser.add_argument('csv', help='CSV path')

class KeeperPerms:
    def __init__(self, params: KeeperParams, interactive: bool = False, config_title: str = 'Perms Config'):
        self.params = params
        self.interactive = interactive
        self.config_title = config_title
        # Authentication is handled by Commander, so no load_or_login needed

    def get_teams(self) -> List[Dict[str, Any]]:
        teams = []
        rq = {"command": "get_available_teams"}
        rs = api.communicate(self.params, rq)
        if rs.get("result") == "success" and "teams" in rs:
            for team in rs["teams"]:
                teams.append({
                    "team_uid": team.get("team_uid", ""),
                    "team_name": team.get("team_name", f"Team {team.get('team_uid', 'Unknown')}")
                })
        return teams

    def get_records(self) -> List[Dict[str, Any]]:
        records = []
        for rec_uid, rec_data in self.params.record_cache.items():
            record = api.get_record(self.params, rec_uid)
            records.append({
                "uid": rec_uid,
                "title": record.title,
                "folder_path": self.get_record_path(rec_uid)
            })
        return records

    def get_record_path(self, record_uid: str) -> str:
        folder_uids = list(find_folders(self.params, record_uid))
        if not folder_uids:
            return ''
        folder_uid = folder_uids[0]
        path = []
        f = self.params.folder_cache.get(folder_uid)
        while f:
            path.append(f.name)
            f = self.params.folder_cache.get(f.parent_uid) if f.parent_uid else None
        return '/' + '/'.join(reversed(path))

    def generate_template(self, output: Union[str, io.StringIO]):
        teams = [t['team_name'] for t in self.get_teams()]
        records = self.get_records()
        close_file = False
        if isinstance(output, str):
            csvfile = open(output, 'w', newline='')
            close_file = True
        else:
            csvfile = output
        writer = csv.writer(csvfile)
        writer.writerow(['Record UID', 'Title', 'Folder Path'] + teams)
        for rec in records:
            writer.writerow([rec['uid'], rec['title'], rec['folder_path']] + [''] * len(teams))
        if close_file:
            csvfile.close()
            logging.info("Template generated at %s", output)
        else:
            logging.info("Template generated in memory")

    def validate_csv(self, csv_path: str) -> bool:
        if not os.path.exists(csv_path):
            logging.error("CSV file not found: %s", csv_path)
            return False
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            required = {'Record UID', 'Title', 'Folder Path'}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                logging.error("CSV missing required columns: %s", ', '.join(required))
                return False
            teams = {t['team_name'].lower() for t in self.get_teams()}
            allowed = {'ro', 'rw', 'rws', 'mgr', 'admin', ''}
            for row_no, row in enumerate(reader, start=2):
                for col, value in row.items():
                    if col in required:
                        continue
                    if col.lower() not in teams:
                        logging.error("Unknown team '%s' on line %d", col, row_no)
                        return False
                    if value and value.lower() not in allowed:
                        logging.error("Invalid permission '%s' on line %d", value, row_no)
                        return False
        return True

    def apply_permissions(self, csv_path: str, dry_run: bool = False, root_name: str = '[Perms]'):
        if not os.path.exists(csv_path):
            logging.error(f'CSV file not found: {csv_path}')
            return
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            logging.info('Fieldnames: %s', reader.fieldnames)

            teams_lookup = {t['team_name'].lower(): t['team_uid'] for t in self.get_teams()}
            root_folder_uid = self.ensure_root_folder(root_name)

            for row in reader:
                logging.debug('Processing row: %s', row)
                record_uid = row['Record UID']
                folder_path = row['Folder Path']

                for team_name, perm_level in row.items():
                    if team_name in ['Record UID', 'Title', 'Folder Path'] or not perm_level:
                        continue

                    team_uid = teams_lookup.get(team_name.lower())
                    if not team_uid:
                        logging.error('Team %s not found', team_name)
                        continue

                    team_folder_uid = self.ensure_team_folder_path(team_name, folder_path, root_folder_uid)
                    if not team_folder_uid:
                        logging.error('Failed to ensure folder path for team %s', team_name)
                        continue

                    permissions = self.permission_level_to_flags(perm_level)
                    if dry_run:
                        logging.info('[DRY-RUN] Would apply %s for team %s to %s in %s', perm_level, team_name, record_uid, folder_path)
                    else:
                        try:
                            self.share_record_to_folder(record_uid, team_folder_uid)
                            self.add_team_to_shared_folder(team_uid, team_folder_uid, permissions)
                        except Exception as exc:
                            logging.error('Failed to apply permission for %s/%s: %s', record_uid, team_name, exc)

            if not dry_run:
                api.sync_down(self.params)
                logging.info('Changes applied successfully')

    def ensure_root_folder(self, root_name: str) -> str:
        cmd = FolderMakeCommand()
        sync_cmd = SyncDownCommand()
        original_current = self.params.current_folder
        self.params.current_folder = None
        try:
            uid = cmd.execute(self.params, folder=root_name, user_folder=True)
            sync_cmd.execute(self.params)
            return uid
        finally:
            self.params.current_folder = original_current

    def ensure_team_folder_path(self, team_name: str, folder_path: str, root_uid: str) -> Optional[str]:
        current_folder_uid = root_uid
        folders = [team_name] + folder_path.strip('/').split('/')
        for folder in folders:
            if not folder:
                continue
            cmd = FolderMakeCommand()
            uid = cmd.execute(self.params, folder=folder, parent=current_folder_uid)
            if not uid:
                return None
            current_folder_uid = uid
        return current_folder_uid

    def share_record_to_folder(self, record_uid: str, folder_uid: str):
        api.move_record(self.params, record_uid, folder_uid, shared=True)

    def add_team_to_shared_folder(self, team_uid: str, folder_uid: str, permissions: Dict[str, bool]):
        add_team_to_shared_folder(self.params, folder_uid, team_uid, **permissions)

    def permission_level_to_flags(self, level: str) -> Dict[str, bool]:
        levels = {
            'ro': {'manage_records': False, 'manage_users': False, 'can_edit': False, 'can_share': False},
            'rw': {'manage_records': False, 'manage_users': False, 'can_edit': True, 'can_share': False},
            'rws': {'manage_records': False, 'manage_users': False, 'can_edit': True, 'can_share': True},
            'mgr': {'manage_records': True, 'manage_users': False, 'can_edit': True, 'can_share': True},
            'admin': {'manage_records': True, 'manage_users': True, 'can_edit': True, 'can_share': True}
        }
        return levels.get(level.lower(), {'manage_records': False, 'can_edit': False})

    def store_in_vault(self, file_path: str, title: str):
        config_record_uid = self.get_config_record()
        config_record = KeeperRecord.load(self.params, config_record_uid)
        if not config_record:
            logging.error('Config record not found')
            return
        task = FileUploadTask(file_path)
        task.title = title
        task.name = os.path.basename(file_path)
        upload_attachments(self.params, config_record, [task])
        update_record(self.params, config_record)
        logging.info(f'Stored {title} in vault under record UID: {config_record_uid}')

    def store_in_vault_bytes(self, data: bytes, title: str):
        config_record_uid = self.get_config_record()
        config_record = KeeperRecord.load(self.params, config_record_uid)
        if not config_record:
            logging.error('Config record not found')
            return
        task = BytesUploadTask(data)
        task.title = title
        task.name = title
        task.mime_type = 'text/csv'
        upload_attachments(self.params, config_record, [task])
        update_record(self.params, config_record)
        logging.info(f'Stored {title} in vault under record UID: {config_record_uid}')

    def get_config_record(self) -> str:
        records = self.get_records()
        for rec in records:
            if rec['title'] == self.config_title:
                return rec['uid']
        record_data = {"title": self.config_title}
        return self.create_record(record_data)

    def create_record(self, record_data: Dict[str, Any]) -> str:
        folder_name = "[Perms Config Folder]" if not self.interactive else input(
            "Enter folder name for Perms Config record (default: [Perms Config Folder]): "
        ) or "[Perms Config Folder]"
        cmd = FolderMakeCommand()
        folder_uid = cmd.execute(self.params, folder=folder_name, user_folder=True)
        if not folder_uid:
            logging.error("Failed to create folder")
            return ''
        record_title = (
            self.config_title
            if not self.interactive
            else input(
                f"Enter record title for Perms Config (default: {self.config_title}): "
            )
            or self.config_title
        )
        record = KeeperRecord.create(self.params, "general")
        record.title = record_title
        add_record_to_folder(self.params, record, folder_uid=folder_uid)
        api.sync_down(self.params)
        return record.record_uid

    def download_from_vault(self, attachment_title: str) -> str:
        config_record_uid = self.get_config_record()
        attachments = list(
            prepare_attachment_download(self.params, config_record_uid, attachment_title)
        )
        if not attachments:
            raise ValueError(
                f'Attachment "{attachment_title}" not found in {self.config_title} record'
            )
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            attachments[0].download_to_file(self.params, temp_file.name)
        return temp_file.name

    def get_team_uid_by_name(self, team_name: str) -> Optional[str]:
        name = team_name.lower()
        for team in self.get_teams():
            if team['team_name'].lower() == name:
                return team['team_uid']
        return None

def register_commands(commands):
    commands['perms'] = PermsCommand()

def register_command_info(aliases, command_info):
    command_info['perms'] = 'Keeper Permissions Automation' 
