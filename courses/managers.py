from django.db.models import Manager, query

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

class SectionPeriodManager(SemesterBasedManager):
    use_for_related_fields = True

    def filter_by_course(self, course):
        return self.filter(section__course=course)

    def select_instructors(self, course):
        return self.filter_by_course(course).values_list('instructor', flat=True).distinct().order_by('instructor')

    def select_kinds(self, course):
        return self.filter_by_course(course).values_list('kind', flat=True).distinct().order_by('kind')
