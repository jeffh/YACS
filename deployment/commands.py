from fabric.context_managers import hide
from remote import run, which, escape

class Command(object):
	"""Make any command line program feel like managing an object.
	"""
	def __init__(self, name, args=None, kwargs=None, tail_args=None, install=None, sudo_install=None, sudo=False, user=None):
		self.__name, self.__args, self.__kwargs = name, tuple(args or ()), kwargs or {}
		if install or sudo_install:
			self.__install_cmd = (install or sudo_install)
			self.__use_sudo_install = bool(sudo_install)
		self.__use_sudo = bool(sudo)
		self.__user = user
		self.__last_path = None
		self.__tail_args = tuple(tail_args or ())
		self.__disabled = False

	@property
	def path(self):
		path = which(self.__name)
		self.__last_path = path
		return path

	def disable_command(self):
		self.__disabled = True
		return self

	def extend(self, args=None, kwargs=None, tail_args=None, sudo=None, user=None):
		if sudo is None:
			sudo = self.__use_sudo
		if user is None:
			user = self.__user
		args = self.__args + tuple(args or ())
		tail_args = self.__tail_args + tuple(tail_args or ())
		options = dict(
			sudo=sudo,
			user=user,
		)
		if self.__use_sudo_install:
			options['sudo_install'] = self.__install_cmd
		else:
			options['install'] = self.__install_cmd

		new_kwargs = {}
		new_kwargs.update(self.__kwargs)
		new_kwargs.update(kwargs or {})

		return Command(self.__name, args, new_kwargs, tail_args, **options)

	def __getattr__(self, name):
		return self.extend(args=(name,))
	
	def __convert_kwargs_into_flags(self, kwargs):
		sb = []
		for name in kwargs:
			if len(name) == 1:
				sb.append('-' + name)
			else:
				sb.append('--' + name)
			sb.append(kwargs[name])
		return tuple(sb)

	def get_command(self, args, kwargs):
		full_args = self.__args + tuple(args)
		full_kwargs = {}
		full_kwargs.update(self.__kwargs)
		full_kwargs.update(kwargs)

		return (self.__name, ) + full_args + \
			self.__convert_kwargs_into_flags(full_kwargs) + self.__tail_args

	def __call__(self, *args, **kwargs):
		if self.__disabled:
			return None
		# install if we must
		with hide('running'):
			if self.__last_path is None:
				self.path
			if not self.__last_path:
				if callable(self.__install_cmd):
					self.__install_cmd(self.__name, {'sudo':self.__use_sudo_install, 'user':self.__user})
				elif self.__install_cmd:
					options = {'sudo': self.__use_sudo_install}
					if self.__use_sudo_install:
						options['user'] = self.__user
					run(self.__install_cmd % {
						'name': self.__name,
						'user': self.__user
					}, **options)
				else:
					raise TypeError("Command %r does not exist on the system." % self.__name)

		return run(*self.get_command(args, kwargs), sudo=self.__use_sudo)
