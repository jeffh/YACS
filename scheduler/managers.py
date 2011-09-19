from django.db.models import Manager
from django.db import transaction
from timetable.courses import models as courses
from timetable.scheduler.scheduler import compute_schedules

class ScheduleManager(Manager):
    def create_all_from_crns(self, crns, semester):
        """Creates all possible schedule objects from a given set of CRNs (sections)."""
        sections = courses.Section.objects.filter(
            crn__in=crns, semesters=semester
        ).select_related('course').distinct()

        selected_courses = {}
        for section in queryset:
            selected_courses[section.course] = selected_courses.get(section.course, []) + [section]
        
        return self._create_from_schedules(compute_schedules(selected_courses), semester)

    def create_all_from_course_ids(self, course_ids, semester):
        """Creates all possible schedule objects from a given set of course ids."""
        selected_courses = courses.Course.objects.filter(
            id__in=course_ids, semesters=semester
        )
        return self._create_from_schedules(compute_schedules(selected_courses), semester)


    def _create_from_schedules(self, schedules, semester):
        with transaction.commit_on_success():
            from timetable.scheduler import models
            collection = []
            for schedule in schedules:
                course_ids, crns = [c.id for c in schedule.keys()], [c.crn for c in schedule.values()]
                obj = self.model(crns=crns, course_ids=course_ids, semester=semester)
                obj.save()
                for course, section in schedule.items():
                    instance, created = models.SectionInSchedule.objects.get_or_create(
                        schedule=obj,
                        section=section,
                        semester=semester,
                    )
                    instance, created = models.CourseInSchedule.objects.get_or_create(
                        schedule=obj,
                        course=course,
                        semester=semester,
                    )
                collection.append(obj)
            return collection

    def get_or_create_all_from_crns(self, crns, semester):
        "Gets all schedules for a given set of CRNs -- creating them if necessary."
        queryset = self.filter(crns_used=self.model.ints_to_str(crns), semester=semester)
        if queryset.exists():
            return queryset
        return self.create_all_from_crns(crns, semester)


    def get_or_create_all_from_course_ids(self, course_ids, semester):
        "Gets all schedules for a given set of CRNs -- creating them of necessary."
        queryset = self.filter(course_ids_used=self.model.ints_to_str(course_ids), semester=semester)
        if queryset.exists():
            return queryset
        return self.create_all_from_course_ids(course_ids, semester)


