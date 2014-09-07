from django.db import models


class Event(models.Model):
    # raw data
    name = models.CharField(max_length=200)
    date = models.DateField(db_index=True)
    date_created = model.DateTimeField(auto_now_add=True)

    # computed data
    has_no_classes = models.BooleanField(default=False)
    is_start_of_vacation_range = models.BooleanField(default=False)
    is_end_of_vacation_range = models.BooleanField(default=False)
    is_start_of_semester = models.BooleanField(default=False)
    is_end_of_semester = models.BooleanField(default=False)
