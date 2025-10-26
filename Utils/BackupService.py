import os
import shutil
import datetime
import uuid
from db.database import get_connection, DB_NAME
from Utils.encryption import Encryptor
from Utils.logger import Logger

BACKUP_DIR = "data/backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

logger = Logger(Encryptor())


class BackupService:
    @staticmethod
    def make_backup():
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.db"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)

        shutil.copy2(DB_NAME, backup_path)

        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO backups (file_name, created_by, created_at)
                VALUES (?, ?, ?)
                """,
                (
                    backup_filename,
                    "super_admin",
                    datetime.datetime.now().isoformat(),
                ),
            )
            conn.commit()

        logger.log(
            username="super_admin",
            description="Created system backup",
            extra=f"Backup file: {backup_filename}",
        )

        print(f"[INFO] Backup created: {backup_filename}")
        return backup_filename

    @staticmethod
    def generate_restore_code(backup_filename: str, assigned_admin: str):
        restore_code = str(uuid.uuid4())

        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE backups
                SET restore_code = ?, assigned_to = ?, used = 0
                WHERE file_name = ?
                """,
                (restore_code, assigned_admin, backup_filename),
            )
            if cur.rowcount == 0:
                raise ValueError("Backup not found.")
            conn.commit()

        logger.log(
            username="super_admin",
            description="Generated restore code",
            extra=f"Code: {restore_code}, Assigned to: {assigned_admin}",
        )

        print(f"[INFO] Restore code {restore_code} generated for {assigned_admin}.")
        return restore_code

    @staticmethod
    def revoke_restore_code(restore_code: str, super_admin_username: str):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE backups
                SET restore_code = NULL, assigned_to = NULL, used = 0
                WHERE restore_code = ?
                """,
                (restore_code,),
            )
            conn.commit()

        logger.log(
            username=super_admin_username,
            description="Revoked restore code",
            extra=f"Restore code: {restore_code}",
        )

        print(f"[INFO] Restore code {restore_code} revoked.")

    @staticmethod
    def restore_backup(restore_code: str, requesting_admin: str):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT file_name, assigned_to, used
                FROM backups
                WHERE restore_code = ?
                """,
                (restore_code,),
            )
            record = cur.fetchone()

            if not record:
                logger.log(
                    username=requesting_admin,
                    description="Attempted restore with invalid code",
                    extra=f"Restore code: {restore_code}",
                    suspicious=True,
                )
                raise ValueError("Invalid restore code.")

            file_name, assigned_to, used = record

            if used:
                logger.log(
                    username=requesting_admin,
                    description="Attempted reuse of restore code",
                    extra=f"Restore code: {restore_code}",
                    suspicious=True,
                )
                raise ValueError("Restore code already used.")
            if assigned_to != requesting_admin:
                logger.log(
                    username=requesting_admin,
                    description="Unauthorized restore attempt",
                    extra=f"Restore code: {restore_code}, belongs to {assigned_to}",
                    suspicious=True,
                )
                raise PermissionError("This restore code is not assigned to you.")

            backup_path = os.path.join(BACKUP_DIR, file_name)
            if not os.path.exists(backup_path):
                raise FileNotFoundError("Backup file not found.")

            shutil.copy2(backup_path, DB_NAME)

            cur.execute(
                "UPDATE backups SET used = 1 WHERE restore_code = ?",
                (restore_code,),
            )
            conn.commit()

        logger.log(
            username=requesting_admin,
            description="Restored backup successfully",
            extra=f"Backup file: {file_name}",
        )

        print(f"[INFO] Backup {file_name} restored successfully by {requesting_admin}.")
        return True
