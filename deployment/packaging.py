# handles local packaging
import os
import zipfile
import sys
import fnmatch
from glob import glob

def _progressbar(*msg):
    sys.stdout.write('\r' + ' '.join(msg))
    sys.stdout.flush()

def zipfiles(files, to, root='.', verbose=True):
    if verbose:
        print
    
    handler = zipfile.ZipFile(to, 'w')
    total = float(len(files))
    for i, filename in enumerate(files):

        if verbose:
            percent = int(i / total * 50)
            _progressbar("Zipping project", '.' * percent)
            
        handler.write(filename, os.path.relpath(filename, root))

    if verbose:
        print ' Done'
    handler.close()

def directory(*paths, **kwargs):
    path = os.path.join(*paths)
    filter = kwargs.pop('filter')
    return dict(path=path, filters=filter)

def _process_directory(path, filters=None, root='.'):
    filters = filters or {}
    matches = []
    for base, dirs, files in os.walk(path):
        for name in fnmatch.filter(files, filters):
            matches.append(os.path.relpath(os.path.join(base, name), root))
    return matches

def get_project_files(root, project_files):
    files = []
    for path in project_files:
        if isinstance(path, dict):
            files += _process_directory(root=root, **path)
        else:
            files += [os.path.relpath(x, root) for x in glob(path)]
    return files

