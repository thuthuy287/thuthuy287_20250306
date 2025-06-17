# PYTHON script
import os
import ansa
from ansa import *

deck = constants.LSDYNA
#@session.defbutton('1_CAD ASSEMBLY', 'DividePartTool','Tách các chi tiết đang bị gộp lại thành 1 part')
def DividePartTool():
	# Need some documentation? Run this with F5
	TopWindow = guitk.BCWindowCreate("Divide Many Element On Single Part", guitk.constants.BCOnExitDestroy)
	
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Options:", guitk.constants.BCHorizontal)
	BCRadioButton_1 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Auto", None, 0)
	BCRadioButton_2 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Visible", None, 0)
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
	VisibleStatus = guitk.BCRadioButtonIsChecked(_window[3])
	
	PartsSelected = []
	if AutoStatus == True:
		PartsSelected = base.CollectEntities(deck, None, ['SECTION_SHELL'])
	if VisibleStatus == True:
		PartsSelected = base.CollectEntities(deck, None, ['SECTION_SHELL'], filter_visible = True)
	
	if len(PartsSelected) >0:
		print(len(PartsSelected))
#		DivideElementOnPart(PartsSelected, Probar, Label)
	
	base.RedrawAll()

def DivideElementOnPart(PartsSelected, Probar, Label):
	
	guitk.BCProgressBarReset(Probar)
	guitk.BCProgressBarSetTotalSteps(Probar, len(PartsSelected))
	
	for i in range(0, len(PartsSelected), 1):
		guitk.BCLabelSetText(Label, 'Loading Props Ids: ' + str(PartsSelected[i]._id))
		ValsOnParts = PartsSelected[i].get_entity_values(deck, ['PID', 'Name', 'User/CAD/StringMetaData/Nomenclature', 'User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]', 'User/CAD/StringParameterData/ParameterSet\Material', 'User/CAD/StringMetaData/Revision'])
		TokensStringPIDPart = ValsOnParts['PID'].split(',')
		if len(TokensStringPIDPart) >1:
			for k in range(1, len(TokensStringPIDPart), 1):
				PropsOnPart = base.GetEntity(deck, 'SECTION_SHELL', int(TokensStringPIDPart[k]))
				if PropsOnPart != None:
					FacesOnProps = base.CollectEntities(deck, PropsOnPart, ['FACE'])
					if len(FacesOnProps) >0:
						ListFacesIsolate = IsolateEntiyOnProps(FacesOnProps)
						print(len(ListFacesIsolate))
						if len(ListFacesIsolate) >1:
							print('OK')
#							SetupInfosToFacesIsolate(ListFacesIsolate, PropsOnPart)
						else:
							SetupInfosNewParts(ValsOnParts, FacesOnProps, PropsOnPart)
			
		guitk.BCProgressBarSetProgress(Probar, i+1)

def SetupInfosToFacesIsolate(ListFacesIsolate, PropsIsolate):
	
	for i in range(1, len(ListFacesIsolate), 1):
		PropsFaceIsolate = base.CopyEntity(None, PropsIsolate)
		PropsFaceIsolate.set_entity_values(deck, {'User/cad_material': PropsIsolate._id})
		for k in range(0, len(ListFacesIsolate[i]), 1):
			ListFacesIsolate[i][k].set_entity_values(deck, {'PID': PropsFaceIsolate._id})
		
		NamePartFaceIsolate = PropsFaceIsolate._name
		ModulePartFaceIsolate = PropsFaceIsolate._id
		
		EntityPartFaceIsolate = CreateNewEntityParts(NamePartFaceIsolate, ModulePartFaceIsolate)
		if EntityPartFaceIsolate != None:
			EntityPartFaceIsolate.set_entity_values(deck, {'Module Id': ModulePartFaceIsolate})
			base.SetEntityPart(ListFacesIsolate[i], EntityPartFaceIsolate)


def SetupInfosNewParts(ValsOnParts, FacesOnProps, PropsOnPart):
	
	NewPartDevide = base.NewPart(ValsOnParts['Name'] + '_' + str(FacesOnProps[0]._id), '')
	base.SetEntityPart(FacesOnProps, NewPartDevide)
	
	NewPartDevide.set_entity_values(deck, {'Module Id': PropsOnPart._id, 
																'User/CAD/StringMetaData/Nomenclature': ValsOnParts['User/CAD/StringMetaData/Nomenclature'],
																'User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]': ValsOnParts['User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]'],
																'User/CAD/StringParameterData/ParameterSet\Material': ValsOnParts['User/CAD/StringParameterData/ParameterSet\Material'], 
																'User/CAD/StringMetaData/Revision': ValsOnParts['User/CAD/StringMetaData/Revision']})
	

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

DividePartTool()
