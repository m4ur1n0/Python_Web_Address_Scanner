# Python_Web_Address_Scanner
Python program to take in lists of domain names, scan them, and generate a report providing useful information. The information a scan performed by a Site_List_Scan object performs using methods of the Domain objects it creates provide the following information:

• IPv4 Addresses associated with domain
• IPv6 Addresses associated with domain
• General geographical locations associated with each IPv4 address
• Whether the site has enabled HTTP Strict Transport Security
• The type of server running the site
• Whether or not the site listens for unencrypted HTTP requests on port 80
• Reverse DNS names associated with each IPv4 address associated with the site
• Whether or not the site eventually redirects to an HTTPS site
• The Root Certificate Authority who certified the site
• The TLS Versions supported by the server

This project was really fun, taught me a lot about retrieving network data from sites using command line tools and using different Python modules. I learned a lot about the texttables, requests, urllib3, and maxminddb modules.
