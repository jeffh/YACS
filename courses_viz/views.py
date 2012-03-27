from courses.views.decorators import Renderer, staff_required


render = Renderer(template_prefix='courses_viz/')


@staff_required
@render()
def render_template(request, template):
    return {
        'template_name': template,
        'context': {},
    }
