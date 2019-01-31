# coding: utf-8


import os
from unittest import TestCase

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "files")


class BaseTestCase(TestCase):
    def _create_file(self, filename, content=""):
        self.files.append(filename)
        with open(filename, "a") as file_:
            file_.write(content)

    def setUp(self):
        self.test_files_path = os.path.join(os.path.dirname(__file__), "files")
        self.files = []

    def tearDown(self):
        for filename in self.files:
            os.remove(filename)
