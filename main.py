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
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch

from utils import BaseHandler, NotFoundHandler
from datetime import datetime
import logging

from twitter_oauth_handler import *
import gdata.calendar.service

CAL_URI='/calendar/feeds/pypg.org_q4t5tc0ihaqgpth5nb3dhf8qg0%40group.calendar.google.com/public/full'
CAL_TIME_FORMAT='%Y-%m-%dT%H:%M:%S.000+02:00'
TWITTER_URI='http://twitter.com/statuses/user_timeline/183262263.rss'
TWITTER_TIME_FORMAT='%a %b %d %H:%M:%S +0000 %Y'

class IndexPage(BaseHandler):
    def get(self):
        tweets = []
        next_events = []
        
        # collect tweets from pyperugia
        # NOTICE: oauth will not work on dev server
        client = OAuthClient('twitter', self)
        items = client.get('/statuses/user_timeline')
        for t in items:
            date = datetime.strptime(t['created_at'], TWITTER_TIME_FORMAT)
            tweets.append( { 'date': date, 'text':t['text']} )
        
        # get next events on public calendar
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

class LegalPage(BaseHandler):
    def get(self):
        # render template        
        self.render_template("legal.html", {
          #
        })

def main():
    application = webapp.WSGIApplication([
      ('/', IndexPage),
      ('/oauth/(.*)/(.*)', OAuthHandler),
      ('/legal', LegalPage),
      ('.*', NotFoundHandler),
      ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
