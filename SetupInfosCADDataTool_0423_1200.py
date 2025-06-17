# PYTHON script
import os
import ansa
from ansa import *


deck = constants.LSDYNA
@session.defbutton('2-MESH', 'MeshReplaceTool','Thay thế mesh sửa penetration....')
def MeshReplaceTool():
	
	for i in range(0, 1000, 1):
		ElemsSelected = base.PickEntities(deck, ['ELEMENT_SHELL'])
		if ElemsSelected != None:
			ListGroupElemsReplace = DivideGroupElemReplace(ElemsSelected)
#			print(len(ListGroupElemsReplace))
			if len(ListGroupElemsReplace) >0:
				base.SetEntityVisibilityValues(deck, {'all': 'off'})
				base.SetEntityVisibilityValues(deck, {'ELEMENT_SHELL': 'on', 'POINT': 'on'})
				
				ReplaceElemsFunc(ListGroupElemsReplace)
				
		else:
			return 1

##**********************************  Thay the tung group mesh tuong ung ********************************************
def ReplaceElemsFunc(ListGroupElemsReplace):
	
	for ShellsSelected in ListGroupElemsReplace:
		base.Or(ShellsSelected)
		ListPointRelative = RelativePointOnShellSelected(ShellsSelected)
		ListBoundaryNodes = FindBoundaryNodesOnShell(ShellsSelected)
		if len(ListBoundaryNodes) >0:
			PartReplace = base.GetEntityPart(ShellsSelected[0])
			ListPartOldsConnect = FindPropAssignMeshReplace(ShellsSelected, PartReplace)
			if len(ListPartOldsConnect) >0:
				base.StoreLockView("Lock1", True)
				ListElemBoundConnect, ListNodesReleaseReq = FindNodesRelease(ListBoundaryNodes, ListPartOldsConnect, ShellsSelected)
				if len(ListElemBoundConnect) >0:
					ListNodesReleaseReq.sort()
					ElemsRemoveReq = FindElemsReplace(ListNodesReleaseReq, ListElemBoundConnect, ListPartOldsConnect)
					if len(ElemsRemoveReq) >0:
						RemoveElemsFunc(ElemsRemoveReq, ShellsSelected)
						
		base.DeleteEntity(ListPointRelative, True)
		base.All()	

##**********************************  Danhh point vao vung mesh thay the ********************************************
def RelativePointOnShellSelected(ShellsSelected):
	
	ListPointRelative = []
	NodesOnShellSelect = base.CollectEntities(deck, ShellsSelected, ['NODE'])
	for i in range(0, len(NodesOnShellSelect), 1):
		ValsNodeSelect = NodesOnShellSelect[i].get_entity_values(deck, ['X', 'Y', 'Z'])
		ListPointRelative.append(base.Newpoint(ValsNodeSelect['X'], ValsNodeSelect['Y'], ValsNodeSelect['Z']))
	
	return ListPointRelative
			
##**********************************  Xoa elem cu va set vao part tuong ung ********************************************
def RemoveElemsFunc(ElemsRemoveReq, ShellsSelected):
	
	base.LoadStoredLockView('Lock1')
	container_highlight = base.CreateEntity(constants.ABAQUS, "HIGHLIGHT_CONTAINER")
	base.AddToHighlight(container = container_highlight, entities = ElemsRemoveReq, colors = ['WHITE'])
	base.RedrawAll()
	
	response = guitk.UserQuestion('Do you want delete element ???')
	if response == 1:
		PartElemRemoveReq = base.GetEntityPart(ElemsRemoveReq[0])
		base.DeleteEntity(ElemsRemoveReq, True)
		base.SetEntityPart(ShellsSelected, PartElemRemoveReq)
		
		ListElemOnPartAutoPase = base.CollectEntities(deck, PartElemRemoveReq, ['ELEMENT_SHELL'])
		mesh.AutoPaste(shells = ListElemOnPartAutoPase, project_on_geometry = False, isolate = False, move_to = 'geometry pos', preserve_id = 'min', distance = 0.1)
		base.DeleteEntity(container_highlight, True)
	else:
		base.DeleteEntity(container_highlight, True)
		return 0

##**********************************  Tim cac element can xoa ********************************************
def FindElemsReplace(ListNodesReleaseReq, ListElemBoundConnect, ListPartOldsConnect):
	
	ElemsRemoveReq = []
	base.Release(ListNodesReleaseReq, 'edges')
	
	AxisCogOfElemBound = base.Cog(ListElemBoundConnect[0])
	ProjCogToElemsOld = calc.ProjectPointToContainer(AxisCogOfElemBound, ListPartOldsConnect)
	ElemsRemoveReq.append(ProjCogToElemsOld[4])
	base.Or(ProjCogToElemsOld[4])
	base.Neighb('ALL')
	
	ElemsRemoveReq = base.CollectEntities(deck, None, 'ELEMENT_SHELL', filter_visible = True)
	
	return ElemsRemoveReq					

##**********************************  Tim cac nodes gan nhat de release ********************************************
def FindNodesRelease(ListBoundaryNodes, ListPartOldsConnect, ShellsSelected):
	
	ListNodesReleaseReq = []
	ListElemBoundConnect = []
	ListNodesBoundaryReq = []
	
	for i in range(0, len(ListBoundaryNodes), 1):
		ValsBoundNode = ListBoundaryNodes[i].get_entity_values(deck, ['X', 'Y', 'Z'])
		AxisBoundNode = [ValsBoundNode['X'], ValsBoundNode['Y'], ValsBoundNode['Z']]
		
		NearestNodeResult = base.NearestNode(coordinates = AxisBoundNode, tolerance = 0.2, search_entities = ListPartOldsConnect)
		if NearestNodeResult[0] != None:
			ListNodesReleaseReq.append(NearestNodeResult[0])
			ListNodesBoundaryReq.append(ListBoundaryNodes[i])
	
	if len(ListNodesReleaseReq) >0:
		for k in range(0, len(ShellsSelected), 1):
			NodeElemsSelected = base.CollectEntities(deck, ShellsSelected[k], ['NODE'])
			ListNodeElemWithNodeBoundReq = list(set(ListNodesBoundaryReq).intersection(NodeElemsSelected))
			if len(ListNodeElemWithNodeBoundReq) >0:
				ListElemBoundConnect.append(ShellsSelected[k])
				break
	
	return ListElemBoundConnect, ListNodesReleaseReq

##**********************************  Tim cac part tuong ung voi tung group shell ********************************************
def FindPropAssignMeshReplace(ShellsSelected, PartReplace):
	
	ListPartOldsConnect = []
	
	base.Near(radius = 0.1)
	PartVisible = base.CollectEntities(deck, None, ['ANSAPART'], filter_visible = True)
	for i in range(0, len(PartVisible), 1):
		if PartVisible[i] != PartReplace:
			ListPartOldsConnect.append(PartVisible[i])
		
	return ListPartOldsConnect

##**********************************  Tim single nodes tuong ung voi tung group shell ********************************************
def FindBoundaryNodesOnShell(ShellsSelected):
	
	ListBoundaryNodes = []
	ObjectBoundaryNodes = base.CollectBoundaryNodes(container = ShellsSelected, include_second_order_nodes = False)
	if ObjectBoundaryNodes != None:
		for chain in ObjectBoundaryNodes.perimeters:
			ListBoundaryNodes.extend(chain)
	
	return ListBoundaryNodes

#**********************************  Chia mesh thanh tung group tuong ung ********************************************
def DivideGroupElemReplace(ElemsSelected):
	
	ListNameGroupIsolateChecked = []
	ListGroupElemsReplace = []
	
	DictIsolateElemsReplace = base.IsolateConnectivityGroups(entities = ElemsSelected, separate_at_blue_bounds = False, separate_at_pid_bounds = True)
	for GroupIsolate1st, ElemsIsolate1st in DictIsolateElemsReplace.items():
		PosSearchNameGroup1st = FindEntityInListElementsFunc(GroupIsolate1st, ListNameGroupIsolateChecked)
#		print(PosSearchNameGroup1st)
		if PosSearchNameGroup1st == None:
			ListGroupNameDouble = []
			ListElemsExport = []
			NodesOnElemIsolate1st = base.CollectEntities(deck, ElemsIsolate1st, ['NODE'])
			for GroupIsolate2nd, ElemsIsolate2nd in DictIsolateElemsReplace.items():
				if GroupIsolate1st != GroupIsolate2nd:
#					print(GroupIsolate1st, GroupIsolate2nd)		
					NodesOnElemIsolate2nd = base.CollectEntities(deck, ElemsIsolate2nd, ['NODE'])
					ListDoubleNode1st_Node2nd = list(set(NodesOnElemIsolate1st).intersection(NodesOnElemIsolate2nd))
#					print(len(ListDoubleNode1st_Node2nd))
					if len(ListDoubleNode1st_Node2nd) >0:
						ListGroupNameDouble.append(GroupIsolate2nd)
						ListGroupNameDouble.append(GroupIsolate1st)
						ListElemsExport.extend(ElemsIsolate1st)
						ListElemsExport.extend(ElemsIsolate2nd)
			
			if len(ListGroupNameDouble) >0:
				ListNameGroupIsolateChecked.extend(ListGroupNameDouble)
				ListGroupElemsReplace.append(ListElemsExport)
			else:
#				print(GroupIsolate1st)
				ListGroupElemsReplace.append(ElemsIsolate1st)
		
	return ListGroupElemsReplace	

#**********************************  Help Function ********************************************
def FindEntityInListElementsFunc(EntityElement, ListElements):
	
	try:
		Pos = ListElements.index(EntityElement)
	except:
		Pos = None
	else:
		Pos = Pos
	
	return Pos	

#MeshReplaceTool()
