# PYTHON script
import ansa
from ansa import *
import os
from os import path

#@session.defbutton('3_FULL ASSEMBLY', 'OutputNastranTool','Output and renumber model Nastran') 
def OutputNastranModelTool():
	TopWindow = guitk.BCWindowCreate("Output Nastran Model Tool version 1.0", guitk.constants.BCOnExitDestroy)
	
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Path Csv Renumber", guitk.constants.BCHorizontal)
	BCLabel_2 = guitk.BCLabelCreate(BCButtonGroup_1, "Path Csv:     ")
	BCLineEditPath_1 = guitk.BCLineEditPathCreate(BCButtonGroup_1, guitk.constants.BCHistoryFiles, "History Csv", guitk.constants.BCHistorySelect, "Select Csv")
	guitk.BCLineEditPathAddFilter(BCLineEditPath_1, 'CSV', 'csv')
	
	BCButtonGroup_2 = guitk.BCButtonGroupCreate(TopWindow, "Select Path Folder Model", guitk.constants.BCHorizontal)
	BCLabel_3 = guitk.BCLabelCreate(BCButtonGroup_2, "Path Model:  ")
	BCLineEditPath_2 = guitk.BCLineEditPathCreate(BCButtonGroup_2, guitk.constants.BCHistoryFolders, "History Model", guitk.constants.BCHistorySelect, "Select Model")
	
	BCButtonGroup_3 = guitk.BCButtonGroupCreate(TopWindow, "Select Path Folder Output", guitk.constants.BCHorizontal)
	BCLabel_4 = guitk.BCLabelCreate(BCButtonGroup_3, "Path Output: ")
	BCLineEditPath_3 = guitk.BCLineEditPathCreate(BCButtonGroup_3, guitk.constants.BCHistoryFolders, "History Output", guitk.constants.BCHistorySelect, "Select Output")
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_1 = guitk.BCLabelCreate(TopWindow, "")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	DataOnTop = [BCProgressBar_1, BCLabel_1, BCLineEditPath_1, BCLineEditPath_2, BCLineEditPath_3]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, DataOnTop)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, DataOnTop)
	
	guitk.BCShow(TopWindow)

def RejectFunc(TopWindow, DataOnTop):
	
	return 1

#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, DataOnTop):
	
	ProBar = DataOnTop[0]
	BCLabel = DataOnTop[1]
	LineEditPathCsv = DataOnTop[2]
	LineEditPathModel = DataOnTop[3]
	LineEditPathOutput = DataOnTop[4]
	
	FlagReport = CheckInfosInTopWindowFunc(LineEditPathCsv, LineEditPathModel, LineEditPathOutput)
	if FlagReport == True:
		ListNameAssyModel, ListPathFilesModel = ReadInfosInFolderModelFunc(LineEditPathModel)
		if len(ListNameAssyModel) >0:
			DictAssy_InfosAssy, ListAssyError = ReadInfosInCsvRenumberFunc(LineEditPathCsv, ListNameAssyModel, ListPathFilesModel)
			if len(ListAssyError) ==0:
				OutputNastranTool(DictAssy_InfosAssy, ProBar, BCLabel, LineEditPathOutput)
			else:
				guitk.UserError('Can not found file ansa: ' + str(ListAssyError))
		
		else:
			guitk.UserError('Can not found ansa file in folder model')

#********************* Output model Nastran
def OutputNastranTool(DictAssy_InfosAssy, ProBar, BCLabel, LineEditPathOutput):
	
	guitk.BCProgressBarReset(ProBar)
	guitk.BCProgressBarSetTotalSteps(ProBar, len(DictAssy_InfosAssy))
	NumStep = 0
	for KeyAssyName, InfosAssyValues in DictAssy_InfosAssy.items():
		guitk.BCLabelSetText(BCLabel, 'Output File: ' + KeyAssyName)
#		print(InfosAssyValues)
		StatusOpen = OpenNewModelFunc(InfosAssyValues)
		if StatusOpen == 0:
			NameFolderOutput = InfosAssyValues[0]
			PathOutputCollect = guitk.BCLineEditPathSelectedFilePaths(LineEditPathOutput)
			PathFolderOutput = CreateNewFolderBaseOnLinkFunc(PathOutputCollect, KeyAssyName)
			if PathFolderOutput:
				ElemsSolidInConnection, ElemsRbe3InConnection = ReleaseSpotFromConnectionFunc(KeyAssyName)
				RenumberModelBaseOnRangeIDsFunc(InfosAssyValues, ElemsSolidInConnection, ElemsRbe3InConnection)
			
				OuputModelPartCardFileFunc(InfosAssyValues, PathFolderOutput)
			
		NumStep += 1
		guitk.BCProgressBarSetProgress(ProBar, NumStep + 1)
		

###****************** Output file model va file mat card
def OuputModelPartCardFileFunc(InfosAssyValues, PathFolderOutput):
	
	InfosNameFiles = InfosAssyValues[3]
	PathFileNameOutput = path.join(PathFolderOutput, InfosNameFiles[0])
	PathFilePartCardOutput = path.join(PathFolderOutput, InfosNameFiles[1])
	######**************** Output file Model
	base.OutputNastran(filename = PathFileNameOutput, 
									mode = 'all',
									write_comments = 'at_eof',
									format = 'short',
									continuation_lines = 'off',
									enddata = 'on',
									split_pyramid = 'off', disregard_includes = 'off',
									output_element_thickness = 'off',
									second_as_first = 'off', first_as_r = 'off', cweld_el_as_grid = 'off',
									apply_subcontainer_rules = 'off', lf_mode = 'system native', beginbulk = 'on',
									output_numbering_rules = 'off',
									version = 'msc nastran',
#									include_output_mode = 'contents',
									output_only_main_file = 'off', update_include_fname = 'off', output_all_same_directory = 'off', use_relative_name_for_readonly_includes = 'off',
									output_parameter_keywords = 'off', output_pcompg_as_pcomp = 'off',
									output_parts_in_xml = 'off', comment_output_name_comment = 'on', comment_output_parts_groups = 'on', comment_output_connections = 'off',
									comment_output_gebs = 'on', comment_output_colors = 'on', comment_output_safety = 'on', comment_output_kinetics = 'on', comment_output_cross_sections = 'on',
									comment_output_results_map = 'on', comment_output_general_comments = 'on', comment_output_info = 'on', comment_output_field_labels = 'off',
									comment_output_inline_include = 'on', comment_output_as_hypermesh = 'off', comment_output_lock_views = 'off',
									advanced_options = 'w Header, Nodes, Elements, Properties, Materials, Sets, Contacts',
									comment_output_annotations = 'on', comment_output_attributes = 'on',
									second_as_first_solids = 'off', comment_output_names_as_plain_comment = 'off', create_include_output_directory = 'off')
	
###****************** Renumber nodes, element, set
def RenumberModelBaseOnRangeIDsFunc(InfosAssyValues, ElemsSolidInConnection, ElemsRbe3InConnection):
	
	RangeIDsInSingleAssy = InfosAssyValues[1]
	RangeIDsSpotInSingleAssy = InfosAssyValues[2]
	##### Renumber NODE
	AllsNodesInModel = base.CollectEntities(constants.NASTRAN, None, ['GRID'])
	if len(AllsNodesInModel) >0:
		NodeRules = base.CreateNumberingRule(constants.NASTRAN, 'TOOL', AllsNodesInModel, 'GRID', 'PER_GROUP', RangeIDsInSingleAssy[0], RangeIDsInSingleAssy[1], 'Node Rule', force_ids = True)
		base.Renumber(NodeRules)
	
	##### Renumber Element
	AllsElementInModel = base.CollectEntities(constants.NASTRAN, None, ['__ELEMENTS__'])
	if len(AllsElementInModel) >0:
		ElementRules = base.CreateNumberingRule(constants.NASTRAN, 'TOOL', AllsElementInModel, 'ELEMENT', 'PER_GROUP', RangeIDsInSingleAssy[0], RangeIDsInSingleAssy[1], 'Elements Rule', force_ids = True)
		base.Renumber(ElementRules)
	
	##### Renumber ID Mats
	AllsMatInModel = base.CollectEntities(constants.NASTRAN, None, ['__MATERIALS__'])
	if len(AllsMatInModel) >0:
		MatsRules = base.CreateNumberingRule(constants.NASTRAN, 'TOOL', AllsMatInModel, 'MATERIAL', 'PER_GROUP', RangeIDsInSingleAssy[0], RangeIDsInSingleAssy[1], 'Materials Rule', force_ids = True)
		base.Renumber(MatsRules)
	
	##### Renumber ID PART	
	AnsaPartsConnect = base.CollectEntities(constants.NASTRAN, None, '__MBCONTAINERS__')
	if len(AnsaPartsConnect) >0:
		#--------Find Max Id Part
		ListGeneralIdsParts = []
		for i in range(0, len(AnsaPartsConnect), 1):
			ListGeneralIdsParts.append(AnsaPartsConnect[i]._id)
		#-------- Reset Id Parts
		for k in range(0, len(AnsaPartsConnect), 1):
			base.SetEntityCardValues(constants.NASTRAN, AnsaPartsConnect[k], {'__id__': RangeIDsInSingleAssy[0] + max(ListGeneralIdsParts) + k})
		#-------- Renumber Id Parts
		StartIdsParts = int(str(RangeIDsInSingleAssy[0])[0:6] + '1')
		for w in range(0, len(AnsaPartsConnect), 1):
			base.SetEntityCardValues(constants.NASTRAN, AnsaPartsConnect[w], {'__id__': StartIdsParts + w})
	
	##### Renumber Element of spot
	if len(ElemsSolidInConnection) >0:
		NodesOnElemsSolidSpot = base.CollectEntities(constants.NASTRAN, ElemsSolidInConnection, ['GRID'])
		NodeSolidSpotRules = base.CreateNumberingRule(constants.NASTRAN, 'TOOL', NodesOnElemsSolidSpot, 'GRID', 'PER_GROUP', RangeIDsSpotInSingleAssy[0], RangeIDsSpotInSingleAssy[1], 'Node Rule Spot', force_ids = True)
		base.Renumber(NodeSolidSpotRules)
	
	ListElemsOnSpotConnection = ElemsSolidInConnection + ElemsRbe3InConnection
	if len(ListElemsOnSpotConnection) >0:
		ElementSpotRules = base.CreateNumberingRule(constants.NASTRAN, 'TOOL', ListElemsOnSpotConnection, 'ELEMENT', 'PER_GROUP', RangeIDsSpotInSingleAssy[0], RangeIDsSpotInSingleAssy[1], 'Elements Rule Spot', force_ids = True)
		base.Renumber(ElementSpotRules)
	
###****************** Release element in spot connection
def ReleaseSpotFromConnectionFunc(KeyAssyName):
	
	GroupsAssyReferenceByName = base.NameToEnts(KeyAssyName)
	ElemsSolidInConnection = []
	ElemsRbe3InConnection = []
	
	ConnectionsSpotType = base.CollectEntities(constants.NASTRAN, None, ['SpotweldPoint_Type'])
	if len(ConnectionsSpotType) >0:
		ElemsSolidInConnection = base.CollectEntities(constants.NASTRAN, ConnectionsSpotType, ['SOLID'])
		ElemsRbe3InConnection = base.CollectEntities(constants.NASTRAN, ConnectionsSpotType, ['RBE3'])
		if len(ElemsSolidInConnection) >0:
			NamePartElemsSolid = 'Solid Spot Weld_' + KeyAssyName
			ModuleIdsPartElemsSolid = ''
			PartElemsSolidSpot = CreateNewPartFunc(NamePartElemsSolid, ModuleIdsPartElemsSolid)
			base.SetEntityPart(ElemsSolidInConnection, PartElemsSolidSpot)
			base.SetEntityPart(PartElemsSolidSpot, GroupsAssyReferenceByName[0])
		
		if len(ElemsRbe3InConnection) >0:
			NamePartElemsRbe3 = 'Rbe3 Spot Weld_' + KeyAssyName
			ModuleIdsPartElemsRbe3 = ''
			PartElemsRbe3Spot = CreateNewPartFunc(NamePartElemsRbe3, ModuleIdsPartElemsRbe3)
			base.SetEntityPart(ElemsRbe3InConnection, PartElemsRbe3Spot)
			base.SetEntityPart(PartElemsRbe3Spot, GroupsAssyReferenceByName[0])
	
	return ElemsSolidInConnection, ElemsRbe3InConnection
	
###****************** Open file
def OpenNewModelFunc(InfosAssyValues):
	
	session.New('discard')
	StatusOpen = base.Open(InfosAssyValues[4])
	
	return StatusOpen
#********************* Lấy thông tin trong file csv renumber
def ReadInfosInCsvRenumberFunc(LineEditPathCsv, ListNameAssyModel, ListPathFilesModel):
	
	DictAssy_InfosAssy = {}
	ListAssyError = []
	
	PathCsvRenumber = guitk.BCLineEditPathSelectedFilePaths(LineEditPathCsv)
	ListLineOnCsvIDs = ReadInfoCsvFunc(PathCsvRenumber)
	if len(ListLineOnCsvIDs) >0:
		for i in range(1, len(ListLineOnCsvIDs), 1):
			TokensLineCsv = ListLineOnCsvIDs[i].split(',')
			if TokensLineCsv[len(TokensLineCsv) -1] != '*':
				NameFileCollect = TokensLineCsv[7] + TokensLineCsv[8] + TokensLineCsv[9] + TokensLineCsv[10] + TokensLineCsv[11] + TokensLineCsv[12] + TokensLineCsv[13] + TokensLineCsv[14] + TokensLineCsv[15]
				NameFilePartCardCollect = TokensLineCsv[7] + TokensLineCsv[8] + TokensLineCsv[9] + TokensLineCsv[10] + TokensLineCsv[11] + TokensLineCsv[12] + TokensLineCsv[13] + '_PART-CARD' +TokensLineCsv[14] + TokensLineCsv[15]
				RangeIDsModel = [int(TokensLineCsv[3]), int(TokensLineCsv[4])]
				RangeIDsSpot = [int(TokensLineCsv[5]), int(TokensLineCsv[6])]
				NameAssyCollect = TokensLineCsv[2]
				PosSearchNameAssy = FindEntityInListElementsFunc(NameAssyCollect, ListNameAssyModel)
				if PosSearchNameAssy != None:
					DictAssy_InfosAssy[NameAssyCollect] = [TokensLineCsv[1], RangeIDsModel, RangeIDsSpot, [NameFileCollect, NameFilePartCardCollect], ListPathFilesModel[PosSearchNameAssy]]
				else:
					ListAssyError.append(NameAssyCollect)
	
	return DictAssy_InfosAssy, ListAssyError	

#********************* Lấy thông tin trong folder chứa file model
def ReadInfosInFolderModelFunc(LineEditPathModel):
	
	ListPathFilesModel = []
	ListNameAssyModel = []
	PathFolderModel = guitk.BCLineEditPathSelectedFilePaths(LineEditPathModel)
	ListFilesOnFolder = os.listdir(PathFolderModel)
	if len(ListFilesOnFolder) >0:
		for i in range(0, len(ListFilesOnFolder), 1):
			if ListFilesOnFolder[i].endswith('.ansa'):
				TokensFileModel = ListFilesOnFolder[i].split('.')
				ListPathFilesModel.append(path.join(PathFolderModel, ListFilesOnFolder[i]))
				ListNameAssyModel.append(TokensFileModel[0])
	
	return ListNameAssyModel, ListPathFilesModel

#********************* Check thông tin trên cửa sổ Window
def CheckInfosInTopWindowFunc(LineEditPathCsv, LineEditPathModel, LineEditPathOutput):
	
	FlagReport = False
	if guitk.BCLineEditPathSelectedFilePaths(LineEditPathCsv) != None:
		FlagReport = True
	else:
		FlagReport = False
		guitk.UserError('Select Path Csv Renumber Ids')
	
	if guitk.BCLineEditPathSelectedFilePaths(LineEditPathModel) != None:
		FlagReport = True
	else:
		FlagReport = False
		guitk.UserError('Select Path Model')

	if guitk.BCLineEditPathSelectedFilePaths(LineEditPathOutput) != None:
		FlagReport = True
	else:
		FlagReport = False
		guitk.UserError('Select Path Output')

	return FlagReport

####**************** Helps Functions************
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

def CreateNewFolderBaseOnLinkFunc(FolderLink, FolderName):
	
	NewPathFolder = path.join(FolderLink, FolderName)
	if not path.exists(NewPathFolder):
		os.makedirs(NewPathFolder)
	
	else:
		NewPathFolder = NewPathFolder
	
	return NewPathFolder

def CreateNewPartFunc(NamePart, ModuleIdsPart):
	
	NewParts = base.NewPart(NamePart, ModuleIdsPart)
	if NewParts == None:
		EntityPart = base.NameToEnts(NamePart)
		
		NewParts = EntityPart[0]
	
	return NewParts

OutputNastranModelTool()
