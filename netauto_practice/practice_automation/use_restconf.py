import logging

from utils import configure_logger
from models import load_inventory, update_credentials
from pprint import pprint
from requests import Session, ConnectionError, Timeout
from requests.auth import HTTPBasicAuth
import urllib3

# Configure console and file loggers
logger = logging.getLogger(__name__)
configure_logger()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

INVENTORY_FILE = "inventory.yaml"

DEVICE = "CSR1"
# DEVICE2 = "IOSXR1" # IOS XR doesn't support RESTCONF

# Read device inventory from YAML file
inventory = load_inventory(INVENTORY_FILE)

# Get credentials in a secure way (e.g. environment variables)
for device in inventory.devices.values():
    update_credentials(device)

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

BASE_URL_DATA = "/restconf/data/"
BASE_URL_OPS = "/restconf/operations/"
REQUEST_TIMEOUT = 10

def create_session(username: str, password: str) -> Session:
    """
    Creates a new Session() object from "requests".
    Sets default parameters:
        - HTTP Basic Authentication with given username and password
        - Disable server TLS certificate validation
        - Sets hearders:
            - Accept: application/yang-data+json
    :param username:
    :param password:
    :return:
    """
    session = Session()
    session.verify = False
    session.auth = HTTPBasicAuth(username, password)
    session.headers.update({"Accept": "application/yang-data+json", "Content-type": "application/yang-data+json"})
    return session

# Gracefully handle connection errors with Exceptions
# Log results (output)
# Close session with the device
# Parse device output   # We don't need to parse device output, because RESTCONF on Cisco IOS XE returns data in JSON format
def send_http_request(session: Session, method: str, url: str, params: dict = None, headers: dict = None, data: dict = None, timeout: float = REQUEST_TIMEOUT):
    """
    Sends HTTP request and return results. Data must be JSON
    :param session:
    :param method: HTTP method: GET, PUT, POST, PATCH, DELETE
    :param url:
    :param params: extra parameters
    :param headers: extra headers
    :param data: data for POST, PUT, PATCH methods in JSON format
    :param timeout: float
    :return:
    """
    try:
        response = session.request(method=method, url=url, params=params, headers=headers, json=data if data is not None else None, timeout=timeout)
        logger.debug(f"Response text: {response.text}")
        logger.debug(f"Response headers: {response.headers}")
        logger.debug(f"Response status code: {response.status_code}")
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return response.text

    except Timeout as e:
        logger.error(f"Timeout error: {e}")
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")



# Create a session to a device with requests.Session
session = create_session(connection_params["username"], connection_params["password"])

URL_HOST = f"https://{connection_params['host']}"
YANG_MODEL = "Cisco-IOS-XE-native:native"
DEVICE_URL = URL_HOST + BASE_URL_DATA + YANG_MODEL
URL_VERSION = DEVICE_URL + "/version"
URL_HOSTNAME = DEVICE_URL + "/hostname"

response = send_http_request(session, "GET", URL_HOSTNAME)
pprint(response)


# Read operational parameters ("show" commands)
INTF_OPER_YANG_MODEL = "Cisco-IOS-XE-interfaces-oper:"
URL_INTERFACES_OPER = URL_HOST + BASE_URL_DATA + INTF_OPER_YANG_MODEL + "interfaces/interface"
oper_interfaces = send_http_request(session, "GET", URL_INTERFACES_OPER)
pprint(oper_interfaces)

oper_interface = send_http_request(session, "GET", URL_INTERFACES_OPER + "=GigabitEthernet4")
pprint(oper_interface)

# Read configuration
URL_INTERFACES_CONFIG = DEVICE_URL + "/interface/GigabitEthernet"
interfaces_config = send_http_request(session, "GET", URL_INTERFACES_CONFIG, timeout=5)
pprint(interfaces_config)

URL_INTERFACE_CONFIG = DEVICE_URL + "/interface/GigabitEthernet=5"
interface_config = send_http_request(session, "GET", URL_INTERFACE_CONFIG)
pprint(interface_config)

URL_INTERFACE_CONFIG_IP = DEVICE_URL + "/interface/GigabitEthernet=5/ip/address/primary"
interface_config_ip = send_http_request(session, "GET", URL_INTERFACE_CONFIG_IP)
pprint(interface_config_ip)

# Configure device
URL_INTERFACE_CONFIG_DESCR = DEVICE_URL + "/interface/GigabitEthernet=7/description"
data = {"description": "New description configured with RESTCONF and Python!"}
interface_config_descr = send_http_request(session, "PATCH", URL_INTERFACE_CONFIG_DESCR, data=data)
pprint(interface_config_descr)

URL_INTERFACE_CONFIG_IP2 = DEVICE_URL + "/interface/GigabitEthernet=7/ip/address/primary"
data2 = {"primary": {"address": "192.168.77.1", "mask": "255.255.255.0"}}
interface_config_ip2 = send_http_request(session, "PUT", URL_INTERFACE_CONFIG_IP2, data=data2)
pprint(interface_config_ip2)

URL_INTERFACE_CONFIG_NO_SHUT = DEVICE_URL + "/interface/GigabitEthernet=7/shutdown"
interface_config_no_shut = send_http_request(session, "DELETE", URL_INTERFACE_CONFIG_NO_SHUT)
pprint(interface_config_no_shut)

# Run operational commands (save config, install software, reboot, etc.)
IA_YANG_MODEL = "cisco-ia:"
URL_SAVE_CONFIG = URL_HOST + BASE_URL_OPS + IA_YANG_MODEL + "save-config"
save_config = send_http_request(session, "POST", URL_SAVE_CONFIG)
pprint(save_config)



