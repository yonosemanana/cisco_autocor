from pydantic import BaseModel, SecretStr, field_validator
from utils import load_yaml, get_credentials
import ipaddress

from pyats.topology import Device

class NetworkDevice(BaseModel):
    """
    Class for a network device in inventory file
    """
    ip: str
    device_type: str
    username: SecretStr
    password: SecretStr

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, value: str):
        """
        Checks, if provided IP address is correct
        :param value:
        :return:
        """
        ipaddress.ip_address(value)
        return value

class Inventory(BaseModel):
    """
    Class for a network devices inventory
    """
    devices: dict[str, NetworkDevice]

def load_inventory(filepath: str) -> Inventory:
    """
    Returns Inventory object after model validation
    :param filepath: Path to a file with network device inventory
    :return: Inventory
    """
    inventory_dict = load_yaml(filepath)
    return Inventory(**inventory_dict)

def get_device_params(device: NetworkDevice) -> dict:
    """
    Reads device parameters from Network Device object, including secrets (username, password) and returns a dictionary.
    :param device: NetworkDevice
    :return: dict
    """
    return {
        "ip": device.ip,
        "device_type": device.device_type,
        "username": device.username.get_secret_value(),
        "password": device.password.get_secret_value()
    }

def update_credentials(device: NetworkDevice):
    """
    Reads secrets (username and password) from environment variables and update them in NetworkDevice as SecretStr
    :return:
    """
    username, password = get_credentials()
    device.username = SecretStr(username)
    device.password = SecretStr(password)

def update_testbed_credentials(device: Device):
    """
    Reads secrets (username and password) from environment variables and update them in Testbed device object in PyATS
    :return:
    """
    username, password = get_credentials()
    device.credentials.default.username = username
    device.credentials.default.password = password
    device.credentials.enable.password = password