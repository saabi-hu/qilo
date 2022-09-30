#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ilo_user_management.py - adds local user to iLO using REST API
"""

import csv
import logging
import argparse
import redfish
import pprint
from redfish.rest.v1 import ServerDownOrUnreachableError

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
    parser.add_argument('-a', '--add', action='add_user')
    parser.add_argument('-d', '--del', action='del_user')
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


def read_user_list(inputfile):
    users = []
    return(users)

def main():
    inputfile = 'userlist.csv'
    logfile = 'ilo_user_management.log'
    loglevel = 'DEBUG'
    pp = pprint.PrettyPrinter(indent=2)
    args = read_arguments()
    loglevel = args.loglevel
    verbosity = args.verbose
    configure_logging(filename=logfile, loglevel=loglevel)

    users = read_user_list(inputfile)
    for user in users:
        username, userpw, ilousr, ilopw, iloip = user
        base_url = 'https://%s' % iloip

        try:
            REST_OBJ = redfish.RedfishClient(
                base_url = base_url,
                username = ilousr,
                password = ilopw
            )
            REST_OBJ.login(auth='session')
        except ServerDownOrUnreachableError:
            errmsg = "Error: server (%s) not reachable or does not support RedFish" % iloip
            logging.warning(errmsg)
            if verbosity:
                print(errmsg)
            return()

        REST_OBJ.logout()
    return()

if __name__ == '__main__':
    main()
