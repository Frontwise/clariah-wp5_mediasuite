from flask import Flask
import requests
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

TEST WITH POLLY: https://netflix.github.io/pollyjs/#/README?id=features
"""

class TestFunctionalities:

    """<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><
    <><><><><><><><><><><><> SETUP & TEARDOWN <><><><><><><><><><><>
    <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><"""

    def setup(self):
        self.strictMode = True
        self.app = Flask(__name__)
        self.app.config.from_object('settings.Config')

        #TODO think of a way to dynamically obtain test data
        self.collectionId = 'nisv-catalogue-aggr'
        self.hostUrl = 'http://%s:%s' % (
            self.app.config['APP_HOST'],
            self.app.config['APP_PORT']
        )
        self.samlDir = os.path.join(myModules, 'components', 'security', 'resources')
        self.staticDir = os.path.join(myModules, 'static')

    def teardown(self):
        pass

    """----------------------------- TEST BASIC SETTINGS -------------------"""

    def test_settings_exist(self):
        assert os.path.exists(os.path.join(myModules, 'settings.py'))

    def test_settings_valid(self):
        assert 'APP_HOST' in self.app.config #'0.0.0.0'
        assert 'APP_PORT' in self.app.config #5304
        assert 'APP_VERSION' in self.app.config #v1.1
        assert 'DEBUG' in self.app.config #True/False
        assert 'SECRET_KEY' in self.app.config #str
        assert 'AUTHENTICATION_METHOD' in self.app.config #basic or OpenConext
        assert 'PW' in self.app.config #str
        assert 'OAUTH_CLIENT_ID' in self.app.config #optional str
        assert 'OAUTH_CLIENT_SECRET' in self.app.config #optional str
        assert 'AUTHZ_SERVER' in self.app.config #optional URL 'https://authz.proxy.clariah.nl'
        assert 'CLIENT_ID' in self.app.config #str 'clariah_test'
        assert 'TOKEN' in self.app.config #str
        assert 'SEARCH_API' in self.app.config #URL 'http://localhost:5320/api/v1.1'
        assert 'ANNOTATION_API' in self.app.config #URL 'http://annotation-test.rdlabs.beeldengeluid.nl/api'
        assert 'USER_SPACE_API' in self.app.config #URL 'http://workspace-test.rdlabs.beeldengeluid.nl/api/v0.1'
        assert 'PLAYOUT_API' in self.app.config #URL 'http://localhost:20999'
        assert 'EXPORT_CONFIGS' in self.app.config #object {}

    """----------------------------- TEST SAML DIRS -------------------"""

    def test_saml_dir_exists(self):
        assert os.path.exists(self.samlDir)

    def test_saml_settings_file_exists(self):
        assert os.path.exists(os.path.join(self.samlDir, 'settings.json'))

    def test_saml_advanced_settings_file_exists(self):
        assert os.path.exists(os.path.join(self.samlDir, 'advanced_settings.json'))

    """----------------------------- TEST JAVASCRIPT & STATIC CONTENT -------------------"""

    def test_static_dir_exists(self):
        assert os.path.exists(self.staticDir)

    def test_npm_installed(self):
        assert os.path.exists(os.path.join(self.staticDir, 'node_modules'))

    def test_labo_components_installed(self):
        assert os.path.exists(os.path.join(self.staticDir, 'node_modules', 'labo-components'))
        assert os.path.exists(os.path.join(self.staticDir, 'node_modules', 'labo-components', 'dist', 'labo-components.js'))
        #TODO change the webpack config in labo-components to change this stupid type and update all references to it
        assert os.path.exists(os.path.join(self.staticDir, 'node_modules', 'labo-components', 'dist', 'labo-component.css'))

    def test_css_stylesheet_generated(self):
        assert os.path.exists(os.path.join(self.staticDir, 'css', 'main.css'))

