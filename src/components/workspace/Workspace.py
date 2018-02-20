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
		#return {'error' : resp.text}, resp.status_code
		return self.__formatAPIErrorResponse(resp)

	def __listProjects(self, clientId, token, userId):
		url = '%s/%s/projects?cid=%s&at=%s' % (
			self.config['USER_SPACE_API'], userId, clientId, token
		)
		resp = requests.get(url)
		if resp.status_code == 200:
			return resp.text

		return self.__formatAPIErrorResponse(resp)

	def __saveProject(self, clientId, token, userId, project, projectId=None):
		url = '%s/%s/projects' % (self.config['USER_SPACE_API'], userId)
		if projectId:
			url += '/%s' % projectId
		url += '?cid=%s&at=%s' % (clientId, token)
		project['clientId'] = clientId
		project['token'] = token
		if projectId:
			resp = requests.put(url, json=project)
		else:
			resp = requests.post(url, json=project)
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
		if 'error' in resp.text:
			return resp
		else:
			try:
				return {'error' : resp.text}, resp.status_code
			except ValueError, e:
				return {'error' : 'Internal server error (route to API not available?)'}, resp.status_code


	"""<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
	<><><><><><><><><><> ANNOTATION API REQUESTS <><><><><><><><><>
	<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"""

	def processAnnotationAPIRequest(self, clientId, token, method, data=None, annotationId=None):
		if method == 'DELETE':
			return self.__deleteAnnotation(clientId, token, annotationId)
		elif method in ['PUT', 'POST']:
			return self.__saveAnnotation(clientId, token, data, annotationId)
		elif method == 'GET' and annotationId:
			return self.__getAnnotation(clientId, token, annotationId)
		return {'error' : 'Bad request'}, 400

	def searchAnnotationsOld(self, clientId, token, params):
		temp = []
		for k in params.keys():
			temp.append(k + '=' + params[k]);
		url =  '%s/annotations/filter?%s' % (self.config['ANNOTATION_API'], '&'.join(temp))
		resp = requests.get(url)
		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)

	def searchAnnotations(self, postData):
		url =  '%s/annotations/filter' % self.config['ANNOTATION_API']
		resp = requests.post(url, json=postData)

		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)

	def __getAnnotation(self, clientId, token, annotationId):
		url = '%s/annotation/%s?cid=%s&at=%s' % (
			self.config['ANNOTATION_API'], annotationId, clientId, token
		)
		resp = requests.get(url)
		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)

	def __saveAnnotation(self, clientId, token, annotation, annotationId=None):
		url = '%s/annotation' % self.config['ANNOTATION_API']
		if annotationId:
			url += '/%s' % annotationId
		url += '?cid=%s&at=%s' % (clientId, token)
		annotation['clientId'] = clientId
		annotation['token'] = token
		if annotationId:
			resp = requests.put(url, json=annotation)
		else:
			resp = requests.post(url, json=annotation)
		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)

	def __deleteAnnotation(self, clientId, token, annotationId):
		url = '%s/annotation/%s?cid=%s&at=%s' % (
			self.config['ANNOTATION_API'], annotationId, clientId, token
		)
		resp = requests.delete(url)
		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)



	"""<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
	<><><><><><><><><><> SEARCH API REQUESTS <><><><><><><><><><><>
	<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"""

	def layeredSearch(self, clientId, token, collectionId, params):
		url = '%s/layered_search/%s?cid=%s&at=%s' % (
			self.config['SEARCH_API'],
			collectionId,
			clientId,
			token
		)
		print url
		if params:
			resp = requests.post(url, json=params)
			if resp.status_code == 200:
				return resp.text
		return self.__formatAPIErrorResponse(resp)

	"""<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
	<><><><><><><><><><> DOCUMENT API REQUESTS <><><><><><><><><><>
	<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"""

	#params => {id : ''}
	def getDoc(self, clientId, token, collectionId, params):
		url = '%s/document/get_doc/%s?cid=%s&at=%s' % (
			self.config['SEARCH_API'],
			collectionId,
			clientId,
			token
		)
		if params:
			resp = requests.post(url, json=params)
			if resp.status_code == 200:
				return resp.text
		return self.__formatAPIErrorResponse(resp)

	#params => {ids : ['', '']}
	def getDocs(self, clientId, token, collectionId, params):
		url = '%s/document/get_docs/%s?cid=%s&at=%s' % (
			self.config['SEARCH_API'],
			collectionId,
			clientId,
			token
		)
		if params:
			resp = requests.post(url, json=params)
			if resp.status_code == 200:
				return resp.text
		return self.__formatAPIErrorResponse(resp)


	"""<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
	<><><><><><><><><><> COLLECTION API REQUESTS <><><><><><><><><>
	<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"""


	def getCollectionStats(self, clientId, token, collectionId):
		url = '%s/collections/show_stats/%s?cid=%s&at=%s' % (
			self.config['SEARCH_API'],
			collectionId,
			clientId,
			token
		)
		resp = requests.post(url)
		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)

	def getCollectionTimeLine(self, clientId, token, collectionId, params):
		url = '%s/collections/show_timeline/%s?cid=%s&at=%s' % (
			self.config['SEARCH_API'],
			collectionId,
			clientId,
			token
		)
		if params:
			resp = requests.post(url, json=params)
			if resp.status_code == 200:
				return resp.text
			return self.__formatAPIErrorResponse(resp)
		return {'error' : 'Bad request: please provide the correct parameters'}, 400

	def analyseField(self, clientId, token, collectionId, params):
		url = '%s/collections/analyse_field/%s?cid=%s&at=%s' % (
			self.config['SEARCH_API'],
			collectionId,
			clientId,
			token
		)
		if params:
			resp = requests.post(url, json=params)
			if resp.status_code == 200:
				return resp.text
			return self.__formatAPIErrorResponse(resp)
		return {'error' : 'Bad request: please provide the correct parameters'}, 400

	"""<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
	<><><><><><><><><><> CKAN API REQUESTS <><><><><><><><><><><><>
	<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"""

	def listCollections(self, clientId, token):
		url = '%s/ckan/list_collections?cid=%s&at=%s' % (
			self.config['SEARCH_API'],
			clientId,
			token
		)
		resp = requests.post(url)
		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)

	def getCollectionInfo(self, clientId, token, collectionId):
		url = '%s/ckan/collection_info/%s?cid=%s&at=%s' % (
			self.config['SEARCH_API'],
			collectionId,
			clientId,
			token
		)
		resp = requests.post(url)
		if resp.status_code == 200:
			return resp.text
		return self.__formatAPIErrorResponse(resp)


