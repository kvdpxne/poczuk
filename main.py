from bot.discord_bot import DiscordBot
from utils.logger import setup_logging, log_info


def main():
    # Inicjalizacja logowania
    setup_logging()

    # Logi startu
    log_info('main', "Discord Channel Cleaner - Uruchamianie")

    # Inicjalizacja menedżera konfiguracji (tworzy tabele)
    from config.config_manager import ConfigManager
    ConfigManager()
    log_info('main', "Baza danych zainicjalizowana")

    # Utwórz i uruchom bota
    bot = DiscordBot()
    bot.run_bot()


if __name__ == "__main__":
    main()