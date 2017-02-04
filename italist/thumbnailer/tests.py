from django.test import TestCase, Client
from django.urls import reverse


class PagesTest(TestCase):

    def setUp(self):
        self.c = Client()

    def test_existing_sizes_pages_200(self):
        r = self.c.get(reverse('italist.thumbnailer:index', kwargs={'size': 120}))
        assert(r.status_code == 200)

        r = self.c.get(reverse('italist.thumbnailer:index', kwargs={'size': 360}))
        assert(r.status_code == 200)

    def test_non_existing_sizes_pages_404(self):
        r = self.c.get(reverse('italist.thumbnailer:index', kwargs={'size': 4096}))
        assert(r.status_code == 404)
