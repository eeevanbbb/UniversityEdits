#!/usr/bin/python2.7
import websocket
import thread
import time
import json
from netaddr import IPNetwork, IPAddress
import tweet

class SubnetHandler():
    def __init__(self):
        self.ip_ranges = {}
        self.pages = []
        self.handles = {}

        self.read_files()

    def read_files(self):
        with open('IP_Ranges.txt') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split(" : ")
                name = parts[0].decode('utf-8')
                part2 = parts[1].strip("\n")
                ranges = part2.split(", ")      
                self.ip_ranges[name] = ranges        

        with open('Monitored_Pages') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split(" : ")
                if len(parts) == 2:
                    page = parts[0].decode('utf-8')
                    handle = parts[1].strip("\n")
                    self.pages.append(page)
                    if len(handle) > 0:
                        self.handles[page] = handle
                else:
                    decoded = line.decode('utf-8')
                    stripped = decoded.strip("\n")
                    self.pages.append(stripped)

class TweetComposer():
    def __init__(self, subnet_handler):
        self.subnet_handler = subnet_handler

    def compose_tweet(page, network_name, url):
        tweet = ""
        if (page == networ_kname):
            tweet = networ_kname + " anonymously edited its own Wikipedia page: " + url
        else:
            tweet = network_name + " anonymously edited the Wikipedia page for " + page + ": " + url
        return tweet 

    def compose_tweet_at(page, network_name, url):
        if (page != network_name and self.subnet_handler.handles[page]):
            editor = network_name
            if self.subnet_handler.handles[network_name]:
                editor = self.subnet_handler.handles[network_name]
            tweet = self.subnet_handler.handles[page] + ": Your Wikipedia page was edited anonymously by " + editor + " " + url
            return tweet
        return None


class WikipediaListener():
    def __init__(self, subnet_handler, composer, tweet_handler):
        self.subnet_handler = subnet_handler
        self.composer = composer
        self.tweet_handler = tweet_handler

        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("ws://wikimon.hatnote.com/en/",
                                on_message = self.on_message,
                                on_error = self.on_error,
                                on_close = self.on_close) 

    def start(self):
        self.ws.run_forever()

	
    def networkForAddress(self, ip):
    	for key in self.subnet_handler.ip_ranges:
    		for ip_range in self.subnet_handler.ip_ranges[key]:
    			if IPAddress(ip) in IPNetwork(ip_range):
    				return key
    	return None

    def on_message(self, ws, message):
        #print message
        dict = json.loads(message)
        ip = dict["user"]
        if (dict["is_anon"]):
            print 'Anonymous Edit'
            network = self.networkForAddress(ip)
            if network:
                page = dict["page_title"]
                print network + " edited " + page
                if page in self.subnet_handler.pages:
                    print "!!! " + page + " edited by " + network
                    tweet1 = self.composer.compose_tweet(page, network, dict["url"])
                    tweet2 = self.composer.compose_tweet_at(page, network, dict["url"]) #in the future, combine these methods?
                    self.tweet_handler.send_tweet(tweet1)
                    self.tweet_handler.send_tweet(tweet2)

    def on_error(self, ws, error):
        print error

    def on_close(self, ws):
        print "### closed ###"


if __name__ == "__main__":
    tweet_handler = tweet.TweetHandler()
    subnet_handler = SubnetHandler()
    tweet_composer = TweetComposer(subnet_handler)
    listener = WikipediaListener(subnet_handler, tweet_composer, tweet_handler)

    listener.start()
