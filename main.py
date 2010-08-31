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

from utils import BaseHandler, NotFoundHandler
from datetime import datetime

import tweepy
import gdata.calendar.service

CAL_URI='/calendar/feeds/pypg.org_q4t5tc0ihaqgpth5nb3dhf8qg0%40group.calendar.google.com/public/full'
CAL_TIME_FORMAT='%Y-%m-%dT%H:%M:%S.000+02:00'

class IndexPage(BaseHandler):    
    def get(self):
        tweets = []
        next_events = []
        
        # collect tweets from pyperugia
        try:
            tweets = tweepy.api.user_timeline('pyperugia', count=5)
        except tweepy.TweepError, err:
            # TODO: log error
            pass
        
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


def main():
    application = webapp.WSGIApplication([
      ('/', IndexPage),
      ('.*', NotFoundHandler),
      ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
