from site_list_parse import Site_List_Parse
import sys
from domain import Domain

# paths to inpt and outpt files will be args
# ideally in this directory

input_txt_file = sys.argv[1]
output_json_file = sys.argv[2]

parse = Site_List_Parse(input_txt_file, output_json_file)
parse.parse()


# # DEBUG =-------------------------------------------------------------           
# clocktab = Domain("en.wikipedia.org")
# ips = clocktab.get_ip_addresses()
# print(ips)
# print(clocktab.get_server_type())
# print(f"INSECURE: {clocktab.test_insecure_http()}")
# print(f"REDIRECTS AND HSTS: {clocktab.test_redirect_to_https_and_hsts()}")




# cloud = Domain("tls13.cloudflare.com")
# # print(cloud.get_ip_addresses())
# # print(cloud.get_server_type())
# print(f"REDIRECTS: {cloud.test_redirect_to_https_and_hsts()}")
# cloud.test_tls()