from typing import Optional
import yaml
import os
from dotenv import load_dotenv
from pathlib import Path
from netmiko import ConnectHandler, BaseConnection
import ipaddress

INVENTORY_FILE = "inventory.yaml"

def enable_interface(conn: BaseConnection, interface: str):
    """
    Configure subinterface on L3 Cisco IOS router
    :param conn: BaseConnection object of Netmiko, it represents a network device
    :param interface: interface
    :return: None
    """

    commands = [
        f"interface {interface}",
        "no shutdown"
    ]

    conn.send_config_set(commands)




def configure_subinterface(conn: BaseConnection, vlan_number: int, interface: str, ip: str, mask: str, description: Optional[str] = None):
    """
    Configure subinterface on L3 Cisco IOS router
    :param conn: BaseConnection object of Netmiko, it represents a network device
    :param vlan_number: VLAN number
    :param interface: interface
    :param ip: IP address
    :param mask: Mask
    :param description: Description
    :return:
    """

    netmask = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False).netmask

    commands = [
        f"interface {interface}.{vlan_number}",
        f"encapsulation dot1q {vlan_number}",
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

    device_name = "l3_router"
    vlan_number = 100
    interface = "GigabitEthernet2"
    ip = "10.10.10.2"
    mask = "24"

    device_params = {
        "device_type": "cisco_ios",
        "host": inventory[device_name]["host"],
        "username": os.environ.get("GNS3_USERNAME"),
        "password": os.environ.get("GNS3_PASSWORD")
    }

    conn = ConnectHandler(**device_params)

    configure_subinterface(conn, vlan_number, interface, ip, mask)
    enable_interface(conn, interface)

    conn.save_config()

    conn.disconnect()