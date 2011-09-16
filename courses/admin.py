from django.contrib import admin
from timetable.courses.models import *

class DepartmentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Department, DepartmentAdmin)

class SemesterAdmin(admin.ModelAdmin):
    pass

admin.site.register(Semester, SemesterAdmin)

class PeriodAdmin(admin.ModelAdmin):
    pass

admin.site.register(Period, PeriodAdmin)

class SectionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Section, SectionAdmin)

class SectionCrosslistingAdmin(admin.ModelAdmin):
    pass

admin.site.register(SectionCrosslisting, SectionCrosslistingAdmin)

class CourseAdmin(admin.ModelAdmin):
    pass

admin.site.register(Course, CourseAdmin)

class OfferedForAdmin(admin.ModelAdmin):
    pass

admin.site.register(OfferedFor, OfferedForAdmin)

class SectionPeriodAdmin(admin.ModelAdmin):
    pass

admin.site.register(SectionPeriod, SectionPeriodAdmin)
