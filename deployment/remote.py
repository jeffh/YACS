import os

from fabric.api import run as fabric_run, sudo as fabric_sudo
from fabric.contrib.files import exists as fabric_exists
from fabric.operations import put as fabric_put
from fabric.context_managers import cd, hide, settings


def _flags(kwargs, options):
    """Converts kwargs recieved by functions into options accepted by a CLI program."""
    sb = []
    for name in options:
        if kwargs.pop(name, 0):
            sb.append(options[name])
    return tuple(sb)


def escape(path, quote=False):
    if quote:
        return '"%s"' % path.replace('"', '\\"')
    return str(path).replace(' ', '\\ ')


def normalize(*path, **kwargs):
    "Joins paths and then normalizes the path."
    if len(path) == 1 and type(path[0]) in (list, tuple):
        path = tuple(path[0])
    root = kwargs.get('root', '')
    result = os.path.normpath(os.path.join(root, *path))
    return result


def normalize_paths(paths, **kwargs):
    "Normalizes on a collection of file paths"
    return tuple(normalize(p, **kwargs) for p in paths)


def exists(*path):
    return fabric_exists(normalize(path))


def run(cmd, *args, **kwargs):
    invoke = fabric_run
    if kwargs.pop('sudo', 0):
        invoke = fabric_sudo
    full = (cmd,) + args
    return invoke(' '.join(escape(s) for s in full if s), **kwargs)


def mkdir(*paths, **kwargs):
    options = _flags(kwargs, {'recursive': '-p'})
    return run('mkdir', *(options + normalize_paths(paths)), **kwargs)


def unzip(*path, **kwargs):
    delete, sudo = kwargs.pop('delete', False), kwargs.pop('sudo', False)
    with settings(
        cd(normalize(*(path + ('..',)))),
        hide('stdout')
    ):
        result = run('unzip', normalize(*path), sudo=False)
        if delete:
            remove(normalize(path), sudo=False)

        return result


def move(src, dest, recursive=False, sudo=False):
    return run(
        'mv',
        '-r' if recursive else '',
        normalize(src),
        normalize(dest),
        sudo=sudo
    )


def put(filename, destination, **kwargs):
    return fabric_put(normalize(filename), normalize(destination), **kwargs)


def chmod(mode, *paths, **kwargs):
    options = _flags(kwargs, {
        'recursive': '-r',
    })
    return run('chmod', *(options + (mode,) + normalize_paths(paths)), **kwargs)


def remove(*paths, **kwargs):
    options = _flags(kwargs, {
        'recursive': '-r',
        'force': '-f',
    })
    return run('rm', *(options + normalize_paths(paths)), **kwargs)


def which(path, all=False):
    with hide('stdout', 'stderr'):
        try:
            return run('which',
                '-a' if all else '',
                path
            ).strip()
        except:
            return None


class phase_out(object):
    """Renames the given file. Use phased_file.delete() to remove the renamed,
    otherwise it will automatically be restored when the block ends.

    This is useful for attempting to upgrade a project, but restoring the old project on failure.
    """
    def __init__(self, path, sudo=False):
        self.path = path
        self.sudo = sudo
        self.__tmpname = None
        self.exists = False

    def delete(self):
        remove(self.__tmpname, force=True, recursive=True)
        self.__tmpname = None
        self.exists = False

    def restore(self):
        if self.__tmpname and self.exists:
            if exists(self.path):
                remove(self.path, recursive=True, force=True)
            move(self.__tmpname, self.path, sudo=self.sudo)
            self.__tmpname = None

    def _create_tmpname(self):
        return normalize(os.path.join(self.path, '..'), os.path.basename(self.path) + '_backup')

    def __enter__(self):
        self.__tmpname = self._create_tmpname()
        self.exists = exists(self.path)
        if self.exists:
            move(self.path, self.__tmpname, sudo=self.sudo)
        return self

    def __exit__(self, type, value, traceback):
        self.restore()

