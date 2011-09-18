from django.db.models import Manager

class ScheduleManager(Manager):
	def create_from_crns(self, crns):
		pass

	def create_from_section_ids(self, sid):
		pass

	def create_all_from_course_ids(self, cid):
		pass

	def get_or_create_from_crns(self, crns):
		pass

	def get_or_create_from_section_ids(self, sid):
		pass

	def get_or_create_all_from_course_ids(self, cid):
		pass
