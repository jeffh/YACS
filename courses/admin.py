from django.contrib import admin

from courses.models import *

admin.site.register(Department)
admin.site.register(Semester)
admin.site.register(Period)
admin.site.register(Section)
admin.site.register(SectionCrosslisting)
admin.site.register(Course)
admin.site.register(OfferedFor)
admin.site.register(SectionPeriod)
