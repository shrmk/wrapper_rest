'''
Created on Dec 15, 2014

@author: fpvn87
'''

# Python imports
import json
import xml.etree.cElementTree as ET

# Our imports
from orion.mgr.util import OrionManagerService
from urllib import urlencode
from orion.mgr.request import RequestWrapper

class OrionManager(object):
    
    service = None
    'Handle to Orion Manager service'
    
    def __init__(self, address='localhost', port=1729):
        self.service = OrionManagerService(address, port)
        self.url = self.service.url + u'orion'
  
    
    def getRequestWrapper(self):
        return RequestWrapper(self.service)
    
        
        
        
