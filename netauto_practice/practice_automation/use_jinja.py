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
GENERATE_VLANS_TEMPLATE_FILE = "gen_vlans.j2"
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
vlans_config_set = vlans_config.split("\n")
pprint(vlans_config_set)

# Apply new VLAN configuration to network devices and verify
# with ConnectHandler(**device_params) as conn:
#     vlans_config_output = handle_send_config_set(conn, vlans_config_set)
#     pprint(vlans_config_output)
#
#     vlans = handle_send_command(conn, "show vlan brief")
#     pprint(vlans)
#
#     conn.save_config()

intfs_template = jinja_env.get_template(INTERFACES_TEMPLATE_FILE)
intfs_data = load_yaml(DATA_DIR / DEVICE / INTERFACES_DATA_FILE)
intfs_config = intfs_template.render(interfaces=intfs_data["interfaces"])
intfs_config_set = intfs_config.split("\n")
# Apply new interfaces configuration to network devices and verify
# with ConnectHandler(**device_params) as conn:
#     intfs = handle_send_command(conn, "show run | sec interface")
#     pprint(intfs)
#
#     intfs_config_output = handle_send_config_set(conn, intfs_config_set)
#     pprint(intfs_config_set)
#
#     intfs = handle_send_command(conn, "show run | sec interface")
#     pprint(intfs)
#
#     conn.save_config()



full_config_template = jinja_env.get_template(CONFIG_TEMPLATE_FILE)
full_config_data = load_yaml(DATA_DIR / DEVICE / CONFIG_DATA_FILE)
full_config = full_config_template.render(interfaces=intfs_data["interfaces"], vlans=vlans_data["vlans"], hostname=full_config_data["hostname"])
full_config_set = full_config.split("\n")
# Apply full new configuration to network devices and verify
with ConnectHandler(**device_params) as conn:
    show_run = handle_send_command(conn, "show run")
    pprint(show_run)

    full_config_output = handle_send_config_set(conn, full_config_set)
    pprint(full_config_output)

    show_run = handle_send_command(conn, "show run")
    pprint(show_run)

    conn.save_config()