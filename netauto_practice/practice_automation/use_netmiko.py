import logging
from pprint import pprint
from utils import configure_logger
from models import load_inventory, update_credentials, get_device_params

from netmiko import ConnectHandler


INVENTORY_FILE = "inventory.yaml"

DEVICE = "CSR1"

# Configure console and file loggers
logger = logging.getLogger(__name__)
configure_logger()

# Read device inventory from YAML file
inventory = load_inventory(INVENTORY_FILE)
pprint(inventory)
pprint(inventory.devices)

# Get credentials in a secure way (e.g. environment variables)
for device in inventory.devices.values():
    update_credentials(device)

# Create a session to a device with ConnectHandler
device = inventory.devices["CSR1"]
device_params = get_device_params(device)

with ConnectHandler(**device_params) as session:
    show_version_raw = session.send_command("show version")
    pprint(show_version_raw)

# Gracefully handle connection errors with Exceptions

# Log results (output)

# Read operational parameters ("show" commands)

# Read configuration

# Configure device

# Run operational commands (save config, install software, reboot, etc.)

# Close session with the device

# Parse device output
with ConnectHandler(**device_params) as session:
    show_version_parsed = session.send_command("show version", use_textfsm=True)
    pprint(show_version_parsed)

