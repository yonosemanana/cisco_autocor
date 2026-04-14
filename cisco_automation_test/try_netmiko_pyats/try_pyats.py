from os import getenv
from dotenv import load_dotenv
from pprint import pprint
from pyats.topology import loader
from pathlib import Path

load_dotenv()

testbed_path = Path(__file__).parent / "try_testbed.yaml"
testbed = loader.load(testbed_path)
l2_switch = testbed.devices["SW1"]


l2_switch.credentials["default"] = {
   "username": getenv("GNS3_USERNAME"),
   "password": getenv("GNS3_PASSWORD")
}


l2_switch.connect()
show_version = l2_switch.parse("show version")
pprint(show_version)
l2_switch.disconnect()
