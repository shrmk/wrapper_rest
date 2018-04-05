import httplib2
from urllib import urlencode


class OrionManagerService(object):
    '''
    Maintains information about the HTTP service
    '''
    address = u''
    'The IP address at which Orion Manager is running'
    
    port = 1729
    'The port at which Orion Manager is running'
    
    url = u''
    'The URL of the REST interface of Orion Manager'

    response = None
    'Holds the response header for any HTTP request'
    
    content = u''
    'Holds the content string for any HTTP request'
    
    
    def __init__(self, address=u'localhost', port=1729):
        httplib2.debuglevel = 0
        self.address = address
        self.port = port
        self.url = u'http://%s:%d/rest/' % (address, port)
        #self.url = u'http://%s:%d/' % (address, port)
        self.h = httplib2.Http(".cache")
        
        
    def get(self, url, acceptHeader):
        headers = {'Accept': '*/*,'+acceptHeader}
        self.response, self.content = self.h.request(url, "GET", headers=headers)
        return self.content
    
    def put_form(self, url, acceptHeader, **data):
        '''
        Submits a form to the server using PUT request.
        '''
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                  'Accept': '*/*,'+acceptHeader}
        body = urlencode(data)
        self.response, self.content = self.h.request(url, "PUT", 
                                                     body=body,
                                                     headers=headers)
        return self.content
        
    
    def post_form(self, url, acceptHeader, **data):
        '''
        Submits a form to the server using POST request.
        '''
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                  'Accept': '*/*,'+acceptHeader}
        body = urlencode(data)
        self.response, self.content = self.h.request(url, "POST", 
                                                     body=body,
                                                     headers=headers)
        return self.content
    
    
    def post(self, url, acceptHeader):
        '''
        Makes a simple POST request to a given URL 
        (without any form data)
        '''
        headers = {'Accept': '*/*,'+acceptHeader}
        self.response, self.content = self.h.request(url, "POST",
                                                     headers=headers)
        return self.content
        
        
    def delete(self, url, acceptHeader):
        headers = {'Accept': '*/*,'+acceptHeader}
        self.response, self.content = self.h.request(url, "DELETE", headers=headers)
        return self.content
        
    def put(self, url, acceptHeader):
        '''
        Makes a simple PUT request to a given URL 
        (without any form data)
        '''
        headers = {'Accept': '*/*,'+acceptHeader}
        self.response, self.content = self.h.request(url, "PUT", headers=headers)
        return self.content
