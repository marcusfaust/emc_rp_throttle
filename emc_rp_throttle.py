#!/usr/bin/python

__author__ = 'marcusfaust'

import requests
from requests.auth import HTTPBasicAuth
import sys, argparse, json
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


def setThrottle(cg, throttle, baseurl):

    for uid, name in CG_NAME_MAP.items():
        if name == cg:
            url = baseurl + '/settings/groups/' + str(uid) + '/full'
            r = requests.get(url, verify=False, auth=AUTH)
            results = r.json()
            firstCopy = results['activeLinksSettings'][0]['groupLinkUID']['firstCopy']
            secondCopy = results['activeLinksSettings'][0]['groupLinkUID']['secondCopy']
            link_policy = results['activeLinksSettings'][0]['linkPolicy']
            link_policy['protectionPolicy']['bandwidthLimit'] = float(throttle)

            url = baseurl + '/settings/groups/' + str(uid) + '/actions/set_link_policy'
            params = [{'firstcopy': firstCopy}, {'secondCopy': secondCopy}, {'policy': link_policy}]
            params = json.dumps(params)
            headers = { 'Content-Type' : 'application/json' }
            r = requests.post(url, data=json.dumps(params), headers=headers,auth=AUTH, verify=False)
            print r.text

            results = r.json()
            print "done"


def outputWanStats(groupstats,groupsettings):
    global CG_NAME_MAP
    wanstats = {}
    total = 0.0
    for group in groupstats:
        wanstats[group['consistencyGroupUID']['id']] = {}
        wanstats[group['consistencyGroupUID']['id']]['name'] = CG_NAME_MAP[group['consistencyGroupUID']['id']]
        wanstats[group['consistencyGroupUID']['id']]['init_throughput'] = group['consistencyGroupLinkStatistics'][0]['initStatistics']['initOutgoingThroughput'] / 1000000
        wanstats[group['consistencyGroupUID']['id']]['init_percent'] = int(group['consistencyGroupLinkStatistics'][0]['initStatistics']['initCompletionPortion'] * 100)
    print '\n\nCurrent CG WAN Statistics:\n'
    for group in wanstats:
        print '{0:20} : {1:10.2f} Mbps : {2:6d} % Init'.format(wanstats[group]['name'], wanstats[group]['init_throughput'], wanstats[group]['init_percent'])
        total += wanstats[group]['init_throughput']

    print '\n{0:20} : {1:10.2f} Mbps'.format('TOTAL:', total)


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
    subparsers = parser.add_subparsers()
    set_throttle = subparsers.add_parser('set_throttle', help="Specify this with -cg and -throttle arguments to set a limit on a CG.")
    set_throttle.add_argument('-cg', '--cg', help="Input the name of the CG here", required=True, dest='cg')
    set_throttle.add_argument('-throttle', '--throttle', help="Input the Mbps throttle value here.", required=True, dest='throttle')
    get_throttles = subparsers.add_parser('get_throttles', help="Displays All CG Throttles")
    args = parser.parse_args()

    if isIP_v2(args.ipaddress):
        #BASEURL = 'https://' + args.ipaddress + '/fapi/rest/4_0/settings/groups/all'
        BASEURL = 'https://' + args.ipaddress + '/fapi/rest/4_0'
        groupstats = getAllGroupStats(BASEURL)
        groupsettings = getAllGroupSettings(BASEURL)
        CG_NAME_MAP = createGroupNameMap(groupsettings)
        bandwidths = getThrottles(groupsettings)
        #outputThrottles(bandwidths)
    else:
        sys.exit("Invalid IP Address detected for --ipaddress parameter.  Exiting.")

    if args.wanstats:
        outputWanStats(groupstats, groupsettings)

    if set_throttle:
        if args.cg in CG_NAME_MAP.values():
            setThrottle(args.cg, args.throttle, BASEURL)
        else:
            sys.exit("Invalid CG Name.  Exiting.")
    elif get_throttles:
        outputThrottles(bandwidths)
