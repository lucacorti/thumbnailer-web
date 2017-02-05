import base64

from aws_requests_auth.aws_auth import AWSRequestsAuth
from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.views.generic import View

import requests


class ThumbnailerView(View):
    template_name = 'index.html'
    thumbnail_sizes = ['120', '360']

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('size') not in self.thumbnail_sizes:
            raise Http404

        return super(ThumbnailerView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, request, *args, **kwargs):
        return {'size': kwargs.get('size'), 'sizes': self.thumbnail_sizes}

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request, *args, **kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(request, *args, **kwargs)
        image = request.FILES.get('image').read()
        size = kwargs.get('size')

        status, payload = self._call_thumbnailer(size, image)

        if status is 'error':
            context.update({'error': payload})

        return render(request, self.template_name, context)

    def _call_thumbnailer(self, size, data):
        config = settings.THUMBNAILER
        url = config.get('URL')
        key = config.get('AWS_KEY')
        secret = config.get('AWS_KEY')
        region = config.get('AWS_REGION')
        auth = None
        if key and secret:
            auth = AWSRequestsAuth(
                aws_access_key=key,
                aws_secret_access_key=secret,
                aws_host=url,
                aws_region=region,
                aws_service='es'
            )

        response = requests.post(
            url,
            auth=auth,
            json={'size': int(size), 'data': base64.b64encode(data)}
        )

        try:
            json = response.json()
        except ValueError:
            return 'error', 'Service temporary unavailable'

        error = json.get('error')
        if error:
            return 'error', error

        thumbnail = base64.b64decode(json.get('data'))

        return 'thumbnail', thumbnail