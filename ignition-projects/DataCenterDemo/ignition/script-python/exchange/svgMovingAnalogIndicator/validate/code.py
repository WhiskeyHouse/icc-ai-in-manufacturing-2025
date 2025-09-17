def handleNumericParam(paramValue, fallbackValue, minValue = None):
	"""
	Checks if a parameter value is numeric. If the parameter has a
		minimum, like indicatorSize, then ensures that the parameter
		is greater than or equal to the minimum.
		
	Args:
		paramValue: Parameter value to check.
		fallbackValue: Value to return if paramValue is not numeric.
		minValue: Minimum value for the parameter (if it has a min).
	
	Returns:
		normalized paramValue.
	"""	
	# Check if param value is null.
	if paramValue == None:
		return fallbackValue
		
	# Check if param value is int, float, or long.
	elif isinstance(paramValue, (int, float, long)):
		number = paramValue
		
	else:
		# Check if param value is a string-represented number.
		try:
			# Try converting to int.
			number = int(paramValue)
			
		except:
			# Failed to convert to int. Trying to convert to float.
			try:
				number = float(paramValue)
				
			except:
				# Failed to convert to float. Returning default value.
				return fallbackValue
				
	# See if the parameter has a minimum value.
	if minValue != None:
		# Make sure that parameter value is greater than or equal to minimum.
		return number if number >= minValue else minValue
	else:
		return number
				
def handleNullableNumericParam(paramValue, fallbackValue):	
	"""
	Checks if a parameter value is numeric.
		
	Args:
		paramValue: Parameter value to check.
		fallbackValue: Value to return if paramValue is not null or numeric.
	
	Returns:
		paramValue if it is numeric, otherwise fallbackValue.
	"""	
	# Check if the param value is not null.
	if paramValue != None:
		# Not null, so check if it is numeric.
		return handleNumericParam(paramValue, fallbackValue)
	
	else:
		# Param is nullable, return paramValue since it is null.
		return paramValue
		
def handleBoolParam(paramValue):
	"""
	Ensures that the parameter value is a bool.
		
	Args:
		paramValue: Parameter value to check.
	
	Returns:
		paramValue if it is a bool, otherwise bool(paramValue).
	"""	
	# Check if param value is already a bool.
	if isinstance(paramValue, bool):
		return paramValue
	
	else:
		# Cast param value as a bool.
		return bool(paramValue)