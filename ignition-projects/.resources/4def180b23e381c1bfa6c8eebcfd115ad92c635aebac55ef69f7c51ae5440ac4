def doGet(request, session):
	#	For more Information please visit the API Docs:
	#		https://sandalwood.com/systems-integration/ignition-rest-api/
	#	EXAMPLE USAGE
	#	POST REQUEST
	#	Postman URL:
	#	http://IGNITIONURL/system/webdev/PROJECTNAME/getGroupData
	#	Headers:
	#	Key:
	#	TagPaths
	#	Value:
	#	[System]Gateway
	#
	# Returns the following data in JSON format:
	#	Folders (Tag folders and UDTs)
	#	Providers (Gateway providers)
	#	Tags (Tagpaths)
	#
	try:
	    Search = request["headers"]["Search"]
	except:
	    return {'json': {'Error': 'Must supply Search in header Example: Search: [System]Gateway or try [Default]'}}
	
	results = system.tag.browse(Search, {"recursive":True}).results
	
	tags = []
	containers = []
	providers = []
	#Searches for Folders, Providers, and Tags
	for tag in results:
		if (str(tag['tagType']) == 'Folder' or str(tag['tagType']) == 'UdtInstance'):
			containers.append(str(tag['fullPath']))
		elif str(tag['tagType']) == 'Provider':
			providers.append(str(tag['fullPath']))
		else:
			tags.append(str(tag['fullPath']))
	
	
	tagData = {"providers":providers, "folders":containers, "tags":tags}
	output = {'Data': tagData}
	
	return {'json': system.util.jsonEncode(output)}