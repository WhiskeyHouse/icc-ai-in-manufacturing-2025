def doGet(request, session):
	#	For more Information please visit the API Docs:
	#		https://sandalwood.com/systems-integration/ignition-rest-api/
	#	EXAMPLE USAGE
	#	GET REQUEST
	#	Postman URL:
	#	http://IGNITIONURL/system/webdev/PROJECTNAME/RunNamedQueries
	#	
	#	Headers:
	#
	#	Key:
	#	Project
	#	Value:
	#	IgnitionProjectName
	#	
	#
	#	Key 2:
	#	Named Query
	#	Value:
	#	QUERYPATH
	#	(If the query is inside of a folder: Foldername/Query1)
	#	(If the namedquery is not inside a folder: Query1)
	#
	#	Key 3 (Optional only use if the named query has parameters):
	#	ParamNames
	#	Value (Each value is seperated by a comma followed by a space):
	#	Parameter1
	#	For multiple parameters:
	#	Param1, Param2, Param3, Param4
	#
	#	Key 4:
	#	ParamValues
	#	Value (Values must match same number of parameters):
	#	Param1Value
	#	for multiple parameters (MUST MATCH same number as ParamNames):
	#	Param1Value, 4321, String3, String4
	#
	#	 Returned data could be different responses
	#	 For Scalar Queries it will return only the value example:
	# 		Value: 57
	#
	#
	#	For Queries as a dataset the value will be returned as:
	#	Column1: Row 1 Value
	#	Column2: Row 1 Value
	# 
	#	Column1: Row 2 Value
	#	Column2: Row 2 Value
	#
	#Function to get parameter names and values paried together in correct format for named query
	def create_params(param_names_str, param_values_str):
	    # Split the input strings by commas to get lists of names and values
	    param_names = param_names_str.split(', ')
	    param_values = param_values_str.split(', ')
	    
	    # Use zip to combine param_names and param_values into pairs
	    param_pairs = zip(param_names, param_values)
	    
	    # Create a dictionary from the pairs
	    params_dict = {}
	    for name, value in param_pairs:
	        try:
	            # Try to convert the value to an integer
	            value = int(value)
	        except ValueError:
	            pass  # If conversion to int fails, leave it as is
	        params_dict[name] = value
	    
	    return params_dict
	
	
	#Grabbing Headers and Data
	try:
	    Project = request["headers"]["Project"]
	    NamedQuery = request["headers"]["NamedQuery"]
	except:
	    return {'json': {'Data': 'Must supply Project and NamedQuery in header Example: Project: TulipConnectorAPI, NamedQuery: Query1', 'Optional Headers': 'ParamNames, ParamValues Example: ParamNames: Param1, Param2 ParamValues: 1, Test '}}
	
	#Trying to grab parameter names and values
	try:
		#Set Paramaters to -1 for invalid input
		Formatparams = -1
		
		ParamNames = request["headers"]["ParamNames"]
		ParamValues = request["headers"]["ParamValues"]
		
		# A List of blacklisted words or characters to protect from SQL Injections.
		# This is not a 100% guarantee of protection against SQL Injections, but will help.
		Blacklisted = ['Delete', 'Update', 'Insert', 'Drop', 'Truncate', 'Alter', 'Create', 'Union', 'Union All', 'Database', 'Table', 'Schema', ';', '[', ']', '(', ')', '1=1']
		
		# Convert ParamValues to lowercase to make the comparison case-insensitive
		param_values_lower = ParamValues.lower()
		
		# Check for blacklisted items in ParamValues
		for item in Blacklisted:
			if item.lower() in param_values_lower:
				return {'json': {'Data': [{'Error':'The following character/string is not allowed: '+str(item)+' This is to help protect against SQL Injections.'}]}}
		
		Formatparams = create_params(str(ParamNames), ParamValues)
		
		# Convert the result to a JSON-formatted string
		Parameters = json.dumps(Formatparams)
	except:
		pass
	
	
	#Runs the named query without parameters
	if Formatparams == -1:
		dataset = system.db.runNamedQuery(Project, NamedQuery)
	else:
		dataset = system.db.runNamedQuery(Project, NamedQuery, Formatparams)
	
	#Converts the data
	try:
		convertedArry = []
		# Convert dataset to a list of dictionaries
		for row in range(dataset.getRowCount()):
		    convertedRow = {}
		    for col in dataset.getColumnNames():
		        convertedRow[col] = dataset.getValueAt(row, col)
		    convertedArry.append(convertedRow)
		
		return {'json': {'Data': convertedArry}}
		#return {'json': {'Data': ParamValues}}
	except:
		return {'json': {'Data': dataset}}
		