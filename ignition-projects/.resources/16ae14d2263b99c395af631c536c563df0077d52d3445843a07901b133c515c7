def doGet(request, session):
	# 	Calling this Endpoint:
	#	The path can be provided as a string param, as the body (data) in one string, or as the remaining path of the endpoint.
	#	params/body = {'path': '[provider]path/to/tag1'}
	#	remaining path = '/system/webdev/project/tags/PROVIDER/FOLDER/TAG'
	#	Any exception will be added to the JSON response under 'exceptions'
		
	#################### Parse the Tag Path ####################
	
	jsonResponse = {}
	
	try:
		tagPath = None
		if 'path' in request['params']:
			tagPath = request['params']['path']
		elif request['remainingPath']:
			pathComponents = request['remainingPath'].split('/', 2)
			tagPath = '[%s]%s' %(pathComponents[1], pathComponents[2])
		elif isinstance(request['data'], str) or isinstance(request['data'], unicode):
			tagPath = request['data']
		
	#################### Read and Build Tag JSON ####################
	
		if tagPath:
			tagQfv = system.tag.readBlocking([tagPath])[0]
			jsonResponse['value'] = tagQfv.value
			jsonResponse['timestamp'] = str(tagQfv.timestamp.toInstant())
			quality = {
				'code': tagQfv.quality.getCode() & 0xFFFF,
				'diagnosticMessage': tagQfv.quality.getDiagnosticMessage() if tagQfv.quality.getDiagnosticMessage() else '',
				'string': str(tagQfv.quality),
			}
			jsonResponse['quality'] = quality
	except (Exception, java.lang.Exception) as e:
		jsonResponse['exceptions'] = e.message
	
	if not jsonResponse:
		jsonResponse['exceptions'] = "No tag path given."
	
	return {'json': jsonResponse}