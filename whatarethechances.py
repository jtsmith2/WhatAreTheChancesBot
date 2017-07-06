#!/usr/bin/python3.6

"""
Anytime a tweet includes the phrase "What are the chances", this bot replies to the tweet
with a random probability.

WARNING: This is against the Twitter TOS / guidelines for automation. Replying to tweets without
the user first opting in or interacting with the accoutn is seen as spam.  Using this code as-is
will get your app restricted or banned.

"""

# imports
from sys import exit
import tweepy
import settings
import time
import random

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = '' 

def debug_print(text):
    """Print text if debugging mode is on"""
    if settings.debug:
        print (text)


def save_id(statefile,id):
    """Save last status ID to a file"""
    last_id = get_last_id(statefile)

    if last_id < id:
        debug_print('Saving new ID %d to %s' % (id,statefile))
        f = open(statefile,'w')
        f.write(str(id)) 
        f.close()
    else:
        debug_print('Received smaller ID, not saving. Old: %d, New: %s' % (
            last_id, id))


def get_last_id(statefile):
    """Retrieve last status ID from a file"""

    debug_print('Getting last ID from %s' % (statefile,))
    try:
        f = open(statefile,'r')
        id = int(f.read())
        f.close()
    except IOError:
        debug_print('IOError raised, returning zero (0)')
        return 0
    debug_print('Got %d' % (id,))
    return id


def careful_reply(api,reply):
    """Perform retweets while avoiding loops and spam"""

    debug_print('Preparing to reply to #%d' % (reply.id,))
    normalized_tweet = reply.text.lower().strip()

    # Don't reply to a retweet
    if hasattr(reply, 'retweeted_status'):
        return

    debug_print('Replying to #%d' % (reply.id,))
    update = "@%s We'd estimate about a %d percent chance, actually." % (reply.user.screen_name, random.randint(0,100),)
    return api.update_status(update, reply.id)


def main():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    auth2 = tweepy.AppAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
    sapi = tweepy.API(auth2, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    while(True):

        last_id = get_last_id(settings.last_id_file)

        for status in tweepy.Cursor(sapi.search,q='"what are the chances"', result_type='latest', since_id=last_id).items():

            try:
                careful_reply(api, status)
            except Exception as e:
                print ('e: %s' % e)
                print (repr(e))
            else:
                save_id(settings.last_id_file, status.id)

        time.sleep(60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        quit()
