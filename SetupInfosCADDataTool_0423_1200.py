# PYTHON script
import os
import ansa
from ansa import *

@session.defbutton('99_OTHER TOOL', 'SetPartPidTool','Set Face To Mesh and reverse')
def SetPartPidTool():
	# Need some documentation? Run this with F5
	TopWindow = guitk.BCWindowCreate("Set Part Pid Tool version 1.0", guitk.constants.BCOnExitDestroy)
	
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Action", guitk.constants.BCHorizontal)
	BCRadioButton_1 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Set Face To Mesh", None, 0)
	BCRadioButton_2 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Set Mesh To Face", None, 0)
	guitk.BCRadioButtonSetChecked(BCRadioButton_1, True)
	
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	DataOnTop = [BCRadioButton_1, BCRadioButton_2]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, DataOnTop)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, DataOnTop)
	
	guitk.BCShow(TopWindow)
	
	
def RejectFunc(TopWindow, DataOnTop):
	
	return 1

#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, DataOnTop):
	
	for i in range(0, 1000, 1):
		SelectFaceData = base.PickEntities(constants.LSDYNA, ['FACE'])
		if SelectFaceData != None:
			base.Not(SelectFaceData)
			SelectMeshData = base.PickEntities(constants.LSDYNA, ['ELEMENT_SHELL'])
			if SelectMeshData != None:
				base.Not(SelectMeshData)
				NameOfPropsFace, PartOnFaces, PropsInFace = GetInfosInFaceSelectFunc(SelectFaceData)
				PropsInShell, PartOnShells = GetInfosInShellsSelectFunc(SelectMeshData)
				if guitk.BCRadioButtonIsChecked(DataOnTop[0]) == True:
	 				SetFaceToMeshFunc(SelectFaceData, NameOfPropsFace, PropsInShell, PartOnShells, SelectMeshData, PartOnFaces, PropsInFace)
				if guitk.BCRadioButtonIsChecked(DataOnTop[1]) == True:
	 				SetMeshToFaceFunc(SelectFaceData, NameOfPropsFace, PropsInShell, PartOnShells, SelectMeshData, PartOnFaces, PropsInFace)

		else:
			return 1

def SetMeshToFaceFunc(SelectFaceData, NameOfPropsFace, PropsInShell, PartOnShells, SelectMeshData, PartOnFaces, PropsInFace):
	
	for i in range(0, len(SelectMeshData), 1):
		base.SetEntityCardValues(constants.LSDYNA, SelectMeshData[i], {'PID': PropsInFace._id})
		
	base.SetEntityCardValues(constants.LSDYNA, PropsInFace, {'Comment': PropsInShell._id})
	
	base.SetEntityCardValues(constants.LSDYNA, PartOnShells, {'Module Id': ''})
	base.SetEntityCardValues(constants.LSDYNA, PartOnFaces, {'Module Id': PropsInShell._id})
	base.SetEntityPart(SelectMeshData, PartOnFaces)	

def SetFaceToMeshFunc(SelectFaceData, NameOfPropsFace, PropsInShell, PartOnShells, SelectMeshData, PartOnFaces, PropsInFace):
	
	ValsPropsFace = PropsInFace.get_entity_values(constants.LSDYNA, ['T1', 'Comment', 'User/cad_thickness', 'User/CAD/Name', 'User/CAD/OriginalId', 'User/original_name', 'Labels'])
	for i in range(0, len(SelectFaceData), 1):
		base.SetEntityCardValues(constants.LSDYNA, SelectFaceData[i], {'PID': PropsInShell._id})
	
	base.SetEntityCardValues(constants.LSDYNA, PropsInShell, {'Name': NameOfPropsFace, 'T1': ValsPropsFace['T1'], 'Comment': ValsPropsFace['Comment'], 'User/cad_thickness': ValsPropsFace['User/cad_thickness'], 'User/CAD/Name': ValsPropsFace['User/CAD/Name'], 'User/CAD/OriginalId': ValsPropsFace['User/CAD/OriginalId'], 'User/original_name': ValsPropsFace['User/original_name'], 'Labels': ValsPropsFace['Labels']})
	
	base.SetEntityCardValues(constants.LSDYNA, PartOnShells, {'Module Id': ''})
	base.SetEntityCardValues(constants.LSDYNA, PartOnFaces, {'Module Id': PropsInShell._id})
	base.SetEntityPart(SelectMeshData, PartOnFaces)

def GetInfosInShellsSelectFunc(SelectMeshData):
	
	ValsOfShell = base.GetEntityCardValues(constants.LSDYNA, SelectMeshData[0], ['PID'])
	PartOnShells = base.GetEntityPart(SelectMeshData[0])
	PropsInShell = base.GetEntity(constants.LSDYNA, 'SECTION_SHELL', ValsOfShell['PID'])
	
	return PropsInShell, PartOnShells

def GetInfosInFaceSelectFunc(SelectFaceData):
	
	ValsOfFace = base.GetEntityCardValues(constants.LSDYNA, SelectFaceData[0], ['PID'])
	PartOnFaces = base.GetEntityPart(SelectFaceData[0])
	ValsPartFaceCollect = base.GetEntityCardValues(constants.LSDYNA, PartOnFaces, ['User/CAD/StringMetaData/Nomenclature'])
	PropsInFace = base.GetEntity(constants.LSDYNA, 'SECTION_SHELL', ValsOfFace['PID'])
	#********************* Lay thong tin cua ten chi tiet
	try:
		NameOfPropsFace = ValsPartFaceCollect['User/CAD/StringMetaData/Nomenclature']
	except:
		NameOfPropsFace = GetInfosFromNamePropFacesFunc(PropsInFace)
	else:
		if NameOfPropsFace != None and NameOfPropsFace != '':
			TokensNameOfFace = NameOfPropsFace.split('_')
			
			ListString = []
			ListStepOutput = []
			for i in range(0, len(TokensNameOfFace), 1):
				if TokensNameOfFace[i] != '':
					ListString.append(TokensNameOfFace[i])
					ListStepOutput.append(i)
			
			StringEndText = ListString[ListStepOutput.index(max(ListStepOutput))]
			NameOfPropsFace = NameOfPropsFace[0: NameOfPropsFace.find(StringEndText) + len(StringEndText)]
			
		else:
			NameOfPropsFace = GetInfosFromNamePropFacesFunc(PropsInFace)
			
	return NameOfPropsFace, PartOnFaces, PropsInFace

def GetInfosFromNamePropFacesFunc(PropsInFace):
	
	ValsPropsInFace = base.GetEntityCardValues(constants.LSDYNA, PropsInFace, ['Name'])
	TokenNameProp = ValsPropsInFace['Name'].split('\\')
	if len(TokenNameProp) == 2:
		NameOnProp = TokenNameProp[0]
	if len(TokenNameProp) == 3:
		NameOnProp = TokenNameProp[1]
	if len(TokenNameProp) == 1:
		NameOnProp = TokenNameProp[0]
	if len(TokenNameProp) >3:	
		NameOnProp = TokenNameProp[0]
	
	return NameOnProp
	
#SetPartPidTool()
