# PYTHON script
import os
import ansa
from ansa import *

#************************************Move part vao tung group tuong ung ****************
def MoveGroupPartCompareFunc(ProBar, LabelStatus):
	
	PartResults = base.CollectEntities(constants.LSDYNA, None, ['ANSAPART'])
	if len(PartResults) >0:
		guitk.BCProgressBarReset(ProBar)
		guitk.BCProgressBarSetTotalSteps(ProBar, len(PartResults))
		for i in range(0, len(PartResults), 1):
			ValsPartResult = base.GetEntityCardValues(constants.LSDYNA, PartResults[i], ['Comment'])
			if ValsPartResult['Comment'] == 'Carry Over':
				NameGroupCarryOver = 'CARRY-OVER'
				GroupPartCarryOver = CreateNewGroupFunc(NameGroupCarryOver)
				base.SetEntityPart(PartResults[i], GroupPartCarryOver)
			
			elif ValsPartResult['Comment'] == 'Prepare':
				NameGroupPrepare = 'PREPARE'
				GroupPartPrepare = CreateNewGroupFunc(NameGroupPrepare)
				base.SetEntityPart(PartResults[i], GroupPartPrepare)
			
			elif ValsPartResult['Comment'] == 'New':
				NameGroupNew = 'NEW'
				GroupPartNew = CreateNewGroupFunc(NameGroupNew)
				base.SetEntityPart(PartResults[i], GroupPartNew)
			
			elif ValsPartResult['Comment'] == 'No Need':
				NameGroupNoNeed = 'NO NEED'
				GroupPartNoNeed = CreateNewGroupFunc(NameGroupNoNeed)
				base.SetEntityPart(PartResults[i], GroupPartNoNeed)
			
			guitk.BCProgressBarSetProgress(ProBar, i +1)
			guitk.BCLabelSetText(LabelStatus, '................Completed..................')
			
#************************************So sanh model moi va model cu ****************
def CompareNewModelWithOldModelFunc(NewPartFaceReq, OldPartFaceConnect, LabelStatus, ProBar):
	
	ListPartImportCompare = NewPartFaceReq + OldPartFaceConnect
	base.Or(ListPartImportCompare)
	
	ListFaceCompareBoth = CompareFaceSameSideFunc(LabelStatus)
	if len(ListFaceCompareBoth) >0:
		guitk.BCProgressBarReset(ProBar)
		guitk.BCProgressBarSetTotalSteps(ProBar, len(NewPartFaceReq))
		
		for i in range(0, len(NewPartFaceReq), 1):
			guitk.BCLabelSetText(LabelStatus, 'Loading Part ids: ' + str(NewPartFaceReq[i]._id) + '..................')
			AreaOfPartNew = base.GetEntityCardValues(constants.LSDYNA, NewPartFaceReq[i], ['Area'])
			FaceOnNewPart = base.CollectEntities(constants.LSDYNA, NewPartFaceReq[i], ['FACE'])
			if len(FaceOnNewPart) >0:
				SetInterFaceNew_FaceBoth = set(ListFaceCompareBoth).intersection(FaceOnNewPart)
				ListFaceNewDuplicate = list(SetInterFaceNew_FaceBoth)
				if len(ListFaceNewDuplicate) == len(FaceOnNewPart):
					NewPartFaceReq[i].set_entity_values(constants.LSDYNA, {'Comment': 'Carry Over'})
				else:
					AreaFaceConnect = CalculateAreaOfFacesFunc(ListFaceNewDuplicate)	
					PercentCarryOver = round(((AreaFaceConnect/AreaOfPartNew['Area'])*100),1)
					if PercentCarryOver >= 50:
						NewPartFaceReq[i].set_entity_values(constants.LSDYNA, {'Comment': 'Prepare'})
					else:
						NewPartFaceReq[i].set_entity_values(constants.LSDYNA, {'Comment': 'New'})
					
					RelavePointOnFaceCarryOverFunc(ListFaceNewDuplicate, FaceOnNewPart, NewPartFaceReq[i])
			
			guitk.BCProgressBarSetProgress(ProBar, i +1)

##************************************Danh point vao cac vi tri face khac nhau ****************
def RelavePointOnFaceCarryOverFunc(ListFaceNewDuplicate, FaceOnNewPart, PartFaceDifference):
	
	SetFaceDifference = set(FaceOnNewPart).difference(ListFaceNewDuplicate)
	if len(SetFaceDifference) >0:	
		ListFaceDifference = list(SetFaceDifference)
		HotPointsOnFace = base.CollectEntities(constants.LSDYNA, ListFaceDifference, ['HOT POINT'])
		ListPointRelative = []
		for i in range(0, len(HotPointsOnFace), 1):
			ValsHotPoints = base.GetEntityCardValues(constants.LSDYNA, HotPointsOnFace[i], ['X', 'Y', 'Z'])
			ListPointRelative.append(base.Newpoint(ValsHotPoints['X'], ValsHotPoints['Y'], ValsHotPoints['Z']))
		
		base.SetEntityPart(ListPointRelative, PartFaceDifference)

##************************************Tinh Dien tich cua face ****************
def CalculateAreaOfFacesFunc(ListFaceArea):
	
	ListAreaOfFace = []
	for i in range(0, len(ListFaceArea), 1):
		ListAreaOfFace.append(base.GetFaceArea(ListFaceArea[i]))
	
	AreaFaceConnect = sum(ListAreaOfFace)
	
	return AreaFaceConnect

#************************************ Import model    *********************************
def ImportCadOldToAnsaFunc(PathDataOld, LabelStatus):
	
	OldPartFaceConnect = []
	collector_PartOld = base.CollectNewModelEntities(constants.LSDYNA, ['ANSAPART'])
	Import_Status = utils.Merge(filename = PathDataOld,
					property_offset = 'offset',
					material_offset = 'offset',
					set_offset = 'offset',
					merge_sets_by_name = False,
					paste_nodes_by_name = False,
					paste_cons_by_name = False,
					merge_parts = False,
					model_action = 'merge_model',
					coord_offset = 'offset',
					node_offset = 'offset')
	
	base.RedrawAll()
	OldPartFaceImport = collector_PartOld.report()
	del collector_PartOld
	if len(OldPartFaceImport) >0:
		OldPartFaceConnect.extend(OldPartFaceImport)
		FindPartDuplicateInNewModelFunc(LabelStatus, OldPartFaceConnect)
		AnsaGroups = base.CollectEntities(constants.LSDYNA, None, ['ANSAGROUP'])
		if len(AnsaGroups) >0:
			for i in range(0, len(AnsaGroups), 1):
				try:
					OldPartFaceConnect.remove(AnsaGroups[i])
				except:
					continue
		
	return OldPartFaceConnect, OldPartFaceImport

###************************************ Tim cac part co face duplicate*********************************
def CheckPartWithFaceDuplicateFunc(FacesConnect, LabelStatus):
	
	guitk.BCLabelSetText(LabelStatus, 'Loading find part duplicate in model.................')
	
	base.Or(FacesConnect)	
	ListPartDuplicateCOG = []
	ListCOGOnSinglePart = []
	ListPartDuplicateFace = []
	
	PartConnectVisible = base.CollectEntities(constants.LSDYNA, None, ['ANSAPART'], filter_visible = True)
	if len(PartConnectVisible) >0:
		for i in range(0, len(PartConnectVisible), 1):
			FaceOnPartConnect = base.CollectEntities(constants.LSDYNA, PartConnectVisible[i], ['FACE'])
			SetIntersection = set(FaceOnPartConnect).intersection(FacesConnect)
			if len(list(SetIntersection)) == len(FaceOnPartConnect):
				ValsPartConnect = base.GetEntityCardValues(constants.LSDYNA, PartConnectVisible[i], ['COG x', 'COG y', 'COG z'])
				StringCogPart = str(round(ValsPartConnect['COG x'], 3)) + '_' + str(round(ValsPartConnect['COG y'], 3)) + '_' + str(round(ValsPartConnect['COG z'], 3))
				ListCOGOnSinglePart.append(StringCogPart)
				ListPartDuplicateCOG.append(PartConnectVisible[i])
			
	if len(ListPartDuplicateCOG) >0:
		CogPartRemoveDuplicate = list(set(ListCOGOnSinglePart))
		for k in range(0, len(CogPartRemoveDuplicate), 1):
			ListPartDuplicateReq = []
			for w in range(0, len(ListCOGOnSinglePart), 1):
				if CogPartRemoveDuplicate[k] == ListCOGOnSinglePart[w]:
					ListPartDuplicateReq.append(ListPartDuplicateCOG[w])
					
			if len(ListPartDuplicateReq) >1:
				for j in range(1, len(ListPartDuplicateReq), 1):
					ListPartDuplicateFace.append(ListPartDuplicateReq[j])
	
	return ListPartDuplicateFace		

###************************************ Compare face to face same side*********************************
def CompareFaceSameSideFunc(LabelStatus):
	
	FacesConnect = []
	guitk.BCLabelSetText(LabelStatus, 'Loading compare same side.................')
	collector_PartConnect = base.CollectNewModelEntities(constants.LSDYNA, ['SET'])
	base.RmdblSameSide(tolerance = 0.1, similarity = 95, positive_negative_both = 'both', link_delete_set = 'set')
	SetConnect = collector_PartConnect.report()
	del collector_PartConnect
		
	if len(SetConnect) >0:
		FacesConnect = base.CollectEntities(constants.LSDYNA, SetConnect, ['FACE'])
		base.DeleteEntity(SetConnect, False)
		
	return FacesConnect

#************************************ OK Click Button*********************************
def AcceptClickButton(TopWindow, _win):
	
	PathDataOld = guitk.BCLineEditPathSelectedFilePaths(_win[2])
	_remove_double_data_status = guitk.BCCheckBoxIsChecked(_win[3])
	_compare_cad_cad_status = guitk.BCCheckBoxIsChecked(_win[4])
	ProBar = _win[0]
	LabelStatus = _win[1]
	
	if _remove_double_data_status:
		alls_faces_model = base.CollectEntities(constants.LSDYNA, None, ['FACE'], filter_visible = True)
		if len(alls_faces_model) >0:
			base.Or(alls_faces_model)
			FacesConnect = CompareFaceSameSideFunc(LabelStatus)
			print(FacesConnect)
			if len(FacesConnect) >0:
				ListPartDuplicateFace = CheckPartWithFaceDuplicateFunc(FacesConnect, LabelStatus)
				if len(ListPartDuplicateFace) >0:
					groups_part_double = CreateNewGroupFunc('Parts Double In Model')
					base.AddLinkedPartsToGroup(ListPartDuplicateFace, groups_part_double)
	
#	if PathDataOld != None:
#		PartConnect = base.CollectEntities(constants.LSDYNA, None, ['ANSAPART'])
#		NewPartFaceReq = FindPartDuplicateInNewModelFunc(LabelStatus, PartConnect)
#		if len(NewPartFaceReq) >0:
##			print(len(NewPartFaceReq))
#			OldPartFaceConnect, OldPartFaceImport = ImportCadOldToAnsaFunc(PathDataOld, LabelStatus)
#			if len(OldPartFaceConnect) >0:
#				CompareNewModelWithOldModelFunc(NewPartFaceReq, OldPartFaceConnect, LabelStatus, ProBar)
#				base.DeleteEntity(OldPartFaceImport, True)
#				MoveGroupPartCompareFunc(ProBar, LabelStatus)
##			print(len(OldPartFaceConnect))
#	else:
#		guitk.UserError('Chọn đường dẫn CAD old....')
#		return 1

#************************************ Select Options******************************	
def _CallRmoveDoubleFunc(cb, state, _win):
	
	 if guitk.BCCheckBoxIsChecked(cb):
	 	guitk.BCButtonGroupSetChecked(_win[5], False)
	 	guitk.BCCheckBoxSetChecked(_win[4], False)
	 else:
	 	guitk.BCButtonGroupSetChecked(_win[5], True)
	 	guitk.BCCheckBoxSetChecked(_win[4], True)

def _CallCompareCadFunc(cb, state, _win):
	if guitk.BCCheckBoxIsChecked(cb):
	 	guitk.BCButtonGroupSetChecked(_win[5], True)
	 	guitk.BCCheckBoxSetChecked(_win[3], False)
	else:
		guitk.BCButtonGroupSetChecked(_win[5], False)
		guitk.BCCheckBoxSetChecked(_win[3], True)
	
#************************************ Cancel Click Button******************************	
def RejectClickButton(TopWindow, _win):
	return 1	
#************************************ Window*******************************************
#@session.defbutton('1_CAD ASSEMBLY', 'CompareCADTool','So sánh cad cũ và cad mới....')
def CompareCadToCadTool():
	
	FileExtension = ['ansa']
	TopWindow = guitk.BCWindowCreate("Comapre Cad To Cad Tool version 1.0", guitk.constants.BCOnExitDestroy)
	
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Options", guitk.constants.BCHorizontal)
	BCCheckBox_1 = guitk.BCCheckBoxCreate(BCButtonGroup_1, 'Remove Double Part')
	BCCheckBox_2 = guitk.BCCheckBoxCreate(BCButtonGroup_1, 'Compare Cad-Cad')
	guitk.BCCheckBoxSetChecked(BCCheckBox_1, True)
	
	BCButtonGroup_2 = guitk.BCButtonGroupCreate(TopWindow, "Path Cad Old", guitk.constants.BCHorizontal)
	BCLabel_2 = guitk.BCLabelCreate(BCButtonGroup_2, "PathOld: ")
	BCLineEditPath_1 = guitk.BCLineEditPathCreate(BCButtonGroup_2, guitk.constants.BCHistoryFiles, "FileOld", guitk.constants.BCHistorySelect, "SelectPathOld")
	guitk.BCLineEditPathAddFilter(BCLineEditPath_1, 'ANSA File:', FileExtension)
	guitk.BCLineEditPathSetDialogEnterEnabled(BCLineEditPath_1, True)
	guitk.BCButtonGroupSetCheckable(BCButtonGroup_2, True)
	guitk.BCButtonGroupSetChecked(BCButtonGroup_2, False)
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_1 = guitk.BCLabelCreate(TopWindow, "")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	_win = [BCProgressBar_1, BCLabel_1, BCLineEditPath_1, BCCheckBox_1, BCCheckBox_2, BCButtonGroup_2]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectClickButton, _win)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptClickButton, _win)
	
	guitk.BCCheckBoxSetToggledFunction(BCCheckBox_1, _CallRmoveDoubleFunc, _win)
	guitk.BCCheckBoxSetToggledFunction(BCCheckBox_2, _CallCompareCadFunc, _win)
	
	guitk.BCShow(TopWindow)

#########$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Help Functions $$$$$$$$$$$$$$$$$$$$$$$$$$$$
###### Create New Groups
def CreateNewGroupFunc(NameNewGroup):
	
	GroupNew = base.NewGroup(NameNewGroup, '')
	if GroupNew == None:
		GroupRefereceByName = base.NameToEnts(NameNewGroup)
		GroupNew = GroupRefereceByName[0]
	
	return GroupNew

CompareCadToCadTool()



# PYTHON script
import os
import ansa
from ansa import *


#************************************Move part vao tung group tuong ung ****************
def MoveGroupPartCompareFunc(ProBar, LabelStatus):
	
	PartResults = base.CollectEntities(constants.LSDYNA, None, ['ANSAPART'])
	if len(PartResults) >0:
		guitk.BCProgressBarReset(ProBar)
		guitk.BCProgressBarSetTotalSteps(ProBar, len(PartResults))
		for i in range(0, len(PartResults), 1):
			ValsPartResult = base.GetEntityCardValues(constants.LSDYNA, PartResults[i], ['Comment'])
			if ValsPartResult['Comment'] == 'Carry Over':
				NameGroupCarryOver = 'CARRY-OVER'
				GroupPartCarryOver = CreateNewGroupFunc(NameGroupCarryOver)
				base.SetEntityPart(PartResults[i], GroupPartCarryOver)
			
			elif ValsPartResult['Comment'] == 'Prepare':
				NameGroupPrepare = 'PREPARE'
				GroupPartPrepare = CreateNewGroupFunc(NameGroupPrepare)
				base.SetEntityPart(PartResults[i], GroupPartPrepare)
			
			elif ValsPartResult['Comment'] == 'New':
				NameGroupNew = 'NEW'
				GroupPartNew = CreateNewGroupFunc(NameGroupNew)
				base.SetEntityPart(PartResults[i], GroupPartNew)
			
			elif ValsPartResult['Comment'] == 'No Need':
				NameGroupNoNeed = 'NO NEED'
				GroupPartNoNeed = CreateNewGroupFunc(NameGroupNoNeed)
				base.SetEntityPart(PartResults[i], GroupPartNoNeed)
			
			guitk.BCProgressBarSetProgress(ProBar, i +1)
			guitk.BCLabelSetText(LabelStatus, '................Completed..................')
			
#************************************So sanh model moi va model cu ****************
def CompareNewModelWithOldModelFunc(NewPartFaceReq, OldPartFaceConnect, LabelStatus, ProBar):
	
	ListPartImportCompare = NewPartFaceReq + OldPartFaceConnect
	base.Or(ListPartImportCompare)
	
	ListFaceCompareBoth = CompareFaceSameSideFunc(LabelStatus)
	if len(ListFaceCompareBoth) >0:
		guitk.BCProgressBarReset(ProBar)
		guitk.BCProgressBarSetTotalSteps(ProBar, len(NewPartFaceReq))
		
		for i in range(0, len(NewPartFaceReq), 1):
			guitk.BCLabelSetText(LabelStatus, 'Loading Part ids: ' + str(NewPartFaceReq[i]._id) + '..................')
			AreaOfPartNew = base.GetEntityCardValues(constants.LSDYNA, NewPartFaceReq[i], ['Area'])
			FaceOnNewPart = base.CollectEntities(constants.LSDYNA, NewPartFaceReq[i], ['FACE'])
			if len(FaceOnNewPart) >0:
				SetInterFaceNew_FaceBoth = set(ListFaceCompareBoth).intersection(FaceOnNewPart)
				ListFaceNewDuplicate = list(SetInterFaceNew_FaceBoth)
				if len(ListFaceNewDuplicate) == len(FaceOnNewPart):
					NewPartFaceReq[i].set_entity_values(constants.LSDYNA, {'Comment': 'Carry Over'})
				else:
					AreaFaceConnect = CalculateAreaOfFacesFunc(ListFaceNewDuplicate)	
					PercentCarryOver = round(((AreaFaceConnect/AreaOfPartNew['Area'])*100),1)
					if PercentCarryOver >= 50:
						NewPartFaceReq[i].set_entity_values(constants.LSDYNA, {'Comment': 'Prepare'})
					else:
						NewPartFaceReq[i].set_entity_values(constants.LSDYNA, {'Comment': 'New'})
					
					RelavePointOnFaceCarryOverFunc(ListFaceNewDuplicate, FaceOnNewPart, NewPartFaceReq[i])
			
			guitk.BCProgressBarSetProgress(ProBar, i +1)

##************************************Danh point vao cac vi tri face khac nhau ****************
def RelavePointOnFaceCarryOverFunc(ListFaceNewDuplicate, FaceOnNewPart, PartFaceDifference):
	
	SetFaceDifference = set(FaceOnNewPart).difference(ListFaceNewDuplicate)
	if len(SetFaceDifference) >0:	
		ListFaceDifference = list(SetFaceDifference)
		HotPointsOnFace = base.CollectEntities(constants.LSDYNA, ListFaceDifference, ['HOT POINT'])
		ListPointRelative = []
		for i in range(0, len(HotPointsOnFace), 1):
			ValsHotPoints = base.GetEntityCardValues(constants.LSDYNA, HotPointsOnFace[i], ['X', 'Y', 'Z'])
			ListPointRelative.append(base.Newpoint(ValsHotPoints['X'], ValsHotPoints['Y'], ValsHotPoints['Z']))
		
		base.SetEntityPart(ListPointRelative, PartFaceDifference)

##************************************Tinh Dien tich cua face ****************
def CalculateAreaOfFacesFunc(ListFaceArea):
	
	ListAreaOfFace = []
	for i in range(0, len(ListFaceArea), 1):
		ListAreaOfFace.append(base.GetFaceArea(ListFaceArea[i]))
	
	AreaFaceConnect = sum(ListAreaOfFace)
	
	return AreaFaceConnect

#************************************ Import model    *********************************
def ImportCadOldToAnsaFunc(PathDataOld, LabelStatus):
	
	OldPartFaceConnect = []
	collector_PartOld = base.CollectNewModelEntities(constants.LSDYNA, ['ANSAPART'])
	Import_Status = utils.Merge(filename = PathDataOld,
					property_offset = 'offset',
					material_offset = 'offset',
					set_offset = 'offset',
					merge_sets_by_name = False,
					paste_nodes_by_name = False,
					paste_cons_by_name = False,
					merge_parts = False,
					model_action = 'merge_model',
					coord_offset = 'offset',
					node_offset = 'offset')
	
	base.RedrawAll()
	OldPartFaceImport = collector_PartOld.report()
	del collector_PartOld
	if len(OldPartFaceImport) >0:
		OldPartFaceConnect.extend(OldPartFaceImport)
		FindPartDuplicateInNewModelFunc(LabelStatus, OldPartFaceConnect)
		AnsaGroups = base.CollectEntities(constants.LSDYNA, None, ['ANSAGROUP'])
		if len(AnsaGroups) >0:
			for i in range(0, len(AnsaGroups), 1):
				try:
					OldPartFaceConnect.remove(AnsaGroups[i])
				except:
					continue
		
	return OldPartFaceConnect, OldPartFaceImport

##************************************ find part duplicate in new model    *********************************
def FindPartDuplicateInNewModelFunc(LabelStatus, PartImportConnect):

	if len(PartImportConnect) >0:
		base.Or(PartImportConnect)
		FacesConnect = CompareFaceSameSideFunc(LabelStatus)
		if len(FacesConnect) >0:
			ListPartDuplicateFace = CheckPartWithFaceDuplicateFunc(FacesConnect, LabelStatus)
			if len(ListPartDuplicateFace) >0:
#				base.Or(ListPartDuplicateFace)
				for i in range(0, len(ListPartDuplicateFace), 1):
					PartImportConnect.remove(ListPartDuplicateFace[i])
					ListPartDuplicateFace[i].set_entity_values(constants.LSDYNA, {'Comment': 'No Need'})
			
	return PartImportConnect		

###************************************ Tim cac part co face duplicate*********************************
def CheckPartWithFaceDuplicateFunc(FacesConnect, LabelStatus):
	
	guitk.BCLabelSetText(LabelStatus, 'Loading find part duplicate in new model.................')
	
	base.Or(FacesConnect)	
	ListPartDuplicateCOG = []
	ListCOGOnSinglePart = []
	ListPartDuplicateFace = []
	
	PartConnectVisible = base.CollectEntities(constants.LSDYNA, None, ['ANSAPART'], filter_visible = True)
	if len(PartConnectVisible) >0:
		for i in range(0, len(PartConnectVisible), 1):
			FaceOnPartConnect = base.CollectEntities(constants.LSDYNA, PartConnectVisible[i], ['FACE'])
			SetIntersection = set(FaceOnPartConnect).intersection(FacesConnect)
			if len(list(SetIntersection)) == len(FaceOnPartConnect):
				ValsPartConnect = base.GetEntityCardValues(constants.LSDYNA, PartConnectVisible[i], ['COG x', 'COG y', 'COG z'])
				StringCogPart = str(round(ValsPartConnect['COG x'], 3)) + '_' + str(round(ValsPartConnect['COG y'], 3)) + '_' + str(round(ValsPartConnect['COG z'], 3))
				ListCOGOnSinglePart.append(StringCogPart)
				ListPartDuplicateCOG.append(PartConnectVisible[i])
			
	if len(ListPartDuplicateCOG) >0:
		CogPartRemoveDuplicate = list(set(ListCOGOnSinglePart))
		for k in range(0, len(CogPartRemoveDuplicate), 1):
			ListPartDuplicateReq = []
			for w in range(0, len(ListCOGOnSinglePart), 1):
				if CogPartRemoveDuplicate[k] == ListCOGOnSinglePart[w]:
					ListPartDuplicateReq.append(ListPartDuplicateCOG[w])
			
			if len(ListPartDuplicateReq) >1:
				for j in range(1, len(ListPartDuplicateReq), 1):
					ListPartDuplicateFace.append(ListPartDuplicateReq[j])
	
	return ListPartDuplicateFace		

###************************************ Compare face to face same side*********************************
def CompareFaceSameSideFunc(LabelStatus):
	
	FacesConnect = []
	guitk.BCLabelSetText(LabelStatus, 'Loading compare same side.................')
	collector_PartConnect = base.CollectNewModelEntities(constants.LSDYNA, ['SET'])
	base.RmdblSameSide(tolerance = 0.1, similarity = 95, positive_negative_both = 'both', link_delete_set = 'set')
	SetConnect = collector_PartConnect.report()
	del collector_PartConnect
		
	if len(SetConnect) >0:
		FacesConnect = base.CollectEntities(constants.LSDYNA, SetConnect, ['FACE'])
		base.DeleteEntity(SetConnect, False)
		
	return FacesConnect

#************************************ OK Click Button*********************************
def AcceptClickButton(TopWindow, _win):
	
	PathDataOld = guitk.BCLineEditPathSelectedFilePaths(_win[2])
	ProBar = _win[0]
	LabelStatus = _win[1]
	
	if PathDataOld != None:
		PartConnect = base.CollectEntities(constants.LSDYNA, None, ['ANSAPART'])
		NewPartFaceReq = FindPartDuplicateInNewModelFunc(LabelStatus, PartConnect)
		if len(NewPartFaceReq) >0:
#			print(len(NewPartFaceReq))
			OldPartFaceConnect, OldPartFaceImport = ImportCadOldToAnsaFunc(PathDataOld, LabelStatus)
			if len(OldPartFaceConnect) >0:
				CompareNewModelWithOldModelFunc(NewPartFaceReq, OldPartFaceConnect, LabelStatus, ProBar)
				base.DeleteEntity(OldPartFaceImport, True)
				MoveGroupPartCompareFunc(ProBar, LabelStatus)
#			print(len(OldPartFaceConnect))
	else:
		guitk.UserError('Chọn đường dẫn CAD old....')
		return 1

#************************************ Cancel Click Button******************************	
def RejectClickButton(TopWindow, _win):
	return 1	
#************************************ Window*******************************************
@session.defbutton('1_CAD ASSEMBLY', 'CompareCADTool','So sánh cad cũ và cad mới....')
def CompareCadToCadTool():
	
	FileExtension = ['ansa']
	TopWindow = guitk.BCWindowCreate("Comapre Cad To Cad Tool version 1.0", guitk.constants.BCOnExitDestroy)
	
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Path Cad Old", guitk.constants.BCHorizontal)
	BCLabel_2 = guitk.BCLabelCreate(BCButtonGroup_1, "PathOld: ")
	BCLineEditPath_1 = guitk.BCLineEditPathCreate(BCButtonGroup_1, guitk.constants.BCHistoryFiles, "FileOld", guitk.constants.BCHistorySelect, "SelectPathOld")
	guitk.BCLineEditPathAddFilter(BCLineEditPath_1, 'ANSA File:', FileExtension)
	guitk.BCLineEditPathSetDialogEnterEnabled(BCLineEditPath_1, True)
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_1 = guitk.BCLabelCreate(TopWindow, "")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	_win = [BCProgressBar_1, BCLabel_1, BCLineEditPath_1]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectClickButton, _win)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptClickButton, _win)
	
	guitk.BCShow(TopWindow)

#########$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Help Functions $$$$$$$$$$$$$$$$$$$$$$$$$$$$
###### Create New Groups
def CreateNewGroupFunc(NameNewGroup):
	
	GroupNew = base.NewGroup(NameNewGroup, '')
	if GroupNew == None:
		GroupRefereceByName = base.NameToEnts(NameNewGroup)
		GroupNew = GroupRefereceByName[0]
	
	return GroupNew
	
#CompareCadToCadTool()



# PYTHON script
import os
import ansa
import math

from ansa import *


@session.defbutton('1_CAD ASSEMBLY', 'CompareCADToMESHTool','So sánh mesh cũ và cad mới đã chạy skin....')
deck = constants.LSDYNA

def CompareCadToMeshTool():
	
	TopWindow = guitk.BCWindowCreate("Compare Cad To Mesh Tool", guitk.constants.BCOnExitDestroy)
	
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Parameters", guitk.constants.BCHorizontal)
	BCLabel_1 = guitk.BCLabelCreate(BCButtonGroup_1, "Nodes Tolerance: ")
	BCLineEdit_1 = guitk.BCLineEditCreate(BCButtonGroup_1, "")
	guitk.BCLineEditSetText(BCLineEdit_1, '0.2')
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_2 = guitk.BCLabelCreate(TopWindow, "")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	_win = [BCProgressBar_1, BCLabel_2, BCLineEdit_1]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectClickButton, _win)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptClickButton, _win)
	
	guitk.BCShow(TopWindow)

#************************************ Cancel Click Button******************************	
def RejectClickButton(TopWindow, _win):	
	return 1	

#************************************ OK Click Button*********************************
def AcceptClickButton(TopWindow, _win):
	
	ProBar = _win[0]
	LabelStatus = _win[1]
	try:
		NodesTolerance = float(guitk.BCLineEditGetText(_win[2]))
	except:
		NodesTolerance = None
	else:
		NodesTolerance = NodesTolerance
	
	if NodesTolerance != None:
		PartsConnect = base.PickEntities(deck, ['ANSAPART'])
		if PartsConnect != None:
			for i in range(0, len(PartsConnect), 1):
				base.Or(PartsConnect[i])
				FaceConnectOnPart = base.CollectEntities(deck, PartsConnect[i], ['FACE'])
				ElemsFailedReport = CompareCadToFemToleranceFunc()
				if len(ElemsFailedReport) >0:
					ListPointsError = CompareNodesOfElemToCadFunc(ElemsFailedReport, FaceConnectOnPart, NodesTolerance, ProBar, LabelStatus)
					if len(ListPointsError) >0:
						base.SetEntityPart(ListPointsError, PartsConnect[i])
	
###************************************ So sanh nodes cua shell loi voi face *********************************
def CompareNodesOfElemToCadFunc(ElemsFailedReport, FaceConnectOnPart, NodesTolerance, ProBar, LabelStatus):
	
	ListPointsError = []
	NodesOnElemFailed = base.CollectEntities(deck, ElemsFailedReport, ['NODE'])
	guitk.BCProgressBarReset(ProBar)
	guitk.BCProgressBarSetTotalSteps(ProBar, len(NodesOnElemFailed))	
	for i in range(0, len(NodesOnElemFailed), 1):
		guitk.BCLabelSetText(LabelStatus, 'Loading Nodes ids: ' + str(NodesOnElemFailed[i]._id) + ' ..................')
		InfosNodesFailed = NodesOnElemFailed[i].get_entity_values(deck, ['X', 'Y', 'Z'])
		AxisNodesFailed = [InfosNodesFailed['X'], InfosNodesFailed['Y'], InfosNodesFailed['Z']]
		FacesNearest = base.NearestGeometry(coordinates = AxisNodesFailed, tolerance = NodesTolerance + 0.05, search_types = 'FACE', entities = FaceConnectOnPart, all_nearest = False)
		if FacesNearest[0] != None:
			ProjectStatus = calc.ProjectPointToContainer(AxisNodesFailed, FacesNearest[0])
			if ProjectStatus[1] > NodesTolerance:
				ListPointsError.append(base.Newpoint(AxisNodesFailed[0], AxisNodesFailed[1], AxisNodesFailed[2]))
		else:
			ListPointsError.append(base.Newpoint(AxisNodesFailed[0], AxisNodesFailed[1], AxisNodesFailed[2]))
		
		guitk.BCProgressBarSetProgress(ProBar, i +1)
	
	return ListPointsError

###************************************ Compare face to mesh same side*********************************
def CompareCadToFemToleranceFunc():
	ElemsFailedReport = []
	
	Colector_SetElemFailed = base.CollectNewModelEntities(deck, ['SET'])
	base.RmdblGeomFem(0.05)
	NewSetElemFailed = Colector_SetElemFailed.report()
	
	if len(NewSetElemFailed) >0:
		ElemsFailedReport = base.CollectEntities(deck, NewSetElemFailed, ['ELEMENT_SHELL'])
		base.DeleteEntity(NewSetElemFailed, False)
		
	return ElemsFailedReport

def CalculateDistance2PointsFunc(Points1st, Points2nd):
	
	VecsAB = [Points2nd[0] - Points1st[0], Points2nd[1] - Points1st[1], Points2nd[2] - Points1st[2]]
	LenVecsAB = math.sqrt((VecsAB[0]*VecsAB[0]) + (VecsAB[1]*VecsAB[1]) + (VecsAB[2]*VecsAB[2]))
	
	return LenVecsAB
	
#CompareCadToMeshTool()




