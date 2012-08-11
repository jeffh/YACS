from django.views.generic import RedirectView
from django.core.urlresolvers import reverse

from courses.views.decorators import Renderer, staff_required


render = Renderer(template_prefix='courses_viz/')


@render()
def render_template(request, template):
    return {
        'template_name': template,
        'context': {},
    }


class DefaultRedirect(RedirectView):
    def get_redirect_url(self):
        return reverse('courses_viz:bubble')
