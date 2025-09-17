def doGet(request, session):
#	For more Information please visit the API Docs:
#		https://sandalwood.com/systems-integration/ignition-rest-api/
#	EXAMPLE USAGE
#	GET REQUEST
#	Postman URL:
#	http://IGNITIONURL/system/webdev/PROJECTNAME/getTagValueUnits
#	Headers:
#	Key:
#	TagPaths
#	Value:
#	[System]Gateway/Performance/Memory Utilization,[System]Gateway/Performance/Memory Usage,[System]Gateway/Performance/Max Memory,[System]Gateway/Performance/Memory Utilization,[System]Gateway/Performance/CPU Usage
#
#
#
#	Returned Data in JSON Format:
#	High: 100
#	Low: 25
#	Value: 0.123456
#	TagPath: "[System]Gateway/Performance/Memory Utilization"
#	Unit: DEG F
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
		
		#Adds .EngUnit to add engineering unit to the path
		EngUnit = [item + '.EngUnit' for item in TagList]
		EngLow = [item + '.EngLow' for item in TagList]
		EngHigh = [item + '.EngHigh' for item in TagList]
		
		
		#Reads the tags values
		TagValues = system.tag.readBlocking(TagList)
		UnitValues = system.tag.readBlocking(EngUnit)
		LowValues = system.tag.readBlocking(EngLow)
		HighValues = system.tag.readBlocking(EngHigh)
		
		#List to store the results
		Results = []
		
		# Helper function to convert empty strings to None
		def ConvertNone(value):
		    return value if value != u'' else None
		
		# Iterate through the tags and collect values and tag paths
		for tag in range(len(TagValues)):
		    Value = ConvertNone(TagValues[tag].value)
		    Unit = ConvertNone(UnitValues[tag].value)
		    Low = ConvertNone(LowValues[tag].value)
		    High = ConvertNone(HighValues[tag].value)
		
		    Results.append({'Value': Value, 'Unit': Unit, 'Low': Low, 'High': High, 'TagPath': TagList[tag]})
		
		# Return the entire list
		return {'json': {'Data': Results}}

	if len(TagPath) <= 0:
	    return {'json': {'Error': "Must supply TagPath in headers"}}