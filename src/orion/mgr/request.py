'''
Created on Dec 15, 2014

@author: fpvn87
'''
# Python imports
import json
import xml.etree.cElementTree as ET
import os

# Our imports


class RequestWrapper(object):
    '''
    Wrapper for Debug REST API
    '''
    service = None
    'Handle to Orion Manager service'
    
    def __init__(self, service):
        self.service = service
        self.url = self.service.url
    
    def scanFeed(self):
        '''
        Discover/scan all the feeds
        '''
        print 'Within request scan feed...'
        acceptHeader = 'orion/setup.feeds.scan.v1'
        extraPath =  self.url + u'setup/feeds/scan'
        return self.service.post(extraPath, acceptHeader)
    
    def scanSpecificFeed(self, content):
        '''
        Scan specific feed based on stream src/dst ip 
        address and dst port
        '''
	print 'content', content
        print 'Within request scan feed...'
        acceptHeader = 'orion/setup.feeds.scan.v1'
        result  = self.service.post_form(self.url + (u'setup/feeds/scan'), acceptHeader, feeds=content)
        return result
    
    def deleteFeed(self):
        acceptHeader = 'orion/setup.feeds.delete.v1'
        extraPath =  self.url + u'setup/feeds/delete'
        return self.service.post(extraPath, acceptHeader)

    def deleteSpecificFeed(self, content):
        acceptHeader = 'orion/setup.feeds.delete.v1'
        result  = self.service.post_form(self.url + (u'setup/feeds/delete'), acceptHeader, feeds=content)
        return result

    def isScanSuccessfullyCompleted(self, requestId):
        acceptHeader = 'orion/setup.feeds.scan.status.v1'
        content  = self.service.get(self.url + (u'setup/feeds/scan/status?requestId=%s' % (requestId)), acceptHeader)
        return json.loads(content)
    
    def writeBinaryFile(self, filePath, content):
        f = open(filePath,'wb')
        f.write(content)
        f.close()
        
    def writeTextFile(self, filePath, content):
        f = open(filePath,'w')
        f.write(content)
        f.close()
    
    def exportCSVFeedWise(self, fromTime, toTime, feedId, filePath):
        acceptHeader = 'orion/reports.alerts.csvReport.v1'
        content  = self.service.get(self.url + (u'reports/alerts/csvReport?fromTime=%d&toTime=%d&numRows=1000&stream=%d' % (fromTime, toTime, feedId)), acceptHeader)
        self.writeTextFile(filePath, content)        
        return content
    
    def logCSVFeedWise(self, fromTime, toTime, feedId):
        acceptHeader = 'orion/reports.alerts.csvReport.v1'
        content  = self.service.get(self.url + (u'reports/alerts/csvReport?fromTime=%d&toTime=%d&numRows=1000&stream=%d' % (fromTime, toTime, feedId)), acceptHeader)
        return content

    def exportCSV(self, fromTime, toTime, filePath):
        acceptHeader = 'orion/reports.alerts.csvReport.v1'
        content  = self.service.get(self.url + (u'reports/alerts/csvReport?fromTime=%d&toTime=%d' % (fromTime, toTime)), acceptHeader)
        self.writeTextFile(filePath, content)        
        return content

    def logCSV(self, fromTime, toTime):
        acceptHeader = 'orion/reports.alerts.csvReport.v1'
        content  = self.service.get(self.url + (u'reports/alerts/csvReport?fromTime=%d&toTime=%d' % (fromTime, toTime)), acceptHeader)
        return content    

    def exportXML(self, fromTime, toTime, feedId, filePath):
        acceptHeader = 'orion/reports.alerts.xmlReport.v1'
        content  = self.service.get(self.url + (u'reports/alerts/xmlReport?fromTime=%d&toTime=%d&numRows=1000&stream=%d' % (fromTime, toTime, feedId)), acceptHeader)
        self.writeTextFile(filePath, content)        
        return content
    
    def exportPDF(self, fromTime, toTime, filePath):
        acceptHeader = 'orion/reports.alerts.pdfReport.v1'
        content  = self.service.get(self.url + (u'reports/alerts/pdfReport?fromTime=%d&toTime=%d&numRows=1000' % (fromTime, toTime)), acceptHeader)
        self.writeBinaryFile(filePath, content)        
        return content
    
    def exportPDFFeedWise(self, fromTime, toTime, feedId, filePath):
        acceptHeader = 'orion/reports.alerts.pdfReport.v1'
        content  = self.service.get(self.url + (u'reports/alerts/pdfReport?fromTime=%d&toTime=%d&numRows=1000&stream=%d' % (fromTime, toTime, feedId)), acceptHeader)
        self.writeBinaryFile(filePath, content)        
        return content

    def getListOfFeedsWithIpPort(self, ip, port):
        acceptHeader = 'orion/setup.feeds.v1'
        content  = self.service.get(self.url + (u'setup/feeds?ip=%s&port=%d'  % (ip, port)), acceptHeader)
        return json.loads(content)

    def getListOfFeedsWithSourceIpPort(self, dip, port, sip):
        acceptHeader = 'orion/setup.feeds.v1'
        content  = self.service.get(self.url + (u'setup/feeds?ip=%s&port=%d&sourceIp=%s'  % (dip, port, sip)), acceptHeader)
        return json.loads(content)

    def getListOfAllScannedFeeds(self):
        acceptHeader = 'orion/setup.feeds.v1'
        content  = self.service.get(self.url + (u'setup/feeds'), acceptHeader)
        return json.loads(content)
 
    def startMultipleFeedMonitoring(self, content):
        acceptHeader = 'orion/livemonitoring.feeds.startMonitoring.v1'
        result  = self.service.post_form(self.url + (u'livemonitoring/feeds/startMonitoring'), acceptHeader, monitoringRequests=content)
        return result
    
    def stopMultipleFeedMonitoring(self, content):
        acceptHeader = 'orion/livemonitoring.feeds.stopMonitoring.v1'
        result  = self.service.post_form(self.url + (u'livemonitoring/feeds/stopMonitoring'), acceptHeader, monitoringRequests=content)
        return result

    def startMultipleServiceMonitoring(self):
        acceptHeader = 'orion/livemonitoring.feeds.startQualityMonitoring.v1'
        result = self.service.get(self.url + (u'livemonitoring/feeds/startQualityMonitoring'), acceptHeader)
        return result

    def stopMultipleServiceMonitoring(self):
        acceptHeader = 'orion/livemonitoring.feeds.stopQualityMonitoring.v1' 
        result = self.service.get(self.url + (u'livemonitoring/feeds/stopQualityMonitoring'), acceptHeader)
        return result

    def getListofProfiles(self):
        acceptHeader = 'orion/setup.profiles.v1'
        result = self.service.get(self.url + (u'setup/profiles'), acceptHeader)
        return result

    def getDefaultProfile(self):
        acceptHeader = 'orion/setup.profiles.default.v1'
        result = self.service.get(self.url + (u'setup/profiles/default'), acceptHeader)
        return result

    def setDefaultProfile(self, content):
        acceptHeader = 'orion/setup.profiles.setDefault.v1'
        result = self.service.post_form(self.url + (u'setup/profiles/setDefault'), acceptHeader, profile=content)
        return result
