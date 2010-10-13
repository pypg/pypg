#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch

from utils import BaseHandler, NotFoundHandler
from datetime import datetime
import os,logging

import gdata.calendar.service

import oauth
from demjson import decode as decode_json

CAL_URI='/calendar/feeds/pypg.org_q4t5tc0ihaqgpth5nb3dhf8qg0%40group.calendar.google.com/public/full'
CAL_TIME_FORMAT='%Y-%m-%dT%H:%M:%S.000+02:00'

TWITTER_TIME_FORMAT='%a %b %d %H:%M:%S +0000 %Y'
TWITTER_CONSUMER_KEYNAME = 'twitter_auth_consumer'
TWITTER_SERVICE_KEYNAME = 'twitter_auth_service'

class TwitterData(db.Model):
    """The model holding oauth tokens&pass for both the consumer and server
    side
    """
    token = db.StringProperty()
    secret = db.StringProperty()

def get_tweets():
    """Gather tweets from Twitter APIs and return a list of tuples of the type:
    (tweet date, tweet body)
    
    """
    tweets = []
    
    td_service = TwitterData.get_by_key_name(TWITTER_SERVICE_KEYNAME)
    if not td_service:
        logging.error('Twitter service data not found')
        return tweets

    td_consumer = TwitterData.get_by_key_name(TWITTER_CONSUMER_KEYNAME)
    if not td_consumer:
        logging.error('Twitter consumer data not found')
        return tweets
    
    timeline_url = "http://api.twitter.com/1/statuses/user_timeline.json"
    params = { "include_rts" : 1, "count" : 5 }   
    client = oauth.TwitterClient(td_service.token, td_service.secret, 
            callback_url='')
    
    contents = client.make_request(url=timeline_url, token=td_consumer.token, 
        secret=td_consumer.secret, protected=True, additional_params=params).content
    
    for t in decode_json(contents):
        date = datetime.strptime(t['created_at'], TWITTER_TIME_FORMAT)
        tweets.append( { 'date': date, 'text':t['text']} )

    return tweets
    
    
class IndexPage(BaseHandler):
    def get(self):
        # get latest tweets
        tweets = get_tweets()
        # get next events on public calendar
        next_events = []        
        cal_service = gdata.calendar.service.CalendarService()
        cal_feed = cal_service.GetCalendarEventFeed(CAL_URI)
        for entry in cal_feed.entry:
            date = datetime.strptime(entry.when[0].start_time, CAL_TIME_FORMAT)
            if date < datetime.now():
                continue
            title = entry.title.text
            next_events.append( {'date':date, 'title':title} )
        
        # render template        
        self.render_template("index.html", {
            'tweets' : tweets,
            'next_events' : next_events, 
        })


class OAuthHandler(webapp.RequestHandler):
    def get(self, mode=''):
        callback_url = "%s/oauth/verify" % self.request.host_url
        td_service = TwitterData.get_by_key_name(TWITTER_SERVICE_KEYNAME)
        if not td_service:
            td_service = TwitterData(key_name=TWITTER_SERVICE_KEYNAME)
            td_service.token = ''
            td_service.secret = ''
            td_service.put()
            logging.error('Please provide service key and secret')
            self.error(500)
        
        application_key = td_service.token#"YnDGZfGt6vQE1ogfNL7Fg" 
        application_secret = td_service.secret#"AZa0Z7ze9gRvP0GTGJmGrzwD12xIrCkDPvtJcw7ACeo"  
        
        client = oauth.TwitterClient(application_key, application_secret, 
            callback_url)
        
        if mode == "login":
            return self.redirect(client.get_authorization_url())
        
        elif mode == "verify":
            auth_token = self.request.get("oauth_token")
            auth_verifier = self.request.get("oauth_verifier")
            user_info = client.get_user_info(auth_token, auth_verifier=auth_verifier)
            td = TwitterData.get_or_insert(TWITTER_CONSUMER_KEYNAME)
            td.token = user_info['token']
            td.secret = user_info['secret']
            td.put()
            return self.response.out.write(user_info)
        
        # a bad request
        self.error(400)
      
    
class LegalPage(BaseHandler):
    def get(self):
        # render template        
        self.render_template("legal.html", {
          #
        })

def main():
    application = webapp.WSGIApplication([
      ('/', IndexPage),
      ('/oauth/(.*)', OAuthHandler),
      ('/legal', LegalPage),
      ('.*', NotFoundHandler),
      ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
