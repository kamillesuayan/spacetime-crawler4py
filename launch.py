from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
# from crawler import Crawler 
from crawler import * 
import tokenizer as tk

def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart) # this function is in server_registration.py
    crawler = Crawler(config, restart)
    crawler.start()

    # ANSWERS
    rprt = open("report.txt","w")

    print("HERE ARE THE ANSWERS TO THE QUESTIONS FOR ASSIGNMENT 2 --------------------------------------")
    # 1. unique pages
    print("     NUMBER OF UNIQUE PAGES:", len(unique_URLs)) # the set should only contain unique URLs
    #u_page = "NUMBER OF UNIQUE PAGES:" + str(len(unique_URLs)) + "\n"
    rprt.write(f"NUMBER OF UNIQUE PAGES {len(unique_URLs)}\n")

    # 2. longest page
    print("     LONGEST PAGE:", longest[1]) 
    print("     LONGEST PAGE LENGTH:", longest[0]) # page length
    rprt.write(f"LONGEST PAGE {longest[1]}\n")
    rprt.write(f"LONGEST PAGE LENGTH {longest[0]}\n")

    # 3. 50 most common words
    print("     MOST COMMON WORDS:", tk.freqs(most_common)[0:50]) # 
    rprt.write(f"MOST COMMON WORDS: {tk.freqs(most_common)[0:50]} \n")
    

    # 4. subdomains
    sorted_subdomains = sorted(subdomains)
    print("     SUBDOMAINS FOR ICS.UCI.EDU:", sorted_subdomains)
    for url in sorted_subdomains:
        rprt.write(f"{url}, {subdomains[url]}\n")
    # rprt.writelines(sorted_subdomains)
    
    rprt.close() # make sure to close the file!
    len_info.close()
    

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)

    
