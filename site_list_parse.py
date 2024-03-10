import json
from domain import Domain
import time
import threading


class Site_List_Parse():

    def __init__(self, path_to_url_list : str, path_to_output: str):
        # url_list should be a file with a list of domains
        self.path_to_url_list = path_to_url_list
        self.url_list = []
        with open(path_to_url_list, "r") as u:
            urls = u.readlines()
            for url in urls:
                if url not in self.url_list:
                    # NO REPEATS -- WILL FUCK W MULTITHREADING
                    self.url_list.append(url)

        self.path_to_output = path_to_output
        self.output_dict = {}
        self.threads = set()

    def parse(self):

        with open(self.path_to_output, "w") as o:
            
            for url in self.url_list:
                # self.get_info_from_url(url)
                url = url.strip()
                if url != "":
                    thread = threading.Thread(target=self.get_info_from_url, args=[url])
                    thread.start()
                    self.threads.add(thread)
                    # for some reason it doesn't always get every IP without this sleep
                    time.sleep(0.2)
            

            for thread in self.threads:
                thread.join()
            # put the dict in human readable format in the output file
            json.dump(self.output_dict, o, sort_keys=True, indent=4)

            for u in self.url_list:
                if u.strip() not in self.output_dict.keys():
                    print(f"why isn't {u} in the dict?")


    def get_info_from_url(self, url):
        
        epoch_time = float(time.time())

        site = Domain(url)
        if not site.is_valid_url():
            # create json for invalid website
            return

        ipv4s, ipv6s, rdns_names = site.get_ip_addresses()
        server = site.get_server_type()
        # print(f"RECEIVED : {url}'s ips: {ipv4s}, {ipv6s}")

        url_dict = {"scan_time" : epoch_time}
        # initialize ip lists (meant to have empty lists if none found)
        url_dict["ipv4_addresses"] = []
        url_dict["ipv6_addresses"] = []
        url_dict["rdns_names"] = []

        # WITH MULTITHREADING, THIS MAY CAUSE ISSUES IF THE SAME DOMAIN IS SUBMITTED MULTIPLE TIMES
        # but honestly it should be ..... okay (knock on wood), because it only does reassignments
        for ipv4 in ipv4s:
            # Domain.get_ip_addresses() returns a list of 4 tuples that have the ips but also some info
            # about their address families and their socket kinds
            if ipv4 and ipv4 not in url_dict['ipv4_addresses']:
                url_dict["ipv4_addresses"].append(ipv4)
            
        for ipv6 in ipv6s:
            if ipv6 and ipv6 not in url_dict['ipv6_addresses']:
                url_dict["ipv6_addresses"].append(ipv6)

        for rdns in rdns_names:
            if rdns not in url_dict["rdns_names"] and rdns != "":
                url_dict["rdns_names"].append(rdns)
        if server:
            url_dict["http_server"] = server
        else:
            url_dict["http_server"] = None

        # USE IPV4 LIST TO GET RTT TIMES
        ipv4s = url_dict['ipv4_addresses']
        
        # rtt_range, locations = site.get_rtt_and_geo(ipv4s)
        # url_dict['rtt_range'] = rtt_range
        url_dict['geo_locations'] = site.get_geo(ipv4s)

        # NOW LETS DO INSECURE, REDIRECT, AND TLS

        url_dict['insecure_http'] = site.test_insecure_http()

        redirect_and_hsts = site.test_redirect_to_https_and_hsts()
        url_dict['redirect_to_https'] = redirect_and_hsts['https']
        url_dict['hsts'] = redirect_and_hsts['hsts']

        url_dict['tls_versions'] = site.test_tls()
        
        # NOW LETS DO ROOT_CA AND
        url_dict['root_ca'] = site.get_root_ca()

        # FINALLY, add this url's info to our class dict
        self.output_dict[url] = url_dict