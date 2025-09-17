def doPost(request, session):
	# 	Calling this Endpoint:
	#	The paths can be provided in a list of strings and/or objects, as either params or the body (data).
	#	objects should include 'path' and 'recursive' properties	
	#	params/data = {
	#		'paths': ['[provider]path/to/tag1', '[provider]path/to/tag2', '[provider]path/to/folder1', {'path': '[provider]path/to/folder2', 'recursive': True}]
	#	}
	#	Any exceptions will be added to the JSON response in an array, under 'exceptions' 
	
	
	#################### Utility Functions ####################
	
	# given a tag result (qfv), return a json compatible dictionary
	def tagToJson(tag):
		tagJson = {}

		tagJson['value'] = tag.value
		tagJson['timestamp'] = str(tag.timestamp.toInstant())
		quality = {
			'code': tag.quality.getCode() & 0xFFFF,
			'diagnosticMessage': tag.quality.getDiagnosticMessage() if tag.quality.getDiagnosticMessage() else '',
			'string': str(tag.quality),
		}
		tagJson['quality'] = quality
		return tagJson
	
	# given a list of tag paths, return either a flat or nested json compatible dictionary
	def tagsToJson(tagPaths, nestedResponse):
			import re
			if nestedResponse:
				nestedValues = {}
				tagValues = system.tag.readBlocking(tagPaths)
				for i in range(len(tagValues)):
					tagPath = re.findall('\[.+\]|[\w\s]+', tagPaths[i])
					nestedValue = nestedValues
					for j in range(len(tagPath) - 1):
						if tagPath[j] not in nestedValue:
							nestedValue[tagPath[j]] = {}
						nestedValue = nestedValue[tagPath[j]]
					nestedValue[tagPath[-1]] = tagToJson(tagValues[i])
				return nestedValues
			else:
				return {tagPath:tagJson for tagPath, tagJson in zip(tagPaths, [tagToJson(tag) for tag in system.tag.readBlocking(tagPaths)])}


	import java.lang.Exception
	
	jsonResponse = {}
	exceptions = []
	tagsToRead = set()
	nestedResponse = False
 
 	#################### Parse Tag Path Params ####################
 
	tagPaths = []
	if 'paths' in request['params']:
		try:
			tagPaths = system.util.jsonDecode(request['params']['paths'])
			if 'nestedResponse' in request['params']:
				nestedResponse = system.util.jsonDecode(request['params']['nestedResponse'])
		except (Exception, java.lang.Exception) as e:
			exceptions.append("Unabled to decode tag/folder paths from the given params: %s" %e.message)
	else:
		data = request['data']
		if isinstance(data, dict) and 'paths' in data:
			tagPaths = data['paths']
			if 'nestedResponse' in data:
				nestedResponse = data['nestedResponse']
		elif isinstance(data, str) or isinstance(data, unicode):
			try:
				data = system.util.jsonDecode(request['data'])
				if 'paths' in data:
					tagPaths = data['paths']
				if 'nestedResponse' in data:
					nestedResponse = data['nestedResponse']
			except (Exception, java.lang.Exception) as e:
				exceptions.append("Unabled to decode tag/folder paths from the given data: %s" %e.message)
	
	#################### Browse and Build the Tag Path List ####################
	
	for tagPath in tagPaths:
		try:
			path = tagPath
			recursive = False
			if isinstance(tagPath, dict):
				path = tagPath['path'] if 'path' in tagPath else ''
				recursive = tagPath['recursive'] if 'recursive' in tagPath else False
			
			if isinstance(path, str) or isinstance(path, unicode):
				if system.tag.getConfiguration(path, False)[0]['tagType'].name() != 'Folder':
						tagsToRead.add(path)
				else:
					filter={"recursive":recursive,"tagType":"AtomicTag"}
					for tagPath in [result['fullPath'].toStringFull() for result in system.tag.browse(path=path, filter=filter).getResults()]:
						tagsToRead.add(tagPath)
			else:
				exceptions.append("Non-string tag path given: '%s'" %tagPath)
		except (Exception, java.lang.Exception) as e:
			exceptions.append("Error reading from tag path '%s': %s" %(tagPath, e.message))


	#################### Build the Tag JSON ####################
	
	try:
		if tagsToRead:
			jsonResponse['values'] = tagsToJson(list(tagsToRead), nestedResponse)
			
	except (Exception, java.lang.Exception) as e:
		exceptions.append('Unable to read tags: %s' %e.message)
	
	#################### Attach Exceptions ####################
	
	if exceptions:
		jsonResponse['exceptions'] = exceptions

	return {'json': jsonResponse}