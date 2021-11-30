from django.test import TestCase


class TestViews(TestCase):

    """Class used to test the views in the home app"""

    def test_get_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/index.html')
