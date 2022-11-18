#!/usr/bin/python3
import sys
import re
import requests
import argparse
import threading
import time
from bs4 import BeautifulSoup
from termcolor import colored
from urllib.parse import urljoin
import analysis
import warnings

#parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--tld')
parser.add_argument('-u', '--url')
parser.add_argument('-l', '--threads')
parser.add_argument('-n', '--maxcrawl')
parser.add_argument('-m', '--max', default=False)
args, domains = parser.parse_known_args()

if not args.url or not args.tld:
 print("URL (-u) and domain (-t) are required!")
 sys.exit(0)
threadnum = 5
if args.threads:
 threadnum = int(args.threads)
url = args.url
tld = args.tld
maximum_tokens = args.max
max_url_crawl_count = 25
if args.maxcrawl:
 max_url_crawl_count = int(args.maxcrawl)
debug_mode = 0

if debug_mode == 0:
 warnings.filterwarnings("ignore")

all_scripts_url_found = []
all_global_tokens = []

def get_all_scripts(url):
 global all_scripts_url_found

 sess = requests.Session()
 try:
  source = sess.get(url, allow_redirects=True, timeout=5).text
  #print(source)
 except:
  return []

 soup = BeautifulSoup(source, "html.parser")
 #print(soup)

 all_script_links = {}
 initial_script_links = []

 #get script links in homepage
 for script in soup.find_all("script"):
  if script.attrs.get("src"):
   #print(script.attrs.get("src"))
   #if the tag has the attribute 'src'
   script_url = urljoin(url, script.attrs.get("src"))
   if not script_url in all_scripts_url_found:
    initial_script_links.append(script_url)
    with threading.Lock(): all_scripts_url_found.append(script_url)


 #search found scripts for more javascript files
 for script_link in initial_script_links:
  #print(script_link)
  try:
   content = sess.get(script_link, timeout=5).text
  except:
   continue
 
  if script_link not in all_script_links:
   all_script_links[script_link] = {'requested': True, 'content': content}
  #this will part of a parser for specific frontends, this is just a taste

  if "require.config" in content:
   base_path = "/".join(script_link.split("/")[:-1])
   for match in re.findall("\'\/(.*?)\'", content):
    url = urljoin(base_path, match) + ".js"
    if url not in all_script_links and url not in all_scripts_url_found:
     all_script_links[url] = {'requested': False, 'content': content}
     with threading.Lock(): all_scripts_url_found.append(url)

 return all_script_links


def get_all_tokens(url):
 global all_global_tokens
 all_tokens = []
 token_data = []
 if debug_mode == 1: print("Starting... {}".format(url))
 #parse script files for tokens
 script_links = get_all_scripts(url)

 for script_link in script_links:
  if not tld in script_link: continue
  #print(script_link)

  #get all script data
  script_data = script_links[script_link]
  if script_data['requested'] == False:
   content = requests.get(script_link, timeout=3).text

   script_data['requested'] == True
   script_data['content'] == content

  tokens = analysis.string_analysis(script_data['content'])


  #add unique tokens to main list
  for token in tokens:
   if token not in all_tokens and token not in all_global_tokens: 
    all_tokens.append(token)
    with threading.Lock(): all_global_tokens.append(token)
    token_data.append({'url': script_link, 'token': token, 'source': script_data['content']})

 return token_data

def get_tokens_local(url):
 token_data = get_all_tokens(url)

 for data in token_data: 

  token = data['token']
  url   = data['url']
 
  content_parts = data['source'].split(token)

  first_slice = content_parts[0][-500:]
  last_slice  = content_parts[1][:500]
  print('\n')
  print(colored(url, 'magenta') + "\n")
  print(first_slice + colored(token, 'red', attrs=["bold"]) + last_slice)
  print('\n\n\n')

urls_crawled = []

def crawl(urllocal, depth=1):
 global urls_crawled
 try:
  if debug_mode == 1: print("Crawling: {}".format(urllocal))
  if depth >= 2: return
  urllist = []
  get_tokens_local(urllocal)
  s = requests.Session()
  r = s.get(url=urllocal, allow_redirects=True, timeout=5)
  soup = BeautifulSoup(r.text, "html.parser")
  urllist = soup.find_all("a")
 except Exception as error:
  if debug_mode == 1: print(error)
  return
 urlcountfound = 0
 for url_list_piece in urllist:
  try:
   urlcountfound += 1
   if urlcountfound >= max_url_crawl_count: break
   url_list_piece = url_list_piece.attrs.get("href")
   url_list_piece = urljoin(urllocal, url_list_piece)
   if debug_mode == 1: print(url_list_piece)
   if not url_list_piece in urls_crawled and tld in url_list_piece:
    with threading.Lock(): urls_crawled.append(url_list_piece)
    while threading.active_count() > threadnum: time.sleep(1)
    t=threading.Thread(target=crawl, args=(urllocal, depth+1))
    t.start()
  except Exception as error:
   if debug_mode == 1: print(error)

crawl(url)
