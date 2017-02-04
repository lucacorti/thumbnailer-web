from django.conf.urls import url, include

urlpatterns = [
    url(r'', include('italist.thumbnailer.urls', namespace='italist.thumbnailer'),)
]
