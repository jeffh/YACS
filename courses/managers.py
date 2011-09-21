from django.db.models import Manager

class SemesterBasedManager(Manager):
    def filter_by_semester(self, year=None, month=None):
        qs = self.get_query_set()
        if year:
            qs = qs.filter(semesters__year__contains=year)
        
        if month:
            qs = qs.filter(semesters__month__contains=month)

        if year or month:
        	qs = qs.distinct()
        
        return qs
