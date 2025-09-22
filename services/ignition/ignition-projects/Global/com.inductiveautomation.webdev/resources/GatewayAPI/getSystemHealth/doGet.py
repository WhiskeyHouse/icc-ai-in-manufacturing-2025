def doGet(request, session):
	#	For more Information please visit the API Docs:
	#		https://sandalwood.com/systems-integration/ignition-rest-api/
	#	EXAMPLE USAGE
	#	GET REQUEST
	#	Postman URL:
	#	http://IGNITIONURL/system/webdev/PROJECTNAME/getSystemHealth
	#
	#	Returns Ignition Gateway system health in JSON format:
	#	"Uptime": "2 Days 10h 14m 02s"
	#	"System Performance": {
	#            "DISK Usage": "84.75%",
	#            "RAM Usage": "36.42%",
	#            "CPU Usage": "3.12%"
	#       }
	#
	cpu = system.tag.read('[System]Gateway/Performance/CPU Usage').value
	ram = system.tag.read('[System]Gateway/Performance/Memory Utilization').value
	disk = system.tag.read('[System]Gateway/Performance/Disk Utilization').value
	
	seconds = system.tag.read('[System]Gateway/UptimeSeconds').value
	
	# Calculate days, hours, minutes, seconds
	days, remainder = divmod(seconds, 86400)
	hours, remainder = divmod(remainder, 3600)
	minutes, seconds = divmod(remainder, 60)
	# Format
	uptime = "%d Days %02dh %02dm %02ds" % (days, hours, minutes, seconds)
	cpu = ("{:.2%}".format(cpu))
	ram = ("{:.2%}".format(ram))
	disk = ("{:.2%}".format(disk))
	
	
	
	return {'json': {
	  "Data": {
	    "System Performance": {
	      "CPU Usage": cpu,
	      "RAM Usage": ram,
	      "DISK Usage": disk
	    },
	    "Uptime": uptime
	  }
	}}