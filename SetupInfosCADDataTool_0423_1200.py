# PYTHON script
import ansa
from ansa import *
import os
from os import *
 
@session.defbutton('3_FULL ASSEMBLY', 'ImportMATCard','Thiết định vật liệu cho model')
def ImportMATCardTool():
	CVals_5 = ["Level", "Name", "Status"]
	TopWindow = guitk.BCWindowCreate("Import MAT Card File Tool version 1.0", guitk.constants.BCOnExitDestroy)
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Path MAT Card", guitk.constants.BCHorizontal)
	BCLabel_1 = guitk.BCLabelCreate(BCButtonGroup_1, "MAT CARD: ")
	BCLineEditPath_1 = guitk.BCLineEditPathCreate(BCButtonGroup_1, guitk.constants.BCHistoryFolders, "Folder History", guitk.constants.BCHistorySelect, "Select Folder")
	guitk.BCLineEditPathSetDialogEnterEnabled(BCLineEditPath_1, True)
	
	BCListView_1 = guitk.BCListViewCreate(TopWindow, 3, CVals_5, True)
	infoBox_6 = guitk.BCItemViewInfoBoxCreate(TopWindow, BCListView_1)
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	DataOnTop = [BCProgressBar_1, BCLineEditPath_1, BCListView_1]
	
	guitk.BCLineEditPathSetEnterPressedFunction(BCLineEditPath_1, AddFilesToListItemsFunc, DataOnTop)
	guitk.BCItemViewInfoBoxUpdate(infoBox_6)
	
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, DataOnTop)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, DataOnTop)
	
	guitk.BCShow(TopWindow)

def AddFilesToListItemsFunc(TopWindow, DataOnTop):
	
	PathFileMatSelected = guitk.BCLineEditPathSelectedFilePaths(DataOnTop[1])
	if PathFileMatSelected != None:
		
		AllsFilesInFloder = os.listdir(PathFileMatSelected)
		if len(AllsFilesInFloder) >0:
			listView = DataOnTop[2]
			rn = [guitk.constants.BCRenameType_None, guitk.constants.BCRenameType_String, guitk.constants.BCRenameType_String]
			cols = guitk.BCListViewColumns(listView)
			for i in range(0, len(AllsFilesInFloder), 1):
				if AllsFilesInFloder[i].endswith('.key') == True:
					ItemLv = guitk.BCListViewAddItem(listView, cols, [str(i), AllsFilesInFloder[i], '3D'], rn)
					guitk.BCListViewItemSetCheckBox(ItemLv, 2, 1, None, None)

def RejectFunc(TopWindow, DataOnTop):
	
	return 1

#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, DataOnTop):
	
	ItemsView = DataOnTop[2]
	ProBar = DataOnTop[0]
	IndexLineEditPath = DataOnTop[1]
	
	ListReportFromItemsView = []
	guitk.BCListViewForEachItem(ItemsView, guitk.constants.BCIterateAll, CheckBoxItemsStatus, ListReportFromItemsView)
	if len(ListReportFromItemsView) >0:
		
		FlagCheckReport = CheckInfosItemsReportFunc(ListReportFromItemsView)
		if FlagCheckReport == True:
			ImportMATCardFileToModelFunc(ListReportFromItemsView, IndexLineEditPath, ProBar)
			base.Compress('')
			
def ImportMATCardFileToModelFunc(ListReportFromItemsView, IndexLineEditPath, ProBar):
	
	ListIDsPropsInMatFile = []
	ListIDsSectionInMatFile = []
	ListIDsMATInMatFile = []
	
	PathFolderMATSelect = guitk.BCLineEditPathSelectedFilePaths(IndexLineEditPath)
	if PathFolderMATSelect != None:
		ListFileMATImport, ListFileSectionImport = FindSectionFromItemsViewFunc(ListReportFromItemsView)
		ListMATSorted = sorted(ListFileMATImport, reverse = False)
		if len(ListFileSectionImport) >0:
			ImportFileLSDynaFunc(ListFileSectionImport, ProBar, PathFolderMATSelect)
		
		if len(ListFileMATImport) >0:
			ImportFileLSDynaFunc(ListFileMATImport, ProBar, PathFolderMATSelect)

def ImportFileLSDynaFunc(ListFilesImport, ProBar, PathFolderMATSelect):
				
		guitk.BCProgressBarReset(ProBar)
		guitk.BCProgressBarSetTotalSteps(ProBar, len(ListFilesImport))
		
		for i in range(0, len(ListFilesImport), 1):
			PathFileMatImport = path.join(PathFolderMATSelect, ListFilesImport[i])	
			base.InputLSDyna(filename = PathFileMatImport,
										nodes_id = 'keep-old',
										elements_id = 'keep-old',
										properties_id = 'keep-new',
										materials_id = 'keep-new',
										sets_id = 'keep-new',
										coords_id = 'keep-new',
										read_comments = 'on',
										merge_sets_by_name = 'off',
										paste_nodes_by_name = 'off',
										new_include = 'off',
										merge_parts = 'off',
										header = 'overwrite',
										ignore_enddata = 'off',
										read_only = 'wp',
										read_hmcomments = 'off',
										create_parameters = 'on',
										comment_input_general_comments = 'on', comment_input_name_comment = 'on', comment_input_inline_include = 'on',
										comment_input_connection = 'on', comment_input_parts_groups = 'on', comment_input_gebs = 'on', comment_input_kinetics = 'on',
										comment_input_safety = 'on', comment_input_cross_sections = 'on', comment_input_results_map = 'on',
										comment_input_colors = 'on', comment_input_numb_rules = 'on', comment_input_misc = 'on', comment_input_lock_views = 'on',
										create_independent_sections = 'on',
										model_action = 'merge_model',
										version = '971r10',
										comment_input_annotations = 'on',
	#									advanced_options = '',
										comment_input_attributes = 'on',
										perform_material_synchronization = 'on',
										ignore_primer_keywords = 'off')
		
			guitk.BCProgressBarSetProgress(ProBar, i +1)	

def FindSectionFromItemsViewFunc(ListReportFromItemsView):
	
	ListFileMATImport = []
	ListFileSectionImport = []
	for i in range(0, len(ListReportFromItemsView), 1):
		TokenNameFileMAT = ListReportFromItemsView[i].split('@')
		if TokenNameFileMAT[1] == 'Section':
			ListFileSectionImport.append(TokenNameFileMAT[0])
		if TokenNameFileMAT[1] == 'MAT':
			ListFileMATImport.append(TokenNameFileMAT[0])
		
	return ListFileMATImport, ListFileSectionImport	

def SetUpIDsMatInModelToDefaustFunc(ProBar):
	
	MATRigids = base.CollectEntities(constants.LSDYNA, None, ['MAT20 MAT_RIGID'])
	AllsPropsInModel = base.CollectEntities(constants.LSDYNA, None, ['__PROPERTIES__'])
	if len(AllsPropsInModel) >0:
		guitk.BCProgressBarReset(ProBar)
		guitk.BCProgressBarSetTotalSteps(ProBar, len(AllsPropsInModel))
		for i in range(0, len(AllsPropsInModel), 1):
			ValsPropsCheckType = base.GetEntityCardValues(constants.LSDYNA, AllsPropsInModel[i], ['__type__', 'MID'])
			MatOnProps = base.GetEntity(constants.LSDYNA, '__MATERIALS__', int(ValsPropsCheckType['MID']))
			PosSearchMat = FindEntityInListElementsFunc(MatOnProps, MATRigids)
			if PosSearchMat == None:
				if ValsPropsCheckType['__type__'] == 'SECTION_SHELL':
					if ValsPropsCheckType['MID'] != 100:
						base.SetEntityCardValues(constants.LSDYNA, AllsPropsInModel[i], {'MID': 100})
				elif ValsPropsCheckType['__type__'] == 'SECTION_SOLID':
					if ValsPropsCheckType['MID'] != 200:
						base.SetEntityCardValues(constants.LSDYNA, AllsPropsInModel[i], {'MID': 200})
			
			guitk.BCProgressBarSetProgress(ProBar, i +1)

def CheckInfosItemsReportFunc(ListReportFromItemsView):
	
	FlagCheckReport = False
	ListMATStatus = []
	ListSectionStatus = []
	for i in range(0, len(ListReportFromItemsView), 1):
		if ListReportFromItemsView[i].find('@MAT') != -1:
			 ListMATStatus.append(ListReportFromItemsView[i])
		if ListReportFromItemsView[i].find('@Section') != -1:
			ListSectionStatus.append(ListReportFromItemsView[i])
	
	if len(ListSectionStatus) >0:
		FlagCheckReport = True
	else:
		FlagCheckReport = False
		guitk.UserError('Can not found file SECTION in folder')
	
	if len(ListMATStatus) >0:
		FlagCheckReport = True
	else:
		FlagCheckReport = False
		guitk.UserError('Select File MAT Input')
	
	return FlagCheckReport
	
def CheckBoxItemsStatus(ItemCheck, ListReportFromItemsView):
		
	StatusCheckBox = guitk.BCListViewItemCheckBoxIsChecked(ItemCheck, 2)
	NameFileMatCollect = guitk.BCListViewItemGetText(ItemCheck, 1)
	if StatusCheckBox == True:
		if NameFileMatCollect.find('SECTION') == -1:
			ListReportFromItemsView.append(NameFileMatCollect + '@MAT' )
		else:
			ListReportFromItemsView.append(NameFileMatCollect + '@Section' )

	if StatusCheckBox == False:
		if NameFileMatCollect.find('SECTION') != -1:
			ListReportFromItemsView.append(NameFileMatCollect + '@Section' )

def FindEntityInListElementsFunc(EntityElement, ListElements):
	
	try:
		Pos = ListElements.index(EntityElement)
	except:
		Pos = None
	else:
		Pos = Pos
	
	return Pos

#ImportMATCardTool()
