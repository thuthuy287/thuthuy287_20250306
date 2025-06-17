# PYTHON script
import os
import ansa
from ansa import *

deck = constants.LSDYNA
@session.defbutton('1_CAD ASSEMBLY', 'DividePartTool','Tách các chi tiết đang bị gộp lại thành 1 part')
def DividePartTool():
	# Need some documentation? Run this with F5
	TopWindow = guitk.BCWindowCreate("Divide Many Element On Single Part", guitk.constants.BCOnExitDestroy)
	
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Options:", guitk.constants.BCHorizontal)
	BCRadioButton_1 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Auto", None, 0)
	BCRadioButton_2 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Manual", None, 0)
	guitk.BCRadioButtonSetChecked(BCRadioButton_1, True)
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_1 = guitk.BCLabelCreate(TopWindow, "")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	_window = [BCProgressBar_1, BCLabel_1, BCRadioButton_1, BCRadioButton_2]
	guitk.BCWindowSetRejectFunction(TopWindow, _Reject_Button, _window)
	guitk.BCWindowSetAcceptFunction(TopWindow, _Accept_Button, _window)
	
	guitk.BCShow(TopWindow)

def _Reject_Button(TopWindow, _window):
	
	return 1

def _Accept_Button(TopWindow, _window):
	
	Probar = _window[0]
	Label = _window[1]
	AutoStatus = guitk.BCRadioButtonIsChecked(_window[2])
	ManualStatus = guitk.BCRadioButtonIsChecked(_window[3])
	
	PropsSelected = []
	if AutoStatus == True:
		PropsSelected = base.CollectEntities(deck, None, ['SECTION_SHELL'])
		PartsSelected = base.CollectEntities(deck, None, ['ANSAPART'])
	if ManualStatus == True:
		PropsSelected = base.PickEntities(deck, ['SECTION_SHELL'])
		PartsSelected = base.CollectEntities(deck, None, ['ANSAPART'], filter_visible = True)
	
	if len(PropsSelected) >0:
		DivideElementOnPart(PropsSelected, Probar, Label)
		DivideEntityPartsFunc(PartsSelected, Probar, Label)
	
	base.RedrawAll()


def DivideEntityPartsFunc(PartsSelected, Probar, Label):
	
	guitk.BCProgressBarReset(Probar)
	guitk.BCProgressBarSetTotalSteps(Probar, len(PartsSelected))
	for i in range(0, len(PartsSelected), 1):
		guitk.BCLabelSetText(Label, 'Loading Parts Ids: ' + str(PartsSelected[i]._id))
		
		ValsPartsSelect = PartsSelected[i].get_entity_values(deck, ['PID', 'Name'])
		TokensStringPID = ValsPartsSelect['PID'].split(',')
		
		if len(TokensStringPID) >1:
			for k in range(1, len(TokensStringPID), 1):
				PropsDivides = base.GetEntity(deck, 'SECTION_SHELL', int(TokensStringPID[k]))
				if PropsDivides != None:
					FacesOnPropsDivide = base.CollectEntities(deck, PropsDivides, ['FACE'])
					if len(FacesOnPropsDivide) >0:
						NamePartDivide = ValsPartsSelect['Name'] + '@' + str(FacesOnPropsDivide[0]._id)
						ModulePartDivide = PropsDivides._id
	
						ListGroupsOld = FindLocationOfPartsOldsFunc(FacesOnPropsDivide)
						EntityPartDivide = CreateNewEntityParts(NamePartDivide, ModulePartDivide)
						if EntityPartDivide != None:
							EntityPartDivide.set_entity_values(deck, {'Module Id': ModulePartDivide})
							base.SetEntityPart(FacesOnPropsDivide, EntityPartDivide)
							if ListGroupsOld != None:
								base.SetEntityPart(EntityPartDivide, ListGroupsOld[0])
				
		guitk.BCProgressBarSetProgress(Probar, i+1)
		
def DivideElementOnPart(PropsSelected, Probar, Label):
	
	guitk.BCProgressBarReset(Probar)
	guitk.BCProgressBarSetTotalSteps(Probar, len(PropsSelected))
	
	for i in range(0, len(PropsSelected), 1):
		guitk.BCLabelSetText(Label, 'Loading Props Ids: ' + str(PropsSelected[i]._id))
		FacesOnProps = base.CollectEntities(deck, PropsSelected[i], ['FACE'])
		if len(FacesOnProps) >0:
			ListFacesIsolate = IsolateEntiyOnProps(FacesOnProps)
			if len(ListFacesIsolate) >1:
				SetupInfosToFacesIsolate(ListFacesIsolate, PropsSelected[i])
			
		guitk.BCProgressBarSetProgress(Probar, i+1)

def SetupInfosToFacesIsolate(ListFacesIsolate, PropsIsolate):
	
	for i in range(1, len(ListFacesIsolate), 1):
		PropsFaceIsolate = base.CopyEntity(None, PropsIsolate)
		PropsFaceIsolate.set_entity_values(deck, {'User/cad_material': PropsIsolate._id})
		for k in range(0, len(ListFacesIsolate[i]), 1):
			ListFacesIsolate[i][k].set_entity_values(deck, {'PID': PropsFaceIsolate._id})
		
		NamePartFaceIsolate = PropsFaceIsolate._name
		ModulePartFaceIsolate = PropsFaceIsolate._id
		
		ListGroupOfPartsOld = FindLocationOfPartsOldsFunc(ListFacesIsolate[i])
		
		EntityPartFaceIsolate = CreateNewEntityParts(NamePartFaceIsolate, ModulePartFaceIsolate)
		if EntityPartFaceIsolate != None:
			EntityPartFaceIsolate.set_entity_values(deck, {'Module Id': ModulePartFaceIsolate})
			base.SetEntityPart(ListFacesIsolate[i], EntityPartFaceIsolate)
			if ListGroupOfPartsOld != None:
				base.SetEntityPart(EntityPartFaceIsolate, ListGroupOfPartsOld[0])

def FindLocationOfPartsOldsFunc(EntityReference):
	
	ListGroupReference = []
	PartReference = base.GetEntityPart(EntityReference[0])
	if PartReference != None:
		ValsPartRefer = PartReference.get_entity_values(deck, ['Hierarchy'])
		TokensHierarchy = ValsPartRefer['Hierarchy'].split('/')
		NameGroupPartRefer = TokensHierarchy[len(TokensHierarchy) -2]
		ListGroupReference = base.NameToEnts(pattern = NameGroupPartRefer, deck = deck, match = constants.ENM_EXACT)
	
	return ListGroupReference
	
def IsolateEntiyOnProps(FacesOnProps):
	ListFacesIsolate = []
	
	GroupFaceIsolate = base.IsolateConnectivityGroups(entities = FacesOnProps, separate_at_blue_bounds = True, separate_at_pid_bounds = True)
	if GroupFaceIsolate != None:
		for NameGroupIsolate, EntityFaceIsolate in GroupFaceIsolate.items():
			ListFacesIsolate.append(EntityFaceIsolate)
	
	return ListFacesIsolate

def CreateNewEntityParts(NamePartFaceIsolate, ModulePartFaceIsolate):
	
	EntiyPart = base.NewPart(NamePartFaceIsolate + '@' + str(ModulePartFaceIsolate))
		
	return EntiyPart

#DividePartTool()
