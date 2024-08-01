#!/usr/bin/env python3
# Using nmap -oX output to XML, create YAML inventory for Ansible

import yaml
import xml.etree.ElementTree as ET
import subprocess
import argparse
import netifaces as ni
import os.path


def nmaprun(subnet,outputfile):
    # Runs nmap on specified vpn subnet
    print(f"Running nmap over {subnet}...")
    command = f"sudo nmap -sP {subnet} -oX {outputfile} &>/dev/null"
    subprocess.run(command, shell=True)
    print("Nmap scan complete.")
    print(f"XML output saved to {outputfile}")

def parseXML(xmlfile):
    # Parses XML file for host list
    peerlist = {}
    with open(xmlfile, 'r') as file:
        # Create element tree object and get root element
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        # XML parsing to get hostname and associated IP addr
        for host in root.iter('host'):
            for name in host.iter('hostname'):
                hostname = name.get('name')
                for address in host.iter('address'):
                    IP = address.get('addr')
                    peerlist[hostname]= IP
    return peerlist

def is_valid_file(parser,arg):
    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist.")

def generate_inventory(peerlist, inventory):
    # Creates ansible inventory from list of dicts in .ini format
    template="""[rpi:vars]\nansible_connection=ssh\nansible_ssh_user=admin\n\n[rpi]\n"""
    for key in peerlist.keys():
        pdu = "pdu" + key[-2:]
        template += key + " pdu=" + pdu + "\n"
    with open(inventory, 'w') as file:
        file.write(template)
        print(f"Peers written to Ansible inventory at {inventory}")

def generate_host_file(peerlist, hostfile):
    # Create /etc/hosts file with updated peerlist
    template = """127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4 \n::1         localhost localhost.localdomain localhost6 localhost6.localdomain6 \n\n# RPi Units\n"""
    for key, value in peerlist.items():
        template += key + "\t\t" + value + "\n"
    # Write to /etc/hosts
    with open(hostfile, 'w') as file:
        file.write(template.expandtabs(4))
        print(f"Peers written to hostfile at {hostfile}")

def main():

    VPN_interface = args.interface
    subnet = args.subnet
    nmapresult = args.output
    hostfile = '/etc/hosts'
    inventory = args.inventory

    # nmap over specified subnet, if not specified
    if args.no_scan is True:
        nmaprun(subnet,nmapresult)

    # Create dict of peers
    peerlist = parseXML(nmapresult)

    # Create Ansible inventory
    generate_inventory(peerlist, inventory)

    # Regenerate /etc/hosts, if specified
    if args.update_hostfile is True:
        generate_host_file(peerlist,hostfile)


if __name__ == '__main__':
    # Global variables
    VPN_interface = 'wg0'
    local_IP = ni.ifaddresses(VPN_interface)[ni.AF_INET][0]['addr']
    
    # Program argument parser
    parser = argparse.ArgumentParser(description='Scans subnet and updates host files')
    parser.add_argument('-i', '--inventory', default='/etc/ansible/hosts', help='specify Ansible inventory file to update (default /etc/ansible/hosts.dynamic)')
    parser.add_argument('-n', '--subnet', default='10.10.10.0/24', help='specify nmap subnet (default 10.10.10.0/24)')
    parser.add_argument('-o', '--output', default='/etc/ansible/dynamic-inventory/nmap-output.xml', help='specify output file for nmap scan')
    parser.add_argument('--interface', default='wg0', help='specify VPN interface (default wg0)')
    parser.add_argument('--update-hostfile', action='store_true', help='update /etc/hosts with the scan results')
    parser.add_argument('--no-scan', action='store_false', help='run without nmap scan, using previous nmap XML result')
    args = parser.parse_args()
    main()
