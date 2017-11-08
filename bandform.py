#!/usr/local/bin/python3

'''
Author: Kevin Kou

The "Band Form Autofill Script" is a script that
autofills the band form with the necessary
inputs, and submits them for that dank Under Armour gear.

This script is reliant on the fact that there are exactly 5 inputs.
This script does not work against captchas.
This script will need to change if there are added/changed inputs.

FOR EDUCATIONAL PURPOSES ONLY, DON'T BE MEAN
'''

import re
import os
from getpass import getpass
import urllib.request as u
import threading
import sys
import signal
import requests
import imaplib
import email
import time
from datetime import datetime

#Email bot thread
class EmailBot(threading.Thread):
    def __init__(self, username, password):
        super(EmailBot, self).__init__()
        self._stop_event = threading.Event()
        self.imap = imaplib.IMAP4_SSL('imap.gmail.com',993)

        ###Your information (FILL THIS OUT CAREFULLY)###
        self.FIRSTNAME = "Kevin"
        self.LASTNAME = "Kou"
        self.INSTRUMENT = "G2 (Trombone 2)"
        self.YEARINBAND = "3"
        self.COMMENTS = ""

        #initialize some values for efficiency sake
        self.submission = {}
        self.submission['fvv'] = '1'
        self.submission['pageHistory'] = '0'

        self.login(username, password)
    
    #stop the email bot thread
    def stop(self):
        self.imap.close()
        self.imap.logout()
        print("Logged out of session")
        self._stop_event.set()

    #checks if the email bot has the stop flag
    def stopped(self):
        return self._stop_event.is_set()

    #attempts login for email address, program exits if failed
    def login(self, username, password):
        try:
            retcode, capabilities = self.imap.login(username, password)
            print(capabilities)
            self.imap.select("Inbox")
            self.checkEmail()
        except:
            print(sys.exc_info()[1])
            sys.exit(1)

    #checks your email every X seconds (specified by the interval)
    def checkEmail(self):
       retcode, messages = self.imap.search(None, '(UNSEEN)')
       if retcode == 'OK':
            for num in messages[0].split():
                typ, data = self.imap.fetch(num,'(RFC822)')
                msg = data[0][1].decode("utf-8").replace('\r\n', '')
                if 'Ken Fisher' in msg:
                    print("Message found, processing %s", re.search('Subject: .* CallM', \
                    msg).group()[:-1])
                    url = re.search('<https:\/\/docs.google.com\/forms\/.*sf_link>', msg).group()[1:-1]
                    url = re.sub('\?.*', '', url)
                    url = url.replace('=', '')
                    print(url)
                    self.submitForm(url=url)
                    typ, data = self.imap.store(data[0].replace(' ',','),'+FLAGS','\Seen')

    #submits the form to said url
    def submitForm(self, url):
        #initialize the structs and get the form
        starttime = datetime.now()
        url_response = re.sub('viewform.*', 'formResponse', url)
        page = u.urlopen(url)
        page_text = page.read().decode("utf-8")
        your_info = {}
        entrylist = []

        #finding the order of the inputs
        instrument_pos = re.search('Instrument', page_text).start(0)
        lastname_pos = re.search('Last Name', page_text).start(0)
        firstname_pos = re.search('First Name', page_text).start(0)
        yearinband_pos = re.search('Year in Band', page_text).start(0)
        comments_pos = re.search('Comments', page_text).start(0)

        your_info[instrument_pos] = self.INSTRUMENT
        your_info[lastname_pos] = self.LASTNAME
        your_info[firstname_pos] = self.FIRSTNAME
        your_info[yearinband_pos] = self.YEARINBAND
        your_info[comments_pos] = self.COMMENTS

        #Finding Google Form entries from the form
        for m in re.finditer('entry\.[0-9-]*', page_text):
            entrylist.append(m.group())

        #Building POST request
        i = 0
        for key in sorted(your_info):
            self.submission[entrylist[i]] = your_info[key]
            i += 1

        #metadata
        fbzx_substring = re.search('\"fbzx\" value=\"[0-9-]*\"', page_text).group()
        fbzx_value = re.search('[0-9-]+', fbzx_substring).group()
        fbzx_value_quotes = '"' + fbzx_value + '"'

        self.submission['draftResponse'] = [None,None,fbzx_value_quotes]
        self.submission['fbzx'] = fbzx_value

        url_refer = re.sub('viewform.*', 'viewform\?fbzx=', url) + fbzx_value
        user_agent = {'Referer': url_refer, 'User-Agent': "Mozilla/5.0 \
        (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/62.0.3202.62 Safari/537.36"}

        response = requests.post(url_response, data=self.submission, headers=user_agent)
        print("Took %s seconds to submit the form" % (datetime.now() - starttime))

    #loop for the email bot
    def run(self):
        while True:
            if (self.stopped()):
                break
            self.checkEmail()
            time.sleep(3)

#main method
def main():
    username = input("Gmail username: ")
    password = getpass()
    e = EmailBot(username, password)
    e.start()
    str = input("Press enter at any time to stop the email bot\n")
    e.stop()

if __name__ == '__main__':
    main()