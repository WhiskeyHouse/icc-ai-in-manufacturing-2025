def doGet(request, session):
	#	For more Information please visit the API Docs:
	#		https://sandalwood.com/systems-integration/ignition-rest-api/
	#	EXAMPLE USAGE
	#	GET REQUEST
	#	Postman URL:
	#	http://IGNITIONURL/system/webdev/PROJECTNAME/getSimpleHealth
	#	
	#	Returns UTC timestamp as an Integer in Miliseconds
	#	In JSON Format Example:
	#	{"Data":1707850103}
	#	
	#	
	import time
	import calendar
	
	# Get current timestamp in UTC as an integer
	timestamp_utc = calendar.timegm(time.gmtime())
	
	print(timestamp_utc)
	return {'json': {"Data":timestamp_utc}}