# PYTHON script
import os
import ansa
from ansa import *

DeckCurrent = constants.OPENFOAM
#@session.defbutton('1_CAD ASSEMBLY', 'CheckPidPart','Check PID and Module IDs In Model')
def CheckMidPartTool():
	# Need some documentation? Run this with F5
	AnsaParts = base.CollectEntities(DeckCurrent, None, ['ANSAPART'])
	if len(AnsaParts) >0:
		SetPidToModuleIdsFunc(AnsaParts)
		
		ListPartsNoModuleIDs, ListPartsDoublePIDs, ListPartNotMatchPID_ModuleId, ListPartError = CheckInfosPIDInPartsFunc(AnsaParts)
		if len(ListPartError) >0:
			base.Or(ListPartError)
			if len(ListPartsNoModuleIDs) >0:
				NameNoModuleIDs = '2_No Module IDs'
				GroupNoModuleIDs = CreateNewGroupsFunc(NameNoModuleIDs)
				base.AddLinkedPartsToGroup(ListPartsNoModuleIDs, GroupNoModuleIDs)
		
			if len(ListPartsDoublePIDs) >0:
				NameDoubleModuleIDs = '1_Part_2PIDs'
				GroupDoubleModuleIDs = CreateNewGroupsFunc(NameDoubleModuleIDs)
				base.AddLinkedPartsToGroup(ListPartsDoublePIDs, GroupDoubleModuleIDs)
		
			if len(ListPartNotMatchPID_ModuleId) >0:
				NamePartNotMatchPID = '3_PID_Part_Unmatch'
				GroupNotMatchPID = CreateNewGroupsFunc(NamePartNotMatchPID)
				base.AddLinkedPartsToGroup(ListPartNotMatchPID_ModuleId, GroupNotMatchPID)
		
		else:
			print('PID and Module Id in model are OK')
		
	guitk.UserError('Done ^.^.....')


def SetPidToModuleIdsFunc(AnsaParts):
	
	for i in range(0, len(AnsaParts), 1):
		ValsPartInfos = base.GetEntityCardValues(DeckCurrent, AnsaParts[i], ['PID', 'Module Id'])
		if ValsPartInfos['Module Id'] != ValsPartInfos['PID']:
			base.SetEntityCardValues(DeckCurrent, AnsaParts[i], {'Module Id': ValsPartInfos['PID']})
		
def CheckInfosPIDInPartsFunc(AnsaParts):
	
	ListPartsNoModuleIDs =[]
	ListPartsDoublePIDs = []
	ListPartNotMatchPID_ModuleId = []
	ListPartError = []
	
	for SinglePart in AnsaParts:
		ElementInParts = base.CollectEntities(DeckCurrent, SinglePart, ['__ELEMENTS__', 'FACE'], recursive = True)
		if len(ElementInParts) >0:
			
			ValsAnsaPart = base.GetEntityCardValues(DeckCurrent, SinglePart, ['Module Id', 'PID'])
			TokensValsPID = ValsAnsaPart['PID'].split(',')
			if ValsAnsaPart['Module Id'] == '':
				ListPartsNoModuleIDs.append(SinglePart)
				ListPartError.append(SinglePart)
		
			if len(TokensValsPID) >1:
				ListPartsDoublePIDs.append(SinglePart)
				ListPartError.append(SinglePart)	
		
			if ValsAnsaPart['Module Id'] != ValsAnsaPart['PID']:
				Pos1st = FindEntityInListElementsFunc(SinglePart, ListPartsNoModuleIDs)
				Pos2nd = FindEntityInListElementsFunc(SinglePart, ListPartsDoublePIDs)
				if Pos1st == None and Pos2nd == None:
					ListPartNotMatchPID_ModuleId.append(SinglePart)
					ListPartError.append(SinglePart)
	
	return ListPartsNoModuleIDs, ListPartsDoublePIDs, ListPartNotMatchPID_ModuleId, ListPartError
	
def FindEntityInListElementsFunc(EntityElement, ListElements):
	
	try:
		Pos = ListElements.index(EntityElement)
	except:
		Pos = None
	else:
		Pos = Pos
	
	return Pos		

def CreateNewGroupsFunc(NameGroup):
	
	NewGroups = base.NewGroup(NameGroup, '')
	if NewGroups == None:
		EntityGroup = base.NameToEnts(NameGroup)
		
		NewGroups = EntityGroup[0]
	
	return NewGroups
	
CheckMidPartTool()
