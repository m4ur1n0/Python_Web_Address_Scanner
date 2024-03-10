import json
import sys
import texttable
from functools import cmp_to_key

def generate_report_body(path_to_json):
    with open(path_to_json, "r") as j:
        loaded = json.load(j)
        table = texttable.Texttable()
        table_cols = ["url domain name"]
        col_h_alignment = ["c"]
        col_v_alignment = ['m']
        col_widths = [len("url domain name")]
        
        k1 = 0 # random key who cares
        for key in loaded:
            #.keys() is not subscriptable???? I'm coding in a car give me a break
            k1 = key
            break

        for k in loaded[k1].keys():
            if k not in table_cols:
                table_cols.append(k)
                col_h_alignment.append("c")
                col_v_alignment.append('m')
                col_widths.append(len(k) + 2)
            # honestly they should all have the same keys so this should just happen the once
        


        table.set_cols_align(col_h_alignment)
        table.set_cols_valign(col_v_alignment)
        table.set_cols_width(col_widths)
        table.add_row(table_cols)

        for url in loaded:
            row = list(range(len(table_cols)))
            row[0] = url
            url_dict = loaded[url]
            for k in url_dict:
                index = table_cols.index(k)
                value = url_dict[k]
                if type(value) == list:
                    # .join only works for lists of strings
                    # value = ", ".join(value)
                    string_version = ""
                    for item in value:
                        string_version += str(item) + ",\n"
                    
                    value = string_version[0:-2]
                        
                
                row[index] = value
            table.add_row(row)
            

        return table.draw()

def rtt_comparator(tuple1, tuple2):
    min1 = tuple1[1][0]
    min2 = tuple2[1][0]
    if min1 < min2:
        return -1
    elif min1 > min2:
        return 1
    else:
        return 0

def generate_rtt_range_report(path_to_json):
    with open(path_to_json, "r") as j:
        loaded = json.load(j)
        table = texttable.Texttable()
        table_cols = ["url domain name", "RTT range"]
        col_h_alignment = ["c", 'c']
        col_v_alignment = ['m', 'm']
        col_widths = [len("url domain name"), len('RTT range')]

        table.set_cols_align(col_h_alignment)
        table.set_cols_valign(col_v_alignment)
        table.set_cols_width(col_widths)
        table.add_row(table_cols)

        tuple_url_to_rtt_map = []
        for url in loaded:
            url_obj = loaded[url]
            if 'rtt_range' in url_obj.keys():
                tuple_url_to_rtt_map.append((url, url_obj['rtt_range']))
        
        min_to_max_url_rtts = sorted(tuple_url_to_rtt_map, key=cmp_to_key(rtt_comparator))
        for url in min_to_max_url_rtts:
            # rtt range will only be two nums so this can be hard coded
            rtt_range = str(url[1][0]) + " - " + str(url[1][1])
            table.add_row([url[0], rtt_range])
        
        return table.draw()

def ca_comparator(tuple1, tuple2):
    count1 = tuple1[1]
    count2 = tuple2[1]
    if count1 > count2:
        return -1
    elif count1 < count2:
        return 1
    else:
        return 0

def generate_root_ca_report(path_to_json):
    with open(path_to_json, "r") as j:
        loaded = json.load(j)
        table = texttable.Texttable()
        table_cols = ["Certificate Authority", "occurences", "used for"]
        col_h_alignment = ["c", 'c', 'c']
        col_v_alignment = ['m', 'm', 'm']
        col_widths = [len("Certificate Authority"), len('occurences'), len("www.vicious.cs.northwestern.edu")]

        table.set_cols_align(col_h_alignment)
        table.set_cols_valign(col_v_alignment)
        table.set_cols_width(col_widths)
        table.add_row(table_cols)

        # ca pop dict will map {'CA NAME' : [count, [list, of, urls]]}
        ca_popularity_dict = {}

        for url in loaded:
            url_dict = loaded[url]
            if 'root_ca' in url_dict:
                root_ca = url_dict['root_ca']
                if root_ca in ca_popularity_dict:
                    ca_popularity_dict[root_ca][0] += 1
                    ca_popularity_dict[root_ca][1].append(url)
                else:
                    ca_popularity_dict[root_ca] = [1, [url]]
        
        # SOOO unnecessarily messy complexity wise but its late....
        # sorting_list = [(cert_auth, count)]
        sorting_list = []
        for ca in  ca_popularity_dict:
            count = ca_popularity_dict[ca][0]
            sorting_list.append((ca, count))
        
        sorted_list = sorted(sorting_list, key=cmp_to_key(ca_comparator))
        for pair in sorted_list:
            ca = pair[0]
            pop_vals = ca_popularity_dict[ca]
            row = [ca, pop_vals[0], "\n".join(pop_vals[1])]
            table.add_row(row)

        return table.draw()

def generate_server_report(path_to_json):
    with open(path_to_json, "r") as j:
        loaded = json.load(j)
        table = texttable.Texttable()
        table_cols = ["Server Type", "occurences", "used for"]
        col_h_alignment = ["c", 'c', 'c']
        col_v_alignment = ['m', 'm', 'm']
        col_widths = [len("Server Type"), len('occurences'), len("www.vicious.cs.northwestern.edu")]

        table.set_cols_align(col_h_alignment)
        table.set_cols_valign(col_v_alignment)
        table.set_cols_width(col_widths)
        table.add_row(table_cols)

        # ca pop dict will map {'CA NAME' : [count, [list, of, urls]]}
        server_popularity_dict = {}

        for url in loaded:
            url_dict = loaded[url]
            if 'http_server' in url_dict:
                server = url_dict['http_server']
                if server in server_popularity_dict:
                    server_popularity_dict[server][0] += 1
                    server_popularity_dict[server][1].append(url)
                else:
                    server_popularity_dict[server] = [1, [url]]
        
        # SOOO unnecessarily messy complexity wise but its late....
        # sorting_list = [(cert_auth, count)]
        sorting_list = []
        for s in  server_popularity_dict:
            count = server_popularity_dict[s][0]
            sorting_list.append((s, count))
        
        sorted_list = sorted(sorting_list, key=cmp_to_key(ca_comparator))

        for pair in sorted_list:
            s = pair[0]
            pop_vals = server_popularity_dict[s]
            row = [s, pop_vals[0], "\n".join(pop_vals[1])]
            table.add_row(row)

        return table.draw()

def generate_percentage_report(path_to_json):
    """SSLv2 (obsolete)
        SSLv3 (obsolete)
        TLSv1.0
        TLSv1.1
        TLSv1.2
        TLSv1.3"""
    with open(path_to_json, "r") as j:
        loaded = json.load(j)
        table = texttable.Texttable()
        table_cols = ["SSLv2", "SSLv3", "TLSv1.0", "TLSv1.2", "TLSv1.3", "insecure http", "redirects", "hsts", "ipv6"]
        col_h_alignment = ["c", 'c', 'c', "c", 'c', 'c', "c", 'c', 'c']
        col_v_alignment = ['m', 'm', 'm', 'm', 'm', 'm', 'm', 'm', 'm']
        col_widths = [12, 12, 12, 12, 12, 12, 12, 12, 12]

        table.set_cols_align(col_h_alignment)
        table.set_cols_valign(col_v_alignment)
        table.set_cols_width(col_widths)
        table.add_row(table_cols)

        counters = {"SSLv2": 0, "SSLv3": 0, "TLSv1.0": 0, "TLSv1.2": 0, "TLSv1.3": 0, "insecure http": 0, "redirects": 0, "hsts": 0, "ipv6": 0}

        total_urls = len(loaded)

        for url in loaded:
            url_dict = loaded[url]

            # GET TLS VERSIONS COUNT
            tls_types = url_dict['tls_versions']
            if tls_types:
                for tls in tls_types:
                    if tls in counters:
                        counters[tls] += 1
            
            # GET INSECURE HTTP COUNT
            http = url_dict['insecure_http']
            if http:
                counters["insecure http"] += 1

            # GET REDIRECTERS COUNT
            redirects = url_dict['redirect_to_https']
            if redirects:
                counters["redirects"] += 1
            
            # GET HSTS COUNT
            hsts = url_dict['hsts']
            if hsts:
                counters['hsts'] += 1

            # GET IPV6 COUNTER
            ipv6 = url_dict['ipv6_addresses']
            if len(ipv6) > 0:
                counters['ipv6'] += 1
        
        row = []
        for count in counters:
            val = float(counters[count])
            total = float(total_urls)
            percentage = round(((val / total) * 100), 2)
            row.append(str(percentage) + "%")
        
        table.add_row(row)
        return table.draw()

def generate(path_to_json):

    report = ""
    report += generate_report_body(path_to_json) + "\n\n"
    report += generate_rtt_range_report(path_to_json) + "\n\n"
    report += generate_root_ca_report(path_to_json) + "\n\n"
    report += generate_server_report(path_to_json) + "\n\n"
    report += generate_percentage_report(path_to_json)
    return report

input_json_file = sys.argv[1]
output_txt_file = sys.argv[2]


with open(output_txt_file, "w") as output:
    output.write(generate(input_json_file))




