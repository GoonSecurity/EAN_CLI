#!/usr/bin/python3
import re
import requests
import argparse
from bs4 import BeautifulSoup
from termcolor import colored
from urllib.parse import urljoin

import analysis



#parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--tld')
parser.add_argument('-u', '--url')
parser.add_argument('-m', '--max', default=False)
args, domains = parser.parse_known_args()


url = args.url
tld = args.tld
maximum_tokens = args.max


def get_all_scripts(url):
	try:
		source = requests.get(url, allow_redirects=True, timeout=5).text
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
	        initial_script_links.append(script_url)



	#search found scripts for more javascript files
	for script_link in initial_script_links:
		#print(script_link)

		try:
			content = requests.get(script_link, timeout=5).text
		except:
			continue

		if script_link not in all_script_links:
			all_script_links[script_link] = {'requested': True, 'content': content}


		#this will part of a parser for specific frontends, this is just a taste
		if "require.config" in content:
			base_path = "/".join(script_link.split("/")[:-1])

			for match in re.findall("\'\/(.*?)\'", content):
				url = urljoin(base_path, match) + ".js"
				
				if url not in all_script_links:
					all_script_links[url] = {'requested': False, 'content': content}

	return all_script_links






def get_all_tokens(url):
	all_tokens = []
	token_data = []
	print("Starting... {}".format(url))
	#parse script files for tokens
	script_links = get_all_scripts(url)

	for script_link in script_links:
		if not tld in script_link: continue
		print(script_link)

		#get all script data
		script_data = script_links[script_link]
		if script_data['requested'] == False:
			content = requests.get(script_link, timeout=3).text

			script_data['requested'] == True
			script_data['content'] == content

		tokens = analysis.string_analysis(script_data['content'])


		#add unique tokens to main list
		for token in tokens:
			if token not in all_tokens: 
				all_tokens.append(token)
				token_data.append({'url': script_link, 'token': token, 'source': script_data['content']})

	return token_data



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
