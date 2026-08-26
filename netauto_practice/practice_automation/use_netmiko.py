import logging
from pprint import pprint
from utils import configure_logger
from models import load_inventory, update_credentials, get_device_params

from netmiko import ConnectHandler, BaseConnection
from netmiko.exceptions import NetmikoBaseException
from paramiko.ssh_exception import SSHException


INVENTORY_FILE = "inventory.yaml"

DEVICE = "CSR1"

# Configure console and file loggers
logger = logging.getLogger(__name__)
configure_logger()

def handle_send_command(device: BaseConnection, command: str, use_textfsm: bool = False) -> str | None:
    """
    Runs send_command() Netmiko function on the given device and handles exceptions
    :return: output from the device or None in case of error
    """
    try:
        output = device.send_command(command, use_textfsm=use_textfsm)
        logger.debug(f"Output of command {command} from device {device.host}: {output}")
        return output
    except (NetmikoBaseException, SSHException) as e:
        logger.error(f"Error when connecting to {device_params['ip']}: {e}")
        return None

def handle_send_config_set(device: BaseConnection, config_set: list[str]) -> str | None:
    """
    Runs send_config_set() Netmiko function on the given device and handles exceptions
    :return: output from the device
    """
    try:
        output = device.send_config_set(config_set)
        logger.debug(f"Output of commands {config_set} from device {device.host}: {output}")
        return output
    except (NetmikoBaseException, SSHException) as e:
        logger.error(f"Error when connecting to {device_params['ip']}: {e}")
        return None

if __name__ == "__main__":
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
        show_version_raw = handle_send_command(session, "show version")
        pprint(show_version_raw)

    # Gracefully handle connection errors with Exceptions
    try:
        session = ConnectHandler(**device_params)
        show_clock = session.send_command("show clock", use_textfsm=True)
        pprint(show_clock)
        session.disconnect()
    except (NetmikoBaseException, SSHException) as e:
        logger.error(f"Error when connecting to {device_params['ip']}: {e}")

    # Log results (output)
    # See above

    # Read operational parameters ("show" commands)
    # See above

    # Read configuration
    with ConnectHandler(**device_params) as session:
        running_config = handle_send_command(session, "show running-config")
        logger.info(f"Running config of device {session.host}: {running_config}")

    # Configure device
    lo_intf_config = [
        "interface Loopback1",
        "description Test Loopback",
        "ip address 1.1.1.1 255.255.255.255"
    ]

    with ConnectHandler(**device_params) as session:
        output = handle_send_config_set(session, lo_intf_config)
        logger.info(f"Configuring Loopback interface on device {session.host}: {output}")

    # Run operational commands (save config, install software, reboot, etc.)
    with ConnectHandler(**device_params) as session:
        session.save_config()
        output = handle_send_command(session, "ping 1.1.1.1")
        logger.info(f"Output of 'ping 1.1.1.1' command: {output}")
    # For more complicated cases you must handle [Yes/No] dialogs!

    # Close session with the device
    # See above.

    # Parse device output
    with ConnectHandler(**device_params) as session:
        show_version = handle_send_command(session, "show version", use_textfsm=True)
        logger.info(f"Software version of device {session.host}: {show_version}")


