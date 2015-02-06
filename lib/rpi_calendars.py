from contextlib import closing
import urllib2
import json
import re

import pytz
from dateutil.parser import parse as parse_datetime


class Event(object):
    def __init__(self, name, guid, start_date, end_date, is_all_day=False):
        self.name, self.guid = name, guid
        self.start, self.end = start_date, end_date
        self.is_all_day = is_all_day

    @classmethod
    def from_dict(cls, obj):
        return cls(
            obj['summary'],
            obj['guid'],
            parse_datetime(obj['start']['utcdate']).replace(tzinfo=pytz.timezone("America/New_York")).astimezone(pytz.utc),
            parse_datetime(obj['end']['utcdate']).replace(tzinfo=pytz.timezone("America/New_York")).astimezone(pytz.utc),
            obj['start']['allday'] == 'true'
        )

    def __hash__(self):
        return hash(self.guid)

    def __eq__(self, other):
        return self.guid == other.guid

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Event(%r, %r, %r, %r, is_all_day=%r)" % (
            self.name, self.guid, self.start, self.end, self.is_all_day
        )


def get_url(num=3000):
    return (
        "http://events.rpi.edu:7070/feeder/main/eventsFeed.do?f=y&" +
        "sort=dtstart.utc:asc&" +
        "fexpr=(((vpath=\"/user/public-user/General%20Calendars\")))%20and%20(entity_type=\"event\"%7Centity_type=\"todo\")&" +
        "skinName=list-json&" +
        "count=" + str(num)
    )


def get_url_by_range(start, end):
    "Broken."
    return (
        "http://events.rpi.edu:7070/feeder/main/eventsFeed.do?f=y&" +
        "sort=dtstart.utc:asc" +
        "&fexpr=(categories.href!=%22/public/.bedework/categories/Ongoing%22)%20and%20(entity_type=%22event%22%7Centity_type=%22todo%22)&" +
        "skinName=list-json&" +
        "start=" + str(start) + "&" +
        "end=" + str(end)
    )


def get_json(url):
    with closing(urllib2.urlopen(url)) as handle:
        return json.loads(handle.read())


def get_events(obj):
    return list(map(Event.from_dict, obj['bwEventList']['events']))


def download_events(url):
    return get_events(get_json(url))


class EventNameParser(object):
    def __init__(self):
        pass

    def matches(self, name):
        return (
            self.has_no_classes(name) or
            self.follows_alternative_schedule(name) or
            self.resume_classes(name) or
            self.is_study_review_day(name) or
            self.is_final_exam_day(name) or
            self.is_break(name)
        )

    def has_word(self, name, word, *words):
        all_words = set(w for w in name.split(' ') if w)
        for w in (word, ) + words:
            if w in all_words:
                return True
        return False

    def has_no_classes(self, name):
        lname = name.lower()
        return 'no classes' in lname or self.has_word(lname, 'end')

    def follows_alternative_schedule(self, name):
        match = re.search(r'follow +([a-z]+) +class +schedule', name.lower())
        if match:
            return match.group(1)

        return None

    def resume_classes(self, name):
        lname = name.lower()
        return self.has_word(lname, 'begin', 'resume', 'recess')

    def is_study_review_day(self, name):
        lname = name.lower()
        return self.has_word(lname, 'study', 'review')

    def is_break(self, name):
        return self.has_word(name.lower(), 'break')

    def is_final_exam_day(self, name):
        return 'final exams' in name.lower()

    def is_summer(self, name):
        return self.has_word(name.lower(), 'summer')

    def is_winter(self, name):
        return self.has_word(name.lower(), 'winter')

    def is_fall(self, name):
        return self.has_word(name.lower(), 'fall')

    def is_spring(self, name):
        return self.has_word(name.lower(), 'spring')


def filter_related_events(events):
    parser = EventNameParser()
    for event in events:
        if parser.matches(event.name):
            yield event
