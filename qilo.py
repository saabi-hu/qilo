#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
qilo.py - collects system information from HPE ProLiant servers
"""

import csv
import logging
import argparse
import redfish
import pprint
from redfish.rest.v1 import ServerDownOrUnreachableError


inputfile = 'serverlist.csv'
outputfile = 'serverdata.csv'
logfile = 'qilo.log'
loglevel = 'DEBUG'
pp = pprint.PrettyPrinter(indent=2)
DISABLE_RESOURCE_DIR = False
firmware_report = {}


def read_arguments():
    parser = argparse.ArgumentParser(
        description=None,
        add_help=True,
        allow_abbrev=True,
        exit_on_error=True
    )
    parser.add_argument(
        '-l', '--loglevel',
        choices=[
            'DEBUG',
            'INFO',
            'WARNING',
            'ERROR',
            'CRITICAL'
        ],
        default='INFO'
    )
    parser.add_argument('-v', '--verbose', action='store_true')
    return parser.parse_args()


def configure_logging(filename, loglevel):
    nloglevel = getattr(logging, loglevel.upper(), None)
    if not isinstance(nloglevel, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(
        filename=filename,
        filemode='w',
        encoding='utf_8',
        level=nloglevel
    )
    logging.info('Loglevel %s' % loglevel)


def get_ILOIPv4Addresses(redfish_obj):
    """ Collect iLO IPv4 addresses """

    iloipv4addresses = []
    members = redfish_obj.get('/redfish/v1/Managers/1/EthernetInterfaces').dict['Members']
    
    for iface in members:
        ilonet = redfish_obj.get(iface['@odata.id'])
        if ilonet.dict['InterfaceEnabled']:
            for j in ilonet.dict['IPv4Addresses']:
                iloipv4addresses.append(j['Address'])

    return(iloipv4addresses)


def get_ILOIPv6Addresses(redfish_obj):
    """ Collect iLO IPv6 addresses """

    iloipv6addresses = []
    members = redfish_obj.get('/redfish/v1/Managers/1/EthernetInterfaces').dict['Members']
    
    for iface in members:
        ilonet = redfish_obj.get(iface['@odata.id'])
        if ilonet.dict['InterfaceEnabled']:
            for j in ilonet.dict['IPv6Addresses']:
                iloipv6addresses.append(j['Address'])

    return(iloipv6addresses)


def get_iLOName(redfish_obj):
    """ Collect iLO's hostname """

    ilohostname = redfish_obj.get('/redfish/v1/Managers/1').dict['Name']
    return(ilohostname)


def get_ProductName(redfish_obj):
    return()


def get_ServerHostName(redfish_obj):
    return()


def get_SerialNumber(redfish_obj):
    return()


def get_iLOFirmware(redfish_obj):
    return()


def get_SystemRom(redfish_obj):
    return()


def get_SystemRomBackup(redfish_obj):
    return()


def get_IntelligentProvisioning(redfish_obj):
    return()


def get_IntelligentPlatformAbstractionData(redfish_obj):
    return()


def get_PowerManagementControllerFirmware(redfish_obj):
    return()


def get_PowerManagementControllerBootloader(redfish_obj):
    return()


def get_SystemProgrammableLogicDevice(redfish_obj):
    return()


def get_ServerPlatformServicesFirmware(redfish_obj):
    return()


def get_PCIDevices_Name(redfish_obj):
    return()


def get_PCIDevices_Version(redfish_obj):
    return()


def get_PCIDevices_Location(redfish_obj):
    return()


def get_NetworkDevices_Name(redfish_obj):
    return()


def get_NetworkDevices_Version(redfish_obj):
    return()


def get_ArrayControllers_Name(redfish_obj):
    return()


def get_ArrayControllers_Version(redfish_obj):
    return()


def get_StorageDevicesName(redfish_obj):
    return()


def get_StorageDevicesVersion(redfish_obj):
    return()


def get_PhysicalDrivesName(redfish_obj):
    return()


def get_PhysicalDrivesVersion(redfish_obj):
    return()
    

def read_server_list(csvfile):
    # Read the list of the servers to check
    serverlist = []
    with open(csvfile) as f:
        # TODO: #1 check the existence of the input file
        reader = csv.reader(f)
        for row in reader:
            serverlist.append(tuple(row))
            logging.debug('Added to server list: %s' % row[0])
    return(serverlist)


def get_resource_directory(redfishobj):
    # copied from
    # https://github.com/HewlettPackard/python-ilorest-library/blob/master/examples/Redfish/get_resource_directory.py

    try:
        resource_uri = redfishobj.root.obj.Oem.Hpe.Links.ResourceDirectory['@odata.id']
    except KeyError:
        logging.warning("Resource directory is only available on HPE servers.")
        return None

    response = redfishobj.get(resource_uri)
    resources = []

    if response.status == 200:
        logging.info("Found resource directory at /redfish/v1/resourcedirectory")
        resources = response.dict["Instances"]
    else:
        logging.warning("Resource directory missing at /redfish/v1/resourcedirectory")

    return resources


def get_gen(_redfishobj):
    # copied from
    # https://github.com/HewlettPackard/python-ilorest-library/blob/master/examples/Redfish/get_resource_directory.py
    rootresp = _redfishobj.root.obj
    # Default iLO 5
    ilogen = 5
    gencompany = next(iter(rootresp.get("Oem", {}).keys()), None) in (
        'Hpe',
        'Hp'
    )
    comp = 'Hp' if gencompany else None
    comp = 'Hpe' if rootresp.get("Oem", {}).get('Hpe', None) else comp
    if comp and next(iter(
            rootresp.get("Oem", {}).get(comp, {}).get("Manager", {})
    )).get('ManagerType', None):
        ilogen = next(iter(
            rootresp.get("Oem", {}).get(comp, {}).get("Manager", {})
        )).get("ManagerType")
        ilover = next(iter(
            rootresp.get("Oem", {}).get(comp, {}).get("Manager", {})
        )).get("ManagerFirmwareVersion")
        if ilogen.split(' ')[-1] == "CM":
            # Assume iLO 4 types in Moonshot
            ilogen = 4
            iloversion = None
        else:
            ilogen = ilogen.split(' ')[1]
            iloversion = float(
                ilogen.split(' ')[-1] + '.' + ''.join(ilover.split('.'))
            )
    return (ilogen, iloversion)


def computer_details(_redfishobj):
    # copied from
    # https://github.com/HewlettPackard/python-ilorest-library/blob/master/examples/Redfish/computer_details.py
    systems_members_uri = None
    systems_members_response = None

    resource_instances = get_resource_directory(_redfishobj)
    if DISABLE_RESOURCE_DIR or not resource_instances:
        # if we do not have a resource directory or want to force it's non use
        # to find the relevant URI
        systems_uri = _redfishobj.root.obj['Systems']['@odata.id']
        systems_response = _redfishobj.get(systems_uri)
        systems_members_uri = next(iter(
            systems_response.obj['Members']
        ))['@odata.id']
        systems_members_response = _redfishobj.get(systems_members_uri)
    else:
        for instance in resource_instances:
            # Use Resource directory to find the relevant URI
            if '#ComputerSystem.' in instance['@odata.type']:
                systems_members_uri = instance['@odata.id']
                systems_members_response = _redfishobj.get(systems_members_uri)

    return systems_members_response


def main():
    args = read_arguments()
    loglevel = args.loglevel
    verbosity = args.verbose
    configure_logging(filename=logfile, loglevel=loglevel)

    servers = read_server_list(inputfile)
    for host in servers:
        ilo_host, ilo_user, ilo_pass = host
        base_url = 'https://%s' % ilo_host

        try:
            REST_OBJ = redfish.RedfishClient(
                base_url=base_url,
                username=ilo_user,
                password=ilo_pass
            )
            REST_OBJ.login(auth='session')
        except ServerDownOrUnreachableError:
            errmsg = "ERROR: server (%s) not reachable or does not support RedFish." % ilo_host
            logging.warning(errmsg)
            if verbosity:
                print(errmsg)
            return()

        # hostinfo = ProLiant_server(REST_OBJ)
        firmware_report['ILOIPv4Address'] = get_ILOIPv4Addresses(REST_OBJ)
        firmware_report['ILOIPv6Address'] = get_ILOIPv6Addresses(REST_OBJ)
        firmware_report['iLOName'] = get_iLOName(REST_OBJ)
        if verbosity:
            pp.pprint(firmware_report)

        REST_OBJ.logout()

    return()


if __name__ == '__main__':
    main()
