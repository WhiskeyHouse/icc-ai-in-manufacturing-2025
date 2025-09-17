def doGet(request, session):
#	For more Information please visit the API Docs:
#		https://sandalwood.com/systems-integration/ignition-rest-api/
#	EXAMPLE USAGE
#	GET REQUEST
#	Postman URL:
#	http://IGNITIONURL/system/webdev/PROJECTNAME/getTagValueData
#	Headers:
#	Key:
#	TagPaths
#	Value:
#	[System]Gateway/Performance/Memory Utilization,[System]Gateway/Performance/Memory Usage,[System]Gateway/Performance/Max Memory,[System]Gateway/Performance/Memory Utilization,[System]Gateway/Performance/CPU Usage
#	
#
#
#	Returned Data in JSON Format:
#	
#	Value: 0.123456
#	TagPath: "[System]Gateway/Performance/Memory Utilization"
#
#
#
#
#
	#Checks headers for TagPaths key if nothing returns or it errors then it returns an error message in JSON
	try:
	    TagPath = request["headers"]["TagPaths"]
	except:
	    return {'json': {'Error': 'Must supply TagPaths in header Example: TagPaths: [System]Gateway/UptimeSeconds'}}
	
	if len(TagPath) >= 1:
	    TagList = [tag.strip() for tag in TagPath.split(',')]
	
	    #Reads the tags values
	    TagValues = system.tag.readBlocking(TagList)
	
	    #List to store the results
	    result_list = []
	
	    #Iterate through the tags and collect values and tag paths
	    for i in range(len(TagValues)):
	        result_list.append({'Value': TagValues[i].value, 'TagPath': TagList[i]})
	
	    #Return the entire list
	    #return {'json': result_list}
	    return {'json': {'Data': result_list}}
	
	if len(TagPath) <= 0:
	    return {'json': {'Error': "Must supply TagPath in headers"}}