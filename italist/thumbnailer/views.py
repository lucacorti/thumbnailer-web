from django.http import Http404

from django.views.generic import TemplateView


class ThumbnailerView(TemplateView):
    template_name = 'index.html'
    thumbnail_sizes = ['120', '360']

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('size') not in self.thumbnail_sizes:
            raise Http404

        return super(ThumbnailerView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ThumbnailerView, self).get_context_data(**kwargs)
        context['size'] = kwargs.get('size')
        context['sizes'] = self.thumbnail_sizes
        return context
