from contextlib import closing
import urllib2
import json
import re

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
            parse_datetime(obj['start']['utcdate']),
            parse_datetime(obj['end']['utcdate']),
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

def get_url(num=356):
    return "http://events.rpi.edu/webcache/v1.0/jsonDays/" + str(num) + "/list-json/%28catuid%3D%2700f18254-27fe1f37-0127-fe1f37da-00000001%27%29/no--object.json"

def get_url_by_range(start, end):
    return "http://events.rpi.edu/webcache/v1.0/jsonRange/"+start+"/"+end+"/list-json/%28catuid%3D%2700f18254-27fe1f37-0127-fe1f37da-00000001%27%29/no--object.json"
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

"""
if __name__ == '__main__':
    events = list(filter_related_events(download_events()))
    from pprint import pprint
    all_events=download_events()
    names=lambda x:[e.name for e in x]
    # "invalid" events
    pprint(set(names(all_events)) - set(names(events)))
    # "valid" events
    pprint(set(names(events)))

"""
