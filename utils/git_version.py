"""
Moduł do pobierania informacji o wersji z Git
"""
import subprocess
import os
from datetime import datetime
import logging


class GitVersion:
    """Klasa do zarządzania wersją z Git"""

    def __init__(self, repo_path=None):
        self.repo_path = repo_path or os.getcwd()
        self.logger = logging.getLogger(__name__)

    def get_git_info(self):
        """Pobiera informacje o wersji z Git"""
        git_info = {
            "commit_hash": "unknown",
            "commit_hash_short": "unknown",
            "commit_date": "unknown",
            "commit_message": "unknown",
            "branch": "unknown",
            "tag": None,
            "is_dirty": False,
            "is_git_repo": False
        }

        try:
            # Sprawdź czy to repozytorium Git
            if not self._is_git_repo():
                self.logger.warning("Katalog nie jest repozytorium Git")
                return git_info

            git_info["is_git_repo"] = True

            # Pobierz hash commita (pełny)
            git_info["commit_hash"] = self._run_git_command(["git", "rev-parse", "HEAD"]).strip()

            # Pobierz krótki hash (7 znaków)
            git_info["commit_hash_short"] = git_info["commit_hash"][:7] if len(git_info["commit_hash"]) >= 7 else \
            git_info["commit_hash"]

            # Pobierz datę commita
            commit_timestamp = self._run_git_command(["git", "log", "-1", "--format=%ct"]).strip()
            if commit_timestamp:
                commit_time = datetime.fromtimestamp(int(commit_timestamp))
                git_info["commit_date"] = commit_time.strftime("%Y-%m-%d %H:%M:%S")

            # Pobierz wiadomość commita (pierwsza linia)
            git_info["commit_message"] = self._run_git_command(["git", "log", "-1", "--pretty=%s"]).strip()

            # Pobierz nazwę brancha
            git_info["branch"] = self._run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()

            # Sprawdź czy są jakieś niezatwierdzone zmiany
            status_output = self._run_git_command(["git", "status", "--porcelain"])
            git_info["is_dirty"] = len(status_output.strip()) > 0

            # Sprawdź czy aktualny commit ma tag
            tag_info = self._run_git_command(
                ["git", "describe", "--tags", "--exact-match", "HEAD", "2>/dev/null"]).strip()
            if tag_info:
                git_info["tag"] = tag_info

            self.logger.info(
                f"Pobrano informacje Git: commit={git_info['commit_hash_short']}, branch={git_info['branch']}")

        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania informacji Git: {e}")

        return git_info

    def get_formatted_version(self):
        """Zwraca sformatowaną informację o wersji"""
        git_info = self.get_git_info()

        if not git_info["is_git_repo"]:
            return "🚧 Wersja deweloperska (nie-Git)"

        version_parts = []

        # Jeśli jest tag, użyj go jako głównej wersji
        if git_info["tag"]:
            version_parts.append(f"v{git_info['tag']}")
        else:
            version_parts.append(f"commit: {git_info['commit_hash_short']}")

        # Dodaj informację o branchu jeśli nie jest to master/main
        if git_info["branch"] not in ["main", "master"]:
            version_parts.append(f"branch: {git_info['branch']}")

        # Dodaj informację o niezatwierdzonych zmianach
        if git_info["is_dirty"]:
            version_parts.append("⚠️ niezapisane zmiany")

        return " | ".join(version_parts)

    def _is_git_repo(self):
        """Sprawdza czy katalog jest repozytorium Git"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False

    def _run_git_command(self, cmd):
        """Wykonuje komendę Git i zwraca wynik"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=2,
                shell=False
            )
            if result.returncode == 0:
                return result.stdout
            return ""
        except subprocess.TimeoutExpired:
            self.logger.warning("Timeout podczas wykonywania komendy Git")
            return ""
        except Exception as e:
            self.logger.error(f"Błąd wykonania komendy Git {cmd}: {e}")
            return ""

    def get_version_embed_data(self):
        """Zwraca dane do embeda wersji"""
        git_info = self.get_git_info()

        data = {
            "title": "📦 Wersja bota",
            "color": 0x5865F2,
            "fields": [],
            "footer": {}
        }

        if not git_info["is_git_repo"]:
            data["description"] = "🚧 Wersja deweloperska (nie-Git)"
            data["color"] = 0xFF0000
            return data

        # Opis z sformatowaną wersją
        data["description"] = self.get_formatted_version()

        # Podstawowe pola
        data["fields"].extend([
            {
                "name": "📝 Commit",
                "value": f"`{git_info['commit_hash_short']}`",
                "inline": True
            },
            {
                "name": "🌿 Branch",
                "value": git_info["branch"],
                "inline": True
            }
        ])

        # Data commita
        if git_info["commit_date"] != "unknown":
            from datetime import datetime
            try:
                commit_dt = datetime.strptime(git_info["commit_date"], "%Y-%m-%d %H:%M:%S")
                discord_timestamp = f"<t:{int(commit_dt.timestamp())}:R>"
                data["fields"].append({
                    "name": "📅 Data commita",
                    "value": discord_timestamp,
                    "inline": True
                })
            except:
                data["fields"].append({
                    "name": "📅 Data commita",
                    "value": git_info["commit_date"],
                    "inline": True
                })

        # Wiadomość commita
        if git_info["commit_message"] != "unknown":
            # Ogranicz długość wiadomości
            message = git_info["commit_message"]
            if len(message) > 50:
                message = message[:47] + "..."

            data["fields"].append({
                "name": "💭 Wiadomość commita",
                "value": message,
                "inline": False
            })

        # Tag jeśli istnieje
        if git_info["tag"]:
            data["fields"].append({
                "name": "🏷️ Tag",
                "value": git_info["tag"],
                "inline": True
            })

        # Status repozytorium
        status_emoji = "⚠️" if git_info["is_dirty"] else "✅"
        status_text = "Niezatwierdzone zmiany" if git_info["is_dirty"] else "Czyste"
        data["fields"].append({
            "name": f"{status_emoji} Status repozytorium",
            "value": status_text,
            "inline": True
        })

        # Pełny hash w footera
        data["footer"] = {
            "text": f"Full hash: {git_info['commit_hash']}"
        }

        return data


# Singleton dla łatwego dostępu
_git_version_instance = None


def get_git_version():
    """Zwraca instancję GitVersion (singleton)"""
    global _git_version_instance
    if _git_version_instance is None:
        _git_version_instance = GitVersion()
    return _git_version_instance