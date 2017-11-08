#!/usr/local/bin/python3

'''
Author: Kevin Kou

The "Band Form Autofill Script" is a script that
autofills the band form with the necessary
inputs, and submits them for that dank Under Armour gear.

Requires the band form link.

This script is reliant on the fact that there are exactly 5 inputs.
This script does not work against captchas.
This script will need to change if there are added/changed inputs.

FOR EDUCATIONAL PURPOSES ONLY, DON'T BE MEAN
'''

import re
import urllib.request as u
import sys
import requests
from datetime import datetime

if len(sys.argv) != 2:
    print('Usage: ./bandform.py <LINK> \nor\npython3 bandform.py <LINK>\n')
    exit(2)

#initialize the structs and get the form
starttime = datetime.now()
url = sys.argv[1]
url_formresponse = re.sub('viewform.*', 'formResponse', url)
page = u.urlopen(url)
page_text = page.read().decode("utf-8")
submission = {}
your_info = {}
entrylist = []

#finding the order of the inputs
instrument_pos = re.search('Instrument', page_text).start(0)
lastname_pos = re.search('Last Name', page_text).start(0)
firstname_pos = re.search('First Name', page_text).start(0)
yearinband_pos = re.search('Year in Band', page_text).start(0)
comments_pos = re.search('Comments', page_text).start(0)

###Your information (FILL THIS OUT CAREFULLY)###
#Your instrument code
your_info[instrument_pos] = "G2 (Trombone 2)"
#Your last name
your_info[lastname_pos] = "Kou"
#Your first name
your_info[firstname_pos] = "Kevin"
#Your year in band
your_info[yearinband_pos] = "3"
#Comments
your_info[comments_pos] = ""

#Finding Google Form entries from the form
for m in re.finditer('entry\.[0-9-]*', page_text):
    entrylist.append(m.group())

#Building POST request
i = 0
for key in sorted(your_info):
    submission[entrylist[i]] = your_info[key]
    i += 1

#metadata
fbzx_substring = re.search('\"fbzx\" value=\"[0-9-]*\"', page_text).group()
fbzx_value = re.search('[0-9-]+', fbzx_substring).group()
fbzx_value_quotes = '"' + fbzx_value + '"'
submission['draftResponse'] = [None,None,fbzx_value_quotes]
submission['fbzx'] = fbzx_value
submission['fvv'] = '1'
submission['pageHistory'] = '0'
url_refer = re.sub('viewform.*', 'viewform\?fbzx=', url) + fbzx_value
user_agent = {'Referer': url_refer, 'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"}

#Debugging info
print("Your form response:\n\n%s\n" % submission)

response = requests.post(url_formresponse, data=submission, headers=user_agent)

#Debugging info
print("Submitted using url %s\n\nResponse from Google: %s\n" % (response.url, response))
print("Took %s seconds" % (datetime.now() - starttime))