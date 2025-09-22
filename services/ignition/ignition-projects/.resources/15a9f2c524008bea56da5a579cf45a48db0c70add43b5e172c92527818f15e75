def doPost(request, session):
	try:
	    Search = request["headers"]["Search"]
	except:
	    return {'json': {'Error': 'Must supply Search in header Example: Search: [System]Gateway or try [Default]'}}
	
	results = system.tag.browse(Search, {"recursive":True}).results
	
	tags = []
	containers = []
	providers = []
	
	for tag in results:
		if (str(tag['tagType']) == 'Folder' or str(tag['tagType']) == 'UdtInstance'):
			containers.append(str(tag['fullPath']))
		elif str(tag['tagType']) == 'Provider':
			providers.append(str(tag['fullPath']))
		else:
			tags.append(str(tag['fullPath']))
	
	
	tagData = {"providers":providers, "folders":containers, "tags":tags}
	
	
	return {'json': system.util.jsonEncode(tagData)}