###############################################################################
#
#  Project: orion_tool.py
#
###############################################################################
#
#                Artesyn Embedded Technologies
#                Embedded Computing
#                Hyderabad, India
#
#        [ ] Open Source   [ ] Contains Open Source Material  [.] Proprietary
#
#  Remarks: Note! This material is proprietary of
#  EMERSON NETWORK POWER - EMBEDDED COMPUTING and may only
#  be viewed under the terms of a signed non-disclosure agreement or a
#  source code license agreement! Copying, compilation, modification,
#  distribution or any other use whatsoever of this material is strictly prohibited
#  without written permission of EMERSON NETWORK POWER - EMBEDDED COMPUTING.
#  The information in this document is subject to change without notice and should
#  not be construed as a commitment by EMERSON NETWORK POWER - EMBEDDED COMPUTING.
#  Neither EMERSON NETWORK POWER - EMBEDDED COMPUTING nor the authors assume any
#  responsibility for the use or reliability of this document or the described
#  software.
#
#  Copyright (c) 2014, EMERSON NETWORK POWER - EMBEDDED COMPUTING Inc.
#  All rights reserved.
#
###############################################################################
#
# modification history:
# *********************
# 1.1,6jan2015,fpvn87    Initial version.
#
# DESCRIPTION:
# Orion_tool.py uses Orion API which provides a complete programming interface to 
# integrate the functionality of Orion in IP/ASI based monitoring workflows. Based 
# on the REST architecture, the Orion API offers flexibility to plug language 
# independent applications that supports HTTP protocolAutomates Real-time Content 
# Monitoring at any point in the workflow
# 
# 1. Enables platform independent and environment independent applications, to 
#    access the Orion system
# 2. Automates Real-time Content Monitoring at any point in the workflow
# 3. Provides complete access to all Orion functions
# 4. Is easy to use and understand
#
"""
orion_tool.py : the usage of Orion Manager Python Client library

@author: fpvn87
"""

# python imports
import xml.etree.cElementTree as ET

# our imports
from orion.mgr.mgr import OrionManager
import time
import os
import sys
import re
import json
import getopt
import datetime
import socket

############################# GLOBALS #########################################
orion_mgr_port = 1729
orion_mgr_ip = 'none'
str_dest_ip = 'none'
str_src_ip = 'none'
str_port = 'none' 
mon_inter = 5
list_profile = 0
def_profile_id = 'none' 
mon_profile_name = 'none'
flag = 0
###############################################################################

def main(argv):
    ret = parse_args(argv)
    if ret != 0:
        print 'Could not handle user input'
        usage()
        return

    if 'none' in orion_mgr_ip:
        print 'Orion Manager IP address is missing' + '\n'
        usage()
        sys.exit()
    
    flag = 0
        
    'get request wrapper object as orionHandle to access methods of request wrapper'
    orionHandle = getOrionHandle();

    'set default profile id'    
    if 'none' is not def_profile_id:
        fid = '{id: ' + def_profile_id +'}'
        orionHandle.setDefaultProfile(fid)
        flag = 1

    'get the list of profiles and default profile'
    if list_profile:
        i = 1
        defaultProfile = orionHandle.getDefaultProfile()
        dpName = re.search(r'"name":"(\w+)"', defaultProfile)
        listAllProfiles = orionHandle.getListofProfiles()
        record1 = listAllProfiles.split("id")
        print '\n' + 'Total Profiles %d' %(len(record1) - 1)
        print '\n' + 'ID' '\t'  'Type' '\t' 'Profile Name' '\t' 'Default' 
        print '--' + '\t' + '----' + '\t' + '------------' + '\t' + '-------'
        while i < len(record1):
            m = re.search(r'":(\d+),"name":"(\w+)","type":"(\w+)', record1[i])
            if m.group(2) == dpName.group(1):
                print m.group(1) + '\t' + m.group(3) + '\t' + m.group(2) + '\t' + 'o'
            else:
                print m.group(1) + '\t' + m.group(3) + '\t' + m.group(2) + '\t' + '-'
            i += 1
        flag = 1 

    if flag:
        sys.exit()

    'delete all registered feeds'
    orionHandle.deleteSpecificFeed('[{feedInfo: {id: -1}}]')

    'send scan request for a feed being streamed from/to a specific IP and port'
    if 'none' in str_dest_ip:
        if 'none' is not str_port:
            print 'Stream destination ip address is missing. Exiting...!' + '\n'
            sys.exit()
        elif 'none' is not str_src_ip:
            print 'Stream destination ip address and port number are missing. Exiting...!' + '\n'
            sys.exit()
        
    if 'none' is not str_dest_ip:
        if 'none' in str_port:
            print 'Port number is missing or incorrect. Exiting...!' + '\n'
            sys.exit()
        if 'none' is not str_src_ip:
            feed = '[{feedInfo: {ip: ' + str_dest_ip + ', port: ' + str_port + ', sourceIp: ' + str_src_ip +'}}]'
            scanFeedResponse = orionHandle.scanSpecificFeed(feed)
        else:
            feed = '[{feedInfo: {ip: ' + str_dest_ip + ', port: ' + str_port + '}}]'
            scanFeedResponse = orionHandle.scanSpecificFeed(feed)
    else:
        'send scan request for all feeds being streamed'
        scanFeedResponse = orionHandle.scanFeed(); 

    'retrieve the request id of scan request'
    scanReqId = getScanRequestId(scanFeedResponse)
    'sleep(wait) for 10 seconds to let the scan request complete, we can loop here as well till we get the scan status as COMPLETED.'
    time.sleep(10)
    scanStatusResponse = orionHandle.isScanSuccessfullyCompleted(scanReqId)
    scanSatus = getScanStatus(scanStatusResponse)
    print scanSatus

    'if scan request is COMPLETED successfully'
    if scanSatus.upper() == "COMPLETED":
        print "Scan Completed" + '\n'

        'get feedId(s) by calling /rest/setup/feeds rest API' 
        if 'none' is not str_dest_ip:
            listOfFeeds = orionHandle.getListOfFeedsWithIpPort(str_dest_ip, int(str_port)) 
            #listOfFeeds = orionHandle.getListOfFeedsWithSourceIpPort(str_dest_ip, int(str_port), str_src_ip) 
            #print listOfFeeds
        else:
            listOfFeeds = orionHandle.getListOfAllScannedFeeds()
        
        'parsing the JASON response'
        feedIds = getScannedFeedId(listOfFeeds)
        #print '------------------FeedID------------------'
        #print feedIds
        #print '------------------------------------------'
 
        if len(feedIds) == 0:
            print 'No FeedId found to start monitoring. Exiting....!' + '\n'
	    sys.exit()

        'get currentTime before starting feed monitoring of scanned feed, it will be used for report generation as start time'
        fromTime =  int(round(time.time()*1000))
        for feedId in feedIds:
            'send feed monitoring request and let it be monitored for 5 minutes.'
            if 'none' is not mon_profile_name:
                startMonResponse = orionHandle.startMultipleFeedMonitoring('[{monitoringRequest: {feedId: %d, profileName: %s}}]' % (feedId, mon_profile_name))
            else:
                startMonResponse = orionHandle.startMultipleFeedMonitoring('[{monitoringRequest: {feedId: %d}}]' % (feedId))
            
            'check for om feed monitor response' 
            if startMonResponse.find("Success") == -1:
                print 'Unable to start monitoring. Either Feed is not registered or incorrect profile name given. Exiting...!' + '\n'
                sys.exit(2)
            else:
                print 'monitoring of feed # ' + str(feedId) + ' has been started....' + '\n'

	'sleep for 5 min.'
        print 'Be right back in %d minute(s)..!'%mon_inter
        time.sleep(mon_inter*60)
        
        'After 5 minutes, stop feed monitoring'
        for feedId in feedIds:
	    stopMonResponse = orionHandle.stopMultipleFeedMonitoring('[{monitoringRequest: {feedId: %d}}]' % (feedId))
            print 'monitoring of feed - ' + str(feedId) + ' has been stopped....' + '\n'

        'get currentTime after stopping feed monitoring, this will be used for report generation as end time'
        toTime =  int(round(time.time()*1000))
        current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filename="Report_"+current_time+".pdf"

        'create PDF report for alerts being reported between fromTime and toTime'
        if 'none' is not str_dest_ip:
            log = orionHandle.logCSVFeedWise(fromTime, toTime, feedId)
            x = log_report(log)
            if x:
                orionHandle.exportPDFFeedWise(fromTime, toTime, feedId, filename)
                print 'PDF exported successfully....' + '\n'
        else:    
            log = orionHandle.logCSV(fromTime, toTime)
            x = log_report(log)
            if x:
                orionHandle.exportPDF(fromTime, toTime, filename)
                print 'PDF exported successfully....' + '\n'
    else :
        print "Scan Pending..." + '\n'


def usage():
    print 'orion_tool.py [-h] -s <orion manager ip> [-d <stream destination ip>] [-i <stream source ip>] [-p <stream port>] [-m <profile name>] [-t <interval>] [-l] [-f <profile id>]'
    print '-h, --help'
    print '\t' + 'This help' + '\n'
    print '-s, --omip'
    print '\t' + 'Orion Manager IP Address' + '\n'
    print '-d, --sdip'
    print '\t' + 'Stream Destination IP Address' + '\n'
    print '-i, --ssip'
    print '\t' + 'Stream Source IP Address' + '\n'
    print '-p, --sport'
    print '\t' + 'Stream Port Number' + '\n'
    print '-m, --mprof'
    print '\t' + 'Name of the Profile used for Monitoring' + '\n'
    print '-t, --inter'
    print '\t' + 'Duration to Monitor Streams (default: 5 min)' + '\n' 
    print '-l, --lprof'
    print '\t' + 'List all Profiles includes default Profile' + '\n'
    print '-f, --sprof'
    print '\t' + 'Set Profile as default Profile' + '\n'

    return

def parse_args(argv):
    global orion_mgr_ip
    global str_dest_ip
    global str_src_ip
    global str_port
    global mon_inter
    global list_profile
    global def_profile_id 
    global mon_profile_name
    try:
        opts, args = getopt.getopt(argv,"hs:d:p:i:m:t:f:l",["help", "omip=", "sdip=", "sport=", "ssip=", "mprof=", "inter=", "sprof=", "lprof"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-s", "--omip"):
            orion_mgr_ip = arg
            if not is_valid_ip(orion_mgr_ip):
                print 'IPv4 address for OM is invalid. Exiting...!' + '\n'
                sys.exit()
            print 'Orion Manager IP Address     : ', orion_mgr_ip
        elif opt in ("-d", "--sdip"):
            str_dest_ip = arg
            if not is_valid_ip(str_dest_ip):
                print 'IPv4 address for stream destination is invalid. Exiting...!' + '\n'
                sys.exit()
            print 'Stream Destination IP Address: ', str_dest_ip 
        elif opt in ("-p", "--sport"):
            str_port = arg
            print 'Stream Port Number           : ', str_port
        elif opt in ("-i", "--ssip"):
            str_src_ip = arg
            if not is_valid_ip(str_src_ip):
                print 'IPv4 address for stream source is invalid. Exiting...!' + '\n'
                sys.exit()
            print 'Stream Source IP Address     : ', str_src_ip 
        elif opt in ("-m", "--mprof"):
            mon_profile_name = arg
            print 'Profile Name for Monitoring  : ', mon_profile_name 
        elif opt in ("-t", "--inter"):
            mon_inter = int(arg)
            print 'Stream Monitoring Duration   :  %d min.' % mon_inter 
        elif opt in ("-l", "--lprof"):
            list_profile = 1
        elif opt in ("-f", "--sprof"):
            def_profile_id = arg
    return 0

def getOrionHandle():
    #global orion_mgr_ip
    mgr = OrionManager(orion_mgr_ip, orion_mgr_port)
    requestWrapper = mgr.getRequestWrapper()
    return requestWrapper;    

def getScanRequestId(res):
    jsonRes = json.loads(res)
    orionResponse = jsonRes['OrionResponse']
    data = orionResponse['data']
    request = data['request']
    reqId = request['id']
    return reqId

def getScanStatus(jsonRes):
    orionResponse = jsonRes['OrionResponse']
    data = orionResponse['data']
    request = data['request']
    status = request['status']
    return status

def getScannedFeedId(jsonRes):
    orionResponse = jsonRes['OrionResponse']
    data = orionResponse['data']
    feedIds = []
    feeds = data['feeds']
    #for feed in feeds:
    #    feedInfo = feed['feedInfo']
    #    feedId = feedInfo['id']
    #    feedIds.append(feedId)
    if feeds:
        print '======================================='
        print 'Registered Feed(s) Details'
        print '======================================='
        for feed in feeds:
            feedInfo = feed['feedInfo']
            feedId = feedInfo['id']
            feedIds.append(feedId)
            print 'Feed ID:' + str(feedInfo['id']) + ', Source IP:' + feedInfo['sourceIp'] + ', Dest IP:' + feedInfo['ip'] + ', Port:' + str(feedInfo['port'])
        print '======================================='
    return feedIds

def log_report(content):
    log_line = content.split('\n')
    if len(log_line) > 2 and content.find("Service QoE error") != -1:
        print '======================================='
        print 'QoE Test Fail. Refer generated report....!!' 
        print '=======================================' + '\n'
        return 1 
    else:
        print '======================================='
        print 'QoE Test Pass.' + '\n'
        print '=======================================' + '\n'
        return 0
    
def is_valid_ip(ip):
    m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip)
    return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))
    
if __name__ == '__main__':
    main(sys.argv[1:])
