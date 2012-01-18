from django.db.models import Manager


class SectionConflictManager(Manager):
    def by_sections(self, section_ids):
        qs = self.filter(section1__id__in=section_ids, section2__id__in=section_ids)
        qs = qs.select_related('section1', 'section2')
        return qs


