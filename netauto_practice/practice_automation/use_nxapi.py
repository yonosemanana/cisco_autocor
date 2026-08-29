import logging
from requests import Session
from pprint import pprint
import json

from utils import configure_logger
from models import load_inventory, update_credentials

logger = logging.getLogger(__name__)
configure_logger()

INVENTORY_FILE = "inventory.yaml"
inventory = load_inventory(INVENTORY_FILE)

for device in inventory.devices.values():
    update_credentials(device)

DEVICE = "NXOS1"

host = inventory.devices[DEVICE].ip
username, password = inventory.devices[DEVICE].username.get_secret_value(), inventory.devices[DEVICE].password.get_secret_value()
BASE_URL = f"http://{host}/ins"

session = Session()
session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
session.verify = False
session.auth = (username, password)

command_type = "cli_show"
command = "show version"
payload = {
    "ins_api": {
        "version": "1.0",
        "type": command_type,
        "chunk": "0",
        "sid": "1",
        "input": command,
        "output_format": "json"
    }
}

# Show version
show_version_response = session.post(BASE_URL, json=payload)
logger.info(show_version_response.status_code)
logger.info(show_version_response.text)
pprint(show_version_response.json())

# Show vlans
payload["ins_api"]["input"] = "show vlan"
logger.info(payload)
show_vlan_response = session.post(BASE_URL, data=json.dumps(payload))
logger.info(show_vlan_response.status_code)
logger.info(show_vlan_response.text)
show_vlan_response_dict = json.loads(show_vlan_response.text)
logger.info(show_vlan_response_dict)
pprint(json.dumps(show_vlan_response_dict, indent=4))

# Configure new VLANs
config_commands = [
    "vlan 10",
    "vlan 20",
    "vlan 30",
    "vlan 100"
]
payload["ins_api"]["type"] = "cli_conf"
payload["ins_api"]["input"] = " ;".join(config_commands)
new_vlans_response = session.post(BASE_URL, json=payload)
logger.info(new_vlans_response.status_code)
pprint(new_vlans_response.json())


# Save config
config_commands = [
    "copy running-config startup-config"
]
payload["ins_api"]["type"] = "cli_conf"
payload["ins_api"]["input"] = " ;".join(config_commands)
save_config_response = session.post(BASE_URL, json=payload)
logger.info(save_config_response.status_code)
pprint(save_config_response.json())