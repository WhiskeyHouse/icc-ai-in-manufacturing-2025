def doGet(request, session):
	#	For more Information please visit the API Docs:
	#		https://sandalwood.com/systems-integration/ignition-rest-api/
	#	EXAMPLE USAGE
	#	GET REQUEST
	#	Postman URL:
	#	http://IGNITIONURL/system/webdev/PROJECTNAME/ListNamedQueries
	#
	# Returns data in the following format:
	# AS JSON
	# Project Name:
	#	Queries:
	#		Query1
	#			Parameters:
	#				Parameter 1
	#				Parameter 2
	import os
	import system
	from com.inductiveautomation.ignition.gateway import IgnitionGateway
	
	FinalData = {}
	#Below function goes into ignition and gets the named query manager it then gets the query from the project name and path
	def get_query_info(project_name, query_path):
	    named_query = IgnitionGateway.get().getNamedQueryManager().getQueryFromPath(project_name, query_path)
	
	    # Check if named_query is None
	    if named_query is not None:
	    	#grabs the RAW SQL Query
	        query_statement = named_query.getQuery()
	        #Grabs all the named parameters
	        parameters = named_query.getParameters()
	        list_of_params = [param.getIdentifier() for param in parameters] if parameters else None
	    else:
	        query_statement = None
	        list_of_params = None
	
	    return {'Parameters': list_of_params, 'QueryStatement': query_statement}
	
	#The following function goes into the OS and looks for named queries
	#Take a look inside the Ignition installation directory to get a better understanding of what is happening
	def find_folders_with_query_sql(root_folder):
	    project_and_query_names = {}
	
	    for foldername, subfolders, filenames in os.walk(root_folder):
	        if 'query.sql' in filenames:
	            # Extracting project name from the path
	            relative_path = os.path.relpath(foldername, root_folder)
	            project_name = relative_path.split(os.path.sep)[0]
	
	            # Extracting query name
	            query_name = os.path.basename(foldername)
	
	            # Extracting subfolder path for queries in subfolders
	            subfolder_path = os.path.relpath(foldername, os.path.join(root_folder, project_name, 'ignition', 'named-query'))
	
	            # Use forward slashes for subfolder path
	            subfolder_path = subfolder_path.replace(os.path.sep, '/')
	
	            # Organizing data into a dictionary
	            if project_name not in project_and_query_names:
	                project_and_query_names[project_name] = {'Queries': {}}
	            if subfolder_path:
	                # Remove the query name from subfolder path
	                subfolder_path = os.path.dirname(subfolder_path)
	                query_info = get_query_info(project_name, (os.path.join(subfolder_path, query_name)).replace('\\', '/'))
	                query_name = os.path.splitext(os.path.basename(query_name))[0]  # Remove file extension
	                project_and_query_names[project_name]['Queries'][os.path.join(subfolder_path, query_name).replace('\\', '/')] = query_info
	            else:
	                query_info = get_query_info(project_name, query_name)
	                query_name = os.path.splitext(os.path.basename(query_name))[0]  # Remove file extension
	                project_and_query_names[project_name]['Queries'][query_name.replace('\\', '/')] = query_info
	
	    return project_and_query_names
	
	##################The script below grabs all Named Queries that exist for a project##################
	context = IgnitionGateway.get()
	project_parent_folder = str(context.systemManager.dataDir.absoluteFile).replace('\\', '/') + '/projects'
	
	# Folder Path
	root_folder_path = project_parent_folder
	
	# Run find folders with query sql
	result = find_folders_with_query_sql(root_folder_path)
	
	FinalData = {'Data': result} if result else {}
	
	# Format to json
	json_data = system.util.jsonEncode(FinalData)
	
	return {'json': json_data}