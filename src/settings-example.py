class Config(object):
	APP_HOST = '0.0.0.0'
	APP_PORT = 5304
	APP_VERSION = 'v1.1'

	DEBUG = True #debug mode (switch off in production environment)

	SECRET_KEY = 'some unique string' #required for using sessions

	AUTHENTICATION_METHOD = 'basic' #'OpenConext', #options [OpenConext, basic]
	OAUTH_CLIENT_ID = 'oauth client id'
	OAUTH_CLIENT_SECRET = 'oauth client secret'
	AUTHZ_SERVER = 'https://yourauthzserver'
	PW = '12345'

	SEARCH_API = 'http://localhost:5320/api/v1.1'

	ANNOTATION_API = 'http://localhost:5300/api'

	EXPORT_CONFIGS = {

	}