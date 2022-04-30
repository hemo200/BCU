#!usr/bin/env python
import csv
from netmiko import ConnectHandler
dic_vlan = []
print ("CS-SW-C1 VLANs:")
with open ("./CS-SW-C1/VLAN.csv", mode='r') as vlan:
    reader = csv.reader(vlan)
    dic_vlan = {vlan[1]:vlan[0] for vlan in reader}

dic_device_credentials = {
    "device_type": "cisco_ios",
    "username" : "LocalAdmin",
    "password" : "Cisco123"
} 

device_instance = {
    "host" :"10.1.13.3",
    "username" : dic_device_credentials["username"],
    "password" : dic_device_credentials["password"],
    "device_type" : dic_device_credentials["device_type"]
}
device_connection = ConnectHandler(**device_instance)


for vlanNum, vlanName in dic_vlan.items():
    print("VLAN number is {0} and its name is {1}".format(vlanNum,vlanName))
    commands = [(" vlan " + vlanNum)]
    device_connection.send_config_set(commands)
device_connection.disconnect()


