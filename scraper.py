import re
from urllib.parse import urlparse,urldefrag
import urllib
import requests
from bs4 import BeautifulSoup
import tokenizer as tkn
import crawler
import re
from simhash import Simhash, SimhashIndex

links_visited = set()

def stop_word():
    file = open('stop.txt', 'r')
    words = []
    for line in file:
        words.append(line.strip('\n'))
    file.close()
    return words

stp_wrds = stop_word()

def get_features(s):
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]

objs = dict()
index = SimhashIndex(objs, k=10) # create index

def scraper(url, resp):
    # do something with resp
    if resp.status >= 200 and resp.status <= 202 and (url not in links_visited):
        reqs = requests.get(url,timeout=15)
        parsed = urlparse(url)
        if parsed.fragment != None and parsed.fragment != "":
            url = urldefrag(url)[0] # defragments the URL that is the parameter
            # print("AHAHA: ", url)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        wrds = soup.get_text()
        
        if url in crawler.unique_URLs:
            return

        # 1. for unique URLs
        crawler.unique_URLs.add(url)
        if len(wrds.split()) < 200 or len(wrds.split()) > 50000:
            return
        
        tkns = tkn.tokenize(wrds, stp_wrds)

        if len(tkns) >= 200 and len(tkns) <= 50000:
            s1 = Simhash(get_features(wrds))
            if len(index.get_near_dups(s1)) > 1:
                print(url,len(index.get_near_dups(s1)))
                return
            index.add(len(crawler.unique_URLs), s1)
            crawler.len_info.write(f"{len(tkns)}\n")
            # 2. keep track of longest page in terms of words
            if crawler.longest[0] < len(tkns):
                crawler.longest[0] = len(tkns)
                crawler.longest[1] = url
            
            # 3. 50 most common
            tkn.computeWordFreq(tkns, crawler.most_common)

            # 4. how many .ics.uci.edu subdomains
            
            if re.search("\.ics.uci.edu", parsed.netloc):
                if re.match("www.",parsed.netloc):
                    new_url = parsed.netloc.strip("www.")
                else:
                    new_url = parsed.netloc
                if new_url not in crawler.subdomains:
                    crawler.subdomains[new_url] = 1
                else:
                    crawler.subdomains[new_url] += 1

            links = extract_next_links(url, resp)
            return [link for link in links if is_valid(link)]
    return

def extract_next_links(url, resp):
    # parsed = urlparse(url)
    urls = []
    reqs = requests.get(url,timeout=15)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    # base = "https://" + parsed.netloc
    for link in soup.find_all('a'): # gets all the links that are on the webpage
        pulled = link.get('href')
        parsed_pulled = urlparse(pulled)
        new_url = urllib.parse.urljoin(url,pulled)
        urls.append(new_url) # we made it through with no redirects!
    return urls

def is_valid(url):
    # change to check for base urls
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        if parsed.fragment != None and parsed.fragment != "":
            return False
            # url = urldefrag(url)[0] # defragments the URL that is the parameter

        if not (re.search("\.ics.uci.edu", parsed.netloc) or re.search("\.cs.uci.edu", parsed.netloc) or 
            re.search("\.informatics.uci.edu", parsed.netloc) or re.search("\.stat.uci.edu", parsed.netloc) or
           re.match(r'today.uci.edu/department/information_computer_sciences/*', parsed.netloc)):
            return False

        if (parsed.netloc != "ics.uci.edu") and (not re.search("community/news",parsed.path)) and (parsed.query != ''):
            return False
        
        if (re.search("/events",parsed.path)) or (re.search("zip-attachment",parsed.path)):
            return False
            
        return (not  (re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|move|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|odc|r|sql|java"
            + r"|thmx|mso|arff|rtf|jar|csv|bam|ipynb"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|z)$", parsed.path.lower())) 
           )

    except TypeError:
        print ("TypeError for ", parsed)
        raise