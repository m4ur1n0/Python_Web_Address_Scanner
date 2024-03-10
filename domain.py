import socket
import subprocess
import sys
from urllib.parse import urlparse
import requests
import re
import maxminddb


class Domain():
    
    def __init__(self, url):
        self.url = url

    def is_valid_url(self):
        try:
            result = urlparse(self.url)
            return True
        except ValueError:
            try:
                result = urlparse("http://" + self.url)
                return True
            except:
                return False
        

    def get_ip_addresses(self):
        ipv4_addresses = []
        ipv6_addresses = []
        url = self.url

        with open("public_dns_resolvers.txt", "r") as dnslist:
            dnses = dnslist.readlines()
            for dns in dnses:
                if dns[-1] == '\n':
                    dns = dns[0:-1]
                
                try:
                    # RUN IPv4 SEARCH
                    result = subprocess.check_output(["nslookup", url, dns], timeout=2, stderr=subprocess.STDOUT).decode("utf-8")
                    # using regex, need to exclude the first two lines, or it will grab server ips
                    result = "\n".join(result.split("\n")[2:])
                    # print(result)
                    # lines = result.split("\n")
                    ipv4_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
                    ipv4s = re.findall(ipv4_pattern, result)
                    for ip in ipv4s:
                        # print(f"captured {url} : {ip}")
                        # sorts thru duplicates AFTER the fact
                        ipv4_addresses.append(ip)

                    # RUN IPv6 SEARCH
                    result = subprocess.check_output(["nslookup", "-type=AAAA", url, dns], timeout=2, stderr=subprocess.STDOUT).decode("utf-8")
                    lines = result.split("\n")
                    # print(f"-----------------------------------------------\n{result}")
                    
                    try:
                        # find where the list of ips will start
                        start = lines.index("Non-authoritative answer:")
                        results = lines[start + 1:]
                        # iterate through rest of lines and grab ips
                        for answer in results:
                            pair = answer.split(':')
                            # print(f"dealing with pair {pair} :")
                            if "Address" in pair:
                                ip = ':'.join(pair[1:]).strip()
                                # print(f"captured {url} : {ip}\n--------------------------------------------------")
                                # can exclude duplicates later
                                ipv6_addresses.append(ip)
                    except:
                        print(f"{e}\ni.e. no answers were given from IPv6 nslookup for {url} using {dns}", file=sys.stderr)

                except Exception as e:
                    print(f"encountered exception: {e} when trying to nslookup {url} using resolver {dns}\n", file=sys.stderr)
                    pass
        
        # print(f"RETURNING: {url} : {ipv4_addresses}, {ipv6_addresses}")
        # NOW GET THE RDNS RESULTS:
        rdns_names = []
        for ip in ipv4_addresses:
            try:
                rdns_name = socket.gethostbyaddr(ip)[0]
                rdns_names.append(rdns_name)
            except socket.herror:
                rdns_names.append("")

        return (ipv4_addresses, ipv6_addresses, rdns_names)
 
    def get_geo(self, ipv4_addresses):
        # min_rtt = float('inf') 
        # max_rtt = float('-inf') 

        reader = maxminddb.open_database("GeoLite2-City.mmdb")
        geo_locations = []
        
        for ip in ipv4_addresses:
            try:
                # # Run telnet command with time
                # command = f"sh -c \"time echo -e '\\x1dclose\\x0d' | telnet {ip} 443\""
                # telnet_result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # out, err = telnet_result.communicate()
                
                # # Extract RTT value from the stderr
                # rtt_pattern = r"real\s+(\d+)m(\d+\.\d+)s"
                # rtt_match = re.search(rtt_pattern, out.decode("utf-8"))
                
                
                # if rtt_match:
                #     minutes = float(rtt_match.group(1))
                #     seconds = float(rtt_match.group(2))
                #     total_rtt = (minutes * 60 + seconds) * 1000
                    
                #     # Update min_rtt and max_rtt if needed
                #     min_rtt = min(min_rtt, total_rtt)
                #     max_rtt = max(max_rtt, total_rtt)


                # GEO LOCATION TIME
                location = reader.get(ip)
                if location:
                    city = location.get('city', {}).get('names', {}).get('en', '')
                    subdivision = location.get('subdivisions', [{}])[0].get('names', {}).get('en', '')
                    country = location.get('country', {}).get('names', {}).get('en', '')
                    # Construct geo location string
                    geo_location = ', '.join(filter(None, [city, subdivision, country]))
                    if geo_location not in geo_locations and geo_location != "":
                        geo_locations.append(geo_location)


            except Exception as e:
                print(f"geolocating did not work with {ip}, raised error: {e}")
                return []

        
        return geo_locations

    def get_server_type(self):
        if "https://" not in self.url:
            url = "https://" + self.url
        else:
            url = self.url

        try:
            resp = requests.head(url)
            return resp.headers.get('Server')
        
        except requests.exceptions.RequestException as e:
            # print(f"{e}")
            return None
    
    # ALL OF THE BELOW HAVE NOT BEEN IMPLEMENTED IN SITE_LIST_PARSE
    
    def test_insecure_http(self):

        try:
            # Attempt to create a socket connection
            conn = socket.create_connection((self.url, 80), timeout=2)
            conn.close()
            return True
        except (socket.timeout, ConnectionRefusedError):
            return False
        
    def test_redirect_to_https_and_hsts(self, max_redirects=10):
        # returns {'https' : bool, 'hsts': bool}
        if not self.url.startswith("http"):
            url = f"http://{self.url}"
        else:
            url = self.url

        https = False
        hsts = False
        try:
            
            redirect_count = 0
            response = ""
            while redirect_count < max_redirects:
                response = requests.get(url, allow_redirects=False, timeout=2)
                if response.status_code in (301, 302, 307, 308) and 'Location' in response.headers:
                    redirect_location = response.headers['Location']
                    if redirect_location.startswith('https://'):
                        # if it redirects to an https site, get that as final url, and break
                        url = redirect_location
                        https = True
                        break
                    else:
                        # if not an https redirect just keep on checking
                        url = redirect_location
                else:
                    # not a redirect = not a check
                    break
                redirect_count += 1
            
            # if the final page has enabled hsts
            final_response = response
            if final_response != "":
                if 'Strict-Transport-Security' in final_response.headers:
                    hsts = True
                else:
                    hsts = False
            
        except requests.RequestException:
            return {'https' : False, 'hsts' : False}
        
        return {'https': https, 'hsts': hsts}
    
    def test_tls(self):
        # nmap --script ssl-enum-ciphers -p 443 northwestern.edu
        url = self.url
        try:
            result = subprocess.check_output(["nmap", "--script", "ssl-enum-ciphers", "-p", "443", url], timeout=4, stderr=subprocess.STDOUT).decode("utf-8")
            lines = result.split("\n")
            tls_types = []
            for line in lines:
                if "TLSv" in line:
                    tls_type = line[1:].strip()
                    if tls_type not in tls_types:
                        if tls_type[-1] == ":":
                            tls_types.append(tls_type[0:-1])
                        else:
                            tls_types.append(tls_type)
            
            return tls_types
        except Exception as e:
            print(f"No luck with nmap on {url} due to:\n{e}", file=sys.stderr)
            return []

    
    def get_root_ca(self):
        
        try:
            result = subprocess.check_output(["openssl", "s_client", "-connect", self.url + ":443"],input=b'', timeout=3, stderr=subprocess.STDOUT).decode("utf-8")
            lines = result.split("\n")
            narrowed = ""
            for line in lines:
                if "O = " in line:
                    # get the first time a CA is mentioned (will be deepest)
                    narrowed = line
                    break
            
            # print(narrowed)
            start_index = narrowed.find('O = ')  
            end_index = narrowed.rfind(',', start_index)
            last_comma_index = narrowed.find(',', start_index, end_index + 1) 
            # print(f"start : {start_index}, end: {end_index}, last comma: {last_comma_index}")

            if start_index != -1 and last_comma_index != -1:
                # get the substring between 'O = ' and the last comma before the next '='
                organization = narrowed[start_index + len('O = '):last_comma_index]
                if organization == "Unspecified":
                    return None
                return organization.strip()
            else:
                print(f"no org????????? : {self.url}")
                return None 

        except Exception as e:
            print(f"Could not get root ca of {self.url} due to:\n{e}")
            return None

