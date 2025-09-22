import math

def createViewBox(verticalDisplay, startPosition, rangesBarStrokeWidth, indicatorSize, rangesBarSize, indicatorStrokeWidth, labelVisible, labelPosition):
	"""
	Calculates the values for the viewBox of the SVG.
		
	Args:
		verticalDisplay: Denotes if the resource is displayed vertically or horizontally.
		startPosition: Start position of the ranges bar.
		rangesBarStrokeWidth: Width of the ranges bar's stroke.
		indicatorSize: Size of the triangular indicator.
		rangesBarSize: Size of the ranges bar.
		indicatorStrokeWidth: Width of the indicator's stroke.
		labelVisible: Denotes whether label is visible.
		labelPosition: Settings regarding the label distance from the indicator.
	
	Returns:
		String containing the 4 values needed for the ViewBox: min-x, min-y, width and height.
	"""	
	# See if the viewbox should take label offsets into account.
	if labelPosition['applyOffsetsOnlyWhenLabelVisible']:
		includeLabelOffsets = True if labelVisible else False
	else:
		includeLabelOffsets = True
	
	# Calculate the side length of the indicator.
	sideLength = 2.0 * indicatorSize / math.sqrt(3.0)
	
	# Define start of the viewport.
	start = 0.0 - sideLength / 2.0 - indicatorStrokeWidth
	
	# Define the length needed for the viewport.
	length = 100.0 + sideLength + indicatorStrokeWidth * 2
	
	if verticalDisplay:
		minY = start
		height = length
		minX = (0 - indicatorSize) - (rangesBarStrokeWidth / 2.0) - 1.5*indicatorStrokeWidth
		width = rangesBarSize + (2.0 * indicatorSize) + rangesBarStrokeWidth + (3*indicatorStrokeWidth)
		
		if includeLabelOffsets:
			minX = min(0, minX - labelPosition['horizontalOffset'])
			width = max(width, width + labelPosition['horizontalOffset'])
	else:
		minX = start
		width = length
		minY = (0 - indicatorSize) - (rangesBarStrokeWidth / 2.0) - 1.5*indicatorStrokeWidth
		height = rangesBarSize + (2.0 * indicatorSize) + rangesBarStrokeWidth + (3*indicatorStrokeWidth)
		
		if includeLabelOffsets:
			minY = min(0, minY - labelPosition['verticalOffset'])
			height = max(height, height + labelPosition['verticalOffset'])
	
	return '{minX} {minY} {width} {height}'.format(minX = minX, minY = minY, width = width, height = height)
	
def getStartPosition(rangesBarStrokeWidth, indicatorSize, rangesBarSize, reverseIndicator, verticalDisplay, indicatorStrokeWidth, labelVisible, labelPosition):
	"""
	Calculates the starting position for the rects in the ranges bar.
		
	Args:
		rangesBarStrokeWidth: Width of the stroke of the ranges bar.
		indicatorSize: Size of the triangular indicator.
		rangesBarSize: Size of the ranges bar.
		reverseIndicator: Puts the indicator on the other side of the ranges bar.
		verticalDisplay: Denotes if the resource is displayed vertically or horizontally.
		indicatorStrokeWidth: Width of the indicator's stroke.
		labelVisible: Denotes whether label is visible.
		labelPosition: Settings regarding the label positioning.
	
	Returns:
		Number representing the starting position for the rects in the ranges bar.
	"""
	# See if the start position should take label offsets into account.
	if labelPosition['applyOffsetsOnlyWhenLabelVisible']:
		includeLabelOffsets = True if labelVisible else False
	else:
		includeLabelOffsets = True
		
	start = 0.0
		
	if includeLabelOffsets:
		offsetToApply = labelPosition['horizontalOffset'] if verticalDisplay else labelPosition['verticalOffset']
			
		start = min(start, start - offsetToApply / 2.0)
		
	return start

def createAlarmRect(alarmValue, isLow, processValue, alarmColor, inactiveAlarmColor, verticalDisplay, strokeWidth, strokeColor, rangesBarSize, 
	startPosition):
	"""
	Creates the rects for the low, low-low, high, and high-high alarms.
		
	Args:
		alarmValue: Threshold to determine if alarm is active.
		isLow: Denotes whether the alarm rect to draw is low (low or low-low) or high (high or high-high).
		processValue: Current value of the process.
		alarmColor: Color of the alarm rect if the alarm is active.
		inactiveAlarmColor: Color of the alarm rect if the alarm is not active.
		verticalDisplay: Denotes if the resource is displayed vertically or horizontally.
		strokeWidth: Width of the stroke for the alarm rect.
		strokeColor: Color of the stroke for the alarm rect.
		rangesBarSize: Size of the ranges bar.
		startPosition: Start position for the ranges bar.
	
	Returns:
		Object that represents the alarm (SVG rect).
	"""
	# Check to see if the alarm rectangle should be drawn.
	if alarmValue != None:
		if isLow:
			# This is either lowAlarm or lowLowAlarm.
			
			if alarmValue > 0.0 and alarmValue <= 100.0:
				# Set the color based on the process value.
				color = alarmColor if processValue <= alarmValue else inactiveAlarmColor
				
				if verticalDisplay:
					# Set the y and flip it such that is appears like Cartesian coordinate system.
					y = 100.0 - alarmValue
					x = startPosition
					
					height = alarmValue
					width = rangesBarSize
				else:
					y = startPosition
					x = 0.0
					
					height = rangesBarSize
					width = alarmValue
			else:
				# Alarm value out of range.
				return None
		else:
			# This is either highAlarm or highHighAlarm.
			
			if alarmValue >= 0.0 and alarmValue < 100.0:
				# Set the color based on the process value.
				color = alarmColor if processValue >= alarmValue else inactiveAlarmColor
				
				if verticalDisplay:
					y = 0.0
					x = startPosition
					
					height = 100.0 - alarmValue
					width = rangesBarSize
				else:					
					y = startPosition
					x = alarmValue
					
					height = rangesBarSize
					width = 100.0 - alarmValue
			else:
				# Alarm value out of range.
				return None
				
		# Create the alarm rectangle.	
		return createRect(x, y, height, width, color, strokeWidth, strokeColor)
	else:
		return None

def createAlarmRects(processValue, lowAlarm, lowLowAlarm, highAlarm, highHighAlarm, verticalDisplay, strokeWidth, strokeColor, inactiveAlarmColor, 
	level1AlarmColor, level2AlarmColor, rangesBarSize, startPosition):
	"""
	Creates the rects for the low, low-low, high, and high-high alarms.
		
	Args:
		processValue: Current value of the process.
		lowAlarm: Value below which is a low alarm.
		lowLowAlarm: Value below which is a low-low alarm.
		highAlarm: Value above which is a high alarm.
		highHighAlarm: Value above which is a high-high alarm.
		verticalDisplay: Denotes if the resource is displayed vertically or horizontally.
		strokeWidth: Width of the stroke for the alarm rect.
		strokeColor: Color of the stroke for the alarm rect.
		inactiveAlarmColor: Color of the alarm rect if the alarm is not active.
		level1AlarmColor: Color of an active level 1 alarm (high-high or low-low).
		level2AlarmColor: Color of an active level 2 alarm (high or low).
		rangesBarSize: Size of the ranges bar.
		startPosition: Start position for the ranges bar.
	
	Returns:
		Object that represents the alarms (group of SVG rects).
	"""
	# Initialize list to hold the rectangles.
	rangesBarRectangles = []
	
	# Define the length of the rangesBar.
	length = 100.0
		
	# Create the low alarm rect.
	lowAlarmRect = createAlarmRect(lowAlarm, True, processValue, level2AlarmColor, inactiveAlarmColor, 
					verticalDisplay, strokeWidth, strokeColor, rangesBarSize, startPosition)
					
	if lowAlarmRect != None:
		rangesBarRectangles.append(lowAlarmRect)
		
	# Create the low-low alarm rect.
	lowLowAlarmRect = createAlarmRect(lowLowAlarm, True, processValue, level1AlarmColor, inactiveAlarmColor, 
						verticalDisplay, strokeWidth, strokeColor, rangesBarSize, startPosition)
						
	if lowLowAlarmRect != None:
		rangesBarRectangles.append(lowLowAlarmRect)
		
	# Create the high alarm rect.
	highAlarmRect = createAlarmRect(highAlarm, False, processValue, level2AlarmColor, inactiveAlarmColor, 
						verticalDisplay, strokeWidth, strokeColor, rangesBarSize, startPosition)
						
	if highAlarmRect != None:
		rangesBarRectangles.append(highAlarmRect)
		
	# Create the high-high alarm rect.
	highHighAlarmRect = createAlarmRect(highHighAlarm, False, processValue, level1AlarmColor, inactiveAlarmColor, 
							verticalDisplay, strokeWidth, strokeColor, rangesBarSize, startPosition)
							
	if highHighAlarmRect != None:
		rangesBarRectangles.append(highHighAlarmRect)
	
	return {'type': 'group', 'elements': rangesBarRectangles}
	

def createInterlockRects(lowInterlock, highInterlock, interlockColor, verticalDisplay, strokeWidth, strokeColor, rangesBarSize, 
	startPosition):
	"""
	Creates the rects for the low and high interlocks.
		
	Args:
		lowInterlock: Value below which an interlock will be activated.
		highInterlock: Value above which an interlock will be activated.
		interlockColor: Color of the interlock range.
		verticalDisplay: Denotes if the resource is displayed vertically or horizontally.
		strokeWidth: Width of the stroke for the interlock rects.
		strokeColor: Color of the stroke for the interlock rects.
		rangesBarSize: Size of the ranges bar.
		startPosition: Start position for the ranges bar.
	
	Returns:
		Object that represents the interlocks (group of SVG rects).
	"""
	# Initialize list to hold the rectangles.
	interlockRectangles = []
	
	# Check to see if low interlock rectangle should be drawn.
	if lowInterlock != None and lowInterlock > 0.0 and lowInterlock <= 100.0:
		if verticalDisplay:
			# Set the y and flip it such that is appears like Cartesian coordinate system.
			y = 100.0 - lowInterlock
			x = startPosition
			
			height = lowInterlock
			width = rangesBarSize
		else:
			y = startPosition
			x = 0.0
			
			height = rangesBarSize
			width = lowInterlock
			
		# Create the rect for the low interlock.
		lowInterlockRange = createRect(x, y, height, width, interlockColor, strokeWidth, strokeColor)
			
		# Add low interlock rect to rectangles list.
		interlockRectangles.append(lowInterlockRange)
			
	# Check to see if high interlock rectangle should be drawn.
	if highInterlock!= None and highInterlock >= 0.0 and highInterlock < 100.0:
		if verticalDisplay:
			# Set the y and flip it such that is appears like Cartesian coordinate system.
			y = 0.0
			x = startPosition
			
			height = 100.0 - highInterlock
			width = rangesBarSize
		else:
			y = startPosition
			x = highInterlock
			
			height = rangesBarSize
			width = 100.0 - highInterlock
			
		# Create the rect for the high interlock.
		highInterlockRange = createRect(x, y, height, width,interlockColor, strokeWidth, strokeColor)
			
		# Add high interlock rect to rectangles list.
		interlockRectangles.append(highInterlockRange)
			
	return {'type': 'group', 'elements': interlockRectangles}

def createRangesBar(desiredLow, desiredHigh, verticalDisplay, strokeWidth, strokeColor, defaultRangeColor, desiredRangeColor, rangesBarSize, 
	startPosition):
	"""
	Creates the rects that represent the default and desired range.
		
	Args:
		desiredLow: Lower value of the desired operating range.
		desiredHigh: Upper value of the desired operating range.
		verticalDisplay: Denotes if the resource is displayed vertically or horizontally.
		strokeWidth: Width of the ranges bar's stroke.
		strokeColor: Color of the ranges bar's stroke.
		defaultRangeColor: Color of the default range.
		desiredRangeColor: Color of the desired range.
		rangesBarSize: Size of the ranges bar.
		startPosition: Start position for the ranges bar.

	Returns:
		Object that represents the default range and desired range (group of SVG rects).
	"""		
	# Initialize list to hold the rectangles.
	rangesBarRectangles = []
	
	# Calculate the length of the ranges bar.
	length = 100.0
	
	if verticalDisplay:
		y = 0.0
		x = startPosition
		
		height = length
		width = rangesBarSize
	else:
		y = startPosition
		x = 0.0

		height = rangesBarSize
		width = length
	
	# Create the rect for the ranges bar base.
	rangesBarBase = createRect(x, y, height, width, defaultRangeColor, strokeWidth, strokeColor)
		
	# Add rangesBar base to rectangles list.
	rangesBarRectangles.append(rangesBarBase)
	
	# Check to see if desired range rectangle should be drawn.
	if desiredLow != None and desiredHigh != None:
		if desiredLow < desiredHigh:
			if desiredLow >= 0.0 and desiredHigh <= 100.0:
				# Calculate the length of the desired range.
				desiredLength = desiredHigh - desiredLow
				
				if verticalDisplay:
					# Set the y flip it such that it appears like Cartesian coordinate system.
					desiredY = 100.0 - desiredLow - desiredLength
					desiredHeight = desiredLength
					desiredX = x
					desiredWidth = width
				else:
					desiredY = y
					desiredHeight = height
					desiredX = desiredLow
					desiredWidth = desiredLength
					
				# Create the rect for the desired range.
				desiredRange = createRect(desiredX, desiredY, desiredHeight, desiredWidth, desiredRangeColor, strokeWidth, strokeColor)
					
				# Add desired range rect to rectangles list.
				rangesBarRectangles.append(desiredRange)
	
	return {'type': 'group', 'elements': rangesBarRectangles}
	
def createRect(x, y, height, width, fill, strokeWidth, strokeColor):
	"""
	Creates an SVG rect.
		
	Args:
		x: x coordinate of the rect.
		y: y coordinate of the rect.
		height: Height of the rect.
		width: Width of the rect.
		fill: Color of the rect.
		strokeWidth: Width of the rect's stroke.
		strokeColor: Color of the rect's stroke.

	Returns:
		Object that represents an SVG rect.
	"""
	return {'type': 'rect', 'fill': {'paint': fill}, 'height': height, 'width': width, 'x': x, 'y': y, 'stroke': strokeColor, 'stroke-width': strokeWidth}

def createSetpoint(setpointValue, setpointColor, verticalDisplay, reverseIndicator, strokeWidth, strokeColor, indicatorSize, rangesBarSize, startPosition,
	rangesBarStrokeWidth, indicatorStrokeWidth, labelVisible, labelPosition):
	"""
	Creates the setpoint polygon.
		
	Args:
		setpointValue: Value of the setpoint.
		setpointColor: Color of the setpoint.
		verticalDisplay: Denotes if the resource is displayed vertically or horizontally.
		reverseIndicator: Puts the indicator on the other side of the ranges bar.
		strokeWidth: Width of the setpoint's stroke.
		strokeColor: Color of the setpoint's stroke.
		indicatorSize: Size (altitude) of the indicator.
		rangesBarSize: Size of the ranges bar.
		startPosition: Start position of ranges bar.
		rangesBarStrokeWidth: Width of the ranges bar's stroke.
		indicatorStrokeWidth: Width of the indicator's stroke.
		labelVisible: Denotes whether label is visible.
		labelPosition: Settings regarding the label distance from the indicator.

	Returns:
		Object that represents the setpoint (SVG polygon).
	"""
	# See if the alarm rect should take label offsets into account.
	if labelPosition['applyOffsetsOnlyWhenLabelVisible']:
		includeLabelOffsets = True if labelVisible else False
	else:
		includeLabelOffsets = True			
	
	if setpointValue != None and setpointValue >= 0.0 and setpointValue <= 100.0:		
		# If strokeWidth is negative, set it to 0.
		if strokeWidth < 0:
			strokeWidth = 0
			
		# Set the length of the sides of the setpoint.
		setpointSideLength = rangesBarSize / 2.0 - rangesBarStrokeWidth / 2.0 - strokeWidth / 2.0
		
		# Calculate x and y for the four points.
		if verticalDisplay:
			# Flip y1 such that it appears like Cartesian coordinate system.
			y1 = 100.0 - setpointValue
			
			x1 = startPosition + strokeWidth / 2.0 + rangesBarStrokeWidth / 2.0
			
			if includeLabelOffsets:
				x1 = max(x1, x1 - (labelPosition['horizontalOffset'] / 2.0))
			
			x2 = x1 + setpointSideLength
			y2 = y1 - setpointSideLength
			
			x3 = x1 + setpointSideLength * 2.0
			y3 = y1
			
			x4 = x1 + setpointSideLength
			y4 = y1 + setpointSideLength
		else:
			x1 = setpointValue
			
			y1 = startPosition + strokeWidth / 2.0 + rangesBarStrokeWidth / 2.0
				
			if includeLabelOffsets:
				y1 = max(y1, y1 - (labelPosition['verticalOffset'] / 2.0))
			
			x2 = x1 + setpointSideLength
			y2 = y1 + setpointSideLength
			
			x3 = x1
			y3 = y2 + setpointSideLength
			
			x4 = x1 - setpointSideLength
			y4 = y2
			
		points = '{x1},{y1} {x2},{y2} {x3},{y3} {x4},{y4}'.format(x1 = x1, y1 = y1, x2 = x2, y2 = y2, x3 = x3, y3 = y3, x4 = x4, y4 = y4)
		
		return {'type': 'polygon', 'fill': {'paint': setpointColor}, 'points': points, 'stroke': strokeColor, 'stroke-width': strokeWidth}
	else:
		return {}
		
def createLabel(processValue, normalizedValue, formattedValue, labelStyle, position, verticalDisplay, reverseIndicator, rangesBarStrokeWidth,
	indicatorSize, rangesBarSize, indicatorStrokeWidth):
	"""
	Creates the process value label.
		
	Args:
		processValue: Current raw value of the process.
		normalizedValue: Process value normalized to 0->100 range.
		formattedValue: String version of the process value, formatted by the label.format parameter. 
		labelStyle: Style of the label.
		position: Settings regarding the distance from the indicator.
		verticalDisplay: Denotes if the resource is displayed vertically or horizontally.
		reverseIndicator: Puts the indicator on the other side of the ranges bar.
		rangesBarStrokeWidth: Width of the ranges bar's stroke.
		indicatorSize: Size (altitude) of the indicator.
		rangesBarSize: Size of the ranges bar.
		indicatorStrokeWidth: Width of the indicator's stroke.

	Returns:
		Object that represents the process value label (SVG text).
	"""
	# Get the distance from indicator vertical offset and horizontal offset.
	verticalOffset, horizontalOffset = position['verticalOffset'], position['horizontalOffset']
	
	# Calculate the side length of the indicator.
	sideLength = 2.0 * indicatorSize / math.sqrt(3.0)	
	
	if verticalDisplay:
		# Flip y1 such that it appears like Cartesian coordinate system.
		y = 100.0 - normalizedValue
		
		# If process value is out of the min-max range, then adjust y
		# so that the label is not outside of the viewport.
		if y < 0.0:
			y = 0.0
		elif y > 100.0:
			y = 100.0
			
		# Calculate the bottom indicator point.
		bottomIndicatorPoint = y + (sideLength / 2.0)	+ indicatorStrokeWidth / 2
		
		# See if label will fit below the bottom indicator point.
		if bottomIndicatorPoint + labelStyle['fontSize'] > 100.0:
			# Process value is too low to fit the label beneath indicator.
			# Place it above it.
			y = y - (sideLength / 2.0) - indicatorStrokeWidth / 2 - verticalOffset
			dominantBaseline = 'auto'
		else:
			# Process value can fit beneath the indicator.
			y = bottomIndicatorPoint + verticalOffset
			dominantBaseline = 'hanging'
		
		# Figure out the x position.
		if reverseIndicator:
			x = rangesBarSize + indicatorSize + rangesBarStrokeWidth + indicatorStrokeWidth * 1.5
			
			if horizontalOffset < 0:
				x = x + horizontalOffset
			
			textAnchor = 'end'
		else:
			x = 0 - horizontalOffset
			textAnchor = 'start'
	else:
		x = normalizedValue
		
		# If process value is out of the min-max range, then adjust x
		# so that the label is not outside of the viewport.
		if x < 0.0:
			x = 0.0
		elif x > 100.0:
			x = 100.0
			
		# Calculate the left indicator point.
		leftIndicatorPoint = x - (sideLength / 2.0) - indicatorStrokeWidth / 2
		
		# See if label will fit to the right of the right indicator point.
		if leftIndicatorPoint - labelStyle['font-size'] * len(formattedValue) < 0.0:
			# Process value is too low to fit the label to the left of the indicator.
			# Place it to the right of it.
			x = x + (sideLength / 2.0)	+ indicatorStrokeWidth / 2 + horizontalOffset
			textAnchor = 'start'
		else:
			x = leftIndicatorPoint - horizontalOffset
			textAnchor = 'end'
		
		# Figure out the y position.
		if reverseIndicator:
			y = rangesBarSize + indicatorSize + rangesBarStrokeWidth + indicatorStrokeWidth * 1.5
			
			if verticalOffset < 0:
				y = y + verticalOffset
			
			# Using text-after-edge rather than auto so that certain numbers (like 3) do not get cut off.
			dominantBaseline = 'text-after-edge'
		else:
			y = 0 - verticalOffset
			dominantBaseline = 'text-before-edge'
	
	# Create and return the SVG text.
	return {'type': 'text', 'style': labelStyle, 'x': x, 'y': y, 'text': formattedValue, 'dominant-baseline': dominantBaseline, 'text-anchor': textAnchor}

def createIndicator(processValue, startPosition, color, size, strokeWidth, strokeColor, verticalDisplay, reverseIndicator, rangesBarStrokeWidth, rangesBarSize,
	labelVisible, labelPosition):
	"""
	Creates the triangular indicator.
		
	Args:
		processValue: Current value of the process.
		startPosition: Start position of ranges bar.
		color: Color of the indicator.
		size: Size (altitude) of the indicator.
		strokeWidth: Size of the stroke.
		strokeColor: Color of the stroke.
		verticalDisplay: Denotes if the resource is displayed vertically or horizontally.
		reverseIndicator: Puts the indicator on the other side of the ranges bar.
		rangesBarStrokeWidth: Width of the ranges bar's stroke.
		rangesBarSize: Size of the ranges bar.
		labelVisible: Denotes whether label is visible.
		labelPosition: Settings regarding the label distance from the indicator.
	
	Returns:
		Object that represents the indicator (SVG polygon).
	"""
	# See if the alarm rect should take label offsets into account.
	if labelPosition['applyOffsetsOnlyWhenLabelVisible']:
		includeLabelOffsets = True if labelVisible else False
	else:
		includeLabelOffsets = True		
	
	# Check to see if processValue is within the range.
	# If it is not, then set it equal to max if it is
	# greater than max, otherwise set it equal to min.
	if processValue < 0.0:
		processValue = 0.0
	elif processValue > 100.0:
		processValue = 100.0
	
	# Calculate the side length.
	sideLength = 2.0 * size / math.sqrt(3.0)
	
	# Calculate x and y for the three points of the triangle.
	if verticalDisplay:
		# Flip y1 such that it appears like Cartesian coordinate system.
		y1 = 100.0 - processValue
		y2 = y1 - (sideLength / 2.0)
		y3 = y1 + (sideLength / 2.0)
		if reverseIndicator:
			x1 = startPosition + rangesBarSize + rangesBarStrokeWidth / 2.0 + strokeWidth
			
			if includeLabelOffsets:
				x1 = max(x1, x1 - (labelPosition['horizontalOffset'] / 2.0))
			
			x2 = x1 + size
			x3 = x2
		else:
			x1 = startPosition - (rangesBarStrokeWidth / 2.0) - strokeWidth
			x2 = x1 - size
			x3 = x1 - size
	else:
		x1 = processValue
		x2 = x1 - (sideLength / 2.0)
		x3 = x1 + (sideLength / 2.0)
		if reverseIndicator:
			y1 = startPosition + rangesBarSize + rangesBarStrokeWidth / 2.0 + strokeWidth
			
			if includeLabelOffsets:
				y1 = max(y1, y1 - (labelPosition['verticalOffset'] / 2.0))
			
			y2 = y1 + size
			y3 = y2
		else:
			y1 = startPosition - (rangesBarStrokeWidth / 2.0) - strokeWidth
			y2 = y1 - size
			y3 = y2
	
	# Create the list of points for the triangle.
	points = '{x1},{y1} {x2},{y2} {x3},{y3}'.format(x1 = x1, y1 = y1, x2 = x2, y2 = y2, x3 = x3, y3 = y3)
	
	return {'type': 'polygon', 'fill': {'paint': color}, 'points': points, 'stroke': strokeColor, 'stroke-width': strokeWidth}
	
def normalizeValue(value, minValue, maxValue):
	"""
	Normalizes the value to be within 0 -> 100 range.
		
	Args:
		value: Value to be normalized.
		minValue: Minimum value of the range.
		maxValue: Maximum value of the range.
	
	Returns:
		Normalized value within 0 -> 100.
	"""
	return (float(value - minValue) / float(maxValue - minValue)) * 100.0