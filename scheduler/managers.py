from django.db.models import Manager

from scheduler.utils import slugify, deserialize_numbers, serialize_numbers


class SavedSelectionManager(Manager):
    def _update_kwargs(self, kwargs):
        tmp = self.model()
        if 'section_ids' in kwargs:
            tmp.section_ids = kwargs.pop('section_ids')
            kwargs['internal_section_ids'] = tmp.internal_section_ids
        if 'blocked_times' in kwargs:
            tmp.blocked_times = kwargs.pop('blocked_times')
            kwargs['internal_blocked_times'] = tmp.internal_blocked_times
        return kwargs

    def get_or_create_by_data(self, **kwargs):
        kwargs = self._update_kwargs(kwargs)
        return self.get_or_create(**kwargs)


class SelectionManager(Manager):
    def _update_kwargs(self, kwargs):
        if 'section_ids' in kwargs:
            section_ids = serialize_numbers(kwargs.pop('section_ids'))
            kwargs['internal_section_ids'] = section_ids or []

        if 'slug' in kwargs:
            kwargs['internal_slug'] = kwargs.pop('slug')
        return kwargs

    def filter(self, *args, **kwargs):
        kwargs = self._update_kwargs(kwargs)
        return super(SelectionManager, self).filter(*args, **kwargs)

    def create(self, **kwargs):
        if 'slug' in kwargs:
            kwargs['internal_slug'] = slugify(kwargs.pop('internal_slug'))
        kwargs = self._update_kwargs(kwargs)
        return super(SelectionManager, self).create(**kwargs)

    def get_or_create(self, **kwargs):
        "Gets or creates a selection. If the selection is created, a slug is given to it."
        new_slug = None
        if 'slug' in kwargs:
            new_slug = slugify(kwargs['slug'])
        kwargs = self._update_kwargs(kwargs)
        if new_slug:
            kwargs['defaults'] = kwargs.get('defaults') or {}
            kwargs['defaults']['internal_slug'] = new_slug
        instance, created = super(SelectionManager, self).get_or_create(**kwargs)
        if created:
            instance.assign_slug_by_id()
            instance.save()
        return instance, created

    def get(self, **kwargs):
        kwargs = self._update_kwargs(kwargs)
        return super(SelectionManager, self).get(**kwargs)


class SectionConflictManager(Manager):
    def by(self, **attributes):
        format = 'section%d__%s'
        attrs = {}
        queryset = self.all()
        for name, value in attributes.items():
            queryset &= self.filter(**{format % (1, name): value}) | self.filter(**{format % (2, name): value})
        return queryset

    def by_unless_none(self, **attributes):
        "Uses by(), but removes keys whose values are None."
        attrs = {}
        for key, value in attributes.items():
            if value is not None:
                attrs[key] = value
        return self.by(**attrs)

    def among(self, **attributes):
        format = 'section%d__%s'
        attrs = {}
        for name, value in attributes.items():
            attrs[format % (1, name)] = value
            attrs[format % (2, name)] = value
        return self.filter(**attrs)

    def among_unless_none(self, **attributes):
        "Uses among(), but removes keys whose values are None."
        attrs = {}
        for key, value in attributes.items():
            if value is not None:
                attrs[key] = value
        return self.among(**attrs)

    def among_sections(self, section_ids, select_related=('section1', 'section2')):
        "Finds conflicts among the given sections."
        #qs = self.filter(section1__id__in=section_ids, section2__id__in=section_ids)
        return self.among(id__in=section_ids).select_related(*select_related)

    def among_crns(self, crns, select_related=('section1', 'section2')):
        "Finds conflicts among the given crns."
        #qs = self.filter(section1__crn__in=crns, section2__crn__in=crns)
        return self.among(crn__in=crns).select_related(*select_related)

    def as_dictionary(self, section_ids=None, queryset=None):
        """Converts a given queryset to a map of section ids => [section-ids which conflict]

        Use section_ids, if you want this method to use among_sections() as the queryset.
        Otherwise, pass your own SectionConflict queryset.
        """
        assert (section_ids is not None) != (queryset is not None), "Either section_ids or queryset is provided."
        if section_ids is not None:
            queryset = self.among_sections(section_ids)
        conflicts = queryset.values_list('section1__id', 'section2__id')

        result = {}  # section_id => [section_ids]
        for s1, s2 in conflicts:
            result.setdefault(s1, []).append(s2)
            result.setdefault(s2, []).append(s1)
        # freeze all sets
        for key in result.keys():
            result[key] = frozenset(result[key])
        return result
