#!/usr/bin/python

__author__ = 'marcusfaust'

import requests
from requests.auth import HTTPBasicAuth
import sys, argparse

BASEURL =''
AUTH = HTTPBasicAuth('admin', 'admin')


def getThrottles(baseurl):
    bandwidths = {}
    r = requests.get(baseurl, verify=False, auth=AUTH)
    results = r.json()

    for group in results:
        bandwidths[group['name']] = group['activeLinksSettings'][0]['linkPolicy']['protectionPolicy']['bandwidthLimit']

    return bandwidths


def outputThrottles(bandwidths):
    total = 0.0
    print '\n\nCurrent CG Bandwidth Limits:\n'
    for name, throttle in bandwidths.items():
        print '{0:20} : {1:10f} Mbps'.format(name, throttle)
        total += throttle
    print '\n{0:20} : {1:10f} Mbps'.format('TOTAL:', total)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--ipaddress', help="Input the ip address of the RPA cluster here")
    args = parser.parse_args()

    BASEURL = 'https://' + args.ipaddress + '/fapi/rest/4_0/settings/groups/all'

    bandwidths = getThrottles(BASEURL)
    outputThrottles(bandwidths)
