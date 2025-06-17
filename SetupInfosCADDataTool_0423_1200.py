# PYTHON script
import ansa
from ansa import *
import os
from os import path

@session.defbutton('3_FULL ASSEMBLY', 'OutputLSDynaTool','Output and renumber model LSDyna') 
def OutputLSDynaModelTool():
	TopWindow = guitk.BCWindowCreate("Output LSDyna Model Tool version 1.0", guitk.constants.BCOnExitDestroy)
	
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
				OutputModelLSDynaFunc(DictAssy_InfosAssy, ProBar, BCLabel, LineEditPathOutput)
			else:
				guitk.UserError('Can not found file ansa: ' + str(ListAssyError))
		
		else:
			guitk.UserError('Can not found ansa file in folder model')

#********************* Output model LSDyna
def OutputModelLSDynaFunc(DictAssy_InfosAssy, ProBar, BCLabel, LineEditPathOutput):
	
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
			PathFolderOutput = CreateNewFolderBaseOnLinkFunc(PathOutputCollect, NameFolderOutput)
			if PathFolderOutput:
				RenumberModelBaseOnRangeIDsFunc(InfosAssyValues)
			
				OuputModelPartCardFileFunc(InfosAssyValues, PathFolderOutput)
			
		NumStep += 1
		guitk.BCProgressBarSetProgress(ProBar, NumStep + 1)
		

###****************** Output file model va file mat card
def OuputModelPartCardFileFunc(InfosAssyValues, PathFolderOutput):
	
	SECS = base.CollectEntities(constants.LSDYNA, None, ['DYNA_SECTION_SHELL', 'DYNA_SECTION_SOLID', 'HOURGLASS'])
	if len(SECS) >0:
		for i in range(0, len(SECS), 1):
			base.SetEntityCardValues(constants.LSDYNA, SECS[i], {'DEFINED': 'NO'})
	
	InfosNameFiles = InfosAssyValues[3]
	PathFileNameOutput = path.join(PathFolderOutput, InfosNameFiles[0])
	PathFilePartCardOutput = path.join(PathFolderOutput, InfosNameFiles[1])
	######**************** Output file Model
	base.OutputLSDyna(filename = PathFileNameOutput, 
									mode = 'all',
									write_comments = 'at_eof',
									format = '971R10',
									enddata = 'on',
									disregard_includes = 'off', output_element_thickness = 'off', apply_subcontainer_rules = 'off', lf_mode = 'system native', output_numbering_rules = 'off',
							#		include_output_mode = 'contents',
									output_only_main_file = 'off', output_parts_in_xml = 'off', update_include_fname = 'off', output_parameter_keywords = 'off', output_all_same_directory = 'off',
									use_relative_name_for_readonly_includes = 'off',
									comment_output_name_comment = 'off', comment_output_parts_groups = 'on', comment_output_connections = 'off', comment_output_gebs = 'off',
									comment_output_colors = 'off', comment_output_safety = 'off', comment_output_kinetics = 'off', comment_output_cross_sections = 'off',
									comment_output_results_map = 'off', comment_output_general_comments = 'off', comment_output_info = 'off', comment_output_field_labels = 'off',
									comment_output_inline_include = 'off', comment_output_lock_views = 'off',
									fields_format = 'short',
							#		advanced_options = 'w Header, Nodes, Elements, Properties, Materials, Sets, Contacts',
							#		include = 
									comment_output_annotations = 'off', comment_output_attributes = 'off', create_include_output_directory = 'off')
	
	######**************** Output file Part Card
#	base.OutputLSDyna(filename = PathFilePartCardOutput, 
#									mode = 'all',
#									write_comments = 'none',
#									format = '971R10',
#									enddata = 'on',
#									advanced_options = 'dw Header, Nodes, Elements, UProperties, UMaterials, Sets, Contacts',
#									fields_format = 'short')
	
###****************** Renumber nodes, element, set
def RenumberModelBaseOnRangeIDsFunc(InfosAssyValues):
	
	RangeIDsInSingleAssy = InfosAssyValues[1]
	##### Renumber NODE
	AllsNodesInModel = base.CollectEntities(constants.LSDYNA, None, ['NODE'])
	if len(AllsNodesInModel) >0:
		NodeRules = base.CreateNumberingRule(constants.LSDYNA, 'TOOL', AllsNodesInModel, 'NODE', 'PER_GROUP', RangeIDsInSingleAssy[0], RangeIDsInSingleAssy[1], 'Node Rule', force_ids = True)
		base.Renumber(NodeRules)
	
	##### Renumber Element
	AllsElementInModel = base.CollectEntities(constants.LSDYNA, None, ['__ELEMENTS__', ])
	if len(AllsElementInModel) >0:
		ElementRules = base.CreateNumberingRule(constants.LSDYNA, 'TOOL', AllsElementInModel, 'ELEMENT', 'PER_GROUP', RangeIDsInSingleAssy[0], RangeIDsInSingleAssy[1], 'Elements Rule', force_ids = True)
		base.Renumber(ElementRules)
	
	##### Renumber Set
	AllsSetInModel = base.CollectEntities(constants.LSDYNA, None, ['SET', ])
	if len(AllsSetInModel) >0:
		for i in range(0, len(AllsSetInModel), 1):
			base.SetEntityCardValues(constants.LSDYNA, AllsSetInModel[i], {'SID': RangeIDsInSingleAssy[0] + i})

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

#OutputLSDynaModelTool()
