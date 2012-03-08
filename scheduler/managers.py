from django.db.models import Manager


from scheduler.utils import slugify, deserialize_crns, serialize_crns


class SelectionManager(Manager):
    def _update_kwargs(self, kwargs):
        if 'crns' in kwargs:
            crns = serialize_crns(kwargs.pop('crns'))
            kwargs['internal_crns'] = crns or []

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
        new_slug = None
        if 'slug' in kwargs:
            new_slug = slugify(kwargs['slug'])
        kwargs = self._update_kwargs(kwargs)
        if new_slug:
            kwargs['defaults'] = kwargs.get('defaults') or {}
            kwargs['defaults']['internal_slug'] = new_slug
        return super(SelectionManager, self).get_or_create(**kwargs)

    def get(self, **kwargs):
        kwargs = self._update_kwargs(kwargs)
        return super(SelectionManager, self).get(**kwargs)


class SectionConflictManager(Manager):
    def by_sections(self, section_ids):
        qs = self.filter(section1__id__in=section_ids, section2__id__in=section_ids)
        qs = qs.select_related('section1', 'section2')
        return qs


