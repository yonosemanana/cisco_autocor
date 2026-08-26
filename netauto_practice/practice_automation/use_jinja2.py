import logging
from pprint import pprint

from utils import configure_logger
from models import load_inventory, update_credentials, get_device_params
from jinja2 import Environment, FileSystemLoader

from use_netmiko import handle_send_command, handle_send_config_set
from netmiko import ConnectHandler

print("Hello0!")

# Configure console and file loggers
# logger = logging.getLogger(__name__)
# configure_logger()

DEVICE = "SW1"
INVENTORY_FILE = "inventory.yaml"
# Read device inventory from YAML file
# inventory = load_inventory(INVENTORY_FILE)
# pprint(inventory)

print("Hello1!")
#
# # Get credentials in a secure way (e.g. environment variables)
# for device in inventory.devices:
#     update_credentials(inventory.devices[device])
#
# print("Hello2!")
#
# # Read current configuration
# device_params = get_device_params(inventory.devices[DEVICE])
# logger.debug(device_params)
# with ConnectHandler(**device_params) as conn:
#     vlans = handle_send_command(conn, "show vlan brief", use_textfsm=True)
#     pprint(vlans)