import logging
from pprint import pprint
from pathlib import Path

from utils import configure_logger
from models import load_inventory, update_credentials, get_device_params
from utils import load_yaml

from jinja2 import Environment, FileSystemLoader
from use_netmiko import handle_send_command, handle_send_config_set
from netmiko import ConnectHandler

# Configure console and file loggers
logger = logging.getLogger(__name__)
configure_logger()

DEVICE = "SW1"
INVENTORY_FILE = "inventory.yaml"
# Read device inventory from YAML file
inventory = load_inventory(INVENTORY_FILE)
# pprint(inventory)

# Get credentials in a secure way (e.g. environment variables)
for device in inventory.devices:
    update_credentials(inventory.devices[device])

device_params = get_device_params(inventory.devices[DEVICE])


# Read current configuration
with ConnectHandler(**device_params) as conn:
    vlans = handle_send_command(conn, "show vlan brief", use_textfsm=True)
    pprint(vlans)

    interfaces = handle_send_command(conn, "show run | sec interface")
    pprint(interfaces)

# Generate config with Jinja2 templates
DATA_DIR = Path("data")
JINJA2_DIR = Path("jinja2_templates")
GENERATE_VLANS_TEMPLATE_FILE = "vlans.j2"
VLANS_TEMPLATE_FILE = "vlans.j2"
INTERFACES_TEMPLATE_FILE = "interfaces.j2"
CONFIG_TEMPLATE_FILE = "config.j2"
VLANS_DATA_FILE = "vlans.yaml"
INTERFACES_DATA_FILE = "interfaces.yaml"
CONFIG_DATA_FILE = "config.yaml"

jinja_env = Environment(loader=FileSystemLoader(JINJA2_DIR), trim_blocks=True)
gen_vlans_template = jinja_env.get_template(GENERATE_VLANS_TEMPLATE_FILE)

generated_vlans_config = gen_vlans_template.render()
pprint(generated_vlans_config)

vlans_template = jinja_env.get_template(VLANS_TEMPLATE_FILE)
vlans_data = load_yaml(DATA_DIR / DEVICE / VLANS_DATA_FILE)
pprint(vlans_data)
vlans_config = vlans_template.render(vlans=vlans_data["vlans"])
pprint(vlans_config)

# Apply new configuration to network devices and verify
with ConnectHandler(**device_params) as conn:
    vlans_config_output = handle_send_config_set(conn, vlans_config)
    pprint(vlans_config_output)

    vlans = handle_send_command(conn, "show vlan brief")
    pprint(vlans)