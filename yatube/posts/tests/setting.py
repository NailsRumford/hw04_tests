import shutil
import tempfile

from django.test import TestCase, override_settings
from yatube.settings import BASE_DIR


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BaseTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    




