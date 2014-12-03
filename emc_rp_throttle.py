#!/usr/bin/python

__author__ = 'marcusfaust'

import requests
from requests.auth import HTTPBasicAuth
import sys, argparse
import socket

BASEURL =''
AUTH = HTTPBasicAuth('admin', 'admin')
CG_NAME_MAP = {}


def getThrottles(groupsettings):
    bandwidths = {}
    #url = baseurl + '/settings/groups/all'
    #r = requests.get(url, verify=False, auth=AUTH)
    #results = r.json()
    results = groupsettings
    for group in results:
        bandwidths[group['name']] = group['activeLinksSettings'][0]['linkPolicy']['protectionPolicy']['bandwidthLimit']
    return bandwidths


def getAllGroupSettings(baseurl):
    url = baseurl + '/settings/groups/all'
    r = requests.get(url, verify=False, auth=AUTH)
    results = r.json()
    return results


def createGroupNameMap(groupsettings):
    cgmap = {}
    for group in groupsettings:
        cgmap[group['groupUID']['id']] = group['name']
    return cgmap


def getAllGroupStats(baseurl):
    url = baseurl + '/statistics/groups/all'
    r = requests.get(url, verify=False, auth=AUTH)
    results = r.json()
    return results


def outputThrottles(bandwidths):
    total = 0.0
    print '\n\nCurrent CG Bandwidth Limits:\n'
    for name, throttle in bandwidths.items():
        print '{0:20} : {1:10f} Mbps'.format(name, throttle)
        total += throttle
    print '\n{0:20} : {1:10f} Mbps'.format('TOTAL:', total)

def outputWanStats(groupstats,groupsettings):
    global CG_NAME_MAP
    wanstats = {}
    total = 0.0
    print CG_NAME_MAP
    for group in groupstats:
        wanstats[group['consistencyGroupUID']['id']]['name'] = CG_NAME_MAP[group['consistencyGroupUID']['id']]
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
    actions_group = parser.add_mutually_exclusive_group()
    actions_group.add_argument('-w', '--wanstats', help="Display WAN CG Statistics", action="store_true")
    required_group = parser.add_argument_group('Required Arguments')
    required_group.add_argument('-ip', '--ipaddress', help="Input the ip address of the RPA cluster here", required=True)
    args = parser.parse_args()
    if isIP_v2(args.ipaddress):
        #BASEURL = 'https://' + args.ipaddress + '/fapi/rest/4_0/settings/groups/all'
        BASEURL = 'https://' + args.ipaddress + '/fapi/rest/4_0'
        groupstats = getAllGroupStats(BASEURL)
        groupsettings = getAllGroupSettings(BASEURL)
        CG_NAME_MAP = createGroupNameMap(groupsettings)
        bandwidths = getThrottles(groupsettings)
        outputThrottles(bandwidths)
    else:
        sys.exit("Invalid IP Address detected for --ipaddress parameter.  Exiting.")

    if args.wanstats:
        outputWanStats(groupstats, groupsettings)
