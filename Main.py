#!/usr/bin/python3
from netmiko import ConnectHandler
import csv
import colorama
from colorama import Fore


def loadDevices(deviceCSV):
    with open (("./bcu/" + deviceCSV), mode="r") as device:
        reader = csv.reader(device)
        dic_device = {device[0]:device[1] for device in reader}
    return dic_device
def loadVlans(deviceName):
    if ( deviceName[3:5] == "SW"):
        with open ("./bcu/"+deviceName +"/VLAN.csv", mode="r") as vlan:
            reader = csv.reader(vlan)
            dic_vlan = {vlan[1]:vlan[0] for vlan in reader}
        return dic_vlan
    else:
        print("{} is not a switch".format(deviceName))
def configureVLAN(Connection,deviceInstance):
    dicVlanList = []
    if (DeviceType(deviceInstance[0]) == "Switch"):
        Connection["host"] = deviceInstance[1]
        device_connection = ConnectHandler(**Connection)
        dicVlanList = loadVlans(deviceInstance[0])
        for vlanNum, vlanName in dicVlanList.items():  
            commands = [("vlan " + vlanNum),("name " + vlanName)]
            device_connection.send_config_set(commands)
        device_connection.disconnect()
        return True
    else:
        return False
def ConnectionTester(device,ConnectionParameters):
    ConnectionParameters["host"] = device[1]
    print("testing {}".format(ConnectionParameters["host"]))
    connection = ConnectHandler(**ConnectionParameters)
    if (connection.find_prompt() == (device[0]+"#")):
        return True
    else:
        print(Fore.RED+"The device is not configureable"+Fore.RESET)
        return False
    connection.disconnect()    
def DeviceType(deviceName):
    deviceAcron = deviceName[3:5]
    if (deviceAcron == "SW"):
        return "Switch"
    else:
        return "Router"
#This function will assign VLANS to the interface and will assign them as trunk or access
def ConfigureInterface(deviceInstance):
    lis_trunked_interface = []
    with open (("./bcu/"+ deviceInstance[0] +"/trunk.csv"), mode="r") as interfaceName:
        reader = csv.reader(interfaceName)
        for item in reader:
            lis_trunked_interface.append(item[0])
    for item in lis_trunked_interface:
        print(item)

dic_Devices_list= {}
testResultFlag = True
mainMenuOption = 0    
dic_Devices_list = loadDevices('list_of_device.csv')    

dic_device_credentials = {
    "device_type": "cisco_ios",
    "username" : "LocalAdmin",
    "password" : "Cisco123"
}
#Script welcome page
print ("Welcome to BCU network configurator\n\n")

#loading the device from a file to a dictionary
print("Loading devices")
dic_Devices_list = loadDevices("list_of_device.csv")

#testing connectivity and ability across all devices.
print("Looping through All Devices")
for device in dic_Devices_list.items():  
    dic_device_credentials["host"] = device[1]
    if (testResultFlag == True):
        testResultFlag = ConnectionTester(device, dic_device_credentials)
    else:
        ConnectionTester(device, dic_device_credentials)
#Display a confirmation message of testing all devices.
if (testResultFlag == True):
    print(Fore.GREEN+"All devices are reachable and configureable"+Fore.RESET)
else:
    print(Fore.RED+"One of more devices are not reachable and configureable. Please check the above"+
    " error messages."+Fore.RESET)
#Configuring VLAN on all switches
print("Configuring vlans on switches:")
for device in dic_Devices_list.items(): 
    if (configureVLAN(dic_device_credentials,device) == True):#Confirmation from switch
        print("The Vlans are added to {}".format(device[0]))
    else:
        print(Fore.RED+"Vlans cannot be added to {0} or {0} is not a switch".format(device[0])+ Fore.RESET)

for device in dic_Devices_list.items():
    ConfigureInterface(device)    






