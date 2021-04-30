import Gaffer
import GafferScene


class __CapturingVisitor( object ) :

	def __init__( self ) :
		self.visited = []

	def __call__( self, node ) :
		self.visited.append( node )
		return True

## Returns a list containing all the referenced source file names for the
# given plug's source node and for all of its upstream nodes
def getRelevantFiles( plug ) :

	# Get the node that provides the plug input
	source = plug.source()
	sourceNode = source.node()

	if isinstance( sourceNode, Gaffer.Node ) :
		return getUpstreamNodeSourceFileNames( sourceNode )

	# No relevant files in the case that the plug has no node input
	return []

## Returns a list containing all the referenced source file names for the
# given node and for all of its upstream nodes
def getUpstreamNodeSourceFileNames( node ) :

	# Get all nodes that are upstream of node
	v = __CapturingVisitor()
	Gaffer.NodeAlgo.visitUpstream( node, v )

	# Return all source file names found under this and upstream nodes
	filenames = []
	for n in [ node ] + v.visited :
		# Collect file names excluding duplicates
		filenames += list( set( getNodeSourceFileNames( n ) ) - set( filenames ) )

	return filenames

## Returns a list of all source files relevant to a single node
# This includes any of the nodes 'fileName' property, any input/output
# scene plugs' globals->outputs file names, and/or any "in_filename"
# under node parameters (an example being OSLShader nodes)
def getNodeSourceFileNames( node ) :

	sourceFileNames = []

	# Check for "fileName" in top level node keys
	if "fileName" in set( node.keys() ):
		sourceFileNames.append( node["fileName"].getValue() )

	# Check for "in_filename" under node parameters
	if "parameters" in set( node.keys() ):
		if "in_filename" in set( node["parameters"].keys() ):
			sourceFileNames.append( node["parameters"]["in_filename"].getValue() )

	# If there is a scene input to/output from the node, also return any
	# of the scene's globals output file names
	if "in" in set( node.keys() ) :
		if isinstance( node['in'], GafferScene.ScenePlug ) :

			# Search input scene plug for source file references
			# and add them to sourceFileNames without duplicates
			sourceFileNames += list( set( getSceneOutputFiles( node['in'] ) ) - set( sourceFileNames ) )

		elif isinstance( node['in'], Gaffer.ArrayPlug ) :

			# Go through all input scene plug for source file references
			# and add them to sourceFileNames without duplicates
			for key in node['in'].keys() :
				if isinstance( node['in'][key], GafferScene.ScenePlug ) :
					sourceFileNames += list( set( getSceneOutputFiles( node['in'][key] ) ) - set( sourceFileNames ) )

	if "out" in set( node.keys() ) and isinstance( node['out'], GafferScene.ScenePlug ) :

		# Search output scene plug for source file references
		# and add them to sourceFileNames without duplicates
		sourceFileNames += list( set( getSceneOutputFiles(node['out'] ) ) - set( sourceFileNames ) )

	return sourceFileNames

## Returns a list of all scene globals output file names
def getSceneOutputFiles( scenePlug ) :

	sceneOutputFiles = []
	sceneGlobals = scenePlug["globals"].getValue()

	for key in sceneGlobals.keys() :

		# Collect the scene globals output file names
		if key[0:7] == "output:" :
			sceneOutputFiles.append( sceneGlobals[ key ].getName() )

	return sceneOutputFiles
