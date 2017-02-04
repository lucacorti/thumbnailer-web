from django.conf.urls import url

from italist.thumbnailer import views

urlpatterns = [
    url(r'(?P<size>\d+)/$', views.ThumbnailerView.as_view(), name='index')
]
