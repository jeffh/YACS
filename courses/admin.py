from django.contrib import admin

from courses.models import *


def make_visible(modeladmin, request, queryset):
    queryset.update(visible=True)
make_visible.short_description = 'Mark selected %(verbose_name_plural)s to be publicly visible'


class SemestersListFilter(admin.SimpleListFilter):
    title = 'Semester'
    parameter_name = 'semesters__id'

    def lookups(self, request, model_admin):
        result = []
        for sem in Semester.objects.all():
            result.append((sem.id, sem.name))
        return result

    def queryset(self, request, queryset):
        if request.user.is_superuser:
            value = self.value()
            if value:
                return queryset.filter(**{self.parameter_name: self.value()})


class SemesterListFilter(SemestersListFilter):
    parameter_name = 'semester_id'


class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'ref', 'date_updated', 'date_created', 'visible')
    search_fields = ('name', 'ref', 'year', 'month')
    fieldsets = (
        (None, {'fields': ('name', 'year', 'month')}),
        ('Advanced options', {'fields': ('ref', 'visible')}),
    )
    ordering = ('-year', '-month')
    actions = [make_visible]


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'department', 'number', 'min_credits', 'max_credits', 'is_comm_intense')
    list_filter = (SemestersListFilter, 'is_comm_intense', 'min_credits', 'max_credits')
    search_fields = ('name', 'department__name', 'department__code', 'number')
    ordering = ('department', 'number')


class SectionAdmin(admin.ModelAdmin):
    list_display = ('crn', 'id', 'course', 'number', 'semester', 'seats_taken', 'seats_total', 'notes')
    list_filter = (SemesterListFilter, 'course__department__code',)
    search_fields = ('crn', 'course__name', 'number', 'course__number', 'notes')

    def queryset(self, request):
        qs = super(SectionAdmin, self).queryset(request)
        return qs.select_related()


class SectionPeriodAdmin(admin.ModelAdmin):
    list_display = ('id', 'Section', 'Period', 'semester', 'instructor', 'location', 'kind')
    list_filter = (SemesterListFilter, 'location', 'kind', 'period__start', 'period__end')
    search_fields = ('section__course__name', 'instructor', 'location', 'kind')
    ordering = ('semester__year', 'semester__month')

    def Section(self, instance):
        return '%s #%s' % (
            instance.section.course.name,
            instance.section.number,
        )

    def Period(self, instance):
        return '%s - %s (%s)' % (
            instance.period.start,
            instance.period.end,
            instance.period.days_of_the_week,
        )

    def queryset(self, request):
        qs = super(SectionPeriodAdmin, self).queryset(request)
        return qs.select_related()


class PeriodAdmin(admin.ModelAdmin):
    list_display = ('start', 'end', 'days_of_the_week')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    list_filter = (SemestersListFilter,)
    search_fields = ('name', 'code')
    ordering = ('code',)


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(SectionPeriod, SectionPeriodAdmin)
