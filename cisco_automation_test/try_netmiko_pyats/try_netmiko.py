from os import getenv
from dotenv import load_dotenv
from pprint import pprint
from netmiko import ConnectHandler

load_dotenv()

l2_switch_params = {
   "device_type": "cisco_ios",
   "host": "10.255.255.6",
   "username": getenv("GNS3_USERNAME"),
   "password": getenv("GNS3_PASSWORD")
}

with ConnectHandler(**l2_switch_params) as l2_switch:
   show_version = l2_switch.send_command("show version")
   pprint(show_version)