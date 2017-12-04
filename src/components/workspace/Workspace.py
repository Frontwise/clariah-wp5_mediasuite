import requests
import json

class Workspace():

	def __init__(self, config):
		self.config = config

	"""<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
	<><><><><><><><><><> PROJECT API REQUESTS <><><><><><><><><><><
	<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"""

	def processProjectAPIRequest(self, clientId, token, method, userId, data=None, projectId=None):
		if method == 'DELETE':
			return self.__deleteProject(clientId, token, userId, projectId)
		elif method in ['PUT', 'POST']:
			return self.__saveProject(clientId, token, userId, data, projectId)
		elif method == 'GET':
			if projectId:
				return self.__getProject(clientId, token, userId, projectId)
			else:
				return self.__listProjects(clientId, token, userId)
		return {'error' : 'Bad request'}, 400

	def __getProject(self, clientId, token, userId, projectId):
		url = '%s/%s/projects/%s?cid=%s&at=%s' % (
			self.config['USER_SPACE_API'], userId, projectId, clientId, token
		)
		resp = requests.get(url)
		if resp.status_code == 200:
			return resp.text
		return {'error' : resp.text}, resp.status_code

	def __listProjects(self, clientId, token, userId):
		print 'getting projects'
		url = '%s/%s/projects?cid=%s&at=%s' % (
			self.config['USER_SPACE_API'], userId, clientId, token
		)
		resp = requests.get(url)
		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)

	def __saveProject(self, clientId, token, userId, project, projectId=None):
		url = '%s/%s/projects?cid=%s&at=%s' % (
			self.config['USER_SPACE_API'], userId, clientId, token
		)
		project['clientId'] = clientId
		project['token'] = token
		if projectId:
			url += '/%s' % projectId
			resp = requests.put(url, data=project)
		else:
			resp = requests.post(url, data=project)
		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)

	def __deleteProject(self, clientId, token, userId, projectId):
		url = '%s/%s/projects/%s?cid=%s&at=%s' % (
			self.config['USER_SPACE_API'], userId, projectId, clientId, token
		)
		resp = requests.delete(url)
		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)

	def __formatAPIErrorResponse(self, resp):
		try:
			return {'error' : resp.text}, resp.status_code
		except ValueError, e:
			return {'error' : 'Internal server error (route to API not available?)'}, resp.status_code


	"""<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
	<><><><><><><><><><> ANNOTATION API REQUESTS <><><><><><><><><>
	<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"""

	def processAnnotationAPIRequest(self, clientId, token, method, userId, data=None, annotationId=None):
		if method == 'DELETE':
			return self.__deleteAnnotation(clientId, token, userId, annotationId)
		elif method in ['PUT', 'POST']:
			return self.__saveAnnotation(clientId, token, userId, data, annotationId)
		elif method == 'GET':
			if annotationId:
				return self.__getAnnotation(clientId, token, userId, annotationId)
			else:
				return self.__listAnnotations(clientId, token, userId)
		return {'error' : 'Bad request'}, 400

	def __getAnnotation(self, clientId, token, userId, annotationId):
		url = '%s/%s/projects/%s?cid=%s&at=%s' % (
			self.config['ANNOTATION_API'], userId, annotationId, clientId, token
		)
		resp = requests.get(url)
		if resp.status_code == 200:
			return resp.text
		return {'error' : resp.text}, resp.status_code

	def __listAnnotations(self, clientId, token, userId):
		print 'getting projects'
		url = '%s/%s/projects?cid=%s&at=%s' % (
			self.config['ANNOTATION_API'], userId, clientId, token
		)
		resp = requests.get(url)
		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)

	def __saveAnnotation(self, clientId, token, userId, annotation, annotationId=None):
		url = '%s/%s/annotations?cid=%s&at=%s' % (
			self.config['ANNOTATION_API'], userId, clientId, token
		)
		annotation['clientId'] = clientId
		annotation['token'] = token
		if annotationId:
			url += '/%s' % annotationId
			resp = requests.put(url, data=annotation)
		else:
			resp = requests.post(url, data=annotation)
		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)

	def __deleteAnnotation(self, clientId, token, userId, annotationId):
		url = '%s/%s/projects/%s?cid=%s&at=%s' % (
			self.config['ANNOTATION_API'], userId, annotationId, clientId, token
		)
		resp = requests.delete(url)
		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)


