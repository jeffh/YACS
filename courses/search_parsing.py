import re
import datetime

from django.db.models import Q, F

from courses.operators import FQ
from courses.utils import force_int


EXTRA_WHITESPACE = re.compile(r'[\t\r\n ]+')
TIME = re.compile(r'(start|end):(\d{1,2})(:(\d{2}))?([ap]m)?', re.I)


class SearchQuery(object):
    def __init__(self, queryset, dept_code=None):
        self.queryset = queryset
        self.dept_code = dept_code
        self.__days = None

    def filter(self, query):
        return self.queryset.filter(
            self._department_filter() & self._process_query(query)
        ).distinct()

    def _department_filter(self):
        from courses.models import Department
        department_filter = Q()
        if isinstance(self.dept_code, Department):
            department_filter = Q(department=self.dept_code)
        elif self.dept_code:
            department_filter = Q(department__code__iexact=self.dept_code)
        return department_filter

    def _process_query(self, query):
        free_query = []
        query = EXTRA_WHITESPACE.sub(query.strip(), ' ').replace(': ', ':')
        times = TIME.findall(query)
        query = TIME.sub('', query)
        words = (w for w in query.split(' ') if w)
        filters = Q()
        for word in words:
            lword = word.lower()
            if lword.startswith('credit:') or lword.startswith('credits:'):
                filters = filters & self._credits_filter(lword[lword.index(':') + 1:])
            elif lword.startswith('com:') or lword.startswith('comm:') or lword.startswith('communication:'):
                filters = filters & self._comm_intensive_filter(lword[lword.index(':') + 1:])
            elif lword.startswith('seats:'):
                filters = filters & self._seats_filter(lword[lword.index(':') + 1])
            elif lword in self._days():
                filters = filters & self._days_filter(lword)
            else:
                filters = filters & self._fuzzy_match_filter(word)
                free_query.append(word)

        filters = filters & self._times_filter(times)
        return filters

    def _times_filter(self, times):
        filters = Q()
        for kind, hour, _, minute, apm in times:
            name = 'sections__periods__%s__%s' % (kind, 'gte' if kind == 'start' else 'lte')
            hour = max(min(force_int(hour), 23), 0)
            minute = max(min(force_int(minute), 59), 0)
            if apm == 'pm':
                hour += 12
            kwargs = {name: datetime.time(hour, minute)}
            filters = filters & Q(**kwargs)
        return filters

    def _days(self):
        if not self.__days:
            from courses.models import Period
            self.__days = dict(
                m=Period.MONDAY,
                mo=Period.MONDAY,
                mon=Period.MONDAY,
                monday=Period.MONDAY,
                t=Period.TUESDAY,
                tu=Period.TUESDAY,
                tue=Period.TUESDAY,
                tues=Period.TUESDAY,
                tuesday=Period.TUESDAY,
                w=Period.WEDNESDAY,
                we=Period.WEDNESDAY,
                wed=Period.WEDNESDAY,
                wednes=Period.WEDNESDAY,
                wednesday=Period.WEDNESDAY,
                th=Period.THURSDAY,
                thur=Period.THURSDAY,
                thurs=Period.THURSDAY,
                thursday=Period.THURSDAY,
                f=Period.FRIDAY,
                fr=Period.FRIDAY,
                fri=Period.FRIDAY,
                friday=Period.FRIDAY,
            )
        return self.__days

    def _days_filter(self, days_str):
        flag = self._days()[days_str]
        return ~Q(sections=None) & FQ(F('sections__periods__days_of_week_flag') & flag, 'gt', 0)

    def _seats_filter(self, seats_str):
        full = seats_str in ('taken', 'full', 'filled', 'closed')
        if full:
            return Q(sections__seats_taken__gte=F('sections__seats_total'))
        free = seats_str in ('free', 'empty', 'open', 'available')
        return Q(sections__seats_taken__lt=F('sections__seats_total'))

    def _comm_intensive_filter(self, comm_str):
        value = comm_str in ('1', 't', 'true', 'yes', 'enabled', 'only', 'on')
        return Q(is_comm_intense=value)

    def _credits_filter(self, credits_str):
        try:
            credits = int(credits_str)
            return Q(min_credits__lte=credits, max_credits__gte=credits)
        except TypeError:
            return Q()

    def _fuzzy_match_filter(self, query):
        if not query:
            return Q()
        return (
            Q(department__name__icontains=query) |
            Q(department__code__iexact=query) |
            Q(name__icontains=query) |
            Q(number__startswith=query) | Q(number__endswith=query) |
            Q(sections__section_times__instructor__icontains=query) |
            Q(prereqs__icontains=query)
        )
