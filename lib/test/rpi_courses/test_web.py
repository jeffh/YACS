import unittest
import urllib2
from rpi_courses import web
from mock import patch
from constants import HTML


class TestListUnits(unittest.TestCase):
    def setUp(self):
        self.url = "http://sis.rpi.edu/reg/rocs/"
        self.expected_files = map(lambda x: self.url + x, [
            '201001.xml',
            '201005.xml',
            '201009.xml',
            '201009.xml_old',
            '201101.xml',
            'testrocs.txt',
        ])

    @patch.object(web, 'get')
    def test_list_rocs_files(self, mock):
        """Lists files to read from a given url page.
        Expects an apache file listing page.
        """
        mock.return_value = HTML

        files = web.list_rocs_files(self.url)

        mock.assert_called_with(self.url)

        self.assertEqual(files, self.expected_files)

    @patch.object(web, 'get')
    def test_list_rocs_xml_files(self, mock):
        """Lists all the files ending with '.xml'.
        Expects an apache file listing page.
        """
        mock.return_value = HTML
        files = web.list_rocs_xml_files(self.url)

        mock.assert_called()

        self.expected_files.remove(self.url + '201009.xml_old')
        self.expected_files.remove(self.url + 'testrocs.txt')

        self.assertEqual(files, self.expected_files)

if __name__ == '__main__':
    unittest.main()
