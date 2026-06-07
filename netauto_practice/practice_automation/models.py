from pydantic import BaseModel, SecretStr, field_validator
from utils import load_yaml
import ipaddress

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
