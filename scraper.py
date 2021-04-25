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

# for simhash
def get_features(s):
    width = 4
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]

objs = dict()
index = SimhashIndex(objs, k=6) # create index

def scraper(url, resp):
    # do something with resp
    if resp.status >= 200 and resp.status <= 202 and (url not in links_visited):
        reqs = requests.get(url,timeout=60)
        parsed = urlparse(url)
        if parsed.fragment != None and parsed.fragment != "":
            url = urldefrag(url)[0] # defragments the URL that is the parameter

        links_visited.add(url)
        
        soup = BeautifulSoup(reqs.text, 'html.parser')
        wrds = soup.get_text()
        
        crawler.len_info.write(f"{url}\n")

        # 1. for unique URLs
        crawler.unique_URLs.add(url)
        tkns = tkn.tokenize(wrds, stp_wrds)

        if len(tkns) >= 200 and len(tkns) <= 50000:
            s1 = Simhash(get_features(wrds))
            if len(index.get_near_dups(s1)) > 2:
                links_visited.add(url)
                return
            index.add(len(links_visited), s1)
            
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

            links_visited.add(url)
            links = extract_next_links(url, resp)
            # print("     Links Visited Length:", len(links_visited))
            # print("     Unique Links:", len(crawler.unique_URLs))
            return [link for link in links if is_valid(link)]
    links_visited.add(url)
    return

def extract_next_links(url, resp):
    # parsed = urlparse(url)
    urls = []
    reqs = requests.get(url,timeout=60)
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
           re.match(r'today.uci.edu/department/information_computer_sciences/*', parsed.netloc + parsed.path)):
            return False
        
        if (parsed.netloc != "ics.uci.edu") and (not re.search("community/news",parsed.path)) and (parsed.query != ''):
            return False
        
        if (re.search("/events",parsed.path)) or (re.search("zip-attachment",parsed.path)):
            return False
            
        return (not  (re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|lsp|pov|mov|svg|ss"
            + r"|png|tiff?|mid|mp2|mp3|mp4|m|py|hqx|nb|sh|war|scm"
            + r"|wav|avi|move|mpeg|ram|m4v|mkv|ogg|ogv|pdf|conf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|class"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|fig"
            + r"|epub|dll|cnf|tgz|sha1|odc|r|sql|java|ff|bib|info"
            + r"|thmx|mso|arff|rtf|jar|csv|bam|ipynb|pps|c|cls"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|z|ma)$", parsed.path.lower())) 
           )

    except TypeError:
        print ("TypeError for ", parsed)
        raise