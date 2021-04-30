import unittest
import Gaffer
import GafferDispatch
import GafferImage
import GafferTest
import GafferDispatchTest
import GafferScene
import IECore

import TaskAlgo

class TaskAlgoTest( GafferTest.TestCase ) :

	def __exampleTaskNodeGraph1( self ) :

		# A Gaffer script with nodes that have the 'fileName' parameter and have downstream task nodes
		#
		#
		#  L1_1
		#   | \
		#   |  \
		#   |   \
		#  L2_1  \    L2_2
		#   | \   |   /
		#   |  \  |  /
		#   |   \ | /
		# L3_1   L3_2

		s = Gaffer.ScriptNode()

		s["L1_1"] = GafferImage.ImageWriter()
		s["L1_1"]["fileName"].setValue( "/some/path/to/some/file/test_1_1" )
		s["L2_1"] = GafferDispatchTest.TextWriter()
		s["L2_1"]["fileName"].setValue( "/some/path/to/some/file/test_2_1" )
		s["L3_1"] = GafferDispatchTest.TextWriter()
		s["L3_1"]["fileName"].setValue( "/some/path/to/some/file/test_3_1" )

		s["L2_1"]["preTasks"][0].setInput( s["L1_1"]["task"] )
		s["L3_1"]["preTasks"][0].setInput( s["L2_1"]["task"] )

		log = []
		s["L3_2"] = GafferDispatchTest.LoggingTaskNode( log = log )

		s["L3_2"]["preTasks"][0].setInput( s["L2_1"]["task"] )
		s["L3_2"]["preTasks"][1].setInput( s["L1_1"]["task"] )

		# Add an upstream node that doesn't have a fileName parameter
		s["L2_2"] = GafferDispatchTest.LoggingTaskNode( log=log )
		s["L3_2"]["preTasks"][2].setInput( s["L2_2"]["task"] )

		return s

	def __exampleTaskNodeGraph2( self ) :

		# A Gaffer script with nodes that have the 'fileName' parameter,
		# have downstream task nodes, and a node outputting a scene with
		# a globals->outputs filename
		#
		#
		#  L1_1             L1_2
		#   |  \ _ _ _       /
		#   |          \    /
		#   |           \  /
		# L2_1   L2_2   L2_3          L2_4
		#     \    |    /  \            |
		#      \   |   /    \           |
		#       \  |  /      \          |
		#        L3_1        L3_2     L3_3

		s = Gaffer.ScriptNode()

		s["L1_1"] = GafferImage.ImageWriter()
		s["L1_1"]["fileName"].setValue( "/some/path/to/some/file/test_1_1" )
		s["L1_2"] = GafferDispatchTest.TextWriter()
		s["L1_2"]["fileName"].setValue( "/some/path/to/some/file/test_1_2" )

		s["L2_1"] = GafferDispatchTest.TextWriter()
		s["L2_1"]["fileName"].setValue( "/some/path/to/some/file/test_2_1" )
		s["L2_2"] = GafferDispatchTest.TextWriter()
		s["L2_2"]["fileName"].setValue( "/some/path/to/some/file/test_2_2" )
		s["L2_3"] = GafferImage.ImageWriter()
		s["L2_3"]["fileName"].setValue( "/some/path/to/some/file/test_2_3" )

		s["L3_1"] = GafferDispatchTest.TextWriter()
		s["L3_1"]["fileName"].setValue( "/some/path/to/some/file/test_3_1" )
		s["L3_2"] = GafferDispatchTest.LoggingTaskNode(log=[])

		s["L2_4"] = GafferScene.StandardOptions()
		s["L3_3"] = GafferScene.Outputs()

		s["L2_4"]["options"]["renderCamera"]["value"].setValue('/group/camera')
		s["L2_4"]["options"]["renderCamera"]["enabled"].setValue(True)

		# Setup for L3_3 (Outputs node), only relevant property is 'fileName' in these unit tests
		s["L3_3"]["outputs"].addChild( Gaffer.ValuePlug( "output1", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		s["L3_3"]["outputs"]["output1"].addChild( Gaffer.StringPlug( "fileName", defaultValue = '', flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		s["L3_3"]["outputs"]["output1"].addChild( Gaffer.BoolPlug("active", defaultValue=True, flags=Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		s["L3_3"]["outputs"]["output1"].addChild( Gaffer.StringPlug( "name", defaultValue = '', flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		s["L3_3"]["outputs"]["output1"].addChild( Gaffer.StringPlug( "type", defaultValue = '', flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		s["L3_3"]["outputs"]["output1"].addChild( Gaffer.StringPlug( "data", defaultValue = '', flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		s["L3_3"]["outputs"]["output1"].addChild( Gaffer.CompoundDataPlug( "parameters", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		s["L3_3"]["outputs"]["output1"]["parameters"].addChild( Gaffer.NameValuePlug( "quantize", Gaffer.IntVectorDataPlug( "value", defaultValue = IECore.IntVectorData( [ 0, 0, 0, 0 ] ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), "quantize" ) )

		s["L3_3"]["outputs"]["output1"]["name"].setValue('Batch/Beauty')
		s["L3_3"]["outputs"]["output1"]["fileName"].setValue('/renders/examples/TaskAlgoTest/beauty.exr')
		s["L3_3"]["outputs"]["output1"]["type"].setValue('exr')
		s["L3_3"]["outputs"]["output1"]["data"].setValue('rgba')

		s["L2_1"]["preTasks"][0].setInput( s["L1_1"]["task"] )
		s["L2_3"]["preTasks"][0].setInput( s["L1_1"]["task"] )
		s["L2_3"]["preTasks"][1].setInput( s["L1_2"]["task"] )
		s["L3_1"]["preTasks"][0].setInput( s["L2_1"]["task"] )
		s["L3_1"]["preTasks"][1].setInput( s["L2_2"]["task"] )
		s["L3_1"]["preTasks"][2].setInput( s["L2_3"]["task"] )
		s["L3_2"]["preTasks"][0].setInput( s["L2_3"]["task"] )
		s["L3_3"]["in"].setInput( s["L2_4"]["out"] )

		return s

	class __CapturingVisitor( object ) :

		def __init__( self ) :
			self.visited = []

		def __call__( self, node ) :
			self.visited.append( node )
			return True

	def testGetRelevantFiles( self ) :

		# Test using a task plug with no source
		taskPlug = GafferDispatch.TaskNode.TaskPlug()
		fileNames = TaskAlgo.getRelevantFiles( taskPlug )
		self.assertEqual( fileNames, [] )

		# Run tests on first example graph (see definition above)
		g1 = self.__exampleTaskNodeGraph1()

		fileNames = TaskAlgo.getRelevantFiles( g1["L3_2"]['task'] )
		self.assertEqual( fileNames, [ "/some/path/to/some/file/test_2_1", "/some/path/to/some/file/test_1_1" ] )

		fileNames = TaskAlgo.getRelevantFiles( g1["L2_2"]['task'] )
		self.assertEqual( fileNames, [] )

		fileNames = TaskAlgo.getRelevantFiles( g1["L3_1"]['task'] )
		self.assertEqual( fileNames, [ "/some/path/to/some/file/test_3_1", "/some/path/to/some/file/test_2_1",
									   "/some/path/to/some/file/test_1_1" ] )

		fileNames = TaskAlgo.getRelevantFiles( g1["L2_1"]['task'] )
		self.assertEqual( fileNames, [ "/some/path/to/some/file/test_2_1", "/some/path/to/some/file/test_1_1" ] )

		fileNames = TaskAlgo.getRelevantFiles( g1["L1_1"]['task'] )
		self.assertEqual( fileNames, [ "/some/path/to/some/file/test_1_1" ] )

		# Run tests on second example graph (see definition above)
		g2 = self.__exampleTaskNodeGraph2()

		fileNames = TaskAlgo.getRelevantFiles( g2["L2_2"]['task'] )
		self.assertEqual( fileNames, [ '/some/path/to/some/file/test_2_2' ] )

		fileNames = TaskAlgo.getRelevantFiles( g2["L3_1"]['task'] )
		self.assertEqual( fileNames, [ '/some/path/to/some/file/test_3_1', '/some/path/to/some/file/test_2_1',
									  '/some/path/to/some/file/test_2_2', '/some/path/to/some/file/test_2_3',
									  '/some/path/to/some/file/test_1_1', '/some/path/to/some/file/test_1_2' ] )

		fileNames = TaskAlgo.getRelevantFiles( g2["L3_2"]['task'] )
		self.assertEqual( fileNames, [ '/some/path/to/some/file/test_2_3', '/some/path/to/some/file/test_1_1',
									  '/some/path/to/some/file/test_1_2' ] )

		fileNames = TaskAlgo.getRelevantFiles( g2["L3_3"]['out'] )
		self.assertEqual( fileNames, [ "/renders/examples/TaskAlgoTest/beauty.exr" ] )

		fileNames = TaskAlgo.getRelevantFiles( g2["L2_4"]['out'] )
		self.assertEqual( fileNames, [] )

	def testGetNodeSourceFileNames( self ) :

		# Run tests on second example graph (see definition above)
		g2 = self.__exampleTaskNodeGraph2()

		fileNames = TaskAlgo.getNodeSourceFileNames( g2["L2_2"] )
		self.assertEqual( fileNames, [ '/some/path/to/some/file/test_2_2' ] )

		fileNames = TaskAlgo.getNodeSourceFileNames( g2["L1_2"] )
		self.assertEqual( fileNames, [ '/some/path/to/some/file/test_1_2' ] )

		fileNames = TaskAlgo.getNodeSourceFileNames( g2["L3_2"] )
		self.assertEqual( fileNames, [] )

	def testGetSceneOutputFiles( self ) :

		# Run tests on second example graph (see definition above)
		g2 = self.__exampleTaskNodeGraph2()

		fileNames = TaskAlgo.getSceneOutputFiles( g2["L3_3"]['out'] )
		self.assertEqual(fileNames, [ "/renders/examples/TaskAlgoTest/beauty.exr" ] )

		fileNames = TaskAlgo.getSceneOutputFiles( g2["L2_4"]['out'] )
		self.assertEqual(fileNames, [] )


	def testGetUpstreamNodeSourceFileNames( self ) :

		# Run tests on first example graph (see definition above)
		g1 = self.__exampleTaskNodeGraph1()

		fileNames = TaskAlgo.getUpstreamNodeSourceFileNames( g1["L2_2"] )
		self.assertEqual( fileNames, [] )

		fileNames = TaskAlgo.getUpstreamNodeSourceFileNames( g1["L3_2"] )
		self.assertEqual( fileNames, [ "/some/path/to/some/file/test_2_1", "/some/path/to/some/file/test_1_1" ] )

		fileNames = TaskAlgo.getUpstreamNodeSourceFileNames( g1["L2_1"] )
		self.assertEqual( fileNames, [ "/some/path/to/some/file/test_2_1", "/some/path/to/some/file/test_1_1" ] )

		# Run tests on second example graph (see definition above)
		g2 = self.__exampleTaskNodeGraph2()

		fileNames = TaskAlgo.getUpstreamNodeSourceFileNames( g2["L2_2"] )
		self.assertEqual( fileNames, [ '/some/path/to/some/file/test_2_2' ] )

		fileNames = TaskAlgo.getUpstreamNodeSourceFileNames( g2["L2_1"] )
		self.assertEqual( fileNames, [ '/some/path/to/some/file/test_2_1', '/some/path/to/some/file/test_1_1' ] )

		fileNames = TaskAlgo.getUpstreamNodeSourceFileNames( g2["L3_2"] )
		self.assertEqual( fileNames, [ '/some/path/to/some/file/test_2_3', '/some/path/to/some/file/test_1_1',
									  '/some/path/to/some/file/test_1_2' ] )

		fileNames = TaskAlgo.getUpstreamNodeSourceFileNames( g2["L3_3"] )
		self.assertEqual( fileNames, [ "/renders/examples/TaskAlgoTest/beauty.exr" ] )

if __name__ == "__main__" :
	unittest.main()
