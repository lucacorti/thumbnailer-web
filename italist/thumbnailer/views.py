import base64
import uuid

from aws_requests_auth.aws_auth import AWSRequestsAuth
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.http import Http404
from django.shortcuts import render
from django.views.generic import View

import requests
from requests import ConnectionError

from italist.thumbnailer.models import Thumbnail


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
        size = kwargs.get('size')
        context.update({'thumbnails': Thumbnail.objects.filter(size=int(size))})
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(request, *args, **kwargs)
        image = request.FILES.get('image').read()
        size = kwargs.get('size')

        status, payload = self._call_thumbnailer(size, image)

        if status is 'error':
            context.update({'error': payload})

        if status is 'thumbnail':
            context.update({'message': 'File uploaded'})
            context.update({'thumbnails': Thumbnail.objects.filter(size=int(size))})

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

        try:
            response = requests.post(
                url,
                auth=auth,
                json={'size': int(size), 'data': base64.b64encode(data)}
            )
            json = response.json()
        except (ConnectionError, ValueError):
            return 'error', 'Service temporary unavailable'

        if response.status_code is not 200:
            error = json.get('error')
            return 'error', error if error else 'Service temporary unavailable'

        try:
            new_data = base64.b64decode(json.get('data'))
        except TypeError:
            return 'error', 'Service temporary unavailable'

        thumbnail = Thumbnail()
        thumbnail.size = int(size)
        thumbnail.image.save(str(uuid.uuid4()), ContentFile(new_data))
        thumbnail.save()

        return 'thumbnail', thumbnail
