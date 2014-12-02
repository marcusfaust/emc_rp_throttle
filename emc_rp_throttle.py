#!/usr/bin/python

__author__ = 'marcusfaust'

import requests
from requests.auth import HTTPBasicAuth
import sys, argparse
import socket

BASEURL =''
AUTH = HTTPBasicAuth('admin', 'admin')


def getThrottles(baseurl):
    bandwidths = {}
    r = requests.get(baseurl, verify=False, auth=AUTH)
    results = r.json()
    for group in results:
        bandwidths[group['name']] = group['activeLinksSettings'][0]['linkPolicy']['protectionPolicy']['bandwidthLimit']
    return bandwidths


def getAllGroupInfo(baseurl):
    r = requests.get(baseurl, verify=False, auth=AUTH)
    results = r.json()
    return results


def outputThrottles(bandwidths):
    total = 0.0
    print '\n\nCurrent CG Bandwidth Limits:\n'
    for name, throttle in bandwidths.items():
        print '{0:20} : {1:10f} Mbps'.format(name, throttle)
        total += throttle
    print '\n{0:20} : {1:10f} Mbps'.format('TOTAL:', total)


def isIP_v2(address):
    try:
        socket.inet_aton(address)
        ip = True
    except socket.error:
        ip = False
    return ip


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Script to display all Consistency Group Bandwidth Limits")
    required_group = parser.add_argument_group('Required Arguments')
    required_group.add_argument('-ip', '--ipaddress', help="Input the ip address of the RPA cluster here", required=True)
    args = parser.parse_args()
    if isIP_v2(args.ipaddress):
        BASEURL = 'https://' + args.ipaddress + '/fapi/rest/4_0/settings/groups/all'
        bandwidths = getThrottles(BASEURL)
        outputThrottles(bandwidths)
    else:
        sys.exit("Invalid IP Address detected for --ipaddress parameter.  Exiting.")

