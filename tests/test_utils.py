#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import unittest

from paper2remarkable.exceptions import NoPDFToolError
from paper2remarkable.utils import chdir
from paper2remarkable.utils import check_pdftool
from paper2remarkable.utils import strip_default_port


class TestUtils(unittest.TestCase):
    def test_check_pdftool(self):
        # Needs a system with both pdftk and qpdf available
        self.assertEqual(check_pdftool("pdftk", "qpdf"), "pdftk")
        self.assertEqual(check_pdftool("pdftk_xyz", "qpdf"), "qpdf")
        self.assertEqual(check_pdftool("pdftk", "qpdf_xyz"), "pdftk")
        with self.assertRaises(NoPDFToolError):
            check_pdftool("pdftk_xyz", "qpdf_xyz")

    def test_chdir_1(self):
        start_dir = os.getcwd()
        tmpdir1 = tempfile.mkdtemp(prefix="p2r_test_chdir_")
        with chdir(tmpdir1):
            pwd = os.getcwd()
        self.assertEqual(pwd, tmpdir1)
        self.assertEqual(start_dir, os.getcwd())

    def test_chdir_2(self):
        start_dir = os.getcwd()
        tmpdir1 = tempfile.mkdtemp(prefix="p2r_test_chdir_")
        with self.assertRaises(ValueError):
            with chdir(tmpdir1):
                pwd = os.getcwd()
                raise ValueError
        self.assertEqual(pwd, tmpdir1)
        self.assertEqual(start_dir, os.getcwd())

    def test_strip_default_port(self):
        # default ports are dropped
        self.assertEqual(
            strip_default_port("https://example.com:443/a/b"),
            "https://example.com/a/b",
        )
        self.assertEqual(
            strip_default_port("http://example.com:80/a/b"),
            "http://example.com/a/b",
        )
        # non-default ports, and ports on the other scheme, are kept
        for url in [
            "https://example.com:8443/a/b",
            "http://example.com:8080/a/b",
            "https://example.com:80/a/b",
            "http://example.com:443/a/b",
        ]:
            self.assertEqual(strip_default_port(url), url)
        # urls without a port are untouched, including query and fragment
        for url in [
            "https://example.com/a/b",
            "https://example.com/a?x=1&y=2#frag",
            "https://example.com",
        ]:
            self.assertEqual(strip_default_port(url), url)
        # credentials survive the rewrite
        self.assertEqual(
            strip_default_port("https://user:pw@example.com:443/a"),
            "https://user:pw@example.com/a",
        )
        # a malformed port is left alone rather than raising
        self.assertEqual(
            strip_default_port("https://example.com:qq/a"),
            "https://example.com:qq/a",
        )


if __name__ == "__main__":
    unittest.main()
