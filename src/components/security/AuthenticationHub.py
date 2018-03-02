# -*- coding: utf-8 -*-
from flask import session, make_response, request, redirect, current_app, render_template, url_for
from flask.views import View

from urlparse import urlparse
from uuid import uuid4
import urllib
import requests
import os
import json

"""------------------------------------------------------------------------
-------------------- INITIALIZES THE AUTH SUPPORT / SHARED INTERFACE ------
------------------------------------------------------------------------"""

class AuthenticationHub(object):

	def __init__(self, app):
		self.app = app
		if self.app.config['AUTHENTICATION_METHOD'] == 'OpenConext':
			self.app.config['SAML_PATH'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'resources')
			self.app.add_url_rule(
				'/saml/login/',
				view_func=SAMLLogin.as_view('login', authenticationHub=self),
				endpoint='saml_login'
			)
			self.app.add_url_rule(
				'/saml/logout/',
				view_func=SAMLLogout.as_view('logout', authenticationHub=self),
				endpoint='saml_logout'
			)
			self.app.add_url_rule(
				'/saml/acs/',
				view_func=SAMLACS.as_view('acs', authenticationHub=self),
				endpoint='saml_acs'
			)
			self.app.add_url_rule(
				'/metadata/',
				view_func=SAMLMetadata.as_view('metadata', authenticationHub=self),
				endpoint='saml_metadata'
			)
			self.app.add_url_rule(
				'/get_code',
				view_func=OauthGetCodeView.as_view('oauth_get_code', authenticationHub=self),
				endpoint='oauth_get_code'
			)

	def getUser(self, request):
		if self.app.config['AUTHENTICATION_METHOD'] == 'OpenConext':
			if len(session)>0 and 'samlUserdata' in session:
				return {
					'id' : session['samlUserdata']['urn:mace:dir:attribute-def:uid'][0], #TODO is there a real ID?
					'name' : session['samlUserdata']['urn:mace:dir:attribute-def:uid'][0],
					'attributes' : session['samlUserdata']
				}
		elif self.isAuthenticated(request): #basic auth
			return {
				'id' : self.app.config['CLIENT_ID'],
				'name' : self.app.config['CLIENT_ID'],
				'attributes' : {
					'allowPersonalCollections' : True #only allow for phoney test user outside of Openconext
				}
			}
		return None

	def isAuthenticated(self, request):
		if self.app.config['AUTHENTICATION_METHOD'] == 'OpenConext':
			if not 'samlIsAuthenticated' in session:
				session['samlIsAuthenticated'] = False
			return session['samlIsAuthenticated']
		else:
			if request.authorization:
				if request.authorization.username == 'admin' and request.authorization.password == self.app.config['PW']:
					return True
		return False

"""------------------------------------------------------------------------
-------------------- ALL THESE VIEWS ARE ADDED TO THE FLASK APPLICATION ---
------------------------------------------------------------------------"""

#PATH=/saml/login/, triggers flow of login requests
class SAMLLogin(View):
	methods = ['GET']

	def __init__(self, authenticationHub):
		self.authenticationHub = authenticationHub

	def dispatch_request(self):
		saml = SAMLRequest(self.authenticationHub, request)
		return redirect(saml.sso())

#PATH=/saml/login/, triggers flow of login requests
class SAMLLogout(View):
	methods = ['GET']

	def __init__(self, authenticationHub):
		self.authenticationHub = authenticationHub

	def dispatch_request(self):
		saml = SAMLRequest(self.authenticationHub, request)
		return redirect(saml.slo())

#PATH=/saml/acs/, called by OpenConext after processing a login request via SAMLRequest.sso()
class SAMLACS(View):
	methods = ['POST']

	def __init__(self, authenticationHub):
		self.authenticationHub = authenticationHub

	def dispatch_request(self):
		saml = SAMLRequest(self.authenticationHub, request)
		return saml.acs()

#PATH=/metadata/, used for registering this SAML Service Provider in OpenConext (called via OpenConext)
class SAMLMetadata(View):
	methods = ['POST']

	def __init__(self, authenticationHub):
		self.authenticationHub = authenticationHub

	def dispatch_request(self):
		saml = SAMLRequest(self.authenticationHub, request)
		return saml.showMetadata()

#PATH=/get_code, called by OpenConext after being called via OAuthRequest.requestOAuthCode()
class OauthGetCodeView(View):
    methods = ['GET']

    def __init__(self, authenticationHub):
		self.authenticationHub = authenticationHub

    def dispatch_request(self):
    	oauth = OAuthRequest(self.authenticationHub)
        return oauth.OAuthCodeReceived()


"""------------------------------------------------------------------------
-------------------- CONTAINS ALL FUNCTIONS FOR SAML REQUESTS ------------_
------------------------------------------------------------------------"""

class SAMLRequest(object):

	def __init__(self, authenticationHub, request_data):
		from onelogin.saml2.auth import OneLogin_Saml2_Auth
		self.authenticationHub = authenticationHub
		self.request = self.prepare_flask_request(request_data)
		self.auth = OneLogin_Saml2_Auth(
			self.request,
			custom_base_path=current_app.config['SAML_PATH']
		)
		self.errors = []
		self.not_auth_warn = False
		self.success_slo = False
		self.attributes = False
		self.logged_in = False

	def serialize(self):
		return dict(
			errors=self.errors,
			not_auth_warn=self.not_auth_warn,
			#success_slo=self.success_slo,
			attributes=self.attributes,
			logged_in=self.logged_in
		)

	def prepare_flask_request(self, request_data):
		url_data = urlparse(request_data.url)
		return {
			'https': 'on' if request_data.scheme == 'https' else 'off',
			'http_host': request_data.host,
			'server_port': url_data.port,
			'script_name': request_data.path,
			'get_data': request_data.args.copy(),
			'post_data': request_data.form.copy()
		}

	def sso(self):
		return self.auth.login()

	def slo(self):
		"""
		name_id = None
		session_index = None
		if 'samlNameId' in session:
			name_id = session['samlNameId']
		if 'samlSessionIndex' in session:
			session_index = session['samlSessionIndex']
		return self.auth.logout(name_id=name_id, session_index=session_index)
		"""
		session.clear()
		return url_for('home')

	def acs(self):
		self.auth.process_response()
		self.errors = self.auth.get_errors()
		self.not_auth_warn = not self.auth.is_authenticated()
		if len(self.errors) == 0:
			session['samlUserdata'] = self.auth.get_attributes()
			session['samlNameId'] = self.auth.get_nameid()
			session['samlSessionIndex'] = self.auth.get_session_index()
			session['samlIsAuthenticated'] = self.auth.is_authenticated()

			#for serialization of the results
			self.logged_in = self.auth.is_authenticated()
			if len(session['samlUserdata']) > 0:
				self.attributes = session['samlUserdata'].items()

		return self.afterACS(self.serialize())

	#gets here only if the user has logged-in successfully, so it can be redirected to the authz server without needing to login
	def afterACS(self, acs):
		if self.authenticationHub.isAuthenticated(request):
			oauth = OAuthRequest(self.authenticationHub)
			return redirect(oauth.requestOAuthCode(request.host))
		#elif not 'OAuthToken' in session:
		#	oauth = OAuthRequest(self.authenticationHub)
		#	return redirect(oauth.requestOAuthCode(request.host))
		#else:
		#	print 'Already got an OAuthToken: %s' % session['OAuthToken']
		if 'errors' in acs:
			return render_template(
				'login-failed.html',
				errors=acs['errors'],
				version=current_app.config['APP_VERSION']
			)
		return redirect(url_for('home'))

	def sls(self):
		dscb = lambda: session.clear()
		url = self.auth.process_slo(delete_session_cb=dscb)
		self.errors = self.auth.get_errors()
		if len(self.errors) == 0:
			if url is not None:
				return url
			else:
				self.success_slo = True
		return self.serialize()

	def showMetadata(self):
		settings = self.auth.get_settings()
		metadata = settings.get_sp_metadata()
		errors = settings.validate_metadata(metadata)
		if len(errors) == 0:
			resp = make_response(metadata, 200)
			resp.headers['Content-Type'] = 'text/xml'
		else:
			resp = make_response(errors.join(', '), 500)
		return resp


"""------------------------------------------------------------------------
-------------------- CONTAINS ALL FUNCTIONS FOR OAUTH REQUESTS ------------
------------------------------------------------------------------------"""

class OAuthRequest(object):

	def __init__(self, authenticationHub):
		self.authenticationHub = authenticationHub

	#1st OAuth step: request a code
	def requestOAuthCode(self, host):
		# Generate a random string for the state parameter
		# Save it for use later to prevent xsrf attacks
		params = {
			"client_id": current_app.config['OAUTH_CLIENT_ID'],
			"response_type": "code",
			"state": str(uuid4()),
			"redirect_uri": 'http://%s/get_code' % host,
			"duration": "temporary",
			"scope": "groups"
		}
		url = "%s/oauth/authorize?%s" % (current_app.config['AUTHZ_SERVER'], urllib.urlencode(params))
		return url

	#PATH=/get_code/ is called by the authz server after receiving a getCode request
	def OAuthCodeReceived(self):
		error = request.args.get('error', '')
		if error:
			return "Error: " + error
		state = request.args.get('state', '')
		if not self.isValidState(state):
			# Uh-oh, this request wasn't started by us!
			abort(403)

		#Now request the OAuth token with the acquired code
		resp = self.requestOAuthToken(request.args.get('code'))
		if 'access_token' in resp:
			oAuthToken = resp['access_token']
			session['OAuthToken'] = oAuthToken
		else:
			print resp

		#always redirect to the URL the user requested
		return redirect(session['requestedURL'])

	#useless function: maybe fill in later?
	def isValidState(self, state):
		return True

	#2nd OAuth step: use the code to request an OAuth token
	def requestOAuthToken(self, code):
		client_auth = requests.auth.HTTPBasicAuth(
			current_app.config['OAUTH_CLIENT_ID'],
			current_app.config['OAUTH_CLIENT_SECRET']
		)
		post_data = {
			"grant_type": "authorization_code",
			"code": code,
			"redirect_uri": 'http://%s/get_code' % request.host
		}
		#headers = base_headers()
		response = requests.post(
			"https://authz.proxy.clariah.nl/oauth/token",
			auth=client_auth,
			headers={'Content-type': 'application/x-www-form-urlencoded'},
			data=post_data,
			verify=False
		)
		token_json = response.json()
		return token_json
