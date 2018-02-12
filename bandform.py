#!/usr/local/bin/python3

'''
Author: Kevin Kou

The "Band Form Autofill Bot" is a script that
autofills the band form with the necessary
inputs, and submits them for that dank Under Armour gear.

This script is reliant on the fact that there are exactly 5 inputs.
This script does not work against captchas.
This script will need to change if there are added/changed inputs.

FOR EDUCATIONAL PURPOSES ONLY, DON'T BE MEAN
'''

import re
import signal
from getpass import getpass
import urllib.request as u
import threading
import sys
import imaplib
import time
from datetime import datetime
import requests

class EmailBot(threading.Thread):
    '''Email bot thread. Where the fun stuff happens.'''
    def __init__(self, username, password):
        super(EmailBot, self).__init__()
        self._stop_event = threading.Event()
        self.imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)

        ###Your information (FILL THIS OUT CAREFULLY)###
        self.first_name = "Kevin"
        self.last_name = "Kou"
        self.instrument = "G2 (Trombone 2)"
        self.year_in_band = "3"
        self.comments = ""

        #initialize some values for efficiency sake
        self.submission = {}
        self.submission['fvv'] = '1'
        self.submission['pageHistory'] = '0'

        self.login(username, password)
    
    def stop(self):
        '''Stop the email bot thread.
        Closes your inbox and logs you out.'''
        self.imap.close()
        self.imap.logout()
        self._stop_event.set()

    def stopped(self):
        '''Checks if the email bot has the stop flag enabled.'''
        return self._stop_event.is_set()

    def login(self, username, password):
        '''Attempts login for email address, program exits if failed.'''
        try:
            retcode, capabilities = self.imap.login(username, password)
            print(capabilities[0].decode("utf-8"))
            self.imap.select("Inbox")
            signal.signal(signal.SIGINT, self.sighandler)
            print("Begin scanning...")
        except:
            print(sys.exc_info()[1])
            sys.exit(1)

    def sighandler(self, signum, frame):
        '''In case someone does CTRL+C instead of press ENTER/RETURN, ends the session'''
        print("I said PRESS ENTER/RETURN, NOT CTRL+C, but whatever I'll still end your session")
        print("Stopping email session...")
        self.stop()
        print("Have a nice day!")
        sys.exit(0)

    def check_email(self):
        '''Checks your email and hunts for the Google Form link if
        an email from Ken Fisher is found.'''
        retcode, messages = self.imap.search(None, '(UNSEEN)')
        if retcode == 'OK':
            for num in messages[0].split():
                typ, data = self.imap.fetch(num, '(RFC822)')
                msg = data[0][1].decode("utf-8").replace('\r\n', '')
                if 'Ken Fisher' in msg and 'Armour' in msg:
                    starttime = datetime.now()
                    title = re.search('Subject: .* CallM', msg)
                    if title != None:
                        print("Message found, processing %s", title.group()[:-1])
                        url = re.search('<https:\/\/docs.google.com\/forms\/.*sf_link>', msg)
                        if url != None:
                            url = url.group()[1:-1]
                            url = re.sub('\?.*', '', url)
                            url = url.replace('=', '')
                            self.submit_form(url=url)
                            typ, data = self.imap.store(num, '+FLAGS', '\\Seen')
                    print("Took %s seconds to process the email" % (datetime.now() - starttime))

    def submit_form(self, url):
        '''Submits the form to the given url.'''
        #initialize the structs and get the form
        url_response = re.sub('viewform.*', 'formResponse', url)
        page = u.urlopen(url)
        page_text = page.read().decode("utf-8")
        your_info = {}
        entrylist = []

        #finding the order of the inputs
        your_info[re.search('Instrument', page_text).start(0)] = self.instrument
        your_info[re.search('Last Name', page_text).start(0)] = self.last_name
        your_info[re.search('First Name', page_text).start(0)] = self.first_name
        your_info[re.search('Year in Band', page_text).start(0)] = self.year_in_band
        your_info[re.search('Comments', page_text).start(0)] = self.comments

        #Finding Google Form entries from the form
        for match in re.finditer('entry\.[0-9-]*', page_text):
            entrylist.append(match.group())

        #Building POST request
        index = 0
        for key in sorted(your_info):
            self.submission[entrylist[index]] = your_info[key]
            index += 1

        #metadata
        fbzx_substring = re.search('\"fbzx\" value=\"[0-9-]*\"', page_text).group()
        fbzx_value = re.search('[0-9-]+', fbzx_substring).group()
        fbzx_value_quotes = '"' + fbzx_value + '"'

        self.submission['draftResponse'] = [None, None, fbzx_value_quotes]
        self.submission['fbzx'] = fbzx_value

        url_refer = re.sub('viewform.*', 'viewform\\?fbzx=', url) + fbzx_value
        user_agent = {'Referer': url_refer, 'User-Agent': "Mozilla/5.0 \
        (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/62.0.3202.62 Safari/537.36"}

        response = requests.post(url_response, data=self.submission, headers=user_agent)
        print("Form submitted")
        
    def run(self):
        '''Event loop for the email bot.
        While the bot isn't stopped, it will check your email every second.'''
        while True:
            if self.stopped():
                break
            self.check_email()
            time.sleep(2)

def main():
    '''The main method.
    Asks for your email account information and does the fun stuff.'''
    username = input("Gmail username: ")
    password = getpass()
    e = EmailBot(username, password)
    e.start()
    input("Press ENTER or RETURN at any time to stop the email bot\n")
    print("Stopping email session...")
    e.stop()
    print("Have a nice day!")

if __name__ == '__main__':
    main()