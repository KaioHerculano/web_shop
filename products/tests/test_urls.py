import importlib

from django.test import TestCase, override_settings

from products import urls as product_urls


class ProductUrlsAdvancedTest(TestCase):

    @override_settings(DEBUG=True)
    def test_urlpatterns_include_media_in_debug(self):
        """
        Força a recarga do módulo de URLs para verificar a adição
        das rotas de mídia quando DEBUG=True.
        """
        original_url_count = len(product_urls.urlpatterns)

        importlib.reload(product_urls)

        reloaded_url_count = len(product_urls.urlpatterns)
        self.assertGreater(reloaded_url_count, original_url_count)

        importlib.reload(product_urls)
