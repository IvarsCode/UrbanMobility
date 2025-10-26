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
    def revoke_restore_code(restore_code: str):
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
            username="super_admin",
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


def backup_menu():
    while True:
        print("\n=== Backup & Restore Menu ===")
        print("1. Create new backup")
        print("2. Generate restore code for an existing backup")
        print("3. Revoke restore code")
        print("4. List all backups")
        print("5. Return to main menu")

        choice = input("Select an option: ").strip()

        if choice == "1":
            try:
                backup_file = BackupService.make_backup()
                print(f"[SUCCESS] Backup created: {backup_file}")
            except Exception as e:
                print(f"[ERROR] Failed to create backup: {e}")

        elif choice == "2":
            try:
                # Show available backups
                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT file_name, created_at FROM backups")
                    backups = cur.fetchall()

                if not backups:
                    print("No backups available.")
                    continue

                print("\nAvailable backups:")
                for i, (file_name, created_at) in enumerate(backups, start=1):
                    print(f"{i}. {file_name} (Created: {created_at})")

                index = input("Select backup number: ").strip()
                if not index.isdigit() or int(index) < 1 or int(index) > len(backups):
                    print("[ERROR] Invalid selection.")
                    continue

                backup_file = backups[int(index) - 1][0]
                assigned_admin = input("Assign restore code to which admin? ").strip()

                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT username, role FROM users")
                    users = cur.fetchall()

                encryptor = Encryptor()
                valid_admin = False
                for enc_username, enc_role in users:
                    username = encryptor.decrypt_text(enc_username)
                    role = encryptor.decrypt_text(enc_role)
                    if (
                        username.lower() == assigned_admin.lower()
                        and role.lower() == "system_administrator"
                    ):
                        valid_admin = True
                        break

                if not valid_admin:
                    print(
                        "[ERROR] That admin does not exist or is not a System Administrator."
                    )
                    continue

                code = BackupService.generate_restore_code(
                    backup_filename=backup_file,
                    assigned_admin=assigned_admin,
                )

                print(f"[SUCCESS] Restore code generated for {assigned_admin}: {code}")

            except Exception as e:
                print(f"[ERROR] Could not generate restore code: {e}")

        elif choice == "3":
            code = input("Enter restore code to revoke: ").strip()
            try:
                BackupService.revoke_restore_code(code)
                print(f"[SUCCESS] Restore code revoked.")
            except Exception as e:
                print(f"[ERROR] Failed to revoke code: {e}")

        elif choice == "4":
            try:
                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT file_name, created_by, created_at, restore_code, assigned_to, used FROM backups"
                    )
                    records = cur.fetchall()

                if not records:
                    print("No backups found.")
                    continue

                print("\n=== Existing Backups ===")
                for (
                    file_name,
                    created_by,
                    created_at,
                    restore_code,
                    assigned_to,
                    used,
                ) in records:
                    status = "✅ Used" if used else "🕒 Active"
                    print(
                        f"{file_name} | Created by: {created_by} | Date: {created_at}\n"
                        f"   Restore code: {restore_code or '-'} | Assigned to: {assigned_to or '-'} | Status: {status}\n"
                    )

            except Exception as e:
                print(f"[ERROR] Could not list backups: {e}")

        elif choice == "5":
            break
        else:
            print("[ERROR] Invalid option.")


def system_admin_backup_menu(admin_username: str):
    while True:
        print("\n=== System Admin Backup Menu ===")
        print("1. Restore Backup with Code")
        print("2. Return to Dashboard")

        choice = input("Select an option: ").strip()

        if choice == "1":
            restore_code = input("Enter your restore code: ").strip()
            try:
                success = BackupService.restore_backup(
                    restore_code=restore_code,
                    requesting_admin=admin_username,
                )
                if success:
                    print(f"[SUCCESS] Database restored successfully!")
                else:
                    print("[ERROR] Restore failed.")
            except Exception as e:
                print(f"[ERROR] {e}")

        elif choice == "2":
            print("Returning to dashboard...")
            break

        else:
            print("[ERROR] Invalid option.")
