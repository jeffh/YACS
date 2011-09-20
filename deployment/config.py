import sys
import json

class DeploymentConfig(object):
    "Abstracts the data storage mechanism from the fabric file."
    def __init__(self, filename, mode):
        self.mode = mode
        with open(filename, 'r') as h:
            self.obj = json.loads(h.read())
    
    def assign_to_env(self, env):
        if 'hosts' in self.deployment_settings:
            env.hosts = self.hosts
        else:
            env.roledefs = self.roles
        return self

    @property
    def deployment_settings(self):
        return self.obj[self.mode]
    
    @property
    def hosts(self):
        results = []
        obj = self.deployment_settings
        for host in obj['hosts']:
            try:
                results.append(self.servers[host])
            except KeyError:
                print >> sys.stderr, "(%(mode)s) Unknown server %(server)r" % {
                    'mode': self.mode,
                    'server': obj['hosts'],
                }
                raise
        return results

    @property
    def roles(self):
        results = {}
        obj = self.deployment_settings
        for role in obj['roles']:
            try:
                results[role] = [self.servers[name] for name in obj['roles'][role]]
            except KeyError:
                print >> sys.stderr, "(%(mode)s) Unknown server %(server)r for role %(role)r" % {
                    'mode': self.mode,
                    'server': obj['roles'][role],
                    'role': role,
                }
                raise
        return results
    
    @property
    def servers(self):
        return self.obj['servers'].copy()

    @property
    def project_root(self):
        return self.deployment_settings['project_root']

    @property
    def virtualenv_name(self):
        return self.deployment_settings['virtualenv']

    @property
    def databases(self):
        return self.deployment_settings['databases']

