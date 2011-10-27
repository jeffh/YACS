import StringIO
import hotshot
import hotshot.stats
import os
import tempfile
import traceback
from django.conf import settings
from django.template import Template, Context
from debug_toolbar.panels import DebugPanel

class ProfilingPanel(DebugPanel):
    """
    Panel that runs the hotshot profiler during the request.
    """

    name = 'Profiling'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(ProfilingPanel, self).__init__(*args, **kwargs)
        self.formatted_stats = ''
        self.stats = None

    def nav_title(self):
        """Title showing in toolbar"""
        return 'Profiling'

    def nav_subtitle(self):
        """Subtitle showing until title in toolbar"""
        if self.stats:
            return "%d function calls in %.3f CPU seconds" % (self.stats.total_calls, self.stats.total_tt)
        else:
            return "self.stats evaluates to False"

    def title(self):
        """Title showing in panel"""
        return 'Profiling'

    def url(self):
        return ''

    def content(self):
        if self.stats and not self.formatted_stats:
            try:
                buffer = StringIO.StringIO()
                self.stats.stream = buffer
                self.stats.sort_stats('time', 'calls')
                self.stats.print_stats(400)
                self.formatted_stats = buffer.getvalue()
            except:
                print "Error getting hotshot stats:"
                traceback.print_exc()

        template = Template("""<code>{{ formatted_stats }}</code>""")
        context = Context()
        context.update(self.context)
        context.update({
            'formatted_stats': self.formatted_stats,
        })
        return template.render(context)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith(settings.ADMIN_MEDIA_PREFIX) or request.path.startswith('/__debug__/'):
            return None

        # Add a timestamp to the profile output when the callable is actually called.
        handle, filename = tempfile.mkstemp(prefix='profiling')
        os.close(handle)
        prof = hotshot.Profile(filename)
        try:
            try:
                try:
                    result = prof.runcall(view_func, *((request,) + view_args), **view_kwargs)
                finally:
                    prof.close()
            except:
                raise
            else:
                self.stats = hotshot.stats.load(filename)
                return result
        finally:
            os.unlink(filename)
