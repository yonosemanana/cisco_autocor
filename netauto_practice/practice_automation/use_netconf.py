import logging

from utils import configure_logger
from models import load_inventory, update_credentials
from pprint import pprint
from lxml import etree

from ncclient import manager
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import SSHError, AuthenticationError, TransportError

# Configure console and file loggers
logger = logging.getLogger(__name__)
configure_logger()

def netconf_call(connection_params: dict, operation_name: str, *args, **kwargs):
    """
    The function creates a device Manager with given params, calls NETCONF operation from it and returns the response, and handles exceptions.
    :param connection_params: Parameters to create Ncclient's Manager
    :param operation_name: Ncclient's operation
    :param args:
    :param kwargs:
    :return:
    """
    try:
        with manager.connect(**connection_params) as m:
            operation = getattr(m, operation_name)
            return operation(*args, **kwargs)
    except SSHError as e:
        logger.error(f"Connection error: {e}")
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
    except RPCError as e:
        logger.error(f"RPC error: {e}")
    except TransportError as e:
        logger.error(f"Transport error: {e}")


def netconf_configure_iosxr(connection_params: dict, *args, **kwargs):
    """
    IOS XR requires changing in "candidate" config and "commit" in the same session.
    The function creates a device Manager with given params, calls NETCONF <edit-config> and <commit> operations from it and returns the response, and handles exceptions.
    :param connection_params: Parameters to create Ncclient's Manager
    :param operation_name: Ncclient's operation
    :param args:
    :param kwargs:
    :return: tuple of responses from <edit-config> and <commit>
    """
    try:
        with manager.connect(**connection_params) as m:
            response1 = m.edit_config(*args, **kwargs)
            response2 = m.commit()
            return response1, response2
    except SSHError as e:
        logger.error(f"Connection error: {e}")
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
    except RPCError as e:
        logger.error(f"RPC error: {e}")
    except TransportError as e:
        logger.error(f"Transport error: {e}")


INVENTORY_FILE = "inventory.yaml"

DEVICE = "CSR1"
DEVICE2 = "IOSXR1"


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
# Open and close session with the device
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
data_filter = ('subtree', '<interfaces xmlns="http://openconfig.net/yang/interfaces"/>')
data_filter2 = ('subtree',
                """<interfaces xmlns="http://openconfig.net/yang/interfaces">
                        <interface>
                            <name>GigabitEthernet0/0/0/0</name>
                        </interface>
                    </interfaces>
                """)

config_data = netconf_call(connection_params2, "get_config", source="candidate", filter=data_filter2)
pprint(config_data)

# Read operational parameters ("show" commands)
data_filter3 = ('xpath', ({'open-if': 'http://openconfig.net/yang/interfaces'},
                          '//open-if:interface[open-if:name="GigabitEthernet1"]')
                )

oper_data = netconf_call(connection_params, "get", filter=data_filter3)
pprint(oper_data.data_xml)

# Configure device
int_config_descr = """
<config>
    <oc-if:interfaces xmlns:oc-if="http://openconfig.net/yang/interfaces">
        <oc-if:interface>
            <oc-if:name>GigabitEthernet0/0/0/0</oc-if:name>
            <oc-if:config>
                <oc-if:description>Configured by NETCONF!</oc-if:description>
            </oc-if:config>
        </oc-if:interface>
    </oc-if:interfaces>
</config>
"""
int_config1 = """
<config>
    <if:interface-configurations xmlns:if="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
        <if:interface-configuration>
            <if:active>act</if:active>
            <if:interface-name>GigabitEthernet0/0/0/0</if:interface-name>
            <if:description>Configured by NETCONF - 2!</if:description>
            <ipv4:ipv4-network xmlns:ipv4="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
                <ipv4:addresses>
                    <ipv4:primary>
                        <ipv4:address>192.168.1.1</ipv4:address>
                        <ipv4:netmask>255.255.255.0</ipv4:netmask>
                    </ipv4:primary>
                </ipv4:addresses>
            </ipv4:ipv4-network>
        </if:interface-configuration>
    </if:interface-configurations>
</config>
"""


IFMGR_NS = "http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg"
IPV4_INT_NS = "http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg"

config = etree.Element("config", nsmap={None: IFMGR_NS})
interface_configurations = etree.SubElement(config, "interface-configurations")
interface_configuration = etree.SubElement(interface_configurations, "interface-configuration")
active = etree.SubElement(interface_configuration, "active")
active.text = "act"
interface_name = etree.SubElement(interface_configuration, "interface-name")
interface_name.text = "GigabitEthernet0/0/0/0"
description = etree.SubElement(interface_configuration, "description")
description.text = "Configured by NETCONF - 3!"
ipv4_network = etree.SubElement(interface_configuration, "ipv4-network", nsmap={None: IPV4_INT_NS})
ipv4_addresses = etree.SubElement(ipv4_network, "addresses")
ipv4_primary = etree.SubElement(ipv4_addresses, "primary")
ipv4_address = etree.SubElement(ipv4_primary, "address")
ipv4_address.text = "172.21.99.1"
ipv4_mask = etree.SubElement(ipv4_primary, "netmask")
ipv4_mask.text = "255.255.192.0"


int_config2 = """
<config>
    <if:interface-configurations xmlns:if="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
        <if:interface-configuration>
            <if:active>act</if:active>
            <if:interface-name>GigabitEthernet0/0/0/0</if:interface-name>
            <if:description>Configured by NETCONF - 2!</if:description>
            <ipv4:ipv4-network xmlns:ipv4="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
                <ipv4:addresses>
                    <ipv4:primary>
                        <ipv4:address>192.168.1.1</ipv4:address>
                        <ipv4:netmask>255.255.255.0</ipv4:netmask>
                    </ipv4:primary>
                </ipv4:addresses>
            </ipv4:ipv4-network>
        </if:interface-configuration>
    </if:interface-configurations>
</config>
"""

config_res = netconf_configure_iosxr(connection_params2, target="candidate", config=config, default_operation="merge")
for res in config_res:
    pprint(res)

# Configure IOS XE router
config_res = netconf_call(connection_params, "get_config", source="running")
pprint(config_res)


IOSXE_NATIVE_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-native"
config2 = etree.Element("config", nsmap={None: IOSXE_NATIVE_NS})
native = etree.SubElement(config2, "native")
intf = etree.SubElement(native, "interface")
intf_type = etree.SubElement(intf, "GigabitEthernet")
intf_name = etree.SubElement(intf_type, "name")
intf_name.text = "3"
description = etree.SubElement(intf_type, "description")
description.text = "Configured by NETCONF - 3!"
ip_intf = etree.SubElement(intf_type, "ip")
ipv4_addresses = etree.SubElement(ip_intf, "address")
ipv4_primary = etree.SubElement(ipv4_addresses, "primary")
ipv4_address = etree.SubElement(ipv4_primary, "address")
ipv4_address.text = "172.21.99.1"
ipv4_mask = etree.SubElement(ipv4_primary, "mask")
ipv4_mask.text = "255.255.192.0"
intf_shutdown = etree.SubElement(intf_type, "shutdown")
intf_shutdown.set("operation", "delete")

config_res = netconf_call(connection_params, "edit_config", target="running", config=config2)
pprint(config_res)


# Run operational commands (save config, install software, reboot, etc.)
config_res = netconf_call(connection_params, "copy_config", source="running", target="startup")
pprint(config_res)


IOS_IA_NS = "http://cisco.com/yang/cisco-ia"
IOSXE_RPC_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-rpc"
save_config = etree.Element(f"{{{IOS_IA_NS}}}" + "save-config")
reload = etree.Element(f"{{{IOSXE_RPC_NS}}}" + "reload")

oper_res = netconf_call(connection_params, "dispatch", save_config)
pprint(oper_res)

oper_res = netconf_call(connection_params, "dispatch", reload)
pprint(oper_res)

# Parse device output
# We don't need to parse device output, because NETCONF with YANG return data that is already structured.

