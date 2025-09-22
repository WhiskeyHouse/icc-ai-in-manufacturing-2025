def doGet(request, session):
	#	For more Information please visit the API Docs:
	#		https://sandalwood.com/systems-integration/ignition-rest-api/
	#	EXAMPLE USAGE
	#	POST REQUEST
	#	Postman URL:
	#	http://IGNITIONURL/system/webdev/PROJECTNAME/getAllTagPaths
	#	
	# Returns the following data in JSON format:
	#	Folders (Tag folders and UDTs)
	#	Providers (Gateway providers)
	#	Tags (Tagpaths)
	#	
	Search = ''
	results = system.tag.browse(Search, {"recursive":True}).results
	
	tags = []
	containers = []
	providers = []
	#Searxhes for Providers
	for tag in results:
		if str(tag['tagType']) == 'Provider':
			providers.append(str(tag['fullPath']))
	#Searches for Folders, Providers, and Tags
	for path in providers:
		subresults = system.tag.browse(path, {"recursive":False}).results
		for tag in subresults:
			if (str(tag['tagType']) == 'Folder' or str(tag['tagType']) == 'UdtInstance'):
				containers.append(str(tag['fullPath']))
			elif str(tag['tagType']) == 'Provider':
				providers.append(str(tag['fullPath']))
			else:
				tags.append(str(tag['fullPath']))
	#Searches for Folders, Providers, and Tags
	for path in containers:
		subsubresults = system.tag.browse(path, {"recursive":True}).results
		for tag in subsubresults:
			if (str(tag['tagType']) == 'Folder' or str(tag['tagType']) == 'UdtInstance'):
				#containers.append(str(tag['fullPath']))
				pass
			elif str(tag['tagType']) == 'Provider':
				providers.append(str(tag['fullPath']))
			else:
				tags.append(str(tag['fullPath']))
	
	
	tagData = {"providers":providers, "folders":containers, "tags":tags}
	output = {'Data': tagData}
	
	return {'json': system.util.jsonEncode(output)}