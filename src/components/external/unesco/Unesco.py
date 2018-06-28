import requests
import json

class Unesco():

	def __init__(self, config):
		self.BASE_URL = '%s/search/vocab__unesco__autocomplete?cid=%s&at=%s' % (
			config['SEARCH_API'],
			config['CLIENT_ID'],
			config['TOKEN']
		)
		self.MODE_MAPPING = ['prefLabel', 'altLabels', 'labels']

	def autocomplete(self, prefix, mode=0, maxHits = 10):
		options = []
		query = {
			"query":{
				"match":{
					"%s" % self.MODE_MAPPING[mode] : "%s" % prefix
				}
			},
			"size" : maxHits
		}
		resp = requests.post(self.BASE_URL, data=json.dumps(query))
		if resp and resp.status_code == 200:
			data = json.loads(resp.text)
			if data:
				if 'hits' in data and data['hits']['total'] > 0:
					for hit in data['hits']['hits']:
						options.append({
							'label' : '%s|%s|%s' % (
								hit['_source']['prefLabel'],
								hit['_source']['domainLabel'],
								hit['_source']['collectionLabel']
							),
							'value' : hit['_source']['uri']
						})

		return options