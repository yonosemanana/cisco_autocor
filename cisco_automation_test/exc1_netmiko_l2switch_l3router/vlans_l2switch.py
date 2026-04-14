from typing import Optional
import yaml
import os
from dotenv import load_dotenv
from pathlib import Path
from netmiko import ConnectHandler, BaseConnection
import ipaddress

INVENTORY_FILE = "inventory.yaml"

def configure_vlan(conn: BaseConnection, vlan_number: int, vlan_name: Optional[str] = None):
    """
    Creates a VLAN on Cisco IOS network device, optionally with its name

    :param conn: BaseConnection object of Netmiko, it represents a network device
    :param vlan_number: VLAN number
    :param vlan_name: VLAN name
    :return: None
    """

    if not isinstance(vlan_number, int) or not vlan_number in range (1, 4095):
        raise ValueError(f"VLAN number must be integer 1-4094! Given value {vlan_number}.")

    commands = [
        f"vlan {vlan_number}",
    ]

    if not vlan_name is None:
        commands.append(f"name {vlan_name}")

    conn.send_config_set(commands)

def configure_trunk(conn: BaseConnection, interface: str):
    """
    Configures interface on Cisco IOS network device in trunk mode

    :param conn: BaseConnection object of Netmiko, it represents a network device
    :param interface: Trunk interface
    :return: None
    """

    commands = [
        f"interface {interface}",
        "switchport trunk encapsulation dot1q",
        "switchport mode trunk"
    ]

    conn.send_config_set(commands)

def trunk_add_vlan(conn: BaseConnection, vlan_number: int, interface: str):
    """
    Adds a VLAN to trunk interface on Cisco IOS network device.

    :param conn: BaseConnection object of Netmiko, it represents a network device
    :param vlan_number: VLAN number
    :param interface: Trunk interface
    :return: None
    """

    commands = [
        f"interface {interface}",
        f"switchport trunk allowed vlan add {vlan_number}"
    ]

    conn.send_config_set(commands)


def configure_svi(conn: BaseConnection, vlan_number: int, ip: str, mask: str, description: Optional[str] = None):
    """
    Configures IP address and mask on the given SVI on Cisco IOS device

    :param conn: BaseConnection object of Netmiko, it represents a network device
    :param vlan_number: VLAN number
    :param ip: IP address
    :param mask: Mask
    :return: None
    """

    netmask = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False).netmask
    commands = [
        f"interface vlan {vlan_number}",
        f"ip address {ip} {netmask}",
        "no shutdown"
    ]

    if not description is None:
        commands.append(f"description {description}")

    conn.send_config_set(commands)

if __name__ == "__main__":

    load_dotenv()

    with open( Path(__file__).parent / INVENTORY_FILE) as f:
        inventory = yaml.safe_load(f)

    device_name = "l2_switch"
    vlan_number = 100
    vlan_name = "Test VLAN"
    interface = "Ethernet0/1"
    ip = "10.10.10.6"
    mask = "24"

    device_params = {
        "device_type": "cisco_ios",
        "host": inventory[device_name]["host"],
        "username": os.environ.get("GNS3_USERNAME"),
        "password": os.environ.get("GNS3_PASSWORD")
    }

    conn = ConnectHandler(**device_params)

    configure_vlan(conn, vlan_number, vlan_name)
    # configure_trunk(conn, interface)
    # trunk_add_vlan(conn, vlan_number, interface)
    configure_svi(conn, vlan_number, ip, mask)

    conn.save_config()

    conn.disconnect()