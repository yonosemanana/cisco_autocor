from genie.testbed import load
from pathlib import Path
from pprint import pprint
from dotenv import load_dotenv
import os

from genie.libs.conf.vlan import Vlan

INVENTORY_FILE = "inventory.yaml"

if __name__ == "__main__":
    load_dotenv()

    inv_path = Path(__file__).parent / INVENTORY_FILE

    tb = load(inv_path)
    nexus = tb.devices["NXOS1"]

    nexus.credentials.default["username"] = os.getenv("GNS3_USERNAME")
    nexus.credentials.default["password"] = os.getenv("GNS3_PASSWORD")

    nexus.connect()
    # # output = nexus.parse("show    ver")
    # # pprint(output)
    # #
    # # # pprint(dir(nexus.api))
    # # # interfaces = nexus.api.get_interfaces_status()
    # # # pprint(interfaces)
    #
    # # output2 = nexus.api.get_hardware_version()
    # # pprint(output2)

    # all_data = nexus.learn('all')
    # pprint(all_data)

    # vlans = nexus.learn("vlan")
    # pprint(vlans.info)
    #
    # vlan_id = 200
    # vlan_name = "New_Test_VLAN"
    # vlan_config = [
    #     f"vlan {vlan_id}",
    #     f"name {vlan_name}"
    # ]
    # nexus.configure(vlan_config)
    #
    # vlans = nexus.learn("vlan")
    # pprint(vlans.info)

    new_vlan = Vlan()
    new_vlan.vlan_id = 201
    new_vlan.device_attr[nexus].name = "New_VLAN"
    new_vlan_config = new_vlan.build_config(devices=[nexus], apply=False)
    pprint(str(new_vlan_config[nexus.name]))

    new_vlan.build_config(devices=[nexus])
    vlans = nexus.learn("vlan")
    pprint(vlans.info)
    new_vlan.build_unconfig(devices=[nexus])

    nexus.execute("copy running-config startup-config")

    nexus.disconnect()

    l2_switch = tb.devices["SW1"]
    l2_switch.credentials.default["username"] = os.getenv("GNS3_USERNAME")
    l2_switch.credentials.default["password"] = os.getenv("GNS3_PASSWORD")

    l2_switch.connect()

    # output = l2_switch.parse("show ver")
    # pprint(output)

    # pprint(dir(l2_switch.api))
    # output2 = l2_switch.api.get_interfaces_status()
    # pprint(output2)

    # all_data = l2_switch.learn('all')
    # pprint(all_data)

    # vlans = l2_switch.learn("vlan")
    # pprint(vlans.info)
    #
    # l2_switch.configure(
    #     """vlan 300
    #     name Test VLAN 3"""
    # )
    #
    # vlans = l2_switch.learn("vlan")
    # pprint(vlans.info)

    test_vlan = Vlan()
    test_vlan.device_attr[l2_switch].name = "Another VLAN"
    test_vlan.device_attr[l2_switch].vlan_id = 201
    test_vlan.build_config(apply=True, devices=[l2_switch])

    test_vlan.build_unconfig(devices=[l2_switch])

    l2_switch.execute("write memory")

    l2_switch.disconnect()