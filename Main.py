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
    if (deviceName[3:5] == "SW"):
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
    try:
        ConnectionParameters["host"] = device[1]
        print("testing {}".format(ConnectionParameters["host"]))
        connection = ConnectHandler(**ConnectionParameters)
        if (connection.find_prompt() == (device[0]+"#")):
            return True
        else:
            print(Fore.RED+"The device is not configureable"+Fore.RESET)
            return False
        connection.disconnect()    
    except:
        print(Fore.RED+"The device {} is not reachable".format(device[1])+Fore.RESET)
        return False 
def DeviceType(deviceName):
    deviceAcron = deviceName[3:5]
    if (deviceAcron == "SW"):
        return "Switch"
    else:
        return "Router"
#This function will assign VLANS to the interface and will assign them as trunk or access
def ConfigureInterface(deviceInstance, connectionInstance):
    lis_trunked_interface = []
    lis_vlan_list = []
    connectionInstance["host"] = deviceInstance[1]
    lis_vlan_list = loadVlans(deviceInstance[0])
    try:
        with open (("./bcu/"+ deviceInstance[0] +"/trunk.csv"), mode="r") as interfaceName:
            reader = csv.reader(interfaceName)
            config_commands = []
            for item in reader:
                lis_trunked_interface.append(item[0])
        connection = ConnectHandler(**connectionInstance)
        for interface in lis_trunked_interface:
            config_commands.append("interface "+ interface)
            vlanList = "switchport trunk allowed vlan add "
            for vlanNum in lis_vlan_list:
                if vlanList == "switchport trunk allowed vlan add ":
                    vlanList = vlanList + vlanNum
                else:    
                    vlanList = vlanList+ "," + vlanNum
            config_commands.append(vlanList)

        connection.send_config_set(config_commands)
        print("VLANs are added to trunk ports in {0}".format(device[1]))
        connection.disconnect()
    except:
        print(Fore.RED + "Error loading trunk.csv file" + Fore.RESET)

def ConfigureNTP (deviceInstance,connectionInstance):
    connectionInstance["host"] = deviceInstance[1]
    
    print("NTP is configured")                        

def SetVlanInterface (deviceInstance,connectionInstance):
    connectionInstance["host"] = deviceInstance[1]
    connection = ConnectHandler(**connectionInstance)
    if (DeviceType(deviceInstance[0]) == "Router"):
        dict_vlans = []
        with open("./bcu/"+ deviceInstance[0][0:2] + ".csv") as vlanNum:
            reader = csv.reader(vlanNum)
            for item in reader:
               dict_vlans.append(item[1]) 
        print(deviceInstance[0][0:2])
        InterfaceCommnadList = []
        for vlnum in dict_vlans:
            if deviceInstance[0][0:2] == "CS":
                InterfaceCommnadList.append("interface Gi2." + vlnum)
                
            else:
                InterfaceCommnadList.append("interface Gi1." + vlnum)
            InterfaceCommnadList.append("encapsulation dot1Q " + vlnum)
            if deviceInstance[0][0:2] == "CS":
                InterfaceCommnadList.append("ip address 10.1."+ vlnum[1:3] + ".1 255.255.255.0")
            elif deviceInstance[0][0:2] == "CC":
                InterfaceCommnadList.append("ip address 10.2."+ vlnum[1:3] + ".1 255.255.255.0")
            else:
                InterfaceCommnadList.append("ip address 10.3."+ vlnum[1:3] + ".1 255.255.255.0")
        for item in InterfaceCommnadList:
            print(item)
        connection.send_config_set(InterfaceCommnadList)
        connection.disconnect()
        return True
    return False
        

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
    print(Fore.RED+
    "One of more devices are not reachable and configureable. Please check the above"+
    " error messages."+Fore.RESET)
#Configuring VLAN on all switches
print("Configuring vlans on switches:")
for device in dic_Devices_list.items(): 
    if (configureVLAN(dic_device_credentials,device) == True):#Confirmation from switch
        print("The Vlans are added to {}".format(device[0]))
    else:
        print(Fore.RED+"Vlans cannot be added to {0} or {0} is not a switch".format(device[0])
        + Fore.RESET)

for device in dic_Devices_list.items():
    ConfigureInterface(device,dic_device_credentials)    
for device in dic_Devices_list.items():
    if SetVlanInterface(device, dic_device_credentials):
        print("Subinterface is configured on {0}".format(device[0]))
    else:
        print("Error configuring {0} or {0} is not a router".format(device[0]))






