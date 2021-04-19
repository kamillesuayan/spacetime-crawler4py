import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import tokenizer as tkn

links_visited = set()

def scraper(url, resp):
    # do something with resp
    if resp.status == 200:
        links_visited.add(url)
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        # print("TEXT ON THE WEBPAGE:", soup.get_text()) # to get the text on a webpage
        tkns = tkn.tokenize(soup.get_text())
        if len(tkns) >= 200:
            print(len(tkns))
            links = extract_next_links(url, resp)
            return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # do something with resp
    
    urls = []
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.find_all('a'): # gets all the links that are on the webpage
        urls.append(link.get('href'))
    return urls

def is_valid(url):
    # change to check for base urls
    # come back later: fix parsed.netloc
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # something.ics.uci.edu
        #today.uci.edu/department/information_computer_sciences/*
        if re.match(r'today.uci.edu', parsed.netloc) and re.match(r'/department/information_computer_sciences/*', parsed.path):
            print("parsed:",parsed)
        if not (re.search(".ics.uci.edu", parsed.netloc) or 
           re.match(r'today.uci.edu/department/information_computer_sciences/*', parsed.netloc)):
            return False
           # re.search(".cs.uci.edu", parsed.netloc) or 
           # re.search(".informatics.uci.edu", parsed.netloc) or 
           # re.search(".stat.uci.edu", parsed.netloc) or 
        if (re.search("share=",parsed.query)) or (re.search("/page",parsed.path)) or (re.search("page_id=",parsed.query)):
            return False
            #return False
        # print("parsed:", parsed)
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise