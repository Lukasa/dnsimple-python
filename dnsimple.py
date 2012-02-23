'''Client for DNSimple REST API
https://dnsimple.com/documentation/api
'''

import base64
import re
import json
import logging
import requests

class DNSimple(object):
    def __init__(self, uname, pwd):
        self.__endpoint = 'https://dnsimple.com'
        self.__authdata = (uname, pwd)
        self.__useragent = 'DNSimple Python API v0.1'
        self.__headers = {"Accept"    : "application/json",
                          "User-Agent": self.__useragent}
        self.__session = requests.session(auth    = self.__authdata,
                                          headers = self.__headers)

    def __resthelper(self,url,postdata=""):    
        '''Does GET requests and (if postdata specified) POST requests.
        
        postdata should be a python dict'''
        url = self.__endpoint + url
       
        # If postdata isn't provided, assume we want a GET.
        if not postdata:
            request = self.__session.get(url)
            request.raise_for_status()
            return json.loads(request.text)
        else:
            postdata = json.dumps(postdata)
            request = self.__session.post(url, data=postdata)

    def __deletehelper(self,url):    
        '''Does DELETE requests.'''
        raise Exception('Not implemented yet')
                  
    def getdomains(self):
        '''Get a list of all domains in your account.'''
        return self.__resthelper('/domains')

    def getdomain(self,domain):
        '''Get the details for a specific domain in your account. .'''
        return self.__resthelper('/domains/' + domain)

    def register(self,domainname,registrant_id=None):
        '''Register a domain name with DNSimple and the appropriate domain
        registry. '''
        if not registrant_id:
            # Get the registrant ID from the first domain in the account
            try:
                registrant_id = self.getdomains()[0]['domain']['registrant_id']
            except:
                print 'Could not find registrant_id! Please specify manually.'
                exit
        
        postdata = {"domain":{"name": domainname,
                              "registrant_id": registrant_id}}
        return self.__resthelper('/domain_registrations', postdata)


    def transfer(self, domainname, registrant_id, authdata):
        '''Transfer a domain name from another domain registrar into DNSimple.
        '''
        postdata = {"domain"        : {"name": domainname,
                                       "registrant_id": registrant_id
                                      },
                    "transfer_order": {"authinfo" : authdata}
                    }
        return self.__resthelper('/domain_transfers', postdata)        

    def adddomains(self, domainname):
        '''Create a single domain in DNSimple in your account.'''
        postdata = {"domain": {"name": domainname}} 
        return self.__resthelper('/domains', postdata)          

    def delete(self,domain):
        '''Delete the given domain from your account. You may use either the 
        domain ID or the domain name.'''
        return self.__deletehelper('/domains/' + domain)
               
