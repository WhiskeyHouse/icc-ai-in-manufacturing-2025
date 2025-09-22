def doPost(request, session):
	#	For more Information please visit the API Docs:
	#		https://sandalwood.com/systems-integration/ignition-rest-api/
	#	EXAMPLE USAGE
	#	POST REQUEST
	#	Postman URL:
	#	http://IGNITIONURL/system/webdev/PROJECTNAME/getTagPaths
	#	Headers:
	#	Key:
	#	TagPaths
	#	Value:
	#	[System]Gateway
	#
	# Returns the following data in JSON Format:
	#	Folders
	#	Tags
	#
	try:
	    Search = request["headers"]["Search"]
	except:
	    return {'json': {'Error': 'Must supply Search in header Example: Search: [System]Gateway or try [Default]'}}
	
	browseTags = system.tag.browseTags(Search)
	tags = [];
	containers = [];
	#Searches for Folders, Providers, and Tags
	for tag in browseTags:
	 if (tag.isFolder() or tag.isUDT()):
	     containers.append(str(Search)+str(tag.name))
	 else:
	     tags.append(str(Search)+'/'+str(tag.name))
	
	tagData = {"tags":tags, "folders":containers}
	
	return {'json': system.util.jsonEncode(tagData)}