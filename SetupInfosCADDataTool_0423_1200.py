# PYTHON script
import ansa
from ansa import *

import os
import shutil
from os import path

@session.defbutton('1_CAD ASSEMBLY', 'SetupInfosCADDataTool','Thiết định thông số cad cho model')
def SetupInfosCADByManual():
	TopWindow = guitk.BCWindowCreate("Setup Infos Cad Data Tool version 1.0", guitk.constants.BCOnExitDestroy)
	
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Chọn đường dẫn file csv renumber ids", guitk.constants.BCHorizontal)
	BCLabel_2 = guitk.BCLabelCreate(BCButtonGroup_1, "Path Files IDs: ")
	BCLineEditPath_1 = guitk.BCLineEditPathCreate(BCButtonGroup_1, guitk.constants.BCHistoryFiles, "File Csv", guitk.constants.BCHistorySelect, "Select Csv")
	guitk.BCLineEditPathAddFilter(BCLineEditPath_1, 'CSV File', '*csv')
	
	BCButtonGroup_2 = guitk.BCButtonGroupCreate(TopWindow, "Chọn đường dẫn file BOM List", guitk.constants.BCHorizontal)
	BCLabel_3 = guitk.BCLabelCreate(BCButtonGroup_2, "Path Files BOM: ")
	BCLineEditPath_2 = guitk.BCLineEditPathCreate(BCButtonGroup_2, guitk.constants.BCHistoryFiles, "File BOM", guitk.constants.BCHistorySelect, "Select BOM")
	guitk.BCLineEditPathAddFilter(BCLineEditPath_2, 'CSV File', '*csv')
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	DataOnTop = [BCProgressBar_1, BCLineEditPath_1, BCLineEditPath_2]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, DataOnTop)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, DataOnTop)
	
	guitk.BCShow(TopWindow)
	
def RejectFunc(TopWindow, DataOnTop):
	
	return 1

#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, DataOnTop):
	
	ProBar = DataOnTop[0]
	PathCsvRenumberIDs = guitk.BCLineEditPathSelectedFilePaths(DataOnTop[1])
	PathBOMList = guitk.BCLineEditPathSelectedFilePaths(DataOnTop[2])
	if PathCsvRenumberIDs != None and PathBOMList != None:
		ListNameAssy, ListIDsRenumber = GetInfosInCsvFunc(PathCsvRenumberIDs)
		if len(ListNameAssy) >0:
			DictBOMLines_InfosRevison = GetInfosOfFileBOMListFunc(PathBOMList)
			if len(DictBOMLines_InfosRevison) >0:
#				print(DictBOMLines_InfosRevison)
				SetupInfosToPartFunc(DictBOMLines_InfosRevison, ListNameAssy, ListIDsRenumber, ProBar)
			
	else:
		guitk.UserError('Chọn lại đường dẫn chứa file CSV Renumber')
		return 1

def SetupInfosToPartFunc(DictBOMLines_InfosRevison, ListNameAssy, ListIDsRenumber, ProBar):
	
	DictNameGroup_ListPartOnGroup = FindAllGroupsAssyNameFunc(ListNameAssy, ListIDsRenumber)
	if len(DictNameGroup_ListPartOnGroup) >0:
		
		AllsPropsDivide = base.CollectEntities(constants.LSDYNA, None, '__PROPERTIES__')
		if len(AllsPropsDivide) >0:
			for j in range(0, len(AllsPropsDivide), 1):
				PidsRenumner = 10000000 + j
				PidsPropsOld = AllsPropsDivide[j]._id
				base.SetEntityCardValues(constants.LSDYNA, AllsPropsDivide[j], {'PID': PidsRenumner})
		
		for KeyNameGroup, ListPartsOnGroup in DictNameGroup_ListPartOnGroup.items():
			TokensNameGroup = KeyNameGroup.split('@')
			NameAssyCollect = TokensNameGroup[0]
			StringIDsRenumber = TokensNameGroup[1]
#			print(KeyNameGroup)
			SetupInfosToSinglePartsFunc(DictBOMLines_InfosRevison, ListPartsOnGroup, NameAssyCollect, StringIDsRenumber, ProBar)
	
	else:
		guitk.UserError('Khong tim thay group trong model')
			
def SetupInfosToSinglePartsFunc(DictBOMLines_InfosRevison, AnsaPartsInfos, NameAssyCollect, StringIDsRenumber, ProBar):
	
	base.Or(AnsaPartsInfos)
	AllsPropsModel = base.CollectEntities(constants.LSDYNA, None, '__PROPERTIES__', filter_visible = True)
	guitk.BCProgressBarReset(ProBar)
	guitk.BCProgressBarSetTotalSteps(ProBar, len(AllsPropsModel))
	for i in range(0, len(AllsPropsModel), 1):
		ValsPropInPart = base.GetEntityCardValues(constants.LSDYNA, AllsPropsModel[i], ['Name', 'User/CAD/OriginalId', 'T1'])
			
		EntityInProps = base.CollectEntities(constants.LSDYNA, AllsPropsModel[i], ['FACE'])
		if len(EntityInProps) >0:
			PartOnProps = base.GetEntityPart(EntityInProps[0])
			StartIdsRenumnber = str(int(StringIDsRenumber[0:5]) + i)
			PIDOnProps = int(StartIdsRenumnber + '00')
			NamePrefix = StringIDsRenumber[0:4]
			TokensNameParts, ThicknessPart, MatNamePart, NameOfProps = GetInfosOfAnsaPartFunc(PartOnProps)
			InfosRevisionIds, InfosVersionIds = GetInfosOfVersionIdOfPartsFunc(DictBOMLines_InfosRevison, NameOfProps, TokensNameParts)
			#### Tìm thông tin của tên chi tiết
			if NameOfProps == None:
				NameOfProps = GetInfosFromNamePropFacesFunc(ValsPropInPart)
			else:
				NameOfProps = NameOfProps

			#### Setup thông tin cho chi tiết	
			base.SetEntityCardValues(constants.LSDYNA, AllsPropsModel[i], {'Comment': TokensNameParts[0],
																												'User/cad_thickness' : NameAssyCollect,
																												'User/CAD/OriginalId': NamePrefix,
																												'User/original_name': InfosRevisionIds,
																												'Labels': InfosVersionIds,
																												'User/CAD/Name': MatNamePart,
																												'Name': NameOfProps,
																												'T1': ThicknessPart,
																												'PID': PIDOnProps})
		guitk.BCProgressBarSetProgress(ProBar, i+1)

############## Lay thong tin version id va revision id cua cad tu bom list
def GetInfosOfVersionIdOfPartsFunc(DictBOMLines_InfosRevison, NameOfProps, TokensNameParts):
	
	InfosRevisionIds = None
	InfosVersionIds = None
	
	for InfosKeyBOMLines, InfosValsRevison in DictBOMLines_InfosRevison.items():
		if NameOfProps == None:
			NameOfProps = TokensNameParts[0]
			
		if InfosKeyBOMLines.find(NameOfProps) != -1 and InfosKeyBOMLines.find(TokensNameParts[0]) != -1:
			InfosRevisionIds = 'R' + InfosValsRevison[0]
			InfosVersionIds = 'V' + InfosValsRevison[1]
			if InfosVersionIds == 'V':
				InfosVersionIds = None
			if InfosRevisionIds == 'R':
				InfosRevisionIds = None
	
	return InfosRevisionIds, InfosVersionIds
																																						
def GetInfosFromNamePropFacesFunc(ValsPropsInFace):
	
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

def GetInfosOfAnsaPartFunc(AnsaPartConnect):
	
	ValsPartCollect = base.GetEntityCardValues(constants.LSDYNA, AnsaPartConnect, ['Name', 'User/CAD/StringMetaData/Nomenclature', 'User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]', 'User/CAD/StringParameterData/ParameterSet\Material', 'User/CAD/StringMetaData/Revision'])
	
	TokensNameParts = ValsPartCollect['Name'].split('_')
	
	#********************* Lay thong tin thickness
	try:
		ThicknessPart = float(ValsPartCollect['User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]'])
	except:
		ThicknessPart = 0.01
	else:
#		print(ThicknessPart)
		if ThicknessPart != 0:
			ThicknessPart = ThicknessPart
		else:
			ThicknessPart = 0.01
	
	#******************** Lay thong tin Vat lieu
	try:
		MatNamePart = ValsPartCollect['User/CAD/StringParameterData/ParameterSet\Material']
	except:
		MatNamePart = None
	else:
		if MatNamePart != None and MatNamePart != '':
			MatNamePart = MatNamePart
		else:
			MatNamePart = None
	
	#********************* Lay thong tin cua ten chi tiet
	try:
		NameOfProps = ValsPartCollect['User/CAD/StringMetaData/Nomenclature']
	except:
		NameOfProps = None
	else:
		if NameOfProps != None and NameOfProps != '':
			TokensNameOfFace = NameOfProps.split('_')
			
			ListString = []
			ListStepOutput = []
			for i in range(0, len(TokensNameOfFace), 1):
				if TokensNameOfFace[i] != '':
					ListString.append(TokensNameOfFace[i])
					ListStepOutput.append(i)
			
			StringEndText = ListString[ListStepOutput.index(max(ListStepOutput))]
			NameOfProps = NameOfProps[0: NameOfProps.find(StringEndText) + len(StringEndText)]
			
		else:
			NameOfProps = None

	return TokensNameParts, ThicknessPart, MatNamePart, NameOfProps

def FindAllGroupsAssyNameFunc(ListNameAssy, ListIDsRenumber):
	
	DictNameGroup_ListPartOnGroup = {}
	
	AnsaGroups = base.CollectEntities(constants.LSDYNA, None, ['ANSAGROUP'])
	if len(AnsaGroups) >0:
		for i in range(0, len(AnsaGroups), 1):
			ValsAnsaGroup = base.GetEntityCardValues(constants.LSDYNA, AnsaGroups[i], ['Hierarchy', 'Name'])
			if ValsAnsaGroup['Hierarchy'] == '':
				NameGroup = ValsAnsaGroup['Name']
#				print(NameGroup)
#				print(ListNameAssy)
				PosFindGroupName = FindEntityInListElementsFunc(NameGroup, ListNameAssy)
				if PosFindGroupName != None:
					AnsaPartsOnGroup = base.CollectEntities(constants.LSDYNA, AnsaGroups[i], ['ANSAPART'], recursive = True)
					DictNameGroup_ListPartOnGroup[NameGroup + '@' + ListIDsRenumber[PosFindGroupName]] = AnsaPartsOnGroup
	
	return DictNameGroup_ListPartOnGroup

############## Lay thong tin tu BOM List
def GetInfosOfFileBOMListFunc(PathBOMList):
	
	DictBOMLines_InfosRevison = {}
	InfosCsvBOMList = ReadInfoCsvFunc(PathBOMList)
	for i in range(1, len(InfosCsvBOMList), 1):
		TokensLinesBOM = InfosCsvBOMList[i].split(',')
		InfosBOMLines = TokensLinesBOM[2]
		InfosRevision = TokensLinesBOM[5]
		
		InfosItemResision = TokensLinesBOM[6]
		TokensItemsRevision = InfosItemResision.split(';')
		TokensItemsRevisionByPoint = TokensItemsRevision[0].split('.')
		if len(TokensItemsRevisionByPoint) >1:
			InfosVersion = TokensItemsRevisionByPoint[1]
		else:
			InfosVersion = ''
		
		DictBOMLines_InfosRevison[InfosBOMLines] = [InfosRevision, InfosVersion]
	
	return DictBOMLines_InfosRevison

############## Lay thong tin tu csv renumber ids
def GetInfosInCsvFunc(PathCsvRenumberIDs):
	
	ListNameAssy = []
	ListIDsRenumber = []
	InfosCsvRenumber = ReadInfoCsvFunc(PathCsvRenumberIDs)
	if len(InfosCsvRenumber) >0:
		for i in range(1, len(InfosCsvRenumber), 1):
			TokensLinesCsv = InfosCsvRenumber[i].split(',')
			ListNameAssy.append(TokensLinesCsv[2])
			ListIDsRenumber.append(TokensLinesCsv[3])		
	
	return ListNameAssy, ListIDsRenumber

def ReadInfoCsvFunc(PathCsv):
	
	OpenCSVFile = open(PathCsv)
	ReadLinesCSV = OpenCSVFile.readlines()
	
	ListLinesInCSV = []
	for i in range(0, len(ReadLinesCSV), 1):
		ListLinesInCSV.append(ReadLinesCSV[i].strip())

	OpenCSVFile.close()
	
	return ListLinesInCSV

def FindEntityInListElementsFunc(EntityElement, ListElements):
	
	try:
		Pos = ListElements.index(EntityElement)
	except:
		Pos = None
	else:
		Pos = Pos
	
	return Pos
	
#SetupInfosCADByManual()
