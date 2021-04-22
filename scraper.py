import re
from urllib.parse import urlparse,urldefrag
import requests
from bs4 import BeautifulSoup
import tokenizer as tkn
import crawler

links_visited = set()

def stop_word():
    file = open('stop.txt', 'r')
    words = []
    for line in file:
        words.append(line.strip('\n'))
    file.close()
    return words

stp_wrds = stop_word()

def scraper(url, resp):
    # do something with resp
    if resp.status == 200:
        reqs = requests.get(url)
        parsed = urlparse(url)
        if parsed.fragment != None and parsed.fragment != "":
            url = urldefrag(url)[0] # defragments the URL that is the parameter
            # print("AHAHA: ", url)

        links_visited.add(url)
        
        soup = BeautifulSoup(reqs.text, 'html.parser')
        # 1. for unique URLs
        wrds = soup.get_text()

        crawler.unique_URLs.add(url)
        if len(wrds.split()) < 200 or len(wrds.split()) > 50000:
            return
        
        tkns = tkn.tokenize(wrds, stp_wrds)
        if len(tkns) >= 200 and len(tkns) <= 50000:
            
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

def extract_next_links(url, resp):
    # do something with resp
    parsed = urlparse(url)
    urls = []
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.find_all('a'): # gets all the links that are on the webpage
        pulled = link.get('href')
        if pulled[0] == '/': # path on website
            new_url = "https://" + parsed.netloc
            urls.append(urldefrag(new_url)[0])
        else:
            urls.append(pulled)


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
        
        # for traps
        # if (re.search("mt-live",parsed.netloc)) and (parsed.query != None or parsed.query != ""):
        #     return False
        
        if (re.search("replytocom=",parsed.query)) or (re.search("share=",parsed.query)) or (re.search("/page/",parsed.path)) or (re.search("/events",parsed.path)) or (re.search("page_id=",parsed.query)):
            return False
        return (not  (re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|move|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|z)$", parsed.path.lower())) 
            and not (re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|move|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|z)$", parsed.query.lower())))

    except TypeError:
        print ("TypeError for ", parsed)
        raise