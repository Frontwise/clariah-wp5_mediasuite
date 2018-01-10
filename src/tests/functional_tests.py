import requests
import unittest
import json
import os
import sys

#only needed if you run this module from command line
parts =  os.path.realpath(__file__).split('/')
myModules = '/'.join(parts[0:len(parts) -2])
if myModules not in sys.path:
	sys.path.append(myModules)


"""
on (integration) tests
	- http://eigenhombre.com/2013/04/13/integration-testing-in-python-with-context-managers/
	- http://stackoverflow.com/questions/1842168/python-unit-test-pass-command-line-arguments-to-setup-of-unittest-testcase
	- http://docs.python-soco.com/en/latest/unittests.html#running-the-unit-tests
	- https://hypothesis.readthedocs.org/en/latest/index.html
	- https://www.toptal.com/python/an-introduction-to-mocking-in-python
"""

class SettingsTest(unittest.TestCase):

    def setUp(self):
        self.settings = os.path.join(myModules, 'settings.py')

    def test_settings_exist(self):
        assert os.path.exists(self.settings)


class ServerTest(unittest.TestCase):

    def setUp(self):
        from settings import config
        self.hostUrl = 'http://%s:%s' % (config['APP_HOST'], config['APP_PORT'])

    def test_server_response_and_content_ok(self):
        response = requests.get(self.hostUrl)
        assert response.status_code == 200
        assert "<html>" in response.content

    def test_invalid_urls(self):
        response = requests.get(self.hostUrl + "/doesnotexist/")
        assert response.status_code == 404

class SearchAPITest(unittest.TestCase):

    def setUp(self):
        from settings import config
        self.searchAPIBase = config['SEARCH_API']

    def test_search_api_response_and_content(self):
        response = requests.get(self.searchAPIBase)
        assert response.status_code == 200

class SAMLTest(unittest.TestCase):

    def setUp(self):
        self.samlDir = os.path.join(myModules, 'components', 'external', 'login', 'saml')

    def test_saml_dir_exists(self):
        assert os.path.exists(self.samlDir)

    def test_saml_settings_file_exists(self):
        assert os.path.exists(os.path.join(self.samlDir, 'settings.json'))

    def test_saml_advanced_settings_file_exists(self):
        assert os.path.exists(os.path.join(self.samlDir, 'advanced_settings.json'))

class ClientTest(unittest.TestCase):

    def setUp(self):
        self.staticDir = os.path.join(myModules, 'static')

    def test_static_dir_exists(self):
        assert os.path.exists(self.staticDir)

    def test_npm_installed(self):
        assert os.path.exists(os.path.join(self.staticDir, 'node_modules'))

    def test_labo_components_installed(self):
        assert os.path.exists(os.path.join(self.staticDir, 'node_modules', 'labo-components'))
        assert os.path.exists(os.path.join(self.staticDir, 'node_modules', 'labo-components', 'dist', 'labo-components.js'))
        assert os.path.exists(os.path.join(self.staticDir, 'node_modules', 'labo-components', 'dist', 'labo-components.css'))

    def test_css_stylesheet_generated(self):
        assert os.path.exists(os.path.join(self.staticDir, 'css', 'main.css'))



if __name__ == "__main__":
    unittest.main()
