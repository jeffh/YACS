import factory

from scheduler import models

class SavedSelectionFactory(factory.Factory):
    FACTORY_FOR = models.SavedSelection

    internal_section_ids = []
    internal_blocked_times = []
