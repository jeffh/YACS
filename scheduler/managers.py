from django.db.models import Manager
from django.db import transaction, IntegrityError, connection
from yacs.courses import models as courses
from yacs.scheduler.scheduler import compute_schedules
#from yacs.scheduler import models

class BulkInsert(object):
    def __init__(self, engine=None):
        if engine is None:
            from django.conf import settings
            engine = settings.DATABASES['default']['ENGINE']
        self.engine = self.bulk_insert_backend_method(engine)

    def __call__(self, table, columns, values):
        return self.engine(table, columns, values)

    def bulk_insert_basesql(self, table, columns, values, single_query=True):
        row_ph = ', '.join(['%s'] * len(columns))
        if single_query:
            placeholder = ['(' + row_ph + ')' for v in values]
        else:
            placeholder = ['(' + row_ph + ')']
        
        query = "INSERT INTO %s (%s) VALUES %s" % (
            table,
            ','.join(columns),
            ', '.join(placeholder)
        )

        return query

    def postgres_bulk_insert(self, table, columns, values):
        if len(values) < 1:
            return []
        query = self.bulk_insert_basesql(table, columns, values) + " RETURNING id"

        cursor = connection.cursor()
        cursor.execute(query, [cell for row in values for cell in row])

        new_ids = cursor.fetchall()

        transaction.commit_unless_managed()
        return new_ids

    def sqlite_bulk_insert(self, table, columns, values):
        "The sqlite backend provides no performance enhancement"
        query = self.bulk_insert_basesql(table, columns, values, single_query=False)
        new_ids = []

        cursor = connection.cursor()
        for row in values:
            cursor.execute(query, row)
            new_ids.append(cursor.lastrowid)

        transaction.commit_unless_managed()
        return new_ids
    
    def bulk_insert_backend_method(self, engine):
        supported_engines = {
            'django.db.backends.postgresql_psycopg2': self.postgres_bulk_insert,
            'django.db.backends.sqlite3': self.sqlite_bulk_insert,
        }
        return supported_engines[engine]
    

class ScheduleManager(Manager):
    def create_all_from_crns(self, crns, semester):
        """Creates all possible schedule objects from a given set of CRNs (sections)."""
        sections_and_periods = courses.SectionPeriod.objects.filter(
            semester=semester,
            section__crn__in=set(crns),
            #section__seats_taken__lt=F('section__seats_total'),
        ).select_related('period', 'section', 'section__course')

        secid_to_periods = {}
        for snp in sections_and_periods:
            secid_to_periods[snp.section_id] = secid_to_periods.get(snp.section_id, []) + [snp.period]

        selected_courses = {}
        for snp in sections_and_periods:
            snp.section.all_periods = secid_to_periods[snp.section_id]
            selected_courses[snp.section.course] = selected_courses.get(snp.section.course, []) + [snp.section]
        
        schedules = compute_schedules(selected_courses)
        
        return self._create_from_schedules(schedules, semester)

    def create_all_from_course_ids(self, course_ids, semester):
        """Creates all possible schedule objects from a given set of course ids."""
        selected_courses = courses.Course.objects.filter(
            id__in=course_ids, semesters=semester
        )
        return self._create_from_schedules(compute_schedules(selected_courses), semester)

    """
    def _create_from_schedules(self, schedules, semester):
        from yacs.scheduler import models
        schedule_values = []
        sis_values = []
        cis_values = []
        all_crns = set()
        for schedule in schedules:
            crns = self.model.ints_to_str([c.crn for c in schedule.values()])
            if crns not in all_crns:
                all_crns = all_crns.union([crns])
        existing_schedules = self.filter(crns_used__in=all_crns).values_list('crns_used', flat=True)

        seen = set()
        for i, schedule in enumerate(schedules):
            course_ids = self.model.ints_to_str([c.id for c in schedule.keys()])
            crns = self.model.ints_to_str([c.crn for c in schedule.values()])
            if crns in existing_schedules or crns in seen:
                continue
            seen = seen.union([crns])
            schedule_values.append([
                crns,
                course_ids,
                semester.id
            ])
            for course, section in schedule.items():
                sis_values = [
                    i,
                    section.id,
                    semester.id,
                ]
                cis_values = [
                    i,
                    course.id,
                    semester.id
                ]
        
        bulk_insert = BulkInsert()

        latest_ids = bulk_insert(
            table=self.model._meta.db_table,
            columns=['crns_used', 'course_ids_used', 'semester_id'],
            values=schedule_values,
        )
        if latest_ids:
            for crn in latest
            bulk_insert(
                table=models.SectionInSchedule._meta.db_table,
                columns=['schedule_id', 'section_id', 'semester_id'],
                values=[(lid, b, c) for (a, b, c), lid in zip(sis_values, latest_ids)],
            )
            bulk_insert(
                table=models.CourseInSchedule._meta.db_table,
                columns=['schedule_id', 'course_id', 'semester_id'],
                values=[(lid, b, c) for (a, b, c), lid in zip(cis_values, latest_ids)],
            )
    """

    #Old method of insertion... very slow
    def _create_from_schedules(self, schedules, semester):
        with transaction.commit_manually():
            from yacs.scheduler import models
            collection = []
            for schedule in schedules:
                course_ids, crns = [c.id for c in schedule.keys()], [c.crn for c in schedule.values()]
                obj = self.model(
                    crns=crns,
                    course_ids=course_ids,
                    semester=semester,
                )
                #obj, created = self.get_or_create(
                #    crns=crns,
                #    course_ids=course_ids,
                #    semester=semester
                #)
                collection.append(obj)
            transaction.commit()
        return collection
    #"""

    def get_or_create_all_from_crns(self, crns, semester):
        "Gets all schedules for a given set of CRNs -- creating them if necessary."
        # looks terribly inefficient here -- since we're fetching the same thing multiple times
        # but the custom create method uses bulk inserts which reduces 340+ queries to 3, which is
        # a small price to pay to execute another read query afterwards.
        schedules = self.filter(
            semester=semester,
            crns=crns,
            #crns_used=self.model.ints_to_str(crns)
        )
        if schedules.exists():
            return schedules
        self.create_all_from_crns(crns, semester)
        return schedules


    def get_or_create_all_from_course_ids(self, course_ids, semester):
        "Gets all schedules for a given set of CRNs -- creating them of necessary."
        # looks terribly inefficient here -- since we're fetching the same thing multiple times
        # but the custom create method uses bulk inserts which reduces 340+ queries to 3, which is
        # a small price to pay to execute another read query afterwards.
        queryset = self.filter(course_ids=course_ids, semester=semester)
        if queryset.exists():
            return queryset
        self.create_all_from_course_ids(course_ids, semester)
        return queryset


