import logging

from utils import configure_logger
from models import load_inventory, update_credentials
from pprint import pprint
import requests
from requests import Session, ConnectionError, Timeout
import urllib3
from lxml import etree
import base64

# Configure console and file loggers
logger = logging.getLogger(__name__)
configure_logger()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

INVENTORY_FILE = "inventory.yaml"

DEVICE = "PA-VM1"

# Read device inventory from YAML file
inventory = load_inventory(INVENTORY_FILE)

# Get credentials in a secure way (e.g. environment variables)
for device in inventory.devices.values():
    update_credentials(device)

# Create a session to a device with ncclient
connection_params = {
    "host": inventory.devices[DEVICE].ip,
    "username": inventory.devices[DEVICE].username.get_secret_value(),
    "password": inventory.devices[DEVICE].password.get_secret_value(),
}

REQUEST_TIMEOUT = 10

# Generate API key for Palo Alto user
def generate_api_key(host: str, username: str, password: str) -> str:
    """
    Generates API key for Palo Alto firewall and given username and password.
    The user must have access rights to generate API key for himself.

    :param host: IP / FQDN of Palo Alto firewall
    :param username:
    :param password:
    :return:
    """
    GEN_API_URL = f"https://{host}/api/"

    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

    response = requests.post(GEN_API_URL, verify=False,
                             headers={"Authorization": "Basic {credentials}"},
                                params={"type": "keygen", "user": username, "password": password})
    response.raise_for_status()

    response_xml = etree.fromstring(response.text)
    return response_xml.find(".//key").text

def create_session() -> Session:
    """
    Creates a new Session() object from "requests".
    X-PAN-KEY header is used by Palo Alto REST API and this function is for XML API.

    Sets default parameters:
        - Disable server TLS certificate validation
        - Sets hearders:
            - Content-Type: application/x-www-form-urlencoded
    :param api_key:
    :return:
    """
    session = Session()
    session.verify = False
    session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
    return session

# Gracefully handle connection errors with Exceptions
# Log results (output)
# Close session with the device
# Parse device output   # We don't need to parse device output, because RESTCONF on Cisco IOS XE returns data in JSON format
def send_http_request_pa(session: Session, method: str, url: str, api_key: str, params: dict = None, headers: dict = None, data: dict = None, timeout: float = REQUEST_TIMEOUT):
    """
    Sends HTTP request and return results. Data must be JSON
    :param session:
    :param method: HTTP method: GET, PUT, POST, PATCH, DELETE
    :param api_key: API Key
    :param url:
    :param params: extra parameters
    :param headers: extra headers
    :param data: data for POST, PUT, PATCH methods in JSON format
    :param timeout: float
    :return:
    """
    if params is None:
        params = {}
    params.update({"key": api_key})

    try:
        response = session.request(method=method, url=url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text

    except Timeout as e:
        logger.error(f"Timeout error: {e}")
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")



# Create a session to a device with requests.Session
api_key = generate_api_key(connection_params["host"], connection_params["username"], connection_params["password"])
session = create_session()

PALO_BASE_URL = f"https://{connection_params['host']}/api"

params_sys_info = {"type": "op",
                   "cmd": "<show><system><info></info></system></show>"}
response = send_http_request_pa(session, "GET", PALO_BASE_URL, api_key, params=params_sys_info)
pprint(response)


# Read operational parameters ("show" commands)
params_sys_info = {"type": "op",
                   "cmd": "<show><high-availability><state></state></high-availability></show>"}
sys_info = send_http_request_pa(session, "GET", PALO_BASE_URL, api_key, params=params_sys_info)
pprint(sys_info)

# Read configuration
params_run_config = {"type": "op",
                   "cmd": "<show><config><running></running></config></show>"}
running_config = send_http_request_pa(session, "GET", PALO_BASE_URL, api_key, params=params_run_config)
pprint(running_config)

params_run_config_network = {"type": "op",
                   "cmd": "<show><config><running><xpath>devices/entry/network</xpath></running></config></show>"}
running_config_network = send_http_request_pa(session, "GET", PALO_BASE_URL, api_key, params=params_run_config_network)
pprint(running_config_network)

params_config_interfaces = {"type": "config",
                   "action": "get",
                   "xpath": "/config/devices/entry[@name='localhost.localdomain']/network/interface/ethernet/entry[@name='ethernet1/2']"}
config_interfaces = send_http_request_pa(session, "GET", PALO_BASE_URL, api_key, params=params_config_interfaces)
pprint(config_interfaces)


# Configure device
params_config_interfaces_ip = {"type": "config",
                   "action": "set",
                   "element": "<entry name='192.168.99.1/24'/>",
                   "xpath": "/config/devices/entry[@name='localhost.localdomain']/network/interface/ethernet/entry[@name='ethernet1/1']/layer3/ip"}
config_interfaces_ip = send_http_request_pa(session, "POST", PALO_BASE_URL, api_key, params=params_config_interfaces_ip)
pprint(config_interfaces_ip)

params_config_interfaces_ip_show = {"type": "config",
                   "action": "get",
                   "xpath": "/config/devices/entry[@name='localhost.localdomain']/network/interface/ethernet/entry[@name='ethernet1/1']"}
config_interfaces_ip_show = send_http_request_pa(session, "GET", PALO_BASE_URL, api_key, params=params_config_interfaces_ip_show)
pprint(config_interfaces_ip_show)

params_config_interfaces_descr = {"type": "config",
                   "action": "set",
                   "element": "<comment>Configured with XML API!</comment>",
                   "xpath": "/config/devices/entry[@name='localhost.localdomain']/network/interface/ethernet/entry[@name='ethernet1/1']"}
config_interfaces_descr = send_http_request_pa(session, "GET", PALO_BASE_URL, api_key, params=params_config_interfaces_descr)
pprint(config_interfaces_descr)

params_config_interfaces_vr = {"type": "config",
                   "action": "set",
                   "element": "<member>ethernet1/1</member>",
                   "xpath": "/config/devices/entry[@name='localhost.localdomain']/network/virtual-router/entry[@name='default']/interface"}
config_interfaces_vr = send_http_request_pa(session, "GET", PALO_BASE_URL, api_key, params=params_config_interfaces_vr)
pprint(config_interfaces_vr)


# Run operational commands (commit config, install software, reboot, etc.)
params_commit = {"type": "commit",
                 "cmd": "<commit></commit>"}
commit = send_http_request_pa(session, "POST", PALO_BASE_URL, api_key, params=params_commit)
pprint(commit)

params_jobs = {"type": "op",
               "cmd": "<show><jobs><all></all></jobs></show>"}
jobs = send_http_request_pa(session, "POST", PALO_BASE_URL, api_key, params=params_jobs)
pprint(jobs)

job_id = 3
params_job = {"type": "op",
              "cmd": f"<show><jobs><id>{job_id}</id></jobs></show>"}
job = send_http_request_pa(session, "POST", PALO_BASE_URL, api_key, params=params_job)
pprint(job)