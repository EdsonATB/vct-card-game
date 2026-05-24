import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    discord_token: str
    database_url: str
    command_prefix: str = "!"
    sync_commands: bool = True


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key:
            os.environ.setdefault(key, value)


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_settings() -> Settings:
    _load_env_file(Path(".env"))

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Define discord token in .env")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("Defina DATABASE_URL no arquivo .env ou nas variaveis de ambiente.")

    return Settings(
        discord_token=token,
        database_url=database_url,
        command_prefix=os.getenv("COMMAND_PREFIX", "!"),
        sync_commands=_get_bool("SYNC_COMMANDS", True),
    )
