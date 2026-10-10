#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Additional tests for the HTML provider

This file is part of paper2remarkable.

"""

import os
import unittest

import pdfplumber

from paper2remarkable.providers.html import HTML
from paper2remarkable.providers.html import make_readable
from paper2remarkable.utils import get_page_with_retry


class TestHTML(unittest.TestCase):
    @unittest.skip("Broken test (other url needed)")
    def test_experimental_fix_lazy_loading(self):
        # 2021-05-11 NOTE: This is the only URL I know where the experimental
        # lazy loading fix was useful. It no longer works because Readability
        # strips out the images for this site. If anyone knows of a test case
        # where the experimental fix makes a difference, let me know.
        url = "https://www.seriouseats.com/2015/01/tea-for-everyone.html"
        prov = HTML(upload=False, experimental=True)
        page = get_page_with_retry(url, return_text=True)
        title, article = make_readable(page)
        html_article = prov.preprocess_html(url, title, article)
        expected_image = "https://www.seriouseats.com/images/2015/01/20150118-tea-max-falkowitz-3.jpg"
        self.assertIn(expected_image, html_article)

    def test_custom_css(self):
        """Custom CSS should reach WeasyPrint, checked through the page size

        This used to render a live hbr.org article and assert a page count,
        but that url is paywalled now, so readability returns only the page
        header and the count no longer means anything. The article is fed in
        through the informer cache instead, which keeps the test offline and
        makes it assert the thing it is named after.
        """
        test_css = """
        @page { size: 702px 936px; margin: 1in; }
        img { display: block; margin: 0 auto; text-align: center; max-width: 70%; max-height: 300px; }
        h1,h2,h3 { font-family: sans-serif; }
        p, li { font-size: 12pt; line-height: 2; text-align: left; }
        """

        prov = HTML(upload=False, css=test_css, font_urls=[])
        prov.informer._cached_title = "Test Article"
        prov.informer._cached_article = "<p>{}</p>".format(
            "Lorem ipsum dolor sit amet. " * 200
        )

        filename = "test_custom_css.pdf"
        prov.retrieve_pdf("https://example.com/article", filename)
        with pdfplumber.open(filename) as pdf:
            # 702px by 936px at 96 css px per inch is 526.5pt by 702pt
            self.assertAlmostEqual(float(pdf.pages[0].width), 526.5, places=1)
            self.assertAlmostEqual(float(pdf.pages[0].height), 702.0, places=1)
            self.assertGreaterEqual(len(pdf.pages), 1)

        os.unlink(filename)

    def test_table_rendering(self):
        """Test that HTML tables are properly rendered in the PDF output."""
        test_html = """
        <html>
        <body>
            <h1>Test Table</h1>
            <table>
                <tr>
                    <th>Header 1</th>
                    <th>Header 2</th>
                </tr>
                <tr>
                    <td>Data 1</td>
                    <td>Data 2</td>
                </tr>
                <tr>
                    <td>Data 3</td>
                    <td>Data 4</td>
                </tr>
            </table>
        </body>
        </html>
        """

        prov = HTML(upload=False)
        title, article = make_readable(test_html)
        html_article = prov.preprocess_html("test_url", title, article)

        # Verify table structure is preserved
        self.assertIn("<table>", html_article)
        self.assertIn("<th>", html_article)
        self.assertIn("<td>", html_article)

        # Verify table content is present
        self.assertIn("Header 1", html_article)
        self.assertIn("Data 1", html_article)
        self.assertIn("Data 4", html_article)


if __name__ == "__main__":
    unittest.main()
