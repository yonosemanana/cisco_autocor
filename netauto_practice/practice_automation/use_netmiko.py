import logging
from pprint import pprint

# from netmiko import ConnectHandler

from utils import configure_logger, get_credentials
from models import load_inventory

INVENTORY_FILE = "inventory.yaml"

# Configure console and file loggers
logger = logging.getLogger(__name__)
configure_logger()

# Read device inventory from YAML file
inventory = load_inventory(INVENTORY_FILE)
pprint(inventory)
pprint(inventory.devices)

# Get credentials in a secure way (e.g. environment variables)
username, password = get_credentials()
for device in inventory.devices.values():
    device.username = username
    device.password = password

# Create a session to a device with ConnectHandler

# Gracefully handle connection errors with Exceptions

# Log results (output)

# Read operational parameters ("show" commands)

# Read configuration

# Configure device

# Run operational commands (save config, install software, reboot, etc.)

# Close session with the device

# Parse device output


