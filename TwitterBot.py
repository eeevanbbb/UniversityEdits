#!/usr/bin/python2.7
import websocket
import thread
import time
import json
from netaddr import IPNetwork, IPAddress
import tweepy

ipranges = {}
pages = []
handles = {}

with open('ipranges.txt') as f:
	lines = f.readlines()
	for line in lines:
		parts = line.split(" : ")
		name = parts[0].decode('utf-8')
		part2 = parts[1].strip("\n")
		ranges = part2.split(", ")		
		ipranges[name] = ranges
		
with open('wikipages.txt') as f:
	lines = f.readlines()
	for line in lines:
		parts = line.split(" : ")
		if len(parts) == 2:
			page = parts[0].decode('utf-8')
			handle = parts[1].strip("\n")
			pages.append(page)
			if len(handle) > 0:
				handles[page] = handle
		else:
			decoded = line.decode('utf-8')
			stripped = decoded.strip("\n")
			pages.append(stripped)
	
print ipranges
print pages
print handles

CONSUMER_KEY = 'REDACTED'
CONSUMER_SECRET = 'REDACTED'
ACCESS_KEY = 'REDACTED'
ACCESS_SECRET = 'REDACTED'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

def sendTweet(page,networkname,url):
	tweet = ""
	if (page == networkname):
		tweet = networkname + " anonymously edited its own Wikipedia page: " + url
	else:
		tweet = networkname + " anonymously edited the Wikipedia page for " + page + ": " + url
	api.update_status(tweet)
	
def tweetAt(page,networkname,url):
	if (page != networkname and handles[page]):
		editor = networkname
		if handles[networkname]:
			editor = handles[networkname]
		tweet = handles[page] + ": Your Wikipedia page was edited anonymously by " + editor + " " + url
		api.update_status(tweet)
	
def networkForAddress(ip):
	for key in ipranges:
		for iprange in ipranges[key]:
			if IPAddress(ip) in IPNetwork(iprange):
				return key
	return None

def on_message(ws, message):
    #print message
    dict = json.loads(message)
    ip = dict["user"]
    if (dict["is_anon"]):
    	print 'Anonymous Edit'
    	network = networkForAddress(ip)
    	if network:
    		page = dict["page_title"]
    		print network + " edited " + page
    		if page in pages:
    			print "!!! " + page + " edited by " + network
    			sendTweet(page,network,dict["url"])
    			tweetAt(page,network,dict["url"]) #in the future, combine these methods?

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"
    ws.run_forever()

def on_open(ws):
    def run(*args):
        for i in range(30000):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print "thread terminating..."
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://wikimon.hatnote.com/en/",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
#    ws.on_open = on_open

    ws.run_forever()
