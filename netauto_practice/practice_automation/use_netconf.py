import logging
from utils import configure_logger
from models import load_inventory, update_credentials
from pprint import pprint
from copy import deepcopy

from ncclient import manager
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import SSHError, AuthenticationError


INVENTORY_FILE = "inventory.yaml"

DEVICE = "CSR1"
DEVICE2 = "IOSXR1"

# Configure console and file loggers
logger = logging.getLogger(__name__)
configure_logger()

# Read device inventory from YAML file
inventory = load_inventory(INVENTORY_FILE)
pprint(inventory)

# Get credentials in a secure way (e.g. environment variables)
for device in inventory.devices.values():
    update_credentials(device)
pprint(inventory)

# Create a session to a device with ncclient
connection_params = {
    "host": inventory.devices[DEVICE].ip,
    "port": 830,
    "username": inventory.devices[DEVICE].username.get_secret_value(),
    "password": inventory.devices[DEVICE].password.get_secret_value(),
    "device_params": {"name": "csr"},
    "hostkey_verify": False,
    "look_for_keys": False,
    "allow_agent": False
}

connection_params2 = {
    "host": inventory.devices[DEVICE2].ip,
    "port": 830,
    "username": inventory.devices[DEVICE2].username.get_secret_value(),
    "password": inventory.devices[DEVICE2].password.get_secret_value(),
    "device_params": {"name": "iosxr"},
    "hostkey_verify": False,
    "look_for_keys": False,
    "allow_agent": False
}

# Gracefully handle connection errors with Exceptions
# Log results (output)

try:
    with manager.connect(**connection_params) as m:
        config = m.get_config(source="running")
        logger.info(f"Printing configuration of device {DEVICE}:")
        pprint(config.data)
        pprint(config.data_xml)
except SSHError as e:
    logger.error(f"Connection error: {e}")
except AuthenticationError as e:
    logger.error(f"Authentication error: {e}")
except RPCError as e:
    logger.error(f"RPC error: {e}")

# Read configuration
filter2 = ('subtree', '<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg"/>')

try:
    with manager.connect(**connection_params2) as m2:
        config2 = m2.get_config(source="candidate", filter=filter2)
        logger.info(f"Printing configuration of device {DEVICE2}:")
        pprint(config2)
        pprint(config.data_xml)
except SSHError as e:
    logger.error(f"Connection error: {e}")
except AuthenticationError as e:
    logger.error(f"Authentication error: {e}")
except RPCError as e:
    logger.error(f"RPC error: {e}")


# Read operational parameters ("show" commands)


# Configure device

# Run operational commands (save config, install software, reboot, etc.)

# Close session with the device

# Parse device output


