from haystack import indexes
from courses import models

class CourseIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    number = indexes.IntegerField(model_attr='number')
    description = indexes.CharField(model_attr='description')
    min_credits = indexes.IntegerField(model_attr='min_credits')
    max_credits = indexes.IntegerField(model_attr='max_credits')
    prereqs = indexes.CharField(model_attr='prereqs')
    is_comm_intense = indexes.BooleanField(model_attr='is_comm_intense')
    grade_type = indexes.CharField(model_attr='grade_type')

    # dynamic fields
    #autocomplete_text = indexes.EdgeNgramField()
    semester_ids = indexes.MultiValueField()
    department_code = indexes.CharField()
    department_name = indexes.CharField()
    instructors = indexes.MultiValueField()
    kinds = indexes.MultiValueField()
    crns = indexes.MultiValueField()
    locations = indexes.MultiValueField()

    def prepare_autocomplete_text(self, obj):
        return ' '.join([obj.name, obj.code])

    def prepare_semester_ids(self, obj):
        return list(obj.semesters.all().values_list('id', flat=True))

    def prepare_department_code(self, obj):
        return obj.department.code

    def prepare_department_name(self, obj):
        return obj.department.name

    def prepare_instructors(self, obj):
        return list(obj.instructors)

    def prepare_kinds(self, obj):
        return list(obj.kinds)

    def prepare_crns(self, obj):
        return list(obj.crns)

    def prepare_locations(self, obj):
        return list(obj.locations)

    def get_model(self):
        return models.Course

    def build_queryset(self, using=None, start_date=None, end_date=None):
        queryset = self.get_model().objects.all()
        if start_date:
            queryset = queryset.filter(date_updated__gte=start_date)
        if end_date:
            queryset = queryset.filter(date_updated__lte=end_date)
        return queryset

    def load_all_queryset(self):
        return self.get_model().objects.full_select()

