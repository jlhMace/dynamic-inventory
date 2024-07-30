#!/usr/bin/env python3
# Using nmap -oX output to XML, create YAML inventory for Ansible

import yaml
import xml.etree.ElementTree as ET
import subprocess
import argparse
import netifaces as ni


VPN_interface = 'wg0'
# Get local VPN_interface IP, to seperate from nodes
local_IP = ni.ifaddresses(VPN_interface)[ni.AF_INET][0]['addr']


def nmaprun(subnet,outputfile):
    # Runs nmap on specified vpn subnet
    command = f"sudo nmap -sP {subnet} -oX {outputfile} &>/dev/null"
    subprocess.run(command, shell=True)

def parseXML(xmlfile):
    # Parses XML file for host list
    peerlist = []
    with open(xmlfile, 'r') as file:
        # Create element tree object and get root element
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        # XML parsing to get hostname and associated IP addr
        for host in root.iter('host'):
            connection = {}
            for name in host.findall('hostnames/hostname'):
                hostname = name.get('name')
                connection['hostname'] = hostname
            for address in host.findall('address'):
                IP = address.get('addr')
                if IP == local_IP:
                    continue
                else:
                    connection['address'] = IP
            if connection:
                peerlist.append(connection)
    return peerlist


def generate_ansible_inventory():
    # Creates ansible inventory from list of dicts, and
    # convert to Ansible-friendly yaml format
    peers = get_peers()

    if peers:
        inventory = {}
        for peer in peers:
            a = 1

def main():

    subnet = '10.10.10.0/24'
    nmapresult = '/etc/ansible/dynamic-inventory/nmap-test.xml'

    # nmap over specified subnet, comment out to make static
    print(f"Running nmap over {subnet}...")
    #nmaprun(subnet,nmapresult)
    print("Nmap scan complete.")
    print(f"XML output saved to {nmapresult}")

    # Create dict of peers
    peerlist = parseXML(nmapresult)


    #inventory = yaml.safe_load(a)

    print(peerlist)


main()
