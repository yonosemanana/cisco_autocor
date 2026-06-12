import logging
from typing import Callable, Any
from pprint import pprint
from utils import configure_logger
from models import update_testbed_credentials

from genie.testbed import load
from pyats.topology import Device
from unicon.core.errors import ConnectionError, TimeoutError, UniconAuthenticationError, StateMachineError, SubCommandFailure, CredentialsExhaustedError
from genie.utils.diff import Diff

TESTBED_FILE = "testbed.yaml"

DEVICE = "CSR1"

SUPPORTED_PYATS_FUNCTIONS = [
    "execute",
    "parse",
    "learn",
    "configure",
    "diff"
]

# Configure console and file loggers
logger = logging.getLogger(__name__)
configure_logger()

def handle_pyats_call(device: Device, func_name: str, *args, **kwargs) -> Any:
    """
    Calls the given PyATS function on the given device and return results. This wrapper catches connection exceptions.

    :param device: Testbed device
    :param func: PyATS function
    :param args: positional arguments of the PyATS function
    :param kwargs: keyword arguments of the PyATS function
    :return:
    """
    if func_name.lower() not in SUPPORTED_PYATS_FUNCTIONS:
        raise ValueError(f"Function '{func_name}' is not supported in PyATS wrapper!")

    try:
        device.connect()
        func = getattr(device, func_name)
        result = func(*args, **kwargs)
        device.disconnect()
        return result
    except (ConnectionError, TimeoutError, StateMachineError, SubCommandFailure, UniconAuthenticationError, CredentialsExhaustedError) as e:
        logger.error(f"Error when connecting to device {device}: {e}")


# Read device inventory from YAML file
testbed = load(TESTBED_FILE)
pprint(testbed)
pprint(testbed.devices)


# Get credentials in a secure way (e.g. environment variables)
for device in testbed.devices:
    update_testbed_credentials(testbed.devices[device])

# Create a session to a device with ConnectHandler
sw1 = testbed.devices["SW1"]
sw1.connect()

show_version = sw1.execute("show version")
pprint(show_version)

# Log results (output)
logger.info(show_version)

# Close session with the device
sw1.disconnect()

# Gracefully handle connection errors with Exceptions
sw1 = testbed.devices["SW1"]
show_version = handle_pyats_call(sw1, "execute", "show version")
logger.info(show_version)


# Read operational parameters ("show" commands)
# See above

# Parse device output
sw1 = testbed.devices["SW1"]
show_version = handle_pyats_call(sw1, "parse", "show version")
logger.info(show_version)


# Read configuration
csr1 = testbed.devices["CSR1"]

config_raw = handle_pyats_call(csr1, "execute", "show running-config")
pprint(config_raw)

config_parsed = handle_pyats_call(csr1, "learn", "config")
pprint(config_parsed)


# Learn device state
csr1 = testbed.devices["CSR1"]
csr1.connect()
intfs = csr1.learn("interface")
pprint(intfs.info)
csr1.disconnect()


# Configure device
lo2_intf_config = [
    "interface Loopback2",
    "description Test2 Loopback",
    "ip address 2.2.2.2 255.255.255.255"
]
handle_pyats_call(csr1, "configure", lo2_intf_config)


# Compare two device states with 'diff'
config_parsed2 = handle_pyats_call(csr1, "learn", "config")

diff_config = Diff(config_parsed, config_parsed2)
diff_config.findDiff()
logger.info(diff_config)

intfs2 = handle_pyats_call(csr1, "learn", "interface")
diff_intfs = Diff(intfs.info, intfs2.info)
diff_intfs.findDiff()
logger.info(diff_intfs)


# Run operational commands (save config, install software, reboot, etc.)
handle_pyats_call(csr1, "execute", "write memory")
# For more complicated cases you must handle [Yes/No] dialogs!

