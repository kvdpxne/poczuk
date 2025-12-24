"""
Zarządzanie tokenem bota
"""
import os


class TokenManager:
    """Zarządza tokenem autoryzacyjnym bota"""
    
    def __init__(self, token_path: str = "data/token.txt"):
        self.token_path = token_path
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Tworzy katalog data jeśli nie istnieje"""
        os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
    
    def load_token(self) -> str:
        """Ładuje token z pliku"""
        if os.path.exists(self.token_path):
            with open(self.token_path, 'r') as f:
                return f.read().strip()
        return ""
    
    def save_token(self, token: str) -> bool:
        """Zapisuje token do pliku"""
        try:
            with open(self.token_path, 'w') as f:
                f.write(token.strip())
            return True
        except Exception:
            return False
    
    def has_token(self) -> bool:
        """Sprawdza czy token istnieje"""
        token = self.load_token()
        return bool(token and token.strip())
