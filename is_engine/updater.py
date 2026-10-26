#!/usr/bin/env python3
"""GitHub integration and auto-update system"""

import json
import logging
import urllib.request
import subprocess
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

REPO_OWNER = "6nmsb4mvzs-ui"
REPO_NAME = "is"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
CURRENT_VERSION = "1.0.0"


class GitHubUpdater:
    """Handles GitHub integration and updates"""

    def __init__(self, app_dir: Path):
        self.app_dir = app_dir
        self.version_file = app_dir / ".version"
        self.backup_dir = app_dir / ".backup"
        self.current_version = self._load_version()

    def _load_version(self) -> str:
        """Load current version from file or use default"""
        if self.version_file.exists():
            try:
                return self.version_file.read_text().strip()
            except Exception as e:
                logger.error(f"Failed to read version: {e}")
        return CURRENT_VERSION

    def _save_version(self, version: str):
        """Save version to file"""
        try:
            self.version_file.write_text(version)
        except Exception as e:
            logger.error(f"Failed to save version: {e}")

    def check_for_updates(self) -> Tuple[bool, Optional[str]]:
        """Check if update available on GitHub. Returns (has_update, latest_version)"""
        try:
            with urllib.request.urlopen(f"{API_URL}/releases/latest", timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_tag = data.get("tag_name", "").lstrip("v")

                if latest_tag and latest_tag != self.current_version:
                    logger.info(f"Update available: {self.current_version} -> {latest_tag}")
                    return True, latest_tag
                return False, None
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            return False, None

    def download_update(self, version: str) -> bool:
        """Download latest version from GitHub"""
        try:
            logger.info(f"Downloading version {version}")

            # Create backup
            self.backup_dir.mkdir(exist_ok=True)
            backup_py = self.backup_dir / f"backup_{self.current_version}"
            backup_py.mkdir(exist_ok=True)

            # Backup current files
            for py_file in self.app_dir.glob("*.py"):
                shutil.copy2(py_file, backup_py / py_file.name)

            # Download from GitHub
            download_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/tags/v{version}.zip"
            zip_path = self.app_dir / f"is_{version}.zip"

            logger.info(f"Downloading from {download_url}")
            urllib.request.urlretrieve(download_url, zip_path)

            # Extract and update
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.app_dir / "temp_extract")

            # Move new files
            extracted_dir = self.app_dir / "temp_extract" / f"{REPO_NAME}-{version}"
            if extracted_dir.exists():
                for py_file in extracted_dir.glob("*.py"):
                    shutil.copy2(py_file, self.app_dir / py_file.name)
                logger.info(f"Update applied: {version}")
                self._save_version(version)
                self.current_version = version
                return True

        except Exception as e:
            logger.error(f"Download/update failed: {e}")
            # Restore backup on failure
            self._restore_backup()
            return False
        finally:
            # Cleanup
            try:
                import shutil
                if (self.app_dir / "temp_extract").exists():
                    shutil.rmtree(self.app_dir / "temp_extract")
                if (self.app_dir / f"is_{version}.zip").exists():
                    (self.app_dir / f"is_{version}.zip").unlink()
            except Exception as e:
                logger.debug(f"Cleanup error: {e}")

    def _restore_backup(self):
        """Restore from backup after failed update"""
        try:
            backup_py = self.backup_dir / f"backup_{self.current_version}"
            if backup_py.exists():
                for py_file in backup_py.glob("*.py"):
                    shutil.copy2(py_file, self.app_dir / py_file.name)
                logger.info("Restored from backup")
        except Exception as e:
            logger.error(f"Backup restore failed: {e}")

    def get_remote_version(self) -> Optional[str]:
        """Get latest version from GitHub without updating"""
        has_update, version = self.check_for_updates()
        return version if has_update else None

    def get_status(self) -> dict:
        """Get update status"""
        has_update, latest = self.check_for_updates()
        return {
            "current_version": self.current_version,
            "latest_version": latest,
            "update_available": has_update,
            "repo": f"{REPO_OWNER}/{REPO_NAME}"
        }


def close_all_app_instances():
    """Close other instances of the app (macOS)"""
    try:
        # Kill other Python processes running this app (exclude self)
        import subprocess
        result = subprocess.run(
            ["pgrep", "-f", "is_engine"],
            capture_output=True, text=True
        )
        pids = result.stdout.strip().split('\n')
        import os
        my_pid = str(os.getpid())
        for pid in pids:
            if pid and pid != my_pid:
                try:
                    os.kill(int(pid), 9)
                    logger.info(f"Closed instance {pid}")
                except Exception as e:
                    logger.debug(f"Failed to close {pid}: {e}")
    except Exception as e:
        logger.debug(f"App instance closure failed: {e}")


def restart_app():
    """Restart the application"""
    import sys
    try:
        close_all_app_instances()
        logger.info("Restarting application")
        python = sys.executable
        script = sys.argv[0]
        os.execv(python, [python, script])
    except Exception as e:
        logger.error(f"Restart failed: {e}")
