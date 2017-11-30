#flask imports
from flask import Flask
from flask import render_template, abort, session, redirect, url_for
from flask import request, Response, send_from_directory
from jinja2.exceptions import TemplateNotFound
from functools import wraps

#for authentication
from components.security.AuthenticationHub import AuthenticationHub

#for autocompletion & searching through external collections (move this to some external API)
from components.external.openskos.OpenSKOS import OpenSKOS
from components.external.dbpedia.DBpedia import DBpedia
from components.external.wikidata.WikiData import WikiData
from components.external.europeana.Europeana import Europeana
from components.external.unesco.Unesco import Unesco

#exporting / generating indices for certain instances of LABO
from components.export.AnnotationExporter import AnnotationExporter

#standard python
import json
import requests
import os

#import the settings and put them in a global variable
#from settings import config

#initialise the application object
app = Flask(__name__)

app.config.from_object('settings.Config')

app.debug = app.config['DEBUG']

app.config['RECIPES'] = None #loaded once when a recipe is requested for the first time
app.config['COLLECTION_DATA'] = None #loaded once on startup


"""------------------------------------------------------------------------------
AUTHENTICATION FUNCTIONS
------------------------------------------------------------------------------"""

#this object is used for everything related to authentication/authorization
_authenticationHub = AuthenticationHub(app)

#decorator that makes sure to check whether the user is authorized based on the configured authorization method
def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		session['requestedURL'] = str(request.path)
		auth = _authenticationHub.isAuthenticated(request)
		#if not logged in redirect the user depending on the authentication method
		if not auth:
			if app.config['AUTHENTICATION_METHOD'] == 'OpenConext':
				return redirect(url_for('saml_login'))
			else: #basic auth
				return Response(
					'Could not verify your access level for that URL.\n'
					'You have to login with proper credentials', 401,
					{'WWW-Authenticate': 'Basic realm="Login Required"'}
				)

		#otherwise the user can access the originally requested page
		return f(*args, **kwargs)
	return decorated


"""------------------------------------------------------------------------------
LOADING RECIPES FROM JSON FILES
------------------------------------------------------------------------------"""

#This function is only executed once on startup and should be used to load global variables/data
@app.before_first_request
def serverInit():
	loadRecipes()

def loadRecipes():
	recipes = {}
	recipeDir = 'default'
	for root, directories, files in os.walk(os.path.join(app.root_path, 'resources', 'recipes')):
		for fn in files:
			if fn.find('.json') != -1:
				path = os.path.join(root, fn)
				recipe = json.load(open(path, 'r'))

				#add the standard URL for recipes that have no URL defined.
				if not 'url' in recipe:
					recipe['url'] = '/recipe/%s' % recipe['id'];

				recipes[fn.replace('.json', '')] = recipe
	app.config['RECIPES'] = recipes

"""------------------------------------------------------------------------------
UNIFIED DEFAULT SUCCESS & ERROR RESPONSE FUNCTIONS
------------------------------------------------------------------------------"""

def getErrorMessage(msg):
	return json.dumps({'error' : msg})

def getSuccessMessage(msg, data):
	return json.dumps({'success' : msg, 'data' : data})


"""------------------------------------------------------------------------------
PING / HEARTBEAT ENDPOINT
------------------------------------------------------------------------------"""

@app.route('/ping')
def ping():
	return Response('pong', mimetype='text/plain')

"""------------------------------------------------------------------------------
STATIC PAGES THAT DO NOT USE THE COMPONENT LIBRARY
------------------------------------------------------------------------------"""

@app.route('/')
def home():
	#check logged in
	for c in request.cookies:
		print c
	return render_template('index.html', user=_authenticationHub.getUser(request), version=app.config['APP_VERSION'])

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
	return send_from_directory(app.static_folder, request.path[1:])

@app.route('/favicon.jpeg')
def favicon():
	return getFavicon()

@app.route('/help-feedback')
def helpfeedback():
	return render_template('help-feedback.html', user=_authenticationHub.getUser(request), version=app.config['APP_VERSION'])

@app.route('/about')
def about():
	return render_template('about.html', user=_authenticationHub.getUser(request), version=app.config['APP_VERSION'])

@app.route('/contact')
def contact():
	return render_template('contact.html', user=_authenticationHub.getUser(request), version=app.config['APP_VERSION'])

@app.route('/datasources')
def datasources():
	return render_template('data-sources.html', user=_authenticationHub.getUser(request), version=app.config['APP_VERSION'])

@app.route('/apis')
@requires_auth
def apis():
	return render_template('apis.html',
		user=_authenticationHub.getUser(request),
		version=app.config['APP_VERSION'],
		searchAPI=app.config['SEARCH_API'],
		annotationAPI=app.config['ANNOTATION_API']
	)

@app.route('/userspace')
@requires_auth
def userspace():
	params = {}
	for x in dict(request.args).keys():
		params[x] = request.args.get(x)

	#determine the token (either from the config or the session)
	token = None
	if 'OAuthToken' in session:
		token = session['OAuthToken']
	elif 'TOKEN' in app.config:
		token = app.config['TOKEN']

	#get the client id from the config
	clientId = None
	if 'CLIENT_ID' in app.config:
		clientId = app.config['CLIENT_ID']

	return render_template('userspace.html',
		recipe=app.config['RECIPES']['user-space'],
		params=params,
		instanceId='clariah',
		searchAPI=app.config['SEARCH_API'],
		searchAPIPath=app.config['SEARCH_API_PATH'],
		user=_authenticationHub.getUser(request),
		userSpaceAPI=app.config['USER_SPACE_API'],
		version=app.config['APP_VERSION'],
		annotationAPI=app.config['ANNOTATION_API'],
		annotationAPIPath=app.config['ANNOTATION_API_PATH'],
		token=token,
		clientId=clientId,
		play=app.config['PLAYOUT_API']
	)

@app.route('/recipes')
@requires_auth
def recipes():
	return render_template(
		'recipes.html',
			recipes=app.config['RECIPES'],
			user=_authenticationHub.getUser(request),
			version=app.config['APP_VERSION']
	)



"""------------------------------------------------------------------------------
WORKSPACE UTILS
------------------------------------------------------------------------------"""

# determine the token (either from the config or the session)
def getToken():
	if 'OAuthToken' in session:
		return session['OAuthToken']
	elif 'TOKEN' in app.config:
		return app.config['TOKEN']
	return None

# flatten the params and put them in a normal dict
def getParams():
	params = {}
	for x in dict(request.args).keys():
		params[x] = request.args.get(x)

# get the client id from the config
def getClientId():
	return app.config['CLIENT_ID'] if 'CLIENT_ID' in app.config else None


"""------------------------------------------------------------------------------
WORKSPACE PAGES
------------------------------------------------------------------------------"""


# Project overview

@app.route('/workspace/projects')
@requires_auth
def wsProjects():

	params = getParams()
	token = getToken()
	clientId = getClientId()

	return render_template('workspace/projects/overview.html',
		params=params,
		userSpaceAPI=app.config['USER_SPACE_API'],
		recipe=app.config['RECIPES']['ws-projects'],
		user=_authenticationHub.getUser(request),
		token=token,
		clientId=clientId
	)

# Show project's bookmarks & annotations
# This is also the default page

@app.route('/workspace/projects/<int:projectId>')
@app.route('/workspace/projects/<int:projectId>/bookmarks')
@requires_auth
def wsProjectBookmarks(projectId):

	params = getParams()
	token = getToken()
	clientId = getClientId()

	return render_template('workspace/projects/bookmarks.html',
		params=params,
		userSpaceAPI=app.config['USER_SPACE_API'],
		projectId=projectId,
		recipe=app.config['RECIPES']['ws-project-bookmarks'],
		user=_authenticationHub.getUser(request),
		token=token,
		clientId=clientId
	)

# Show project's details

@app.route('/workspace/projects/<int:projectId>/details')
@requires_auth
def wsProjectDetails(projectId):

	params = getParams()
	token = getToken()
	clientId = getClientId()

	return render_template('workspace/projects/details.html',
		params=params,
		userSpaceAPI=app.config['USER_SPACE_API'],
		projectId=projectId,
		user=_authenticationHub.getUser(request),
		token=token,
		clientId=clientId
	)

# Show project's tool sessions

@app.route('/workspace/projects/<int:projectId>/sessions')
@requires_auth
def wsProjectSessions(projectId):

	params = getParams()
	token = getToken()
	clientId = getClientId()

	return render_template('workspace/projects/sessions.html',
		params=params,
		recipe=app.config['RECIPES']['ws-project-sessions'],
		userSpaceAPI=app.config['USER_SPACE_API'],
		projectId=projectId,
		user=_authenticationHub.getUser(request),
		token=token,
		clientId=clientId
	)

# Create a new project

@app.route('/workspace/projects/create', methods=['GET', 'POST'])
@requires_auth
def wsProjectCreate():

	#todo: handle post

	params = getParams()
	token = getToken()
	clientId = getClientId()

	return render_template('workspace/projects/create.html',
		params=params,
		user=_authenticationHub.getUser(request),
		token=token,
		clientId=clientId
	)


# Edit a project

@app.route('/workspace/projects/<int:projectId>/edit', methods=['GET', 'POST'])
@requires_auth
def wsProjectEdit(projectId):

	#todo: handle post
	#
	params = getParams()
	token = getToken()
	clientId = getClientId()

	return render_template('workspace/projects/edit.html',
		params=params,
		projectId=projectId,
		# todo: project entity
		# project=project
		user=_authenticationHub.getUser(request),
		token=token,
		clientId=clientId
	)


"""------------------------------------------------------------------------------
PAGES THAT DO USE THE COMPONENT LIBRARY
------------------------------------------------------------------------------"""

@app.route('/recipe/<recipeId>')
@requires_auth
def recipe(recipeId):
	#flatten the params and put them in a normal dict
	params = {}
	for x in dict(request.args).keys():
		params[x] = request.args.get(x)

	if app.config['RECIPES'].has_key(recipeId):
		recipe = app.config['RECIPES'][recipeId]

		#determine the token (either from the config or the session)
		token = None
		if 'OAuthToken' in session:
			token = session['OAuthToken']
		elif 'TOKEN' in app.config:
			token = app.config['TOKEN']

		#get the client id from the config
		clientId = None
		if 'CLIENT_ID' in app.config:
			clientId = app.config['CLIENT_ID']
		return render_template(
			'recipe.html',
				recipe=recipe,
				params=params,
				instanceId='clariah',
				searchAPI=app.config['SEARCH_API'],
				searchAPIPath=app.config['SEARCH_API_PATH'],
				user=_authenticationHub.getUser(request),
				userSpaceAPI=app.config['USER_SPACE_API'],
				version=app.config['APP_VERSION'],
				annotationAPI=app.config['ANNOTATION_API'],
				annotationAPIPath=app.config['ANNOTATION_API_PATH'],
				token=token,
				clientId=clientId,
				play=app.config['PLAYOUT_API']
		), 200, {'Access-Control-Allow-Credentials' : 'true'}

	return render_template('404.html', user=_authenticationHub.getUser(request), version=app.config['APP_VERSION']), 404

@app.route('/components')
@requires_auth
def components():
	return render_template('components.html',
		user=_authenticationHub.getUser(request),
		version=app.config['APP_VERSION'],
		instanceId='clariah',
		searchAPI=app.config['SEARCH_API'],
		searchAPIPath=app.config['SEARCH_API_PATH'],
		annotationAPI=app.config['ANNOTATION_API'],
		annotationAPIPath=app.config['ANNOTATION_API_PATH']
	)

"""------------------------------------------------------------------------------
EXPORT API
------------------------------------------------------------------------------"""

@app.route('/export')
@requires_auth
def export():
	script = request.args.get('s', None)
	operation = request.args.get('o', None)
	if script:
		ex = AnnotationExporter(app.config)
		resp = ex.execute(script, operation)
		if resp:
			return Response(getSuccessMessage('Succesfully run the %s script' % script, resp), mimetype='application/json')
		return Response(getErrorMessage('Failed to run the %s script' % script), mimetype='application/json')
	return Response(getErrorMessage('Please provide all the necessary parameters'), mimetype='application/json')

"""------------------------------------------------------------------------------
AUTOCOMPLETE END POINT
------------------------------------------------------------------------------"""

#see the components.external package for different autocompletion APIs
@app.route('/autocomplete')
@requires_auth
def autocomplete():
	term = request.args.get('term', None)
	vocab = request.args.get('vocab', 'DBpedia')
	conceptScheme = request.args.get('cs', None) #only for GTAA (not used yet!!)
	if term:
		options = None
		if vocab == 'GTAA':
			handler = OpenSKOS()
			options = handler.autoCompleteTable(term.lower(), conceptScheme)
		elif vocab == 'DBpedia':
			dac = DBpedia()
			options = dac.autoComplete(term)#dbpedia lookup seems down...
		elif vocab == 'UNESCO':
			u = Unesco(app.config)
			options = u.autocomplete(term)
		if options:
			return Response(json.dumps(options), mimetype='application/json')
		else:
			return Response(getErrorMessage('Nothing found'), mimetype='application/json')
	return Response(getErrorMessage('Please specify a search term'), mimetype='application/json')

#TODO later dynamically load the api class as well:
#See: http://stackoverflow.com/questions/4246000/how-to-call-python-functions-dynamically
#TODO also create a separate API for this, with a nice swagger def
#FIXME summary: this is pretty basic and not yet generic enough
@app.route('/link/<api>/<command>')
@requires_auth
def link(api, command):
	resp = None
	apiHandler = None
	params = request.args
	if api == 'wikidata':
		apiHandler = WikiData()
		if command == 'get_entity':
			params = {
				'ids' : [request.args.get('id')],
				'get_references' : True,
				'props' : ("labels", "descriptions", "sitelinks"),
				'languages' : ['nl']
			}
	elif api == 'europeana':
		apiHandler = Europeana()
	if apiHandler:
		resp = resp = getattr(apiHandler, "%s" % command)(params)
	if resp:
		return Response(json.dumps(resp), mimetype='application/json')
	return Response(getErrorMessage('Nothing found'), mimetype='application/json')

@app.route('/logout')
def logout():
	if app.config['AUTHENTICATION_METHOD'] == 'OpenConext':
		return redirect(url_for('saml_logout'))
	else:
		session.clear()
		return redirect(url_for('home'))
	return Response(getErrorMessage('logout not implemented'))

"""------------------------------------------------------------------------------
ERROR HANDLERS
------------------------------------------------------------------------------"""

#TODO fix the underlying template
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html', user=_authenticationHub.getUser(request), version=app.config['APP_VERSION']), 404

@app.errorhandler(500)
def page_not_found(e):
	return render_template('500.html', user=_authenticationHub.getUser(request), version=app.config['APP_VERSION']), 500

#main function that will run the server
if __name__ == '__main__':
	app.run(port=app.config['APP_PORT'], host=app.config['APP_HOST'])
