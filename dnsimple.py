'''Client for DNSimple REST API
https://dnsimple.com/documentation/api
'''

import re
import json
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

    def __resthelper(self, method, url, data=""):    
        '''Handles requests.
        
        url is the url for the request
        method should be a string indicating the method, e.g. 'get'
        postdata should be a python dict'''
        url = self.__endpoint + url
       
        # No assumptions. Check the method given.
        if (method == 'get'):
            request = self.__session.get(url)
            request.raise_for_status()
            return json.loads(request.text)
        
        elif ((method == "post") && data):
            # Refuse to post without data.
            extra_header = {"Content-Type": "application/json"}
            postdata = json.dumps(data)
            request = self.__session.post(url,
                                          data = postdata, 
                                          headers = extra_header)
       
        elif (method == "put"):
            pass
        
        elif (method == "delete"):
            pass
        
        else:
            raise Exception('Could not find valid method to perform.')

    def __deletehelper(self,url):    
        '''Does DELETE requests.'''
        raise Exception('Not implemented yet')
                  
    def getdomains(self):
        '''Get a list of all domains in your account.'''
        return self.__resthelper('get', '/domains')

    def getdomain(self,domain):
        '''Get the details for a specific domain in your account. .'''
        return self.__resthelper('get', '/domains/' + domain)

    def createdomain(self, domainname):
        '''Create a single domain in DNSimple in your account.'''
        postdata = {"domain": {"name": domainname}} 
        return self.__resthelper('post', '/domains', postdata)

    def checkdomain(self, domainname):
        '''Check if a given domain is available for registration.'''
        raise Exception('Not implemented yet')

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
        return self.__resthelper('post', '/domain_registrations', postdata)


    def transfer(self, domainname, registrant_id, authdata):
        '''Transfer a domain name from another domain registrar into DNSimple.
        '''
        postdata = {"domain"        : {"name": domainname,
                                       "registrant_id": registrant_id
                                      },
                    "transfer_order": {"authinfo" : authdata}
                    }
        return self.__resthelper('post', '/domain_transfers', postdata)        

    def renewdomain(self, domainname):
        '''Renew a domain name in your account.'''
        raise Exception('Not implemented yet')

    def enable_auto_renewal(self, domain):
        '''Enable auto renewal for a domain.'''
        raise Exception('Not implemented yet.')

    def disable_auto_renewal(self, domain):
        '''Disable auto renewal for a domain.'''
        raise Exception('Not implemented yet.')
    
    def delete(self,domain):
        '''Delete the given domain from your account. You may use either the 
        domain ID or the domain name.'''
        return self.__deletehelper('delete', '/domains/' + domain)

    def nameservers(self, nameservers="", reset=False):
        '''Change the name servers to either external nameservers or back to
        DNSimple's nameservers.'''
        raise Exception('Not implemented yet.')

    def getservices(self):
        '''Get a list of all the services supported.'''
        raise Exception('Not implemented yet.')

    def getservices(self, serviceid):
        '''Describe a particular services by ID.'''
        raise Exception('Not implemented yet.')

    def get_applied_services(self, domain):
        '''List services already applied to a domain.'''
        raise Exception('Not implemented yet.')

    def get_available_services(self, domain):
        '''List services available for a domain.'''
        raise Exception('Not implemented yet.')

    def apply_service(self, service):
        '''Add a services to a domain.
        
        service must be either the short name of the service or the service id.
        '''
        raise Exception('Not implemented yet.')

    def remove_service(self, service):
        '''Remove a service from a domain.
        
        service must be either the short name of the service or the service id.
        '''
        raise Exception('Not implemented yet.')

    def get_records(self, domain):
        '''Get a list of records for a specific domain.
        
        domain must be the domain name or id.'''
        raise Exception('Not implemented yet.')

    def get_record(self, domain, record_id):
        '''Display details about a specific record.
        
        domain must be the domain name or id.
        record_id must be the record id.'''
        raise Exception('Not implemented yet.')

    def create_record(self, domain):
        '''Create a record for the given domain.
        
        domain must be the domain name or id.'''
        raise Exception('Not implemented yet.')

    def update_record(self, domain, record_id):
        '''Update the given record for a given domain
        
        domain must be the domain name or id.
        record_id must be the record id.'''
        raise Exception('Not implemented yet.')

    def delete_record(self, domain, record_id):
        '''Delete the record with the given id for the given domain.
        
        domain must be the domain name or id.
        record_id must be the record id.'''
        raise Exception('Not implemented yet.')

    def enable_vanity_name_servers(self, domain):
        '''Enable vanity name servers for the given domain.
        
        domain must be the domain name or id.'''
        raise Exception('Not implemented yet.')

    def disable_vanity_name_servers(self, domain):
        '''Disable vanity name servers for the given domain.
        
        domain must be the domain name or id.'''
        raise Exception('Not implemented yet.')

    def get_contacts(self, domain):
        '''Get a list of all the contacts in the account.
        
        domain must be the domain name or id.'''
        raise Exception('Not implemented yet.')

    def get_contact(self, contact_id):
        '''List a specific contact in the account using the contact_id.
        
        contact_id must be the contact id.'''
        raise Exception('Not implemented yet.')

    def create_contact(self):
        '''Create a contact in DNSimple.'''
        raise Exception('Not implemented yet.')

    def update_contact(self, contact_id):
        '''Update a contact in DNSimple.
        
        contact_id must be the contact id.'''
        raise Exception('Not implemented yet.')

    def delete_contact(self, contact_id):
        '''Delete a contact from DNSimple.

        contact_id must be the contact id.'''
        raise Exception('Not implemented yet.')

    def get_templates(self):
        '''List all of the custom templates in the account.'''
        raise Exception('Not implemented yet.')

    def get_template(self, template):
        '''Get a specific template.

        template must be the template short name or id.'''
        raise Exception('Not implemented yet.')

    def create_template(self):
        '''Create a custom template.'''
        raise Exception('Not implemented yet.')

    def delete_template(self, template):
        '''Delete a given template.

        template must be the template short name or id.'''
        raise Exception('Not implemented yet.')

    def apply_template_to_domain(self, domain, template):
        '''Apply a template to a domain.

        domain must be the domain name or ID for the domain.
        template must be the short name or ID for the template.'''
        raise Exception('Not implemented yet.')

    def get_template_records(self, template):
        '''List the template records for a template.

        template must be the short name or id for a template.'''
        raise Exception('Not implemented yet.')

    def get_template_record(self, template, record_id):
        '''View a specific template record.

        template must be the short name or id for a template.
        record_id must be the record id.'''
        raise Exception('Not implemented yet.')

    def create_template_record(self, template):
        '''Create a template record in the given template.

        template must be the short name or id of the template.'''
        raise Exception('Not implemented yet.')

    def delete_template_record(self, template, record_id):
        '''Delete a specific template record.

        template must be the short name or id of the template.
        record_id must be the record id.'''
        raise Exception('Not implemented yet.')

    def required_extended_attributes(self, tld):
        '''Get details on the required extended attributes for a particular
        top-level domain.

        tld must be the relevant top-level domain.'''
        raise Exception('Not implemented yet.')

    def enable_privacy_protection(self, domain):
        '''Turn on WHOIS privacy protection for a given domain.

        domain must be the domain name or id.'''
        raise Exception('Not implemented yet.')

    def disable_privacy_protection(self, domain):
        '''Turn off WHOIS privacy protection for a given domain.

        domain must be the domain name or id.'''
        raise Exception('Not implemented yet.')

    def get_domain_members(self, domain):
        '''List all of the current members for a domain.

        domain must be the domain name or id.'''
        raise Exception('Not implemented yet.')

    def add_domain_member(self, domain):
        '''Add another DNSimple customer to a domain's memberships.

        domain must be the domain name or id.'''
        raise Exception('Not implemented yet.')
    
    def remove_domain_member(self, domain, email):
        '''Remove a DNSimple customer from the domain's memberships.

        domain must be the domain name or id.
        email must be the email address of the member.'''
        raise Exception('Not implemented yet.')

    def get_ssl_certificates(self, domain):
        '''Get a list of certificates purchased under the given domain.

        domain must be the domain name or id.'''
        raise Exception('Not implemented yet.')

    def get_ssl_certificate(self, domain, cert_id):
        '''Get a specificate certificate purchased under the given domain.

        domain must be the domain name or id.
        cert_id must be the certificate id.'''
        raise Exception('Not implemented yet.')

    def purchase_ssl_certificate_for_domain(self, domain):
        '''Purchase an SSL certificate for a given domain. This is the first
        step in buying a certificate. For more information on the correct
        process, see https://dnsimple.com/documentation/api
        
        domain must be the domain name or id.'''
        raise Exception('Not implemented yet.')

    def submit_ssl_certificate(self, domain, cert_id):
        '''Submit a purchased certificate for signing by the cert authority.

        domain must be the domain name or id.
        cert_id must be the id for the certificate created by purchasing it.
        '''
        raise Exception('Not implemented yet.')

    def create_user_account(self):
        '''Provision a new user account.'''
        raise Exception('Not implemented yet.')
        
