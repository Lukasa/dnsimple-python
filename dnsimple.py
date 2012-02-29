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

    def __resthelper(self, method, url, data="", expect_404=False):    
        '''Handles requests.
        
        url is the url for the request
        method should be a string indicating the method, e.g. 'get'
        postdata should be a python dict'''
        url = self.__endpoint + url
       
        # No assumptions. Check the method given.
        if (method == 'get'):
            request = self.__session.get(url)
            
            # For reasons totally opaque to me, some methods of the DNSimple
            # API legitimately return a 404. We don't want to die when that
            # happens, so be careful.
            if (expect_404 and (request.status_code == 404)): pass
            else:
                request.raise_for_status()
            return json.loads(request.text)
        
        elif ((method == "post") and data):
            # Refuse to post without data.
            extra_header = {"Content-Type": "application/json"}
            postdata = json.dumps(data)
            request = self.__session.post(url,
                                          data = postdata, 
                                          headers = extra_header)
            return json.loads(request.text)
       
        elif ((method == "put") and data):
            # Refuse to put without data.
            extra_header = {"Content-Type": "application/json"}
            postdata = json.dumps(data)
            request = self.__session.put(url,
                                         data = postdata,
                                         headers = extra_header)
            return json.loads(request.text)
        
        elif (method == "delete"):
            request = self.__session.delete(url)
            request.raise_for_status()
            return json.loads(request.text)
        
        else:
            raise Exception('Could not find valid method to perform.')

    ###########################################################################
    # DOMAINS                                                                 #
    ###########################################################################
    
    def get_domain(self,domain=""):
        '''Get either a specific domain or all domains in your account.
        
        domain may be absent, blank, the name of a domain or the id of a
        domain'''
        return self.__resthelper('get', '/domains/' + domain)

    def create_domain(self, domainname):
        '''Create a single domain in DNSimple in your account.'''
        postdata = {"domain": {"name": domainname}} 
        return self.__resthelper('post', '/domains', data = postdata)

    def check_domain(self, domainname):
        '''Check if a given domain is available for registration.'''
        return self.__resthelper('get',
                                 '/domains/' + domainname + '/check',
                                 expect_404=True)

    def register_domain(self,
                        domainname,
                        registrant_id="",
                        extended_attributes={}):
        '''Register a domain name with DNSimple and the appropriate domain
        registry.
        
        registrant_id can be inferred from the first domain in the account if
        not provided.
        
        Some domains require extended attributes. If you need them, you must
        provide them. They are expected to be a Python dict.'''
        if not registrant_id:
            # Get the registrant ID from the first domain in the account
            try:
                registrant_id = self.getdomains()[0]['domain']['registrant_id']
            except:
                print 'Could not find registrant_id! Please specify manually.'
                exit
        
        postdata = {"domain":{"name": domainname,
                              "registrant_id": registrant_id}}

        if (extended_attributes and isinstance(extended_attributes, dict)):
            (postdata["domain"])["extended_attribute"] = extended_attributes

        return self.__resthelper('post',
                                 '/domain_registrations',
                                 data = postdata)

    def transfer_domain(self, domainname, registrant_id, authdata=""):
        '''Transfer a domain name from another domain registrar into DNSimple.

        Some TLDs require authorization codes. If it does, it's your job to
        get it and pass it into the authdata field.
        '''
        postdata = {"domain": {"name": domainname,
                               "registrant_id": registrant_id}}
        
        if authdata:
            postdata["transfer_order"] = {"authinfo": authdata}
        
        return self.__resthelper('post',
                                 '/domain_transfers',
                                 data = postdata)        

    def renew_domain(self, domainname, renew_whois=False):
        '''Renew a domain name in your account.
        
        domainname must be the domain name
        renew_whois is optional. Set to true if you wish to renew the whois
        privacy.'''
        postdata = {"domain": {"name": domainname}}

        if renew_whois:
            postdata["domain"]["renew_whois_privacy"] = {}

        return self.__resthelper('post',
                                 '/domain_renewal',
                                 data = postdata)

    def enable_auto_renewal(self, domain):
        '''Enable auto renewal for a domain.
        
        domain must be the domain name or domain id.'''
        postdata = {"auto_renewal": {}}
        
        return self.__resthelper('post',
                                 '/domains/' + domain + '/auto_renewal',
                                 data = postdata)

    def disable_auto_renewal(self, domain):
        '''Disable auto renewal for a domain.
        
        domain must be the domain name or domain id.'''
        return self.__resthelper('delete',
                                 '/domains/' + domain + '/auto_renewal')
    
    def delete_domain(self, domain):
        '''Delete the given domain from your account.
        
        domain must be the domain name or domain id.'''
        return self.__resthelper('delete', '/domains/' + domain)

    ###########################################################################
    # NAMESERVERS                                                             #
    ###########################################################################
    
    def nameservers(self, domain, nameservers="", reset=False):
        '''Change the name servers to either external nameservers or back to
        DNSimple's nameservers.
        
        Either nameservers must be provided or reset must be true. If
        nameservers are provided, they should be in the form of a Python dict,
        with keys in the form 'ns1', 'ns2' etc., and values being hostnames.
        Provide no more than 6.
        
        If reset is true, the nameservers will be set back to DNSimple's.
        
        domain must be either the domain name or id.'''
        default_nameservers = {"ns1": "ns1.dnsimple.com",
                               "ns2": "ns2.dnsimple.com",
                               "ns3": "ns3.dnsimple.com",
                               "ns4": "ns4.dnsimple.com"}

        if (nameservers and reset):
            raise ValueError("Provide either nameservers or reset, not both.")
        
        elif nameservers:
            if ((not isinstance(nameservers, dict)) and 
                                                      (len(nameservers) < 7)):
                postdata = {"name_servers": nameservers}
            
            else:
                raise ValueError("nameservers must be a dict " +
                                 "of length 6 or less.")
        
        elif reset:
            postdata = {"name_servers": default_nameservers}
        
        else:
            raise ValueError("Must provide either nameservers or reset.")

        return self.__resthelper('post',
                                 '/domains/' + domain + '/name_servers',
                                 data = postdata)

    ###########################################################################
    # SERVICES                                                                #
    ###########################################################################

    def get_services(self, serviceid=""):
        '''Describe all services or a particular service.'''
        return self.__resthelper('get', '/services/' + serviceid)

    def get_applied_services(self, domain):
        '''List services already applied to a domain.
        
        domain must be a domain name or id.'''
        return self.__resthelper('get',
                                 '/domains/' + domain + '/applied_services')

    def get_available_services(self, domain):
        '''List services available for a domain.
        
        domain must be a domain name or id.'''
        return self.__resthelper('get',
                                 '/domains/' + domain + '/available_services')

    def apply_service(self, domain, service):
        '''Add a services to a domain.
        
        domain must be either the domain name or the domain id.
        service must be either the short name of the service or the service id.
        '''
        postdata = {"service": {"name_or_id": service}}
        return self.__resthelper('post',
                                 '/domains/' + domain + '/applied_services',
                                 data = postdata)

    def remove_service(self, domain, service_id):
        '''Remove a service from a domain.
        
        domain must be either the domain name or domain id.
        service_id must be the service id.
        '''
        return self.__resthelper('delete',
                                 ('/domains/' + domain + 
                                  '/applied_services/' + service_id))

    ###########################################################################
    # RECORDS                                                                 #
    ###########################################################################

    def get_record(self, domain, record_id=""):
        '''Display all records or a specific record associated with a given
        domain.
        
        domain must be the domain name or id.
        record_id must be absent, the emptry string or the record id.'''
        return self.__resthelper('get',
                                 '/domains/' + domain + '/records/' + record_id)

    def create_record(self,
                      domain,
                      record_name,
                      record_type,
                      record_content,
                      record_ttl='',
                      record_prio=''):
        '''Create a record for the given domain.
        
        domain must be the domain name or id.
        You must provide the record name, type and content. The TTL and PRIO
        are optional.'''
        postdata = {"record": {"name"       : record_name,
                               "record_type": record_type,
                               "content"    : record_content}
                   }

        if record_ttl:
            (postdata["record"])["ttl"] = record_ttl

        if record_prio:
            (postdata["record"])["prio"] = record_prio

        return self.__resthelper('post',
                                 '/domains/' + domain + '/records',
                                 data = postdata)

    def update_record(self,
                      domain,
                      record_id,
                      record_name="",
                      record_content="",
                      record_ttl="",
                      record_prio=""):
        '''Update the given record for a given domain
        
        domain must be the domain name or id.
        record_id must be the record id.
        Any or all of the other options may be provided.'''
        postdata = {"record": {}}

        if record_name:
            (postdata["record"])["name"] = record_name

        if record_content:
            (postdata["record"])["content"] = record_content

        if record_ttl:
            (postdata["record"])["ttl"] = record_ttl

        if record_prio:
            (postdata["record"])["prio"] = record_prio

        return self.__resthelper('put',
                                 '/domains/' + domain + '/records/' + record_id,
                                 data = postdata)

    def delete_record(self, domain, record_id):
        '''Delete the record with the given id for the given domain.
        
        domain must be the domain name or id.
        record_id must be the record id.'''
        return self.__resthelper('delete',
                                 '/domains/' + domain + '/records/' + record_id)

    ###########################################################################
    # VANITY NAME SERVERS                                                     #
    ###########################################################################

    def enable_vanity_name_servers(self,
                                   domain,
                                   server_source,
                                   nameservers={}):
        '''Enable vanity name servers for the given domain.
        
        domain must be the domain name or id.
        server_source must be either "dnsimple" or "external".
        If server_source is "external", nameservers must be a dictionary of
        nameservers, with keys ns1 through ns4.'''
        keystring = "vanity_nameserver_configuration"
        postdata = {keystring: {"server_source": server_source}}
                                              
        if (server_source == "dnsimple"):
            pass
        
        elif (server_source == "external"
              and nameservers
              and isinstance(nameservers, dict)):
            
            for k, v in nameservers.items():
                (postdata[server_source])[k] = v
        
        else:
            raise ValueError("Incorrect parameters passed to method.")
        
        return self.__resthelper('post',
                                 '/domains/' + domain + '/vanity_name_servers',
                                 data = postdata)

    def disable_vanity_name_servers(self, domain):
        '''Disable vanity name servers for the given domain.
        
        domain must be the domain name or id.'''
        return self.__resthelper('delete',
                                 '/domains/' + domain + '/vanity_name_servers')

    ###########################################################################
    # CONTACTS                                                                #
    ###########################################################################
    
    def get_contact(self, contact_id=""):
        '''Get all contacts or a specific contact from the account
        
        contact_id must be absent, the empty string or the contact id.'''
        return self.__resthelper('get',
                                 '/contacts/' + contact_id)

    def create_contact(self,
                       first_name,
                       last_name,
                       address1,
                       city,
                       state_province,
                       postal_code,
                       country,
                       email_address,
                       phone,
                       org_name="",
                       job_title="",
                       fax="",
                       phone_ext="",
                       label=""):
        '''Create a contact in DNSimple.
        
        All the variables, required or optional, are expected to be strings.'''
        postdata = {"contact":
                       {"first_name"    : first_name,
                        "last_name"     : last_name,
                        "address1"      : address1,
                        "city"          : city,
                        "state_province": state_province,
                        "postal_code"   : postal_code,
                        "country"       : country,
                        "email_address" : email_address,
                        "phone"         : phone}
                   }

        if org_name:
            (postdata["contact"])["organization_name"] = org_name
        
        if job_title:
            (postdata["contact"])["job_title"] = job_title
        
        if fax:
            (postdata["contact"])["fax"] = fax
        
        if phone_ext:
            (postdata["contact"])["phone_ext"] = phone_ext
        
        if label:
            (postdata["contact"])["label"] = label

        return self.__resthelper('post',
                                 '/contacts',
                                 data = postdata)

    def update_contact(self,
                       contact_id,
                       first_name,
                       last_name,
                       address1,
                       city,
                       state_province,
                       postal_code,
                       country,
                       email_address,
                       phone,
                       org_name="",
                       job_title="",
                       fax="",
                       phone_ext="",
                       label=""):
        '''Update a contact in DNSimple.
        
        contact_id must be the contact id.'''
        postdata = {"contact":
                       {"first_name"    : first_name,
                        "last_name"     : last_name,
                        "address1"      : address1,
                        "city"          : city,
                        "state_province": state_province,
                        "postal_code"   : postal_code,
                        "country"       : country,
                        "email_address" : email_address,
                        "phone"         : phone}
                   }

        if org_name:
            (postdata["contact"])["organization_name"] = org_name
        
        if job_title:
            (postdata["contact"])["job_title"] = job_title
        
        if fax:
            (postdata["contact"])["fax"] = fax
        
        if phone_ext:
            (postdata["contact"])["phone_ext"] = phone_ext
        
        if label:
            (postdata["contact"])["label"] = label

        return self.__resthelper("put",
                                 "/contacts/" + contact_id,
                                 postdata)

    def delete_contact(self, contact_id):
        '''Delete a contact from DNSimple.

        contact_id must be the contact id.'''
        return self.__resthelper('delete',
                                 '/contacts/' + contact_id)

    ###########################################################################
    # TEMPLATES                                                               #
    ###########################################################################
    
    def get_template(self, template=""):
        '''Get all templates or a specific template from the account.

        template must be absent, the empty string or the template short name or
        id.'''
        return self.__resthelper('get',
                                 '/templates/' + template)

    def create_template(self, name, short_name, description=""):
        '''Create a custom template.'''
        postdata = {"dns_template": {"name"      : name,
                                     "short_name": short_name}
                   }

        if description:
            (postdata["dns_template"])["description"] = description

        return self.__resthelper('post',
                                 '/templates',
                                 data = postdata)

    def delete_template(self, template):
        '''Delete a given template.

        template must be the template short name or id.'''
        return self.__resthelper('delete',
                                 '/templates/' + template)

    def apply_template_to_domain(self, domain, template):
        '''Apply a template to a domain.

        domain must be the domain name or ID for the domain.
        template must be the short name or ID for the template.'''
        return self.__resthelper('post',
                                 ('/domains/' + domain + '/templates/' +
                                  template + '/apply'))

    ###########################################################################
    # TEMPLATE RECORDS                                                        #
    ###########################################################################
    
    def get_template_record(self, template, record_id=""):
        '''Get either all the template records for a template, or a specific
        record.

        template must be the short name or id for a template.
        record_id must be absent, the empty string or the record id.'''
        return self.__resthelper('get',
                                 ('/templates/' + template + 
                                 '/template_records/' + record_id))

    def create_template_record(self,
                               template,
                               name,
                               record_type,
                               content,
                               ttl="",
                               prio=""):
        '''Create a template record in the given template.

        template must be the short name or id of the template.'''
        postdata = {"dns_template_record": {"name"       : name,
                                            "record_type": record_type,
                                            "content"    : content}}
        if ttl:
            (postdata["dns_template_record"])["ttl"] = ttl

        if prio:
            (postdata["dns_template_record"])["prio"] = prio

        return self.__resthelper('post',
                                 '/templates/' + template + '/template_records',
                                 data = postdata)

    def delete_template_record(self, template, record_id):
        '''Delete a specific template record.

        template must be the short name or id of the template.
        record_id must be the record id.'''
        return self.__resthelper('delete',
                                 ('/templates/' + template +
                                 '/template_records/' + record_id))

    ###########################################################################
    # EXTENDED ATTRIBUTES                                                     #
    ###########################################################################

    def required_extended_attributes(self, tld):
        '''Get details on the required extended attributes for a particular
        top-level domain.

        tld must be the relevant top-level domain.'''
        # For the moment, this URI does not work unless it ends in .json.
        # DNSimple have been informed about this inconsistency.
        return self.__resthelper('get',
                                 '/extended_attributes/' + tld)

    ###########################################################################
    # WHOIS PRIVACY PROTECTION                                                #
    ###########################################################################

    def enable_privacy_protection(self, domain):
        '''Turn on WHOIS privacy protection for a given domain.

        domain must be the domain name or id.'''
        return self.__resthelper('post',
                                 '/domains/' + domain + '/whois_privacy')

    def disable_privacy_protection(self, domain):
        '''Turn off WHOIS privacy protection for a given domain.

        domain must be the domain name or id.'''
        return self.__resthelper('delete',
                                 '/domains/' + domain + '/whois_privacy')

    ###########################################################################
    # SHARING                                                                 #
    ###########################################################################
    
    def get_domain_members(self, domain):
        '''List all of the current members for a domain.

        domain must be the domain name or id.'''
        return self.__resthelper('get',
                                 '/domains/' + domain + '/memberships')

    def add_domain_member(self, domain, email):
        '''Add another DNSimple customer to a domain's memberships.

        domain must be the domain name or id.'''
        postdata = {"membership": {"email": email}}
        return self.__resthelper('post',
                                 '/domains/' + domain + '/memberships')
        
    
    def remove_domain_member(self, domain, email):
        '''Remove a DNSimple customer from the domain's memberships.

        domain must be the domain name or id.
        email must be the email address of the member.'''
        return self.__resthelper('delete',
                                 ('/domains/' + domain + 
                                  '/memberships/' + email))

    ###########################################################################
    # SSL CERTIFICATES                                                        #
    ###########################################################################
    
    def get_ssl_certificate(self, domain, cert_id=""):
        '''Get either all of the certificates or a specific certificate
        associated with a given domain.

        domain must be the domain name or id.
        cert_id must be absent, the empty string, or the certificate id.'''
        return self.__resthelper('get',
                                 ('/domains/' + domain +
                                  '/certificates/' + cert_id))

    def purchase_ssl_certificate_for_domain(self,
                                            domain,
                                            name,
                                            contact_id,
                                            csr=""):
        '''Purchase an SSL certificate for a given domain. This is the first
        step in buying a certificate. For more information on the correct
        process, see https://dnsimple.com/documentation/api
        
        domain must be the domain name or id.'''
        postdata = {"certificate": {"name"      : name,
                                    "contact_id": contact_id}}
        if csr:
            (postdata["certificate"])["csr"] = csr

        return self.__resthelper('post',
                                 '/domains/' + domain + '/certificates')

    def submit_ssl_certificate(self, domain, cert_id):
        '''Submit a purchased certificate for signing by the cert authority.

        domain must be the domain name or id.
        cert_id must be the id for the certificate created by purchasing it.
        '''
        return self.__resthelper('put',
                                 ('/domains/' + domain + '/certificates/' +
                                 cert_id + '/submit'))

    ###########################################################################
    # USERS                                                                   #
    ###########################################################################

    def create_user_account(self, email, password):
        '''Provision a new user account.
        
        This method DOES NOT CONFIRM passwords. Be sure you've submitted the
        right password.'''
        postdata = {"user": {"email"                : email,
                             "password"             : password,
                             "password_confirmation": password}}
        return self.__resthelper('post',
                                 '/users',
                                 data = postdata)
