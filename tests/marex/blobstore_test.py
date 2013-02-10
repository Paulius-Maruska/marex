#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest

from google.appengine.api import files
from google.appengine.ext import blobstore

from tests.gaehelper import gaetestbed

from marex.blobstore import remove_files


class RemoveFilesTests(unittest.TestCase):
    def setUp(self):
        def create_dummy_file(name=None):
            blobstore_filename = files.blobstore.create(
                mime_type="text/plain",
                _blobinfo_uploaded_filename=name
            )
            with files.open(blobstore_filename, "a") as blobstore_file:
                blobstore_file.write("Lobster ALL the fetish!")

            files.finalize(blobstore_filename)

            return files.blobstore.get_blob_key(blobstore_filename)

        self.testbed = gaetestbed()
        self.testbed.activate('datastore', 'blobstore', 'files')

        self.blob_keys = [create_dummy_file(name='file_{}.bin'.format(i)) for i in range(10)]
        self.blob_uris = [files.blobstore.get_file_name(blob_key) for blob_key in self.blob_keys]
        self.blob_infos = blobstore.BlobInfo.get(self.blob_keys)

    def tearDown(self):
        self.testbed.deactivate()

    def count_existing_files(self):
        return len(filter(lambda blob_info: blob_info is not None, blobstore.BlobInfo.get(self.blob_keys)))

    def test_raises_when_passing_wrong_kwargs(self):
        with self.assertRaises(NameError):
            remove_files(*self.blob_keys, lobster='ALL the fetish!')

    def test_ignores_wrong_kwargs_when_ignore_errors_passed(self):
        self.assertEqual(len(self.blob_keys), self.count_existing_files())
        remove_files(*self.blob_keys, ignore_errors=True, lobster='ALL the fetish!')
        self.assertEqual(0, self.count_existing_files())

    def test_raises_when_no_parameters_given(self):
        with self.assertRaises(ValueError):
            remove_files()

    def test_ignores_no_parameters_when_ignore_errors_passed(self):
        self.assertEqual(len(self.blob_keys), self.count_existing_files())
        remove_files(ignore_errors=True)
        self.assertEqual(len(self.blob_keys), self.count_existing_files())

    def test_raises_when_passing_wrong_types(self):
        with self.assertRaises(TypeError):
            remove_files(*range(5))

    def test_ignores_wrong_types_when_ignore_errors_passed(self):
        self.assertEqual(len(self.blob_keys), self.count_existing_files())
        remove_files(*range(5), ignore_errors=True)
        self.assertEqual(len(self.blob_keys), self.count_existing_files())

    def test_removes_nothing_when_random_strings_are_passed(self):
        self.assertEqual(len(self.blob_keys), self.count_existing_files())
        remove_files(*["Lobster ALL the fetish {0}".format(i) for i in range(10)])
        self.assertEqual(len(self.blob_keys), self.count_existing_files())

    def test_removes_all_blobs_by_key(self):
        self.assertEqual(len(self.blob_keys), self.count_existing_files())
        remove_files(*self.blob_keys)
        self.assertEqual(0, self.count_existing_files())

    def test_removes_all_blobs_by_key_string(self):
        self.assertEqual(len(self.blob_keys), self.count_existing_files())
        remove_files(*[str(key) for key in self.blob_keys])
        self.assertEqual(0, self.count_existing_files())

    def test_removes_all_blobs_by_uri(self):
        self.assertEqual(len(self.blob_keys), self.count_existing_files())
        remove_files(*self.blob_uris)
        self.assertEqual(0, self.count_existing_files())

    def test_removes_all_blobs_by_info(self):
        self.assertEqual(len(self.blob_keys), self.count_existing_files())
        remove_files(*self.blob_infos)
        self.assertEqual(0, self.count_existing_files())

    def test_removes_all_blobs_with_mixed_parameters(self):
        self.assertEqual(len(self.blob_keys), self.count_existing_files())
        remove_files(*(self.blob_keys + self.blob_uris + self.blob_infos))
        self.assertEqual(0, self.count_existing_files())

    def test_removes_all_blobs_with_mixed_parameters_and_ignores_bad_values_with_ignore_errors(self):
        self.assertEqual(len(self.blob_keys), self.count_existing_files())
        remove_files(*(self.blob_keys + self.blob_uris + self.blob_infos + range(5)), ignore_errors=True)
        self.assertEqual(0, self.count_existing_files())
