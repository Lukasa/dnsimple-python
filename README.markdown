Python DNSimple
===============

## Introduction

This is a client for the DNSimple REST API. It currently allows you to fetch existing domain info, as well as bulk-register new domains. More features are on the way.

### Requirements

Before you begin, you will need the excellent [requests](https://github.com/kennethreitz/requests) module, by Kenneth Reitz. To install it, run either
        
        pip install requests

or, if you absolutely must:

        easy_install requests

But, you know, don't do it that way.

### Getting started

From your code, import the module:

	from dnsimple import DNSimple

Create a DNSimple object, using your username and password.
	
	dns = DNSimple(username, password) 

### Check out your existing domains:

Just run:

	domains = dns.getdomains()

Results appear as list of Python dicts:

	['domain': {'created_at': '2010-10-14T09:45:32Z',
	            'expires_at': '10/14/2011 5:45:00 AM',
	            'id': 999,
	            'last_enom_order_id': None,
	            'name': 'yourdomain.com',
	            'name_server_status': 'active',
	            'registrant_id': 99,
	            'registration_status': 'registered',
	            'updated_at': '2010-10-14T10:00:14Z',
	            'user_id': 99}},
	{'domain': {'created_at': '2010-10-15T16:02:34Z',
	            'expires_at': '10/15/2011 12:02:00 PM',
	            'id': 999,
	            'last_enom_order_id': None,
	            'name': 'anotherdomain.com',
	            'name_server_status': 'active',
	            'registrant_id': 99,
	            'registration_status': 'registered',
	            'updated_at': '2010-10-15T16:30:16Z',
	            'user_id': 99}}]


### Check out a specific domain

	dns.getdomain('mikemaccana.com')

Results are the same as getdomains() above, but only show the domain specified.

### Register a new domain

Just run:

	dns.register('newdomain.com')

This will register 'newdomain.com', automatically picking the registrant\_id from your first domain. To specify a particularly registrant\_id, just run:

	dns.register('newdomain.com',99)

Responses will be in a dictionary describing the newly created domain, same as the getdomain() above.
	
### License

Licensed under the [MIT license](http://www.opensource.org/licenses/mit-license.php)	
