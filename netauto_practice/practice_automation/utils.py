import logging
from logging.handlers import RotatingFileHandler
from typing import List, Dict, Tuple
import yaml
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

LOG_FILE = "debug.log"
NET_USERNAME = "NET_USERNAME"
NET_PASSWORD = "NET_PASSWORD"

class ConfigFileError(Exception):
    """
    Custom exception to handle errors when loading data from YAML config files.
    """
    pass

class EnvVarError(Exception):
    """
    Custom exception to handle errors when reading OS environment variables.
    """
    pass

class CredentialsError(Exception):
    """
    Custom exception to handle errors when credentials (username, password) not provided
    """
    pass

def configure_logger():
    """
    Configure logging. Configure console and file loggers
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes = 1 * 1024 * 1024, backupCount = 5, encoding = "utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def load_yaml(filepath: str) -> Dict | List:
    """
    Load data from the YAML file.

    :return: data from the YAML file (dict or list)
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            return yaml.safe_load(f)

    except FileNotFoundError as e:
        raise ConfigFileError(f"File not found: {filepath}")
    except PermissionError as e:
        raise ConfigFileError(f"Permissions error: {e}")
    except OSError as e:
        raise ConfigFileError(f"Generic I/O error: {e}")
    except UnicodeDecodeError as e:
        raise ConfigFileError(f"Unicode decoding error: {e}")
    except yaml.YAMLError as e:
        raise ConfigFileError(f"Error when loading YAML file: {e}")

def get_env_var(envvar_name: str) -> str:
    """
    Gets OS environment variable by its name
    :param envvar_name: environment variable name
    :return: OS environment variable value
    """
    envvar = os.getenv(envvar_name)

    if envvar is None:
        raise EnvVarError(f"Environment variable {envvar_name} is not set")
    envvar = envvar.strip()
    if not envvar:
        raise EnvVarError(f"Environment variable {envvar_name} is empty")
    return envvar


def get_credentials() -> Tuple[str, str]:
    """
    Get network device credentials (username and password) from environment variables.

    Environment variables must be set in OS:
        - NET_USERNAME
        - NET_PASSWORD

    :return: tuple (username, password)
    """
    try:
        load_dotenv()
        net_username = get_env_var(NET_USERNAME)
        net_password = get_env_var(NET_PASSWORD)
        return net_username, net_password
    except EnvVarError as e:
        raise CredentialsError(f"Credentials (username, password) are not set as environment variables: {NET_USERNAME}, "
                               f"{NET_PASSWORD}.\n{e}")


