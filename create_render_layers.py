#create_render_layers.py
#Ignatius Jonathan Sugijono
#February 20, 2021

import nuke

node = nuke.selectedNode()
dot = nuke.nodes.Dot(inputs = [node])

#Creating the shuffle nodes
def shuffleLayer( node, layer ):
	shuffleNode = nuke.nodes.Shuffle( label = layer , inputs=[dot] )
	shuffleNode['in'].setValue( layer )
	shuffleNode['postage_stamp'].setValue( True )
	CCNode = nuke.nodes.ColorCorrect( label = layer ,inputs = [shuffleNode] )
	GradeNode = nuke.nodes.Grade(label = layer , inputs = [CCNode] )
	return  GradeNode

def autoComp(node):
	
	#List of a channels
	channels = node.channels()
	layers = list( set([c.split('.')[0] for c in channels]) )
	layers.sort()  

	# Create a UI for user to use
	p = nuke.Panel( 'Create Shuffle Nodes' )
	layers.remove('diffuse_direct')
	layers.insert(0, 'diffuse_direct')
	p.addEnumerationPulldown( 'diffuse direct', ' '.join( layers ) )
	layers.remove('diffuse_indirect')
	layers.insert(0, 'diffuse_indirect')
	p.addEnumerationPulldown( 'diffuse indirect', ' '.join( layers ) )
	layers.remove('specular_direct')
	layers.insert(0, 'specular_direct')
	p.addEnumerationPulldown( 'specular direct', ' '.join( layers ) )
	layers.remove('specular_indirect')
	layers.insert(0, 'specular_indirect')
	p.addEnumerationPulldown( 'specular indirect', ' '.join( layers ) )
	layers.remove('sss_direct')
	layers.insert(0, 'sss_direct')
	p.addEnumerationPulldown( 'sss direct', ' '.join( layers ) )
	layers.remove('sss_indirect')
	layers.insert(0, 'sss_indirect')
	p.addEnumerationPulldown( 'sss indirect', ' '.join( layers ) )
	layers.remove('transmission')
	layers.insert(0, 'transmission')
	p.addEnumerationPulldown( 'transmission', ' '.join( layers ) )
	channels.remove('depth.Z')
	channels.insert(0, 'depth.Z')
	p.addEnumerationPulldown( 'depth', ' '.join( channels ) )
	if not p.show():
		return

	# STORE PANEL RESULT IN VARIABLES FOR EASE OF USE
	diffDirect = p.value( 'diffuse direct' )
	diffIndirect = p.value( 'diffuse indirect' )
	specDirect = p.value( 'specular direct' )
	specIndirect = p.value( 'specular indirect' )
	sssDirect = p.value( 'sss direct' )
	sssIndirect = p.value( 'sss indirect' )
	transmission = p.value( 'transmission' )
	depth = p.value( 'depth' )    

	# CREATE SHUFFLE AND COLOR CORRECT NODES
	diffDirectCCNode = shuffleLayer( node, diffDirect )
	diffIndirectCCNode = shuffleLayer( node,  diffIndirect )

	specDirectCCNode = shuffleLayer( node, specDirect )
	specIndirectCCNode = shuffleLayer( node, specIndirect )
	
	sssDirectCCNode = shuffleLayer( node, sssDirect )
	sssIndirectCCNode = shuffleLayer( node, sssIndirect )
	
	TransmissionCCNode = shuffleLayer (node, transmission)

	#Creating a merge node for ShuffleNode
	resultDiff = nuke.nodes.Merge2( operation='plus', inputs=[ diffIndirectCCNode, diffDirectCCNode ], output = 'rgb')
	resultSpec = nuke.nodes.Merge2( operation='plus', inputs=[ specIndirectCCNode, specDirectCCNode ], output = 'rgb')
	resultSSS = nuke.nodes.Merge2( operation='plus', inputs=[ sssIndirectCCNode, sssDirectCCNode ], output = 'rgb')

	#Creating a second merge
	result1 = nuke.nodes.Merge2( operation='plus', inputs=[ resultDiff, resultSpec ], output = 'rgb')
	result2 = nuke.nodes.Merge2( operation='plus', inputs=[ resultSSS, TransmissionCCNode ], output = 'rgb')
	result3 = nuke.nodes.Merge2( operation='plus', inputs=[ result1, result2 ], output = 'rgb', label = 'FINAL MERGE' )

#From Foundry Developer Website
def scaleNodes( scale ):
	nodes = nuke.selectedNodes()    # GET SELECTED NODES
	amount = len( nodes )    # GET NUMBER OF SELECTED NODES
	if amount == 0:    return # DO NOTHING IF NO NODES WERE SELECTED

	allX = sum( [ n.xpos()+n.screenWidth()/2 for n in nodes ] )  # SUM OF ALL X VALUES
	allY = sum( [ n.ypos()+n.screenHeight()/2 for n in nodes ] ) # SUM OF ALL Y VALUES

	# CENTER OF SELECTED NODES
	centreX = allX / amount
	centreY = allY / amount

	# REASSIGN NODE POSITIONS AS A FACTOR OF THEIR DISTANCE TO THE SELECTION CENTER
	for n in nodes:
		n.setXpos( centreX + ( n.xpos() - centreX ) * scale )
		n.setYpos( centreY + ( n.ypos() - centreY ) * scale )

def CreateShuffleNode(node , scale):
	autoComp(node)
	scaleNodes(scale)
	for n in nuke.allNodes():
		nuke.autoplaceSnap( n )

CreateShuffleNode(node , 3)
