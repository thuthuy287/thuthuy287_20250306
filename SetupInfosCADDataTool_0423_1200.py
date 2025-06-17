import ansa
from ansa import *
 
deck = constants.LSDYNA
@session.defbutton('4_SPOT-WELD', 'DivideSpotWeldTool','Chia Spot theo vật liệu của chi tiết ....')
def DivideSpotWeldTool():
	TopWindow = guitk.BCWindowCreate("Divide SpotWeld Tool version 1.0", guitk.constants.BCOnExitDestroy)
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, 'Select Options: ', guitk.constants.BCHorizontal)
	BCCheckBox_1 = guitk.BCCheckBoxCreate(BCButtonGroup_1, 'ApllySpot')
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_1 = guitk.BCLabelCreate(TopWindow, "")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	_win = [BCProgressBar_1, BCLabel_1, BCCheckBox_1]
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
	AppySpotStatus = _win[2]
	
	ElemsSpot = base.PickEntities(deck, ['ELEMENT_SOLID'])
	if ElemsSpot != None:
		base.Or(ElemsSpot)
		base.Near(radius = 5)
		
		MatVisbleOnModel = base.CollectEntities(deck, None, ['__MATERIALS__'], filter_visible = True)
		for w in range(0, len(MatVisbleOnModel), 1):
			if MatVisbleOnModel[w]._id == 19000000 or MatVisbleOnModel[w]._id == 91000001:
				base.Not(MatVisbleOnModel[w])
			
		ElemsShellVis = base.CollectEntities(deck, None, ['ELEMENT_SHELL'], filter_visible = True)
		guitk.BCProgressBarSetTotalSteps(ProBar, len(ElemsSpot))
		for i in range(0, len(ElemsSpot), 1):
			ListElemsProjected = FindElemsShellAroundSpotFunc(ElemsSpot, i, ElemsShellVis)
#			print(ListElemsProjected)
			if len(ListElemsProjected) != 2:
				print('ERR_' + str(ElemsSpot[i]._id))
			else:
				SetInfosElemsSpotFunc(ListElemsProjected, ElemsSpot, i)
				
			print(str(i+1) + '/' + str(len(ElemsSpot)) + ':' + str(ElemsSpot[i]._id))
			guitk.BCProgressBarSetProgress(ProBar, i+1)
			

def SetInfosElemsSpotFunc(ListElemsProjected, ElemsSpot, i):
	
	ValsElemsProj_1st = base.GetEntityCardValues(deck, ListElemsProjected[0], ['PID'])
	ValsElemsProj_2nd = base.GetEntityCardValues(deck, ListElemsProjected[1], ['PID'])

	PropsProj_1st = base.GetEntity(deck, 'SECTION_SHELL', int(ValsElemsProj_1st['PID']))
	PropsProj_2nd = base.GetEntity(deck, 'SECTION_SHELL', int(ValsElemsProj_2nd['PID']))
	
	ValsProps1st = PropsProj_1st.get_entity_values(deck, {'SECID', 'MID'})
	ValsProps2nd = PropsProj_2nd.get_entity_values(deck, {'SECID', 'MID'})
	
	ThicknessProps1st = str(ValsProps1st['SECID']._id)[4:8]
	ThicknessProps2nd = str(ValsProps2nd['SECID']._id)[4:8]
	ListThicknessAdd = [ThicknessProps1st, ThicknessProps2nd]
	
	MatOnProps1st = base.GetEntity(deck, '__MATERIALS__', int(ValsProps1st['MID']._id))
	MatOnProps2nd = base.GetEntity(deck, '__MATERIALS__', int(ValsProps2nd['MID']._id))
	
	ValsMat1st = MatOnProps1st.get_entity_values(deck, {'SIGY'})
	ValsMat2nd = MatOnProps2nd.get_entity_values(deck, {'SIGY'})
	ListSIGY_MaterialAdd = [ValsMat1st['SIGY'], ValsMat2nd['SIGY']]
	
	ValsElemsSpotOld = ElemsSpot[i].get_entity_values(deck, ['PID'])
	PropsOnElemsSpotOld = base.GetEntity(deck, 'SECTION_SOLID', int(ValsElemsSpotOld['PID']._id))
	ValsPropsSpotOld = PropsOnElemsSpotOld.get_entity_values(deck, ['SECID', 'MID', 'Name'])
	
	IdPropsSpot = '9' + str(min(ListSIGY_MaterialAdd)).replace('.', '') + str(min(ListThicknessAdd))
	
	PropsAddToSpotElems = base.GetEntity(deck, 'SECTION_SOLID', int(IdPropsSpot))
	if PropsAddToSpotElems != None:
		PropsAddToSpotElems = PropsAddToSpotElems
	else:
		PropsAddToSpotElems = base.CreateEntity(deck, 'SECTION_SOLID', {'PID': int(IdPropsSpot)})
	
	ElemsSpot[i].set_entity_values(deck, {'PID': PropsAddToSpotElems._id})
	PropsAddToSpotElems.set_entity_values(deck, {'Name': ValsPropsSpotOld['Name'], 'USER_SECID': 'SECTION', 'SECID': ValsPropsSpotOld['SECID'], 'MID': ValsPropsSpotOld['MID']})

def FindElemsShellAroundSpotFunc(ElemsSpot, i, ElemsShellVis):
	
	ListElemsAddOnSpots = []
	ListElemsAroundSpot = []
	ListDistanceProjElems = []
	
	ShellOnSolids = mesh.CreateShellsOnSolidsPidSkin(solids = ElemsSpot[i], ret_ents = True)
	for k in range(0, len(ShellOnSolids), 1):
		CogOfShells = base.Cog(ShellOnSolids[k])
				
		ProjCogShellToElems = calc.ProjectPointsToElements(coordinates = CogOfShells, entities = ElemsShellVis, tolerance = 1)
		if ProjCogShellToElems[0].entity != None:
			ElemsProjected = ProjCogShellToElems[0].entity
			DistanceProjected = ProjCogShellToElems[0].distance
			ListElemsAroundSpot.append(ElemsProjected)
			ListDistanceProjElems.append(DistanceProjected)
			
			ValsCommentElemProj = ElemsProjected.get_entity_values(deck, ['Comment'])
			if ValsCommentElemProj['Comment'] == '':
				ElemsProjected.set_entity_values(deck, {'Comment': DistanceProjected})
			else:
				if DistanceProjected < float(ValsCommentElemProj['Comment']):
					ElemsProjected.set_entity_values(deck, {'Comment': DistanceProjected})
	
	if len(ListElemsAroundSpot) >0:
		ListElemsAroundSpotRemoveDouble = list(set(ListElemsAroundSpot))
		ListDistanceOnComment = []
		DictElems_DistanceProject = {}
		for i in range(0, len(ListElemsAroundSpotRemoveDouble), 1):
			CommnentElemsAround = ListElemsAroundSpotRemoveDouble[i].get_entity_values(deck, ['Comment'])
			ListDistanceOnComment.append(float(CommnentElemsAround['Comment']))
			DictElems_DistanceProject[ListElemsAroundSpotRemoveDouble[i]] = float(CommnentElemsAround['Comment'])
		
		ListDistanceOnComment.sort()
		min_distance_proj_1st = ListDistanceOnComment[0]
		min_distance_proj_2nd = ListDistanceOnComment[1]
		for ElemsProjection, DistanceProjection in DictElems_DistanceProject.items():
			if DistanceProjection == min_distance_proj_1st or DistanceProjection == min_distance_proj_2nd:
				ListElemsAddOnSpots.append(ElemsProjection)
			
			ElemsProjection.set_entity_values(deck, {'Comment': ''})
		
	base.DeleteEntity(ShellOnSolids, True)
	
	return ListElemsAddOnSpots

#DivideSpotWeldTool()

D:\Kyty180389\Script\19.Divide SpotWeld Tool
















# PYTHON script
import ansa
from ansa import *

deck_infos = constants.LSDYNA
@session.defbutton('4_MATERIAL', 'CompareMaterialTool','So sánh vật liệu của các chi tiết đối xứng ....')
def CompareMaterialTool():
	TopWindow = guitk.BCWindowCreate("Compare Material On Model Tool ver1.0", guitk.constants.BCOnExitDestroy)
	
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Type Of Model:", guitk.constants.BCHorizontal)
	BCRadioButton_1 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "NVH Model", None, 0)
	BCRadioButton_2 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Crash Model", None, 0)
	guitk.BCRadioButtonSetChecked(BCRadioButton_1, True)
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_1 = guitk.BCLabelCreate(TopWindow, "")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	_window = [BCProgressBar_1, BCLabel_1, BCRadioButton_1, BCRadioButton_2]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, _window)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, _window)
	
	guitk.BCShow(TopWindow)

def RejectFunc(TopWindow, _window):
	return 1
	
#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, _window):
	
	ProbarStatus = _window[0]
	LabelStatus = _window[1]
	NVH_ModelStatus = guitk.BCRadioButtonIsChecked(_window[2])
	Crash_ModelStatus = guitk.BCRadioButtonIsChecked(_window[3])
	
	AllsProps = base.CollectEntities(deck_infos, None, ['__PROPERTIES__'], filter_visible = True)
#	AllsProps = base.CollectEntities(deck, None, ['__PROPERTIES__'])
	if len(AllsProps) >0:
		ListPropsLH_Side, ListPropsRH_Side, ListPropsCommon_Side = FindPropsLH_RHSideFunc(AllsProps, LabelStatus, ProbarStatus)
		if len(ListPropsLH_Side) >0 and len(ListPropsRH_Side) >0:
			
			ListPairsPidsPenetration = FindPairsPropsIntersectionFunc(ListPropsLH_Side, ListPropsRH_Side)
#			print(ListPairsPidsPenetration)
			if ListPairsPidsPenetration != None:
				ListPairPropsSimilarsReq = FindPairsPropsSimilarFunc(ListPairsPidsPenetration, ProbarStatus, LabelStatus)
#				print(ListPairPropsSimilarsReq)
				if len(ListPairPropsSimilarsReq) >0:
					CompareMaterialOfPairsPropsFunc(ListPairPropsSimilarsReq, NVH_ModelStatus, Crash_ModelStatus)
				
					guitk.BCLabelSetText(LabelStatus, 'Done ^..^....Check Status In Comment Properties....:')
				
########## Comapre materials of pid in model lh, rh
def CompareMaterialOfPairsPropsFunc(ListPairPropsSimilarsReq, NVH_ModelStatus, Crash_ModelStatus):
	
	for i in range(0, len(ListPairPropsSimilarsReq), 1):
		if NVH_ModelStatus == True:
			vals_props_compare_1st = base.GetEntityCardValues(constants.NASTRAN, ListPairPropsSimilarsReq[i][0], ['T'])
			vals_props_compare_2nd = base.GetEntityCardValues(constants.NASTRAN, ListPairPropsSimilarsReq[i][1], ['T'])
#			print(ListPairPropsSimilarsReq[i])
#			print(vals_props_compare_1st, vals_props_compare_2nd)
			if vals_props_compare_1st['T'] != vals_props_compare_2nd['T']:
				ListPairPropsSimilarsReq[i][0].set_entity_values(constants.NASTRAN, {'Comment': 'Diff_Thickness'})
				ListPairPropsSimilarsReq[i][1].set_entity_values(constants.NASTRAN, {'Comment': 'Diff_Thickness'})
			
		if Crash_ModelStatus == True:
			vals_props_compare_1st = base.GetEntityCardValues(deck_infos, ListPairPropsSimilarsReq[i][0], ['SECID', 'MID'])
			vals_props_compare_2nd = base.GetEntityCardValues(deck_infos, ListPairPropsSimilarsReq[i][1], ['SECID', 'MID'])
			if vals_props_compare_1st['MID'] != vals_props_compare_2nd['MID']:
				ListPairPropsSimilarsReq[i][0].set_entity_values(deck_infos, {'Comment': 'Diff_MAT'})
				ListPairPropsSimilarsReq[i][1].set_entity_values(deck_infos, {'Comment': 'Diff_MAT'})
				
			if vals_props_compare_1st['SECID'] != vals_props_compare_2nd['SECID']:
				ListPairPropsSimilarsReq[i][0].set_entity_values(deck_infos, {'Comment': 'Diff_Thickness'})
				ListPairPropsSimilarsReq[i][1].set_entity_values(deck_infos, {'Comment': 'Diff_Thickness'})
			

########## Find pairs props similar in model: lh, rh side
def FindPairsPropsSimilarFunc(ListPairsPidsPenetration, ProbarStatus, LabelStatus):
	
	ListPidsChecked = []
	ListPairPropsSimilarsReq = []
	
	guitk.BCProgressBarSetTotalSteps(ProbarStatus, len(ListPairsPidsPenetration))
	for i in range(0, len(ListPairsPidsPenetration), 1):
#		print('Loading Pairs Ids: ' + str(ListPairsPidsPenetration[i]) + '....' + str(i+1) + '/' + str(len(ListPairsPidsPenetration)))
		guitk.BCLabelSetText(LabelStatus, 'Loading Props Ids: ' + str(ListPairsPidsPenetration[i]) + '....' + str(i+1) + '/' + str(len(ListPairsPidsPenetration)))
		if ListPairsPidsPenetration[i] != 0:
			IdsProps_1st = ListPairsPidsPenetration[i][0]
			IdsProps_2nd = ListPairsPidsPenetration[i][1]
			pos_ids_1st = FindEntityInListElementsFunc(IdsProps_1st, ListPidsChecked)
			pos_ids_2nd = FindEntityInListElementsFunc(IdsProps_2nd, ListPidsChecked)
			
			if pos_ids_1st == None and pos_ids_2nd == None:
				status_similar, ListPropsConnect = CompareMeshToMeshSameSideFunc(ListPairsPidsPenetration[i])
#				print(status_similar)
				if status_similar == True:
					ListPidsChecked.extend(ListPairsPidsPenetration[i])
					ListPairPropsSimilarsReq.append(ListPropsConnect)
		guitk.BCProgressBarSetProgress(ProbarStatus, i+1)
	
	return ListPairPropsSimilarsReq

########## Comapre mesh to mesh sameside in model	
def CompareMeshToMeshSameSideFunc(ListIdsPropsCompare):
	
	ListPropsConnect = []
	status_similar = False
	
	for i in range(0, len(ListIdsPropsCompare), 1):
		ListPropsConnect.append(base.GetEntity(deck_infos, '__PROPERTIES__', ListIdsPropsCompare[i]))
	
	base.Or(ListPropsConnect)
	collector_sets_elems_diff = base.CollectNewModelEntities(deck_infos, 'SET')
	status_compare = base.RmdblFemFem(0.5, 2)
	new_sets_elems_diff = collector_sets_elems_diff.report()
	del collector_sets_elems_diff
	
	if status_compare != 0:
		if len(new_sets_elems_diff) >0:
			status_similar = False
			ElemsOnSetDiff = base.CollectEntities(deck_infos, new_sets_elems_diff, ['__ELEMENTS__'])
			list_props_similar = ComparePropsBaseOnAreaOfPartsFunc(ElemsOnSetDiff, ListPropsConnect)
			if len(list_props_similar) == 2:
				status_similar = True
			
			base.DeleteEntity(new_sets_elems_diff, True)
		else:
			status_similar = True
	
#	else:
#		print(ListIdsPropsCompare)
	
	return status_similar, ListPropsConnect

########## Compare props similar base on area of parts
def ComparePropsBaseOnAreaOfPartsFunc(ElemsOnSetDiff, ListPropsConnect):
	
	list_props_similar = []
	for i in range(0, len(ListPropsConnect), 1):
		type_of_props = ListPropsConnect[i].get_entity_values(deck_infos, ['__type__'])
		elems_on_props_connect = base.CollectEntities(deck_infos, ListPropsConnect[i], ['__ELEMENTS__'])
		elems_on_set_diff_props = list(set(elems_on_props_connect).intersection(ElemsOnSetDiff))
		if type_of_props['__type__'] == 'SECTION_SHELL':
			area_of_props_connect = CalcAreaOnListElemsFunc(elems_on_props_connect)
			area_of_elems_diff = CalcAreaOnListElemsFunc(elems_on_set_diff_props)
			
			AreaSimilarFactor = (area_of_elems_diff/area_of_props_connect)*100
			if AreaSimilarFactor <= 50:
				list_props_similar.append(ListPropsConnect[i])
		
		else:
			number_elems_similar = (len(elems_on_set_diff_props)/len(elems_on_props_connect))*100
			if number_elems_similar <= 50:
				list_props_similar.append(ListPropsConnect[i])
		
	return list_props_similar
		
########## Find pairs pid intersection in model
def FindPairsPropsIntersectionFunc(ListPropsLH_Side, ListPropsRH_Side):
	
	ListPairsPidsPenetration = []
	base.Or(ListPropsLH_Side)
	base.And(ListPropsRH_Side)
	base.GeoSymmetry(input_function_type = "MOVE", 
									pid_offset = 0, 
									group_offset = "NEW PART", 
									input_sets_type = "NONE", 
									entities = ListPropsRH_Side,
									)
			
	ListPairsPidsPenetration = base.ReportPenetratedPairsOfPIDs(check_type = 3, fix = False, user_thickness = 0.4)
	
	return ListPairsPidsPenetration
			
########## Find props LH, RH side
def FindPropsLH_RHSideFunc(AllsProps, LabelStatus, ProbarStatus):
	
	ListPropsLH_Side = []
	ListPropsRH_Side = []
	ListPropsCommon_Side = []
	
	guitk.BCProgressBarSetTotalSteps(ProbarStatus, len(AllsProps))
	for i in range(0, len(AllsProps), 1):
#		print('Loading Props Ids: ' + str(AllsProps[i]._id) + '....' + str(i+1) + '/' + str(len(AllsProps)))
		guitk.BCLabelSetText(LabelStatus, 'Loading Props Ids: ' + str(AllsProps[i]._id) + '....' + str(i+1) + '/' + str(len(AllsProps)))
		ListNodesPositive = []
		ListNodesNegative = []
		
		ElemsOnProps = base.CollectEntities(deck_infos, AllsProps[i], ['__ELEMENTS__'])
		if len(ElemsOnProps) >0:
			NodesOnProps = base.CollectEntities(deck_infos, ElemsOnProps, ['NODE'])
			for k in range(0, len(NodesOnProps), 1):
				if NodesOnProps[k].position[1] <0:
					ListNodesNegative.append(NodesOnProps[k])
				else:
					ListNodesPositive.append(NodesOnProps[k])
			
		if len(ListNodesNegative) >0 and len(ListNodesPositive) >0:
			ListPropsCommon_Side.append(AllsProps[i])
			AllsProps[i].set_entity_values(deck_infos, {'Comment': 'Common Side'})
		else:
			if len(ListNodesPositive) >0:
				ListPropsRH_Side.append(AllsProps[i])
				AllsProps[i].set_entity_values(deck_infos, {'Comment': 'RH Side'})
			if len(ListNodesNegative) >0:
				ListPropsLH_Side.append(AllsProps[i])
				AllsProps[i].set_entity_values(deck_infos, {'Comment': 'LH Side'})
		
		guitk.BCProgressBarSetProgress(ProbarStatus, i+1)
		
	return ListPropsLH_Side, ListPropsRH_Side, ListPropsCommon_Side


##$$$$$$$$$$$$$$$$$$$ Help Functions
def FindEntityInListElementsFunc(EntityElement, ListElements):
	
	try:
		Pos = ListElements.index(EntityElement)
	except:
		Pos = None
	else:
		Pos = Pos
	
	return Pos

def CalcAreaOnListElemsFunc(ListElemsImport):
	
	ListTotalArea = []
	for i in range(0, len(ListElemsImport), 1):
		ListTotalArea.append(base.CalcShellArea(ListElemsImport[i]))
	
	TotalAreaReq = sum(ListTotalArea)
	
	return TotalAreaReq
	
#CompareMaterialTool()
D:\Kyty180389\Script\20.CompareMaterial






# PYTHON script
import os
import ansa
from ansa import *

deck_infos = constants.NASTRAN
def main():
	# Need some documentation? Run this with F5

	for i in range(0, 100, 1):
		base.SetPickMethod(base.constants.PID_REGION_SELECTION)
		ElemsWeldSelect = base.PickEntities(deck_infos, ['SHELL'])
		if ElemsWeldSelect != None:
			PropsOfSolids = base.PickEntities(deck_infos, ['PSOLID'])
			if PropsOfSolids != None:
				SetInfosPropsOfWeldSolidFunc(PropsOfSolids, ElemsWeldSelect)
				
		else:
			return 1

def SetInfosPropsOfWeldSolidFunc(PropsOfSolids, ElemsWeldSelect):
	
	base.Or(ElemsWeldSelect)
	base.Neighb('1')
	ListGroupElemAroundWeldSolid = FindElemsAroundArcWeldFunc(ElemsWeldSelect)
	if len(ListGroupElemAroundWeldSolid) >0:
		StatusTypes = None
		if len(PropsOfSolids) == 1:
			StatusTypes = 'SongSong'
		else:
			StatusTypes = 'VuongGoc'
		
		StringEndIdsSolidsWeld = '09'
		NameSolidsWeld = 'ArcWeld'
		StatusWeldProps = 'PSHELL'
		ThicknessWeld = 4
		SetupInfosPropSolidsWeldFunc(ElemsWeldSelect, PropsOfSolids[0], StringEndIdsSolidsWeld, NameSolidsWeld, StatusWeldProps, ThicknessWeld)
		
		for i in range(0, len(ListGroupElemAroundWeldSolid), 1):
			PidsElemsAroundSolidsWeldOrigin = ListGroupElemAroundWeldSolid[i][0].get_entity_values(deck_infos, ['PID'])
			PropsElemsAroundSolidsWeldOrigin = PidsElemsAroundSolidsWeldOrigin['PID']
			if StatusTypes == 'SongSong':
				if PropsOfSolids[0] == PropsElemsAroundSolidsWeldOrigin:
					ListShellsVolHeatZone1st = SetupInfosWithSolidWeldParallelFunc(ListGroupElemAroundWeldSolid[i], PropsElemsAroundSolidsWeldOrigin, ElemsWeldSelect)
				else:
					SetupInfosWithSolidWeldRectangularFunc(ListGroupElemAroundWeldSolid[i], PropsElemsAroundSolidsWeldOrigin, ElemsWeldSelect)
					
			elif StatusTypes == 'VuongGoc':
				SetupInfosWithSolidWeldRectangularFunc(ListGroupElemAroundWeldSolid[i], PropsElemsAroundSolidsWeldOrigin, ElemsWeldSelect)
							
def SetupInfosWithSolidWeldRectangularFunc(InfosSolidWeldRectangular, PropsElemsAroundSolidsWeldOrigin, ElemsWeldSelect):
	
	ListShellsVolHeatZone1st = SetupInfosWithSolidWeldParallelFunc(InfosSolidWeldRectangular, PropsElemsAroundSolidsWeldOrigin, ElemsWeldSelect)
	if len(ListShellsVolHeatZone1st) >0:
		base.Neighb('1')
		ListGroupsSolidsHeatZone_2nd = FindElemsAroundArcWeldFunc(ListShellsVolHeatZone1st)
		if len(ListGroupsSolidsHeatZone_2nd) >0:
			for i in range(0, len(ListGroupsSolidsHeatZone_2nd), 1):
				PidsHeatZone2ndOrigin = ListGroupsSolidsHeatZone_2nd[i][0].get_entity_values(deck_infos, ['PID'])
				PropsHeatZones_2ndOrigin = PidsHeatZone2ndOrigin['PID']
				StringEndHeatZone_2nd = '02'
				NameHeatZone_2nd = 'HeatZone_2nd'
				StatusProps = 'PSOLID'
				ThiknessHeatZone2nd = None
				SetupInfosPropSolidsWeldFunc(ListGroupsSolidsHeatZone_2nd[i], PropsHeatZones_2ndOrigin, StringEndHeatZone_2nd, NameHeatZone_2nd, StatusProps, ThiknessHeatZone2nd)				

#######*********************** Thiet dinh thong tin properties cho cac part song song **********************######
def SetupInfosWithSolidWeldParallelFunc(InfosListElemsSolidWeld, PropsElemsAroundSolidsWeldOrigin, ElemsWeldSelect):
	
	StringEndHeatZone_1st = '01'
	NameHeatZone_1st = 'HeatZone_1st'
	StatusProps = 'PSOLID'
	ThicknessHeatZone_1st = None
	SetupInfosPropSolidsWeldFunc(InfosListElemsSolidWeld, PropsElemsAroundSolidsWeldOrigin, StringEndHeatZone_1st, NameHeatZone_1st, StatusProps, ThicknessHeatZone_1st)
	ListElemsHeatZone_1st, ListShellsVolHeatZone1st = CreateVolShellOfHeatZone1stFunc(InfosListElemsSolidWeld, ElemsWeldSelect)
	if len(ListElemsHeatZone_1st) >0:
		StringEndVolShellsHeatZone_1st = '07'
		NameVolShellsHeatZone_1st = 'VolShells_HeatZone_1st'
		StatusProps = 'PSHELL'
		ThicknessVolShellHEatZone_1st = 2
		SetupInfosPropSolidsWeldFunc(ListElemsHeatZone_1st, PropsElemsAroundSolidsWeldOrigin, StringEndVolShellsHeatZone_1st, NameVolShellsHeatZone_1st, StatusProps, ThicknessVolShellHEatZone_1st)	
	
	return ListShellsVolHeatZone1st
					
#######*********************** Thiet dinh thong tin properties cho cac part **********************######
def CreateVolShellOfHeatZone1stFunc(InfosElemsSolidHeatZone1st, ElemsWeldSelect):
	
	ListElemsVolShellReq = []
	ListShellsVolHeatZone1st = []
	
	VolsShellsAroundSolids = mesh.CreateShellsOnSolidsPidSkin(solids = InfosElemsSolidHeatZone1st, ret_ents = True)
	if len(VolsShellsAroundSolids) >0:
		GridsOnWeldSolids = base.CollectEntities(deck_infos, ElemsWeldSelect, ['GRID'])
		for i in range(0, len(VolsShellsAroundSolids), 1):
			GridsOnElemsVolShells = base.CollectEntities(deck_infos, VolsShellsAroundSolids[i], ['GRID'])
			ListGridsVolShellsCommonWithArc = list(set(GridsOnWeldSolids).intersection(GridsOnElemsVolShells))
			if len(ListGridsVolShellsCommonWithArc) >0:
				ListElemsVolShellReq.append(VolsShellsAroundSolids[i])
				if len(ListGridsVolShellsCommonWithArc) >1:
					ListShellsVolHeatZone1st.append(VolsShellsAroundSolids[i])
			else:
				base.DeleteEntity(VolsShellsAroundSolids[i], True)
				
	return ListElemsVolShellReq, ListShellsVolHeatZone1st

#######*********************** Thiet dinh thong tin properties cho cac part **********************######
def SetupInfosPropSolidsWeldFunc(ListElemsSolidsWeld, PropsSolidWeldOrigin, EntityStringEndHeatZone, EntityNameHeatZone, StatusProps, InfosThickness):
	
	ValsPropsSolidOrigin = PropsSolidWeldOrigin.get_entity_values(deck_infos, ['MID'])
	InfosMatsSolidsOrigin = ValsPropsSolidOrigin['MID']
	NameOfMatSolidsOrigin = InfosMatsSolidsOrigin._name
	MatIdsOnNewSolidsProps = int(str(InfosMatsSolidsOrigin._id)[0:6]+EntityStringEndHeatZone)
	MatsSolidsReferenIds = base.GetEntity(deck_infos, '__MATERIALS__', int(MatIdsOnNewSolidsProps))
	if MatsSolidsReferenIds == None:
		NewMatsSolidsOnPropsReferen = base.CopyEntity(None, InfosMatsSolidsOrigin)
		NewMatsSolidsOnPropsReferen.set_entity_values(deck_infos, {'MID': MatIdsOnNewSolidsProps, 'Name': NameOfMatSolidsOrigin + '_' + EntityNameHeatZone})		
	
	NewIdsOnSolidsProps = int(str(PropsSolidWeldOrigin._id)[0:5]+EntityStringEndHeatZone)
	
	if StatusProps == 'PSOLID':
		PropsSolidsReferenIds = base.GetEntity(deck_infos, 'PSOLID', int(NewIdsOnSolidsProps))
		if PropsSolidsReferenIds != None:
			PropsSolidsReferenIds.set_entity_values(deck_infos, {'MID': MatIdsOnNewSolidsProps})
		else:
			NewPropsSolidsElems = base.CopyEntity(None, PropsSolidWeldOrigin)
			NewPropsSolidsElems.set_entity_values(deck_infos, {'PID': NewIdsOnSolidsProps, 'Name': EntityNameHeatZone, 'MID': MatIdsOnNewSolidsProps})
	
	elif StatusProps == 'PSHELL':
		PropsShellsReferenIds = base.GetEntity(deck_infos, 'PSHELL', int(NewIdsOnSolidsProps))
		if PropsShellsReferenIds != None:
			PropsShellsReferenIds.set_entity_values(deck_infos, {'MID1': MatIdsOnNewSolidsProps, 'MID2': MatIdsOnNewSolidsProps, 'MID3': MatIdsOnNewSolidsProps})
		else:
			NewPropsShellsElems = base.CreateEntity(deck_infos, 'PSHELL', {'PID': NewIdsOnSolidsProps, 'Name': EntityNameHeatZone, 'T': InfosThickness, 'MID1': MatIdsOnNewSolidsProps, 'MID2': MatIdsOnNewSolidsProps, 'MID3': MatIdsOnNewSolidsProps})
		
	for i in range(0, len(ListElemsSolidsWeld), 1):
		ListElemsSolidsWeld[i].set_entity_values(deck_infos, {'PID': NewIdsOnSolidsProps})

##########################################################
def FindElemsAroundArcWeldFunc(ListElemsArcWeld):
	
	ListGroupsShellsAroundArcWeld = []
	
	AllsPropsVisible = base.CollectEntities(deck_infos, None, ['__PROPERTIES__'], filter_visible = True)
	if len(AllsPropsVisible) >0:
		ListPropsVisAroundArc = RemovePropsArcOnListPropsVisVisFunc(AllsPropsVisible, ListElemsArcWeld)
		if len(ListPropsVisAroundArc) >0:
			NodesOnElemsArc = base.CollectEntities(deck_infos, ListElemsArcWeld, ['GRID'])
			for k in range(0, len(ListPropsVisAroundArc), 1):
				ListElemsCommonOnSingleProps = []
				ElemsOnPropsVis = base.CollectEntities(deck_infos, ListPropsVisAroundArc[k], ['__ELEMENTS__'], filter_visible = True)
				for i in range(0, len(ElemsOnPropsVis), 1):
					GridsOfElemsVis = base.CollectEntities(deck_infos, ElemsOnPropsVis[i], ['GRID'])
					ListGridsCommonWithArc = list(set(GridsOfElemsVis).intersection(NodesOnElemsArc))
					if len(ListGridsCommonWithArc) >0:
						ListElemsCommonOnSingleProps.append(ElemsOnPropsVis[i])
			
				if len(ListElemsCommonOnSingleProps) >0:			
					ListGroupsShellsAroundArcWeld.append(ListElemsCommonOnSingleProps)
#					aaa = base.CreateEntity(constants.NASTRAN, "SET")
#					base.AddToSet(aaa, ListElemsCommonOnSingleProps)
	return ListGroupsShellsAroundArcWeld

#######*********************** Loai bo cac PID khong co duoi la 00 **********************######
def RemovePropsArcOnListPropsVisVisFunc(AllsPropsVisible, ListElemsArcWeld):
	
	ListPropsVisAroundArc = []
	for i in range(0, len(AllsPropsVisible), 1):
		if len(str(AllsPropsVisible[i]._id)) == 7 and str(AllsPropsVisible[i]._id).endswith('00'):
			ElemsOnPropVis = base.CollectEntities(deck_infos, AllsPropsVisible[i], ['SHELL', 'SOLID'], filter_visible = True)
			ListCommonShellArc = list(set(ListElemsArcWeld).intersection(ElemsOnPropVis))
			if len(ListCommonShellArc) == 0:
				ListPropsVisAroundArc.append(AllsPropsVisible[i])
			
	return ListPropsVisAroundArc

if __name__ == '__main__':
	main()
DividePropsOfArcWeld_Solid_Tool_0623



# PYTHON script
import os
import ansa
from ansa import *

deck_infos = constants.NASTRAN
def main():
	# Need some documentation? Run this with F5

	for i in range(0, 100, 1):
		base.SetPickMethod(base.constants.PID_REGION_SELECTION)
		ElemsWeldSelect = base.PickEntities(deck_infos, ['SHELL'])
		if ElemsWeldSelect != None:
			PropsOfShells = base.PickEntities(deck_infos, ['__PROPERTIES__'], 'PROPERTY')
			if PropsOfShells != None:
				SetInfosPropsOfWeldSolidShellsFunc(PropsOfShells, ElemsWeldSelect)
				
		else:
			return 1

def SetInfosPropsOfWeldSolidShellsFunc(PropsOfShells, ElemsWeldSelect):
	
	base.Or(ElemsWeldSelect)
	base.Neighb('1')
	
	if len(PropsOfShells) ==1:
		status_active = 'SHELL_Active'
	else:
		status_active = 'SOLID_Active'
	
	props_vis = base.CollectEntities(deck_infos, None, ['__PROPERTIES__'], filter_visible = True)
	if len(props_vis)>0:
		FindPropsAroundArcWeldShellsFunc(props_vis, status_active, ElemsWeldSelect)

def FindPropsAroundArcWeldShellsFunc(props_vis, status_active, ElemsWeldSelect):
	
	ListPropsVisAroundArc = RemovePropsArcOnListPropsVisVisFunc(props_vis, ElemsWeldSelect)
	NodesOnArcWeldSelect = base.CollectEntities(deck_infos, ElemsWeldSelect, ['GRID'])
	
	for i in range(0, len(ListPropsVisAroundArc), 1):
		infos_props = ListPropsVisAroundArc[i].get_entity_values(deck_infos, ['__type__'])
		type_of_props = infos_props['__type__']
		ElemsOnPropsVis = base.CollectEntities(deck_infos, ListPropsVisAroundArc[i], ['__ELEMENTS__'], filter_visible = True)
		if type_of_props == 'PSHELL':
			ListElemsCommonOnSingleProps = FindElemsShellsAroundArcWeldFunc(ElemsOnPropsVis, NodesOnArcWeldSelect)
			if len(ListElemsCommonOnSingleProps) >0:
				StringEndIdsHeatZoneShells = '02'
				NameElemsHeatZoneShells = 'HeatZone'
				StatusHeatZoneColor = False
				SetupInfosPropArcWeldFunc(ListElemsCommonOnSingleProps, ListPropsVisAroundArc[i], StringEndIdsHeatZoneShells, NameElemsHeatZoneShells, StatusHeatZoneColor)
				
		if type_of_props == 'PSOLID':
			if status_active == 'SHELL_Active':
				
			

def FindElemsShellsAroundArcWeldFunc(ElemsOnPropsVis, NodesOnArcWeldSelect):
	
	ListElemsCommonOnSingleProps = []
	for i in range(0, len(ElemsOnPropsVis), 1):
		GridsOfElemsVis = base.CollectEntities(deck_infos, ElemsOnPropsVis[i], ['GRID'])
		ListGridsCommonWithArc = list(set(GridsOfElemsVis).intersection(NodesOnArcWeldSelect))
		if len(ListGridsCommonWithArc) >0:
			ListElemsCommonOnSingleProps.append(ElemsOnPropsVis[i])
	
	return ListElemsCommonOnSingleProps	

#######*********************** Loai bo cac PID khong co duoi la 00 **********************######
def RemovePropsArcOnListPropsVisVisFunc(props_vis, ElemsWeldSelect):
	
	ListPropsVisAroundArc = []
	for i in range(0, len(props_vis), 1):
		if len(str(props_vis[i]._id)) == 7 and str(props_vis[i]._id).endswith('00'):
			ElemsOnPropVis = base.CollectEntities(deck_infos, props_vis[i], ['SHELL'], filter_visible = True)
			ListCommonShellArc = list(set(ElemsWeldSelect).intersection(ElemsOnPropVis))
			if len(ListCommonShellArc) == 0:
				ListPropsVisAroundArc.append(props_vis[i])
			
	return ListPropsVisAroundArc

#######*********************** Thiet dinh thong tin properties cho cac part **********************######
def SetupInfosPropArcWeldFunc(ListInfosElemsWeld, InfosPropsOrigin, StringEndIdsWeld, NamePropsElems, StatusColor):
	
	type_props_origin = InfosPropsOrigin.get_entity_values(deck_infos, ['__type__'])
	if type_props_origin['__type__'] == 'PSHELL': 
		ValsColor = InfosPropsOrigin.get_entity_values(deck_infos, ['COLOR_R', 'COLOR_G', 'COLOR_B', 'MID1'])
		
		InfosMatsOrigin = ValsColor['MID1']
		NameOfMatOrigin = InfosMatsOrigin._name
		MatIdsOnNewProps = int(str(InfosMatsOrigin._id)[0:6]+StringEndIdsWeld)
		MatsReferenIds = base.GetEntity(deck_infos, '__MATERIALS__', int(MatIdsOnNewProps))
		if MatsReferenIds == None:
			NewMatsOnPropsReferen = base.CopyEntity(None, InfosMatsOrigin)
			NewMatsOnPropsReferen.set_entity_values(deck_infos, {'MID': MatIdsOnNewProps, 'Name': NameOfMatOrigin + '_' + NamePropsElems})
	
		NewIdsOnProps = int(str(InfosPropsOrigin._id)[0:5]+StringEndIdsWeld)
		PropsReferenIds = base.GetEntity(deck_infos, 'PSHELL', int(NewIdsOnProps))
		if PropsReferenIds == None:
			NewPropsElems = base.CopyEntity(None, InfosPropsOrigin)
			NewPropsElems.set_entity_values(deck_infos, {'PID': NewIdsOnProps, 'Name': NamePropsElems, 'MID1': MatIdsOnNewProps, 'MID2': MatIdsOnNewProps, 'MID3': MatIdsOnNewProps})
			if StatusColor == True:
				NewPropsElems.set_entity_values(deck_infos, {'COLOR_R': ValsColor['COLOR_R'], 'COLOR_G': ValsColor['COLOR_G'], 'COLOR_B': ValsColor['COLOR_B']})
		else:
			PropsReferenIds.set_entity_values(deck_infos, {'MID1': MatIdsOnNewProps, 'MID2': MatIdsOnNewProps, 'MID3': MatIdsOnNewProps})
			if StatusColor == True:
				PropsReferenIds.set_entity_values(deck_infos, {'COLOR_R': ValsColor['COLOR_R'], 'COLOR_G': ValsColor['COLOR_G'], 'COLOR_B': ValsColor['COLOR_B']})
	
		for i in range(0, len(ListInfosElemsWeld), 1):
			ListInfosElemsWeld[i].set_entity_values(deck_infos, {'PID': NewIdsOnProps})
	
	else:
		vals_props_origin = InfosPropsOrigin.get_entity_values(deck_infos, ['MID'])
		infos_mat_solid_origin = vals_props_origin['MID']
		NameOfMatSolidOrigin = infos_mat_solid_origin._name
		MatIdsOnNewSolidProps = int(str(infos_mat_solid_origin._id)[0:6]+StringEndIdsWeld)
		MatsReferenSolidIds = base.GetEntity(deck_infos, '__MATERIALS__', int(MatIdsOnNewSolidProps))
		if MatsReferenSolidIds == None:
			NewMatsOnPropsSolids = base.CopyEntity(None, infos_mat_solid_origin)
			NewMatsOnPropsSolids.set_entity_values(deck_infos, {'MID': MatIdsOnNewSolidProps, 'Name': NameOfMatSolidOrigin + '_' + NamePropsElems})
		
		NewIdsOnSolidsProps = int(str(InfosPropsOrigin._id)[0:5]+StringEndIdsWeld)
		PropsSolidsReferenIds = base.GetEntity(deck_infos, 'PSOLID', int(NewIdsOnSolidsProps))
		if PropsSolidsReferenIds == None:
			NewPropsSolids = base.CopyEntity(None, InfosPropsOrigin)
			NewPropsSolids.set_entity_values(deck_infos, {'PID': NewIdsOnSolidsProps, 'Name': NamePropsElems, 'MID': MatIdsOnNewSolidProps})
		else:
			PropsSolidsReferenIds.set_entity_values(deck_infos, {'MID': MatIdsOnNewSolidProps})
		
		for i in range(0, len(ListInfosElemsWeld), 1):
			ListInfosElemsWeld[i].set_entity_values(deck_infos, {'PID': NewIdsOnSolidsProps})

if __name__ == '__main__':
	main()
DividePropsOfArcWeld_Solid-Shell_Tool_0930




# PYTHON script
import os
import ansa
from ansa import *
import math

deck_infos = constants.NASTRAN
#@session.defbutton('2-MESH', 'DividePropsOfArcWeldTool','Chia vùng zone Arc theo tiêu chuẩn SSD')
def DividePropsOfArcWeldTool():
	
	TopWindow = guitk.BCWindowCreate("Setup Infos for Welding Props Tool ver01", guitk.constants.BCOnExitDestroy)
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Options: ", guitk.constants.BCHorizontal)
	BCRadioButton_1 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Auto", None, 0)
	BCRadioButton_2 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Manual", None, 0)
	guitk.BCRadioButtonSetChecked(BCRadioButton_2, True)
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_1 = guitk.BCLabelCreate(TopWindow, " ")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	_window = [BCProgressBar_1, BCLabel_1, BCRadioButton_1, BCRadioButton_2]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, _window)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, _window)
	
	guitk.BCShow(TopWindow)

def RejectFunc(TopWindow, _window):
	return 1
	
#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, _window):
	
	ProbarStatus = _window[0]
	LabelStatus = _window[1]
	AutoStatus = guitk.BCRadioButtonIsChecked(_window[2])
	ManualStatus = guitk.BCRadioButtonIsChecked(_window[3])
	if AutoStatus == True:
		AuttoDividePropsOfArcWeldFunc(ProbarStatus, LabelStatus)
	if ManualStatus == True:
		DividePropsOfArcWeldByManualFunc(ProbarStatus, LabelStatus)

#######****************** Chia pid cua arc shell va base sheet bang tay *****************#######
def DividePropsOfArcWeldByManualFunc(ProbarStatus, LabelStatus):
	
	for i in range(0, 100, 1):
		base.SetPickMethod(base.constants.PID_REGION_SELECTION)
		ElemsWeldSelect = base.PickEntities(deck_infos, ['SHELL'])
		if ElemsWeldSelect != None:
			PropsOfArcWeld = base.PickEntities(deck_infos, ['__PROPERTIES__'], 'PROPERTY')
			if PropsOfArcWeld != None:
				if len(PropsOfArcWeld) ==1:
					PropsOfWeldReq = PropsOfArcWeld[0]
				else:
					ListThicknessPropsReq = []
					for w in range(0, len(PropsOfArcWeld), 1):
						ValsThickness = PropsOfArcWeld[w].get_entity_values(deck_infos, ['T'])
						ListThicknessPropsReq.append(ValsThickness['T'])
					IndexMinThicknessProps = ListThicknessPropsReq.index(min(ListThicknessPropsReq))
					PropsOfWeldReq = PropsOfArcWeld[IndexMinThicknessProps]
					
				StringEndIdsElemsWeld = '09'
				StatusAddColor = True
				NameElemsWeld = 'ArcWeld'
				SetupInfosPropArcWeldFunc(ElemsWeldSelect, PropsOfWeldReq, StringEndIdsElemsWeld, NameElemsWeld, StatusAddColor)
				
				base.Or(ElemsWeldSelect)
				base.Neighb('1')
				ListShellAroundElemsWeld = FindElemsAroundArcWeldFunc(ElemsWeldSelect)
				for k in range(0, len(ListShellAroundElemsWeld), 1):
					PidsElemsAroundWeldOrigin = ListShellAroundElemsWeld[k][0].get_entity_values(deck_infos, ['PID'])
					PropsElemsAroundWeldOrigin = PidsElemsAroundWeldOrigin['PID']
					StringEndIdsElemsAroundWeld = '02'
					NameElemsAroundWeld = 'HeatZone'
					StatusAddColor = False
					SetupInfosPropArcWeldFunc(ListShellAroundElemsWeld[k], PropsElemsAroundWeldOrigin, StringEndIdsElemsAroundWeld, NameElemsAroundWeld, StatusAddColor)
				
		else:
			return 1

#######****************** Chia pid cua arc shell va base sheet auto *****************#######
def AuttoDividePropsOfArcWeldFunc(ProbarStatus, LabelStatus):
	
	ArcWeldElems = base.PickEntities(deck_infos, ['SHELL'])
	if ArcWeldElems != None:
		base.Or(ArcWeldElems)
		base.Neighb('1')
		ListInfosGroupWeldIsolate = DivideGroupsShellsArcFunc(ArcWeldElems)
		if len(ListInfosGroupWeldIsolate) >0:
			DividePropsOfArcWeldOnRuleFunc(ListInfosGroupWeldIsolate, ProbarStatus, LabelStatus)
	
#######****************** Chia pid cua arc shell va base sheet theo rule *****************#######
def DividePropsOfArcWeldOnRuleFunc(ListInfosGroupWeldIsolate, ProbarStatus, LabelStatus):
	
	guitk.BCProgressBarSetTotalSteps(ProbarStatus, len(ListInfosGroupWeldIsolate))
	for i in range(0, len(ListInfosGroupWeldIsolate), 1):
		guitk.BCLabelSetText(LabelStatus, 'Loading Group ArcWeld ' + str(i+1)+'/'+str(len(ListInfosGroupWeldIsolate)))
		base.Or(ListInfosGroupWeldIsolate[i])
		base.Neighb('1')
		ListGroupsShellsAroundArcWeld = FindElemsAroundArcWeldFunc(ListInfosGroupWeldIsolate[i])
		if len(ListGroupsShellsAroundArcWeld) >0:
			if len(ListGroupsShellsAroundArcWeld) == 2:
				type_elem_req = CheckTypeOfElemsFunc(ListGroupsShellsAroundArcWeld)
				if type_elem_req == True:
					StatusBreak = True
					ListShellsOnBaseSideReq, ListShellsOnSheetSideReq, TypeAngleReq, StatusCheckResult = FindBaseSheetSideAroundArcWeldFunc(ListGroupsShellsAroundArcWeld, ListInfosGroupWeldIsolate[i], StatusBreak)
					if StatusCheckResult == True or TypeAngleReq == 'Check':
						RelativeOnArcWeldErrorFunc(ListInfosGroupWeldIsolate[i])
#				print(len(ListShellsOnBaseSideReq), len(ListShellsOnSheetSideReq), TypeAngleReq)
					if len(ListShellsOnBaseSideReq)>0 and len(ListShellsOnSheetSideReq) >0 and TypeAngleReq != 'Check':
						SetupInfosOfArcWeldOnRuleFunc(ListShellsOnBaseSideReq, ListShellsOnSheetSideReq, ListInfosGroupWeldIsolate[i], TypeAngleReq)
				
				else:
					RelativeOnArcWeldErrorFunc(ListInfosGroupWeldIsolate[i])
			else:
				RelativeOnArcWeldErrorFunc(ListInfosGroupWeldIsolate[i])
		
		guitk.BCProgressBarSetProgress(ProbarStatus, i+1)


def CheckTypeOfElemsFunc(ListGroupsShellsAroundArcWeld):
	
	type_elem_req = True
	for i in range(0, len(ListGroupsShellsAroundArcWeld), 1):
		type_shells = ListGroupsShellsAroundArcWeld[i][0].get_entity_values(deck_infos, ['__type__'])
		if type_shells['__type__'] == 'SOLID':
			type_elem_req = False
	
	return type_elem_req
	
def RelativeOnArcWeldErrorFunc(InfosShellsOfArcWeldError):
	
	PartsPointError = base.GetPartFromModuleId('Point Error')
	if PartsPointError == None:
		PartsPointError = base.NewPart('Point Error', 'Point Error')
		
	NodesOnShellsError = base.CollectEntities(deck_infos, InfosShellsOfArcWeldError, ['GRID'])
	for i in range(0, len(NodesOnShellsError), 1):
		AxisOfNodes = NodesOnShellsError[i].position
		ElemsPointError = base.Newpoint(AxisOfNodes[0], AxisOfNodes[1], AxisOfNodes[2])
		base.SetEntityPart(ElemsPointError, PartsPointError)
	
def SetupInfosOfArcWeldOnRuleFunc(ListShellsOnBaseSideReq, ListShellsOnSheetSideReq, ListShellsOnArcWeld, TypeAngleReq):

	PidsBaseSideOrigin = ListShellsOnBaseSideReq[0].get_entity_values(deck_infos, ['PID'])
	PidsSheetSideOrigin = ListShellsOnSheetSideReq[0].get_entity_values(deck_infos, ['PID'])
#	print(PidsBaseSideOrigin)
	
	PropsBaseSideOrigin = PidsBaseSideOrigin['PID']
	PropsSheetSideOrigin = PidsSheetSideOrigin['PID']
	
	ThicknessOfBaseSideOrigin = PropsBaseSideOrigin.get_entity_values(deck_infos, ['T'])
	ThicknessOfSheetSideOrigin = PropsSheetSideOrigin.get_entity_values(deck_infos, ['T'])
	
	if TypeAngleReq == 'SONGSONG':
		PropsArcWeldOrigin = PropsSheetSideOrigin
	if TypeAngleReq == 'VUONGGOC':
#		print(ThicknessOfBaseSideOrigin['T'], ThicknessOfSheetSideOrigin['T'])
		if ThicknessOfBaseSideOrigin['T'] >ThicknessOfSheetSideOrigin['T']:
			PropsArcWeldOrigin = PropsSheetSideOrigin
		elif ThicknessOfBaseSideOrigin['T'] < ThicknessOfSheetSideOrigin['T']:
			PropsArcWeldOrigin = PropsBaseSideOrigin
		else:
			PropsArcWeldOrigin = PropsSheetSideOrigin
	
	if len(ListShellsOnBaseSideReq) >0:
		StringEndIdsBaseSide = '02'
		NameBaseSide = 'HeatZone'
		StatusColor = False
		SetupInfosPropArcWeldFunc(ListShellsOnBaseSideReq, PropsBaseSideOrigin, StringEndIdsBaseSide, NameBaseSide, StatusColor)
	if len(ListShellsOnSheetSideReq) >0:
		StringEndIdsSheetSide = '02'
		NameSheetSide = 'HeatZone'
		StatusColor = False
		SetupInfosPropArcWeldFunc(ListShellsOnSheetSideReq, PropsSheetSideOrigin, StringEndIdsSheetSide, NameSheetSide, StatusColor)
	if len(ListShellsOnArcWeld) >0:
		StringEndIdsArcWeld = '09'
		NameArcWeld = 'ArcWeld'
		StatusColor = True
		SetupInfosPropArcWeldFunc(ListShellsOnArcWeld, PropsArcWeldOrigin, StringEndIdsArcWeld, NameArcWeld, StatusColor)

#######*********************** Thiet dinh thong tin properties cho cac part **********************######
def SetupInfosPropArcWeldFunc(ListInfosElemsWeld, InfosPropsOrigin, StringEndIdsWeld, NamePropsElems, StatusColor):
	
	type_props_origin = InfosPropsOrigin.get_entity_values(deck_infos, ['__type__'])
	if type_props_origin['__type__'] == 'PSHELL': 
		ValsColor = InfosPropsOrigin.get_entity_values(deck_infos, ['COLOR_R', 'COLOR_G', 'COLOR_B', 'MID1'])
		
		InfosMatsOrigin = ValsColor['MID1']
		NameOfMatOrigin = InfosMatsOrigin._name
		MatIdsOnNewProps = int(str(InfosMatsOrigin._id)[0:6]+StringEndIdsWeld)
		MatsReferenIds = base.GetEntity(deck_infos, '__MATERIALS__', int(MatIdsOnNewProps))
		if MatsReferenIds == None:
			NewMatsOnPropsReferen = base.CopyEntity(None, InfosMatsOrigin)
			NewMatsOnPropsReferen.set_entity_values(deck_infos, {'MID': MatIdsOnNewProps, 'Name': NameOfMatOrigin + '_' + NamePropsElems})
	
		NewIdsOnProps = int(str(InfosPropsOrigin._id)[0:5]+StringEndIdsWeld)
		PropsReferenIds = base.GetEntity(deck_infos, 'PSHELL', int(NewIdsOnProps))
		if PropsReferenIds == None:
			NewPropsElems = base.CopyEntity(None, InfosPropsOrigin)
			NewPropsElems.set_entity_values(deck_infos, {'PID': NewIdsOnProps, 'Name': NamePropsElems, 'MID1': MatIdsOnNewProps, 'MID2': MatIdsOnNewProps, 'MID3': MatIdsOnNewProps})
			if StatusColor == True:
				NewPropsElems.set_entity_values(deck_infos, {'COLOR_R': ValsColor['COLOR_R'], 'COLOR_G': ValsColor['COLOR_G'], 'COLOR_B': ValsColor['COLOR_B']})
		else:
			PropsReferenIds.set_entity_values(deck_infos, {'MID1': MatIdsOnNewProps, 'MID2': MatIdsOnNewProps, 'MID3': MatIdsOnNewProps})
			if StatusColor == True:
				PropsReferenIds.set_entity_values(deck_infos, {'COLOR_R': ValsColor['COLOR_R'], 'COLOR_G': ValsColor['COLOR_G'], 'COLOR_B': ValsColor['COLOR_B']})
	
		for i in range(0, len(ListInfosElemsWeld), 1):
			ListInfosElemsWeld[i].set_entity_values(deck_infos, {'PID': NewIdsOnProps})
	
	else:
		vals_props_origin = InfosPropsOrigin.get_entity_values(deck_infos, ['MID'])
		infos_mat_solid_origin = vals_props_origin['MID']
		NameOfMatSolidOrigin = infos_mat_solid_origin._name
		MatIdsOnNewSolidProps = int(str(infos_mat_solid_origin._id)[0:6]+StringEndIdsWeld)
		MatsReferenSolidIds = base.GetEntity(deck_infos, '__MATERIALS__', int(MatIdsOnNewSolidProps))
		if MatsReferenSolidIds == None:
			NewMatsOnPropsSolids = base.CopyEntity(None, infos_mat_solid_origin)
			NewMatsOnPropsSolids.set_entity_values(deck_infos, {'MID': MatIdsOnNewSolidProps, 'Name': NameOfMatSolidOrigin + '_' + NamePropsElems})
		
		NewIdsOnSolidsProps = int(str(InfosPropsOrigin._id)[0:5]+StringEndIdsWeld)
		PropsSolidsReferenIds = base.GetEntity(deck_infos, 'PSOLID', int(NewIdsOnSolidsProps))
		if PropsSolidsReferenIds == None:
			NewPropsSolids = base.CopyEntity(None, InfosPropsOrigin)
			NewPropsSolids.set_entity_values(deck_infos, {'PID': NewIdsOnSolidsProps, 'Name': NamePropsElems, 'MID': MatIdsOnNewSolidProps})
		else:
			PropsSolidsReferenIds.set_entity_values(deck_infos, {'MID': MatIdsOnNewSolidProps})
		
		for i in range(0, len(ListInfosElemsWeld), 1):
			ListInfosElemsWeld[i].set_entity_values(deck_infos, {'PID': NewIdsOnSolidsProps})
	
#######*********************** Tim kiem Base side va Sheet side xung quanh arc weld **********************######
def FindBaseSheetSideAroundArcWeldFunc(ListGroupsShellsAroundArcWeld, ListInfosArcWeldConnect, StatusBreak):
	
	TypeAngleReq = None
	ListShellsOnBaseSideReq = []
	ListShellsOnSheetSideReq = []
	
	for i in range(0, len(ListInfosArcWeldConnect), 1):
#		print(ListInfosArcWeldConnect[i]._id)
		ListGroupsShellsCalculateAngle = []
		ValsShellOfArcWelds = ListInfosArcWeldConnect[i].get_entity_values(deck_infos, {'type'})
		if ValsShellOfArcWelds['type'] == 'CQUAD4':
			NodesOnShellArc = base.CollectEntities(deck_infos, ListInfosArcWeldConnect[i], ['GRID'])
#			print(len(NodesOnShellArc))
			for SingleGroupShellAround in ListGroupsShellsAroundArcWeld:
				ListShellsCheckAngle = []
				for k in range(0, len(SingleGroupShellAround), 1):
					NodesOnShellAroundArc = base.CollectEntities(deck_infos, SingleGroupShellAround[k], ['GRID'])
					ListNodesCommonCheck = list(set(NodesOnShellArc).intersection(NodesOnShellAroundArc))
					if len(ListNodesCommonCheck) >= 2:
						ListShellsCheckAngle.append(SingleGroupShellAround[k])
#						print(SingleGroupShellAround[k]._id)
				if len(ListShellsCheckAngle) >0:
					ListGroupsShellsCalculateAngle.append(ListShellsCheckAngle)
		
		if len(ListGroupsShellsCalculateAngle) >0:
#			print(ListGroupsShellsCalculateAngle)
			ListGroupElemsBaseSide, ListGroupElemsSheetSide, StatusAngleCheck, StatusCheckResult = CheckAngleTwoGroupsShellsFunc(ListGroupsShellsCalculateAngle)
			if StatusAngleCheck != None:
				if StatusBreak == True:
					TypeAngleReq = StatusAngleCheck
					for w in range(0, len(ListGroupsShellsAroundArcWeld), 1):
						ListCommonShellsZoneBaseSide = set(ListGroupsShellsAroundArcWeld[w]).intersection(ListGroupElemsBaseSide)
						ListCommonShellsZoneSheetSide = set(ListGroupsShellsAroundArcWeld[w]).intersection(ListGroupElemsSheetSide)
						if len(ListCommonShellsZoneBaseSide)>0:
							ListShellsOnBaseSideReq = ListGroupsShellsAroundArcWeld[w]
						if len(ListCommonShellsZoneSheetSide)>0:
							ListShellsOnSheetSideReq = ListGroupsShellsAroundArcWeld[w]
					break
					
	return ListShellsOnBaseSideReq, ListShellsOnSheetSideReq, TypeAngleReq, StatusCheckResult
	
#######*********************** Check goc giua base side va sheet side **********************######
def CheckAngleTwoGroupsShellsFunc(ListGroupsShellsCalculateAngle):
	
	ListGroupElemsBaseSide = []
	ListGroupElemsSheetSide = []
	StatusAngleCheck = None
	StatusCheckResult = None
	if len(ListGroupsShellsCalculateAngle)>1:
		if len(ListGroupsShellsCalculateAngle[0]) > len(ListGroupsShellsCalculateAngle[1]):
			ListGroupElemsBaseSide = ListGroupsShellsCalculateAngle[0]
			ListGroupElemsSheetSide = ListGroupsShellsCalculateAngle[1]
		elif len(ListGroupsShellsCalculateAngle[0]) < len(ListGroupsShellsCalculateAngle[1]):
			ListGroupElemsBaseSide = ListGroupsShellsCalculateAngle[1]
			ListGroupElemsSheetSide = ListGroupsShellsCalculateAngle[0]
		else:
			ListGroupElemsBaseSide = ListGroupsShellsCalculateAngle[0]
			ListGroupElemsSheetSide = ListGroupsShellsCalculateAngle[1]
			StatusCheckResult = True
	else:
		StatusAngleCheck = 'Check'		
	
	if len(ListGroupElemsBaseSide) >0 and len(ListGroupElemsSheetSide) >0:
		ListAngleSheetToBaseSideCheck = []
		for i in range(0, len(ListGroupElemsSheetSide), 1):
			VecsOfShellsSheetSide = base.GetNormalVectorOfShell(ListGroupElemsSheetSide[i])
			for k in range(0, len(ListGroupElemsBaseSide), 1):
				VecsOfShellsBaseSide = base.GetNormalVectorOfShell(ListGroupElemsBaseSide[k])
				Angle2ShellsSheetToBaseSide = math.degrees(calc.CalcAngleOfVectors(VecsOfShellsSheetSide, VecsOfShellsBaseSide))
				ListAngleSheetToBaseSideCheck.append(Angle2ShellsSheetToBaseSide)
		
		if len(ListAngleSheetToBaseSideCheck)>0:
#			print(ListAngleSheetToBaseSideCheck)
			if min(ListAngleSheetToBaseSideCheck)<= 5 or max(ListAngleSheetToBaseSideCheck) >=175:
				StatusAngleCheck = 'SONGSONG'
			elif 80<= min(ListAngleSheetToBaseSideCheck)<=100 or 80<= max(ListAngleSheetToBaseSideCheck)<=100:
				StatusAngleCheck = 'VUONGGOC'
			else:
				StatusAngleCheck = 'Check'
	
	return ListGroupElemsBaseSide, ListGroupElemsSheetSide, StatusAngleCheck, StatusCheckResult

#######*********************** Tim vung zone xung quanh arc **********************######
def FindElemsAroundArcWeldFunc(ListElemsArcWeld):
	
	ListGroupsShellsAroundArcWeld = []
	
	AllsPropsVisible = base.CollectEntities(deck_infos, None, ['PSHELL', 'PSOLID'], filter_visible = True)
	if len(AllsPropsVisible) >0:
		ListPropsVisAroundArc = RemovePropsArcOnListPropsVisVisFunc(AllsPropsVisible, ListElemsArcWeld)
		if len(ListPropsVisAroundArc) >0:
			NodesOnElemsArc = base.CollectEntities(deck_infos, ListElemsArcWeld, ['GRID'])
			for k in range(0, len(ListPropsVisAroundArc), 1):
				ListElemsCommonOnSingleProps = []
				ElemsOnPropsVis = base.CollectEntities(deck_infos, ListPropsVisAroundArc[k], ['__ELEMENTS__'], filter_visible = True)
				for i in range(0, len(ElemsOnPropsVis), 1):
					GridsOfElemsVis = base.CollectEntities(deck_infos, ElemsOnPropsVis[i], ['GRID'])
					ListGridsCommonWithArc = list(set(GridsOfElemsVis).intersection(NodesOnElemsArc))
					if len(ListGridsCommonWithArc) >0:
						ListElemsCommonOnSingleProps.append(ElemsOnPropsVis[i])
			
				if len(ListElemsCommonOnSingleProps) >0:			
					ListGroupsShellsAroundArcWeld.append(ListElemsCommonOnSingleProps)
#					aaa = base.CreateEntity(constants.NASTRAN, "SET")
#					base.AddToSet(aaa, ListElemsCommonOnSingleProps)
	return ListGroupsShellsAroundArcWeld

#######*********************** Loai bo cac PID khong co duoi la 00 **********************######
def RemovePropsArcOnListPropsVisVisFunc(AllsPropsVisible, ListElemsArcWeld):
	
	ListPropsVisAroundArc = []
	for i in range(0, len(AllsPropsVisible), 1):
		if len(str(AllsPropsVisible[i]._id)) == 7 and str(AllsPropsVisible[i]._id).endswith('00'):
			ElemsOnPropVis = base.CollectEntities(deck_infos, AllsPropsVisible[i], ['SHELL'], filter_visible = True)
			ListCommonShellArc = list(set(ListElemsArcWeld).intersection(ElemsOnPropVis))
			if len(ListCommonShellArc) == 0:
				ListPropsVisAroundArc.append(AllsPropsVisible[i])
			
	return ListPropsVisAroundArc

#######****************** Chia group shell arc weld *****************#######
def DivideGroupsShellsArcFunc(InfosElemsIsolate):
	
	ListInfosGroupWeldIsolate = []
	AllsElemsVisConnect = base.CollectEntities(deck_infos, None, ['SHELL'], filter_visible = True)
	if len(AllsElemsVisConnect) >0:
		DictIsolateElemsVis = base.IsolateConnectivityGroups(entities = AllsElemsVisConnect, separate_at_blue_bounds = True, separate_at_pid_bounds = True, feature_angle = 90)
		if DictIsolateElemsVis != None:
			for GroupsNameIsolate,  InfosEntityIsolate in DictIsolateElemsVis.items():
				ListGroupsShellsCommon = list(set(InfosEntityIsolate).intersection(InfosElemsIsolate))
				if len(ListGroupsShellsCommon) >0:
					ListInfosGroupWeldIsolate.append(ListGroupsShellsCommon)
#					a = base.CreateEntity(constants.NASTRAN, "SET")
#					base.AddToSet(a, ListGroupsShellsCommon)
	return ListInfosGroupWeldIsolate
	
DividePropsOfArcWeldTool()
DividePropsOfArcWeldTool_0728_1000



# PYTHON script
import os
import ansa
from ansa import *
import math

deck_infos = constants.NASTRAN
#@session.defbutton('2-MESH', 'DividePropsOfArcWeldTool','Chia vùng zone Arc theo tiêu chuẩn SSD')
def DividePropsOfArcWeldTool():
	
	TopWindow = guitk.BCWindowCreate("Setup Infos for Welding Props Tool ver01", guitk.constants.BCOnExitDestroy)
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Options: ", guitk.constants.BCHorizontal)
	BCRadioButton_1 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Auto", None, 0)
	BCRadioButton_2 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Manual", None, 0)
	guitk.BCRadioButtonSetChecked(BCRadioButton_2, True)
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_1 = guitk.BCLabelCreate(TopWindow, " ")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	_window = [BCProgressBar_1, BCLabel_1, BCRadioButton_1, BCRadioButton_2]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, _window)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, _window)
	
	guitk.BCShow(TopWindow)

def RejectFunc(TopWindow, _window):
	return 1
	
#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, _window):
	
	ProbarStatus = _window[0]
	LabelStatus = _window[1]
	AutoStatus = guitk.BCRadioButtonIsChecked(_window[2])
	ManualStatus = guitk.BCRadioButtonIsChecked(_window[3])
	if AutoStatus == True:
		AuttoDividePropsOfArcWeldFunc(ProbarStatus, LabelStatus)
	if ManualStatus == True:
		DividePropsOfArcWeldByManualFunc(ProbarStatus, LabelStatus)

#######****************** Chia pid cua arc shell va base sheet bang tay *****************#######
def DividePropsOfArcWeldByManualFunc(ProbarStatus, LabelStatus):
	
	for i in range(0, 100, 1):
		base.SetPickMethod(base.constants.PID_REGION_SELECTION)
		ElemsWeldSelect = base.PickEntities(deck_infos, ['SHELL'])
		if ElemsWeldSelect != None:
			PropsOfArcWeld = base.PickEntities(deck_infos, ['PSHELL'])
			if PropsOfArcWeld != None:
				SetInfosPropsOfArcWeldFunc(PropsOfArcWeld, ElemsWeldSelect)
				
		else:
			return 1

#######****************** Chia pid cua arc shell va base sheet auto *****************#######
def AuttoDividePropsOfArcWeldFunc(ProbarStatus, LabelStatus):
	
	ArcWeldElems = base.PickEntities(deck_infos, ['SHELL'])
	if ArcWeldElems != None:
		base.Or(ArcWeldElems)
		base.Neighb('1')
		ListInfosGroupWeldIsolate = DivideGroupsShellsArcFunc(ArcWeldElems)
		if len(ListInfosGroupWeldIsolate) >0:
#			print(len(ListInfosGroupWeldIsolate))
			DividePropsOfArcWeldOnRuleFunc(ListInfosGroupWeldIsolate, ProbarStatus, LabelStatus)
	
#######****************** Chia pid cua arc shell va base sheet theo rule *****************#######
def DividePropsOfArcWeldOnRuleFunc(ListInfosGroupWeldIsolate, ProbarStatus, LabelStatus):
	
	guitk.BCProgressBarSetTotalSteps(ProbarStatus, len(ListInfosGroupWeldIsolate))
	for i in range(0, len(ListInfosGroupWeldIsolate), 1):
		print('Loading Step: ' + str(i+1) + '/' + str(len(ListInfosGroupWeldIsolate)))
		guitk.BCLabelSetText(LabelStatus, 'Loading Group ArcWeld ' + str(i+1)+'/'+str(len(ListInfosGroupWeldIsolate)))
		base.Or(ListInfosGroupWeldIsolate[i])
		base.Neighb('1')
		ListGroupsShellsAroundArcWeld = FindElemsAroundArcWeldFunc(ListInfosGroupWeldIsolate[i])
		
		guitk.BCProgressBarSetProgress(ProbarStatus, i+1)

#######*********************** Tim vung zone xung quanh arc **********************######
def FindElemsAroundArcWeldFunc(ListElemsArcWeld):
	
	AllsPropsVisible = base.CollectEntities(deck_infos, None, ['PSHELL'], filter_visible = True)
	if len(AllsPropsVisible) >0:
		ListPropsVisAroundArc = RemovePropsArcOnListPropsVisVisFunc(AllsPropsVisible, ListElemsArcWeld)
		if len(ListPropsVisAroundArc) >0:
			for i in range(0, len(ListElemsArcWeld), 1):
				NodesOnElemsArc = base.CollectEntities(deck_infos, ListElemsArcWeld[i], ['GRID'])
				ListPropsOnArcWeld = []
				for k in range(0, len(ListPropsVisAroundArc), 1):
					ElemsOnPropsVis = base.CollectEntities(deck_infos, ListPropsVisAroundArc[k], ['SHELL'], filter_visible = True)
					GridsOfElemsVis = base.CollectEntities(deck_infos, ElemsOnPropsVis, ['GRID'])
					ListGridsCommonWithArc = list(set(GridsOfElemsVis).intersection(NodesOnElemsArc))
					if len(ListGridsCommonWithArc) >0:
						ListPropsOnArcWeld.append(ListPropsVisAroundArc[k]) 
				
				if len(ListPropsOnArcWeld) >0:
					SetInfosPropsOfArcWeldFunc(ListPropsOnArcWeld, [ListElemsArcWeld[i]])
					
	
def SetInfosPropsOfArcWeldFunc(ListPropsOnArcWeld, InfosElemsWeld):
	
	ListThicknessOnProps = []
	ThicknessOfWeld = None
#	MinThicknessWeld = None
	
	for i in range(0, len(ListPropsOnArcWeld), 1):
		ValsPropsOnWeld = ListPropsOnArcWeld[i].get_entity_values(deck_infos, ['T'])
		ListThicknessOnProps.append(ValsPropsOnWeld['T'])
	
	if len(ListThicknessOnProps) >0:
		if len(ListThicknessOnProps) <3:
			ThicknessOfWeld = sum(ListThicknessOnProps)/len(ListThicknessOnProps)
			MinThicknessWeld = min(ListThicknessOnProps)
		else:
			ListThicknessRemoveDouble = list(set(ListThicknessOnProps))
			if len(ListThicknessRemoveDouble) == 1:
				ThicknessOfWeld = sum(ListThicknessRemoveDouble)/len(ListThicknessRemoveDouble)
##				MinThicknessWeld = min(ListThicknessRemoveDouble)	
			
	if ThicknessOfWeld != None:
		IdsOdPropsWeld = int(str(9000)+str(ThicknessOfWeld).replace('.',''))
		PropsReferenIds = base.GetEntity(deck_infos, 'PSHELL', int(IdsOdPropsWeld))
		if PropsReferenIds == None:
			NewPropsElems = base.CreateEntity(deck_infos, 'PSHELL', {'PID': IdsOdPropsWeld, 'Name': 'ArcWeld_Thickness_' + str(ThicknessOfWeld), 'T': ThicknessOfWeld})
		
		for w in range(0, len(InfosElemsWeld), 1):	
			InfosElemsWeld[w].set_entity_values(deck_infos, {'PID': IdsOdPropsWeld})	

#######*********************** Loai bo cac PID khong co duoi la 00 **********************######
def RemovePropsArcOnListPropsVisVisFunc(AllsPropsVisible, ListElemsArcWeld):
	
	ListPropsVisAroundArc = []
	for i in range(0, len(AllsPropsVisible), 1):
		if len(str(AllsPropsVisible[i]._id)) == 7 and str(AllsPropsVisible[i]._id).endswith('00'):
			ElemsOnPropVis = base.CollectEntities(deck_infos, AllsPropsVisible[i], ['SHELL'], filter_visible = True)
			ListCommonShellArc = list(set(ListElemsArcWeld).intersection(ElemsOnPropVis))
			if len(ListCommonShellArc) == 0:
				ListPropsVisAroundArc.append(AllsPropsVisible[i])
			
	return ListPropsVisAroundArc

#######****************** Chia group shell arc weld *****************#######
def DivideGroupsShellsArcFunc(InfosElemsIsolate):
	
	ListInfosGroupWeldIsolate = []
	AllsElemsVisConnect = base.CollectEntities(deck_infos, None, ['SHELL'], filter_visible = True)
	if len(AllsElemsVisConnect) >0:
		DictIsolateElemsVis = base.IsolateConnectivityGroups(entities = AllsElemsVisConnect, separate_at_blue_bounds = True, separate_at_pid_bounds = True, feature_angle = 90)
		if DictIsolateElemsVis != None:
			for GroupsNameIsolate,  InfosEntityIsolate in DictIsolateElemsVis.items():
				ListGroupsShellsCommon = list(set(InfosEntityIsolate).intersection(InfosElemsIsolate))
				if len(ListGroupsShellsCommon) >0:
					ListInfosGroupWeldIsolate.append(ListGroupsShellsCommon)
#					a = base.CreateEntity(constants.NASTRAN, "SET")
#					base.AddToSet(a, ListGroupsShellsCommon)
	return ListInfosGroupWeldIsolate
	
DividePropsOfArcWeldTool()
DivideThicknessOfArcWeldTool_0611

D:\Kyty180389\Script\23.DividePropsOfArcWeld





# PYTHON script
import os
import ansa
from ansa import *

deck_infos = constants.NASTRAN
@session.defbutton('6_CONNECTION', 'ChangeConnectionNVHToAbaqusTool','Convert liên kết dạng RBE2-BEAM-RBE2 sang RBE2 ....')
def ChangeConnectionNVHToAbaqusTool():
	# Need some documentation? Run this with F5
	BeamsSelected = base.PickEntities(deck_infos, ['CBEAM'])
	if BeamsSelected != None:
#		print(len(BeamsSelected))
		dict_infos_beams = base.IsolateConnectivityGroups	(entities = BeamsSelected, separate_at_blue_bounds = True, separate_at_pid_bounds = True)
		if dict_infos_beams != None:
			base.Or(BeamsSelected)
			base.Neighb('1')
			AllRbe2Visible = base.CollectEntities(deck_infos, None, ['RBE2'], filter_visible = True)
			if len(AllRbe2Visible) >0:
				EntityClear = []
				for infos_group_name, infos_group_beam in dict_infos_beams.items():
					ListNodesRbe2ReferenElemsBeams, ListEntityElemsNeedClear = FindRbe2ReferenElementBeamFunc(infos_group_beam, AllRbe2Visible)
					if len(ListNodesRbe2ReferenElemsBeams) >0:
						CreateEntityRbe2ForAbaqusStandardFunc(ListNodesRbe2ReferenElemsBeams)
						EntityClear.extend(ListEntityElemsNeedClear)
				
				if len(EntityClear) >0:
					base.DeleteEntity(EntityClear, True)
		
		guitk.UserError('Done........')

def CreateEntityRbe2ForAbaqusStandardFunc(ListEntityNodesRbe2):
	
	NumOfNodesRbe2 = len(ListEntityNodesRbe2) + 1
	
	InfosIdsNodesRbe2 = []
	InfosAxisNodesX = []
	InfosAxisNodesY = []
	InfosAxisNodesZ = []
	
	for i in range(0, len(ListEntityNodesRbe2), 1):
		InfosIdsNodesRbe2.append(ListEntityNodesRbe2[i]._id)
		AxisNodesRbe2 = ListEntityNodesRbe2[i].position
		InfosAxisNodesX.append(AxisNodesRbe2[0])
		InfosAxisNodesY.append(AxisNodesRbe2[1])
		InfosAxisNodesZ.append(AxisNodesRbe2[2])
	
	AxisCOGRbe2_X = sum(InfosAxisNodesX)/len(InfosAxisNodesX)
	AxisCOGRbe2_Y = sum(InfosAxisNodesY)/len(InfosAxisNodesY)
	AxisCOGRbe2_Z = sum(InfosAxisNodesZ)/len(InfosAxisNodesZ)
	
	NodesCOGRbe2 = base.CreateEntity(deck_infos, 'GRID', {'X1': AxisCOGRbe2_X, 'X2': AxisCOGRbe2_Y, 'X3': AxisCOGRbe2_Z})
	
	Rbe2ForAbaqus = base.CreateEntity(deck_infos, 'RBE2', {'GN': NodesCOGRbe2._id, 'CM': 123456, 'No.of.Nodes': 3, 'GM1': InfosIdsNodesRbe2[0],  'GM2': InfosIdsNodesRbe2[1]})	
	if Rbe2ForAbaqus != None:
#		InfosIdsNodesRbe2.remove(InfosIdsNodesRbe2[0])
#		InfosIdsNodesRbe2.remove(InfosIdsNodesRbe2[1])
		base.BranchEntity(Rbe2ForAbaqus, InfosIdsNodesRbe2, 'add')
		base.ResetSpiderCog(Rbe2ForAbaqus, 'cog')
					
def FindRbe2ReferenElementBeamFunc(ElementBeams, ListElemsRbe2Vis):
	
	ListNodesRbe2ReferenElemsBeams = []
	ListEntityElemsNeedClear = []
	ListEntityElemsNeedClear.extend(ElementBeams)
	
	NodesOfElemsBeam = base.CollectEntities(deck_infos, ElementBeams, ['GRID'])
	for i in range(0, len(ListElemsRbe2Vis), 1):
		NodesOnElemsRbe2 = base.CollectEntities(deck_infos, ListElemsRbe2Vis[i], ['GRID'])
		ValsElemsRbe2 = ListElemsRbe2Vis[i].get_entity_values(deck_infos, ['GN'])
		infos_COG_rbe2 = ValsElemsRbe2['GN']

		StatusSearchCOGRbe2 = FindEntityInListElementsFunc(infos_COG_rbe2, NodesOfElemsBeam)
		if StatusSearchCOGRbe2 != None:
			NodesOnElemsRbe2.remove(infos_COG_rbe2)
#			print(NodesOnElemsRbe2)
			ListNodesRbe2ReferenElemsBeams.extend(NodesOnElemsRbe2)
			ListEntityElemsNeedClear.append(ListElemsRbe2Vis[i])
	
	return ListNodesRbe2ReferenElemsBeams, ListEntityElemsNeedClear

def FindEntityInListElementsFunc(EntityElement, ListElements):
	
	try:
		Pos = ListElements.index(EntityElement)
	except:
		Pos = None
	else:
		Pos = Pos
	
	return Pos	
	
#ChangeConnectionNVHToAbaqusTool()
ChangeConnectionNVHToAbaqusTool_0523

D:\Kyty180389\Script\25.ChangeConnectionNVHToAbaqus



# PYTHON script
import os
import ansa
from ansa import *

#@session.defbutton('4_MATERIAL', 'ConvertMatOfNVHToAbaqusTool',' Chuyển vật liệu từ môi trường Nastran sang Abaqus....')
def ConvertMatOfNVHToAbaqusTool():
	# Need some documentation? Run this with F5
	AllPropsModel = base.CollectEntities(constants.NASTRAN, None, ['PSHELL', 'PSOLID'], filter_visible = True)
	if len(AllPropsModel) >0:
		for i in range(0, len(AllPropsModel), 1):
			mats_reference_props_nvh = GetInfosMatOnPropsFunc(AllPropsModel[i])
			
			if mats_reference_props_nvh != None:
				ChangeTypeMatsToAbaqusFunc(mats_reference_props_nvh, AllPropsModel[i])
	
	guitk.UserError('Done....')			

def ChangeTypeMatsToAbaqusFunc(mats_reference_props_nvh, EntityPropsChange):
	
	vals_mats_referen_nvh = mats_reference_props_nvh.get_entity_values(constants.NASTRAN, ['MID', 'Name', 'E', 'NU', 'RHO'])
#	print(vals_mats_referen_nvh)
	mats_referen_abaqus = base.GetEntity(constants.ABAQUS, 'MATERIAL', vals_mats_referen_nvh['MID'])
	if mats_referen_abaqus == None:
		mats_referen_abaqus = base.CreateEntity(constants.ABAQUS, 'MATERIAL', {'MID': vals_mats_referen_nvh['MID']})
	
#	print(mats_referen_abaqus)
	mats_referen_abaqus.set_entity_values(constants.ABAQUS, {'Name': vals_mats_referen_nvh['Name'], '*DENSITY': 'YES', 'DENS': vals_mats_referen_nvh['RHO'], '*ELASTIC': 'YES', 'YOUNG': vals_mats_referen_nvh['E'], 'POISSON': vals_mats_referen_nvh['NU']})
	EntityPropsChange.set_entity_values(constants.ABAQUS, {'MID': mats_referen_abaqus._id})				
				
def GetInfosMatOnPropsFunc(EntityProps):
	
	mats_reference_props_nvh = None
	vals_props = EntityProps.get_entity_values(constants.NASTRAN, ['__type__'])
	if vals_props['__type__'] == 'PSOLID':
		vals_mats_nvh = EntityProps.get_entity_values(constants.NASTRAN, ['MID'])
		mats_reference_props_nvh = vals_mats_nvh['MID']
	else:
		vals_mats_nvh = EntityProps.get_entity_values(constants.NASTRAN, ['MID1'])
		mats_reference_props_nvh = vals_mats_nvh['MID1']
	
	return mats_reference_props_nvh	
	
ConvertMatOfNVHToAbaqusTool()
ConvertMatOfNVHToAbaqusTool_0701_1500
D:\Kyty180389\Script\26.ConvertMaterialNVHToAbaqus


# PYTHON script
import os
import ansa
from ansa import *

deck_infos = constants.LSDYNA
def ConvertShellsToRigids2NodesTool():
	# Need some documentation? Run this with F5
	for i in range(0, 1000, 1):
		ShellsConvert = base.PickEntities(deck_infos, ['ELEMENT_SHELL'])
		if ShellsConvert != None:
			infos_faces_on_shells = mesh.FEMToSurf(shells = ShellsConvert, delete = False, ret_ents = True)
			if len(infos_faces_on_shells) >0:
				infos_cons_double = FindConsDoubleFunc(infos_faces_on_shells)
				if len(infos_cons_double) >0:
					CreateRigids2NodesOnDoubleConsFunc(infos_cons_double)
					mesh.AutoPaste(visible = True, project_on_geometry = False, isolate = False, move_to = 'geometry pos', preserve_id = 'max', distance = 0.1, allow_element_collapse = False)
			
				base.DeleteEntity(infos_faces_on_shells, True)
		else:
			return 1
	
	
def CreateRigids2NodesOnDoubleConsFunc(infos_cons_double):
	
	for i in range(0, len(infos_cons_double), 1):
		infos_nodes_on_double_cons = []
		HotPointsOnDoubleCons = base.CollectEntities(deck_infos, infos_cons_double[i], ['HOT POINT'])
		for k in range(0, len(HotPointsOnDoubleCons), 1):
			axis_of_hotpoints = HotPointsOnDoubleCons[k].position
			infos_nodes_on_double_cons.append(base.CreateEntity(deck_infos, 'NODE', {'X': axis_of_hotpoints[0], 'Y': axis_of_hotpoints[1], 'Z': axis_of_hotpoints[2]}))
		
		if len(infos_nodes_on_double_cons) >0:
			Rigids2nodes = base.CreateEntity(deck_infos, 'CONSTRAINED_NODAL_RIGID_BODY', {'NID1': infos_nodes_on_double_cons[0]._id, 'NID2': infos_nodes_on_double_cons[1]._id, 'No.of.Nodes': 2})

def FindConsDoubleFunc(infos_faces_on_shells):
	
	infos_cons_on_faces = base.CollectEntities(deck_infos, infos_faces_on_shells, ['CONS'])
	infos_cons_double = []
	infos_cons_single = []
	for i in range(0, len(infos_cons_on_faces), 1):
		vals_cons_faces = infos_cons_on_faces[i].get_entity_values(deck_infos, ['Number of Pasted Cons'])
		if vals_cons_faces['Number of Pasted Cons'] >1:
			infos_cons_double.append(infos_cons_on_faces[i])
		else:
			infos_cons_single.append(infos_cons_on_faces[i])
	
	if len(infos_cons_single) >0:
		for k in range(0, len(infos_cons_single), 1):
			HotPointsOnSingleCons = base.CollectEntities(deck_infos, infos_cons_single[k], ['HOT POINT'])
			cons_referen_hotpoints_single = base.GetConsOfHotPoints(HotPointsOnSingleCons)
			
			infos_cons_diff = list(set(cons_referen_hotpoints_single).intersection(infos_cons_double))
			if len(infos_cons_diff) == 0:
				infos_cons_double.append(infos_cons_single[k])
	
	return infos_cons_double
			
ConvertShellsToRigids2NodesTool()
ConvertShellsToRigids2NodesTool_0710
D:\Kyty180389\Script\28.ConvertShellsToRigids2NodesTool


D:\Kyty180389\Script\98.Trim-up-Tool

D:\Kyty180389\Script\98.Trim-up-Tool\01.AdjustMassTool


import ansa
from ansa import *
 
deck_infos = constants.NASTRAN
#@session.defbutton('7_TRIM-UP', 'AdjustMassTool','Adjust Mass By RHO')
def AdjustMassTool():
	TopWindow = guitk.BCWindowCreate("Auto Adjust Mass Of Part Tool version 1.0", guitk.constants.BCOnExitDestroy)
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Import Mass: ", guitk.constants.BCHorizontal)
	BCLabel_1 = guitk.BCLabelCreate(BCButtonGroup_1, "Mass(Kg): ")
	BCLineEdit_1 = guitk.BCLineEditCreate(BCButtonGroup_1, "")
	
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	_window = [BCLineEdit_1]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, _window)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, _window)
	
	guitk.BCShow(TopWindow)

def RejectFunc(TopWindow, _window):
	return 1
	
#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, _window):
	
	MassInfos = guitk.BCLineEditGetText(_window[0])
	if MassInfos != '':
		for i in range(0, 100, 1):
			ElemsSelect = base.PickEntities(deck_infos, ['__ELEMENTS__'], 'ELEMENT')
			if ElemsSelect != None:
				PropsAdjustMass = base.PickEntities(deck_infos, ['__PROPERTIES__'], 'PROPERTY')
				if PropsAdjustMass != None:
					MassOfElemsSelect = base.CalcElementMass(entities = ElemsSelect, no_nsm = True, deck = deck_infos)
					if len(MassOfElemsSelect) >0:
						MassNotEnough = float(MassInfos) - (MassOfElemsSelect[0]*1000)
						AdjustMassToRHOofPropsFunc(MassNotEnough, PropsAdjustMass)
			else:
				return 1
		
	else:
		guitk.UserError('Import Infos Of Mass')

#***************** Dieu chinh khoi luong vao RHO cua MAT
def AdjustMassToRHOofPropsFunc(MassNotEnough, PropsAdjustMass):
	
	MassOfProps = base.CalcElementMass(entities = PropsAdjustMass, no_nsm = True, deck = deck_infos)
	MATReferen, ListPropsUseMATReferen = FindInfosMATInPropsFunc(PropsAdjustMass)
	if MATReferen != None:
		if len(ListPropsUseMATReferen)>0:
			MATReferenNew = base.CopyEntity(None, MATReferen)
			try:
				PropsAdjustMass[0].set_entity_values(deck_infos, {'MID': MATReferenNew._id})
			except:
				print('None')
			else:
				PropsAdjustMass[0].set_entity_values(deck_infos, {'MID1': MATReferenNew._id, 'MID2': MATReferenNew._id, 'MID3': MATReferenNew._id})
		else:
			MATReferenNew = MATReferen
		
		ValsMatReferenNew = MATReferenNew.get_entity_values(deck_infos, ['RHO'])
		MassAdjustToProps = MassOfProps[0]*1000 + MassNotEnough
		RHOAdjustToMAT = (MassAdjustToProps*ValsMatReferenNew['RHO'])/(MassOfProps[0]*1000)
		MATReferenNew.set_entity_values(deck_infos, {'RHO': RHOAdjustToMAT})
		

#***************** Lay thong tin cua MAT
def FindInfosMATInPropsFunc(PropsAdjustMass):
	
	MATReferen = None
	ListPropsUseMATReferen = []
	
	ValsOfProps = PropsAdjustMass[0].get_entity_values(deck_infos, ['__type__', 'MID', 'MID1'])
	if ValsOfProps['__type__'] == 'PSOLID' or ValsOfProps['__type__'].find('PBEAM') != -1:
		MATReferen = ValsOfProps['MID']
	elif ValsOfProps['__type__'] == 'PSHELL':
		MATReferen = ValsOfProps['MID1']

	if MATReferen != None:
		AllsPropsConnect = base.CollectEntities(deck_infos, None, ['__PROPERTIES__'])
		if len(AllsPropsConnect) >0:
			for i in range(0, len(AllsPropsConnect), 1):
				if AllsPropsConnect[i] != PropsAdjustMass[0]:
					ValsPropsConnect = AllsPropsConnect[i].get_entity_values(deck_infos, ['__type__', 'MID', 'MID1'])
					if ValsPropsConnect['__type__'] == 'PSOLID' or ValsPropsConnect['__type__'].find('PBEAM') != -1:
						MATConnect = ValsPropsConnect['MID']
					elif ValsPropsConnect['__type__'] == 'PSHELL':
						MATConnect = ValsPropsConnect['MID1']
					else:
						MATConnect = None
#					print(MATConnect)	
					if MATConnect != None:
						if MATConnect._id == MATReferen._id:
							ListPropsUseMATReferen.append(AllsPropsConnect[i])
		
	return MATReferen, ListPropsUseMATReferen
	
#AdjustMassTool()

AdjustMassTool_20200521

import ansa
from ansa import *
 
deck_infos = constants.NASTRAN
@session.defbutton('7_TRIM-UP', 'AdjustMassTool','Adjust Mass By RHO')
def AdjustMassTool():
	TopWindow = guitk.BCWindowCreate("Auto Adjust Mass Of Part Tool version 1.0", guitk.constants.BCOnExitDestroy)
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Import Mass: ", guitk.constants.BCHorizontal)
	BCLabel_1 = guitk.BCLabelCreate(BCButtonGroup_1, "Mass(Kg): ")
	BCLineEdit_1 = guitk.BCLineEditCreate(BCButtonGroup_1, "")
	
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	_window = [BCLineEdit_1]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, _window)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, _window)
	
	guitk.BCShow(TopWindow)

def RejectFunc(TopWindow, _window):
	return 1
	
#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, _window):
	
	MassInfos = guitk.BCLineEditGetText(_window[0])
	if MassInfos != '':
		for i in range(0, 100, 1):
			ElemsSelect = base.PickEntities(deck_infos, ['__ELEMENTS__'], 'ELEMENT')
			if ElemsSelect != None:
				PropsAdjustMass = base.PickEntities(deck_infos, ['__PROPERTIES__'], 'PROPERTY')
				if PropsAdjustMass != None:
					MassOfElemsSelect = base.CalcElementMass(entities = ElemsSelect, no_nsm = True, deck = deck_infos)
					if len(MassOfElemsSelect) >0:
						MassNotEnough = float(MassInfos) - (MassOfElemsSelect[0]*1000)
						AdjustMassToRHOofPropsFunc(MassNotEnough, PropsAdjustMass)
			else:
				return 1
		
	else:
		guitk.UserError('Import Infos Of Mass')

#***************** Dieu chinh khoi luong vao RHO cua MAT
def AdjustMassToRHOofPropsFunc(MassNotEnough, PropsAdjustMass):
	
	MassOfProps = base.CalcElementMass(entities = PropsAdjustMass, no_nsm = True, deck = deck_infos)
	status_error, MATReferen, ListPropsUseMATReferen = FindInfosMATInPropsFunc(PropsAdjustMass)
	if status_error == False:
		if len(ListPropsUseMATReferen)>0:
			MATReferenNew = base.CopyEntity(None, MATReferen)
			for i in range(0, len(PropsAdjustMass), 1):
				try:
					PropsAdjustMass[i].set_entity_values(deck_infos, {'MID': MATReferenNew._id})
				except:
					print('None')
				else:
					PropsAdjustMass[i].set_entity_values(deck_infos, {'MID1': MATReferenNew._id, 'MID2': MATReferenNew._id, 'MID3': MATReferenNew._id})
					
		else:
			MATReferenNew = MATReferen
		
		ValsMatReferenNew = MATReferenNew.get_entity_values(deck_infos, ['RHO'])
		MassAdjustToProps = MassOfProps[0]*1000 + MassNotEnough
		RHOAdjustToMAT = (MassAdjustToProps*ValsMatReferenNew['RHO'])/(MassOfProps[0]*1000)
		MATReferenNew.set_entity_values(deck_infos, {'RHO': RHOAdjustToMAT})
				
	else:
		guitk.UserError('Check infos mat of props')
		return 1

#***************** Lay thong tin cua MAT
def FindInfosMATInPropsFunc(PropsAdjustMass):
	
	ListPropsUseMATReferen = []
	MATReferen = None
	
	infos_mats_referen = base.CollectEntities(deck_infos, PropsAdjustMass, '__MATERIALS__', recursive = True)
	if len(infos_mats_referen) >0:
		if len(infos_mats_referen) == 1:
			MATReferen = infos_mats_referen[0]
			status_error = False
			AllsPropsConnect = base.CollectEntities(deck_infos, None, ['__PROPERTIES__'])
			if len(AllsPropsConnect) >0:
				ListPropsDiff = [set(AllsPropsConnect).difference(PropsAdjustMass)]
				for i in range(0, len(ListPropsDiff), 1):
					infos_mats_props_diff = base.CollectEntities(deck_infos, ListPropsDiff[i], '__MATERIALS__', recursive = True)
					if len(infos_mats_props_diff) >0:
						if infos_mats_props_diff[0]._id == infos_mats_referen[0]._id:
							ListPropsUseMATReferen.append(ListPropsDiff[i])
		else:
			status_error = True
	else:
		status_error = True
		
	return status_error, MATReferen, ListPropsUseMATReferen
	
#AdjustMassTool()
AdjustMassTool_20200708


D:\Kyty180389\Script\98.Trim-up-Tool\02.CheckAndFixBeamInLineNVHTool

# PYTHON script
import os
import ansa
import math
from ansa import *

deck_infos = constants.NASTRAN
@session.defbutton('7_TRIM-UP', 'CheckAndFixBeamInLineNVHTool','Check va sua loi beam khong thang hang')
def CheckAndFixBeamInLineNVHTool():
	# Need some documentation? Run this with F5
	alls_props = base.CollectEntities(deck_infos, None, ['__PROPERTIES__'])
	if len(alls_props) >0:
		infos_beams_check, infos_beams_not_check = FindBoltBeamFunc(alls_props)
		if len(infos_beams_check) >0:
			ListPointsError = CheckBeamInLineFunc(infos_beams_check)
			if len(ListPointsError) >0:
				infos_parts_points = CreateNewPartFunc('Beams Error', 'Beams Error')
				base.SetEntityPart(ListPointsError, infos_parts_points)
	
	guitk.UserError('Done.......^.^')

def CheckBeamInLineFunc(infos_beams_check):
	
	ListPointsError = []
	for Single_groups_beams in infos_beams_check:
		infos_nodes_beam_startends, infos_nodes_beam_middle = FindNodesStartEndsOnGroupBeamFunc(Single_groups_beams)
		if len(infos_nodes_beam_startends) >0 and len(infos_nodes_beam_middle) >0:
			infos_curves_beams = CreateInfosCurvesOnStartEndsBeamFunc(infos_nodes_beam_startends)
			if infos_curves_beams != None:
				for i in range(0, len(infos_nodes_beam_middle), 1):
					axis_nodes_middle_beam = infos_nodes_beam_middle[i].position
					infos_project_points = base.ProjectPoint(axis_nodes_middle_beam[0], axis_nodes_middle_beam[1], axis_nodes_middle_beam[2], infos_curves_beams)
					if infos_project_points != 0:
						axis_points_proj_result = [infos_project_points[1], infos_project_points[2], infos_project_points[3]]
						distance_node_beam_to_curves = CalculateDistance2PointsFunc(axis_nodes_middle_beam, axis_points_proj_result)
						if distance_node_beam_to_curves >0.01:
							infos_nodes_beam_middle[i].set_entity_values(deck_infos, {'X1': infos_project_points[1], 'X2': infos_project_points[2], 'X3': infos_project_points[3]})
							ListPointsError.append(base.Newpoint(axis_nodes_middle_beam[0], axis_nodes_middle_beam[1], axis_nodes_middle_beam[2]))
				
				base.DeleteEntity(infos_curves_beams, True)
				
	return ListPointsError
		
############ Tao curves giua diem dau va diem cuoi cua doan beam
def CreateInfosCurvesOnStartEndsBeamFunc(infos_nodes_beam_startends):
	
	infos_curves_beams = None
	infos_axis_curve_X = []
	infos_axis_curve_Y = []
	infos_axis_curve_Z = []
	for i in range(0, len(infos_nodes_beam_startends), 1):
		axis_nodes_starts_beams = infos_nodes_beam_startends[i].position
		infos_axis_curve_X.append(axis_nodes_starts_beams[0])
		infos_axis_curve_Y.append(axis_nodes_starts_beams[1])
		infos_axis_curve_Z.append(axis_nodes_starts_beams[2])
	
	
	infos_curves_beams = base.CreateCurve(len(infos_axis_curve_X), infos_axis_curve_X, infos_axis_curve_Y, infos_axis_curve_Z)
	return infos_curves_beams
		
######### Tim nodes dau va node cuoi cua 1 doan beam
def FindNodesStartEndsOnGroupBeamFunc(Single_groups_beams):
	
	infos_nodes_beam_startends = []
	infos_nodes_beam_middle = []
	
	alls_nodes_beams = base.CollectEntities(deck_infos, Single_groups_beams, ['GRID'])
	if len(alls_nodes_beams)>0:
		for k in range(0, len(alls_nodes_beams), 1):
			ListBeamsReferenceNodes = []
			for w in range(0, len(Single_groups_beams), 1):
				node_on_single_beams = base.CollectEntities(deck_infos, Single_groups_beams[w], ['GRID'])
				infos_nodes_intersection = list(set(node_on_single_beams).intersection([alls_nodes_beams[k]]))
				if len(infos_nodes_intersection)>0:
					ListBeamsReferenceNodes.append(Single_groups_beams[w])
				
			if len(ListBeamsReferenceNodes) >0:
				if len(ListBeamsReferenceNodes) == 1:
					infos_nodes_beam_startends.append(alls_nodes_beams[k])	
				else:
					infos_nodes_beam_middle.append(alls_nodes_beams[k])		

	return infos_nodes_beam_startends, infos_nodes_beam_middle
					
######### Find Beam Need Check
def FindBoltBeamFunc(alls_props):
	
	infos_beams_check = []
	infos_beams_not_check = []
	ListPropsBeamBolt = []
	
	for i in range(0, len(alls_props), 1):
		ids_props = alls_props[i]._id
		vals_props = alls_props[i].get_entity_values(deck_infos, ['__type__'])
		if vals_props['__type__'].find('BEAM') != -1 and ids_props <= 100500:
			ListPropsBeamBolt.append(alls_props[i])
	
	if len(ListPropsBeamBolt) >0:
		set_beam_check = base.CreateEntity(deck_infos, "SET")
		elems_on_props = base.CollectEntities(deck_infos, ListPropsBeamBolt, ['CBEAM'])
		dict_isolate_groups = base.IsolateConnectivityGroups(entities = elems_on_props, separate_at_blue_bounds = 0, separate_at_pid_bounds = 0)
		if dict_isolate_groups != None:
			for key_name_group, infos_vals_elems in dict_isolate_groups.items():
				if len(infos_vals_elems) >1:
					infos_beams_check.append(infos_vals_elems)
					base.AddToSet(set_beam_check, infos_vals_elems)
				else:
					infos_beams_not_check.append(infos_vals_elems)
			
	return infos_beams_check, infos_beams_not_check


#################Help Funs
def CalculateDistance2PointsFunc(Points1st, Points2nd):
	
	VecsAB = [Points2nd[0] - Points1st[0], Points2nd[1] - Points1st[1], Points2nd[2] - Points1st[2]]
	LenVecsAB = math.sqrt((VecsAB[0]*VecsAB[0]) + (VecsAB[1]*VecsAB[1]) + (VecsAB[2]*VecsAB[2]))
	
	return LenVecsAB

def CreateNewPartFunc(NamePart, ModuleIdsPart):
	
	NewParts = base.NewPart(NamePart, ModuleIdsPart)
	if NewParts == None:
		EntityPart = base.NameToEnts(NamePart)
		
		NewParts = EntityPart[0]
	
	return NewParts	

#CheckBeamInLineNVHTool()
CheckAndFixBeamInLineNVHTool_20200812



D:\Kyty180389\Script\98.Trim-up-Tool\03.CreatePanelTool

# PYTHON script
import os
import ansa
from ansa import *

deck_infos = constants.NASTRAN
def Create_Panel_Tool():
	
	props_selected = base.PickEntities(deck_infos, ['__PROPERTIES__'], 'PROPERTY')
	if props_selected != None:
		infos_list_string_panel = []	
		infos_list_names, infos_list_ids_names = GetInfosNameIdsFunc(props_selected, infos_list_string_panel)
		
		if len(infos_list_ids_names)>0:
			infos_list_string_panel.append('$\n')
			infos_list_string_panel.append('$------1-------2-------3-------4-------5-------6-------7-------8-------9-------0\n')
			infos_list_string_panel.append('$\n')
			
			GetInfosPANELFunc(infos_list_ids_names, infos_list_string_panel)
			infos_list_string_panel.append('$------1-------2-------3-------4-------5-------6-------7-------8-------9-------0\n')
			infos_list_string_panel.append('$\n')
			GetInfosSet_20Func(infos_list_names, infos_list_string_panel)
			
		
		if len(infos_list_string_panel) >0:
			panel_text = open('D:/infos_panel_output.txt', 'w')
			for w in range(0, len(infos_list_string_panel), 1):
				panel_text.write(infos_list_string_panel[w])
			panel_text.close()

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$	
def GetInfosSet_20Func(infos_list_names, infos_list_string_panel):
	
	infos_string_set_20 = DivideStepLoadFunc(infos_list_names)
	if len(infos_string_set_20) >0:
		if len(infos_string_set_20) == 1:
			string_text_set_20_add = 'SET 20 ='+''.join(infos_string_set_20[0])
			infos_list_string_panel.append(string_text_set_20_add[0:len(string_text_set_20_add) - 1] + '\n')
		else:
			infos_list_string_panel.append('SET 20 ='+''.join(infos_string_set_20[0])+'\n')
			for w1 in range(1, len(infos_string_set_20)-1, 1):
				infos_list_string_panel.append('        '+''.join(infos_string_set_20[w1])+'\n')
				
			string_text_set_20_end_add = '        '+''.join(infos_string_set_20[len(infos_string_set_20)-1])
			infos_list_string_panel.append(string_text_set_20_end_add[0:len(string_text_set_20_end_add) - 1] + '\n')

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$	
def GetInfosPANELFunc(infos_list_ids_names, infos_list_string_panel):
	
	infos_string_panel = DivideStepLoadFunc(infos_list_ids_names)
	if len(infos_string_panel) >0:
		if len(infos_string_panel) == 1:
			infos_list_string_panel.append('PANEL   '+''.join(infos_string_panel[0])+'\n')
		else:
			infos_list_string_panel.append('PANEL   '+''.join(infos_string_panel[0])+'\n')
			for w1 in range(1, len(infos_string_panel), 1):
				infos_list_string_panel.append('        '+''.join(infos_string_panel[w1])+'\n')

######$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def DivideStepLoadFunc(infos_list_divide_step):
	
	step_range = []
	infos_string_panel = []
	for k in range(0, len(infos_list_divide_step), 4):
		step_range.append(k)
	if max(step_range) < len(infos_list_divide_step):
		step_range.append(len(infos_list_divide_step))
	
	if len(step_range) >0:
		for j in range(0, len(step_range)-1, 1):
			infos_string_step_panel = []
			for j1 in range(step_range[j], step_range[j+1], 1):
				infos_string_step_panel.append(infos_list_divide_step[j1])
			if len(infos_string_step_panel)>0:
				infos_string_panel.append(infos_string_step_panel)
						
	return infos_string_panel
		
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def GetInfosNameIdsFunc(props_selected, infos_list_string_panel):

	infos_list_names = []
	infos_list_ids_names = []
	
	for i in range(0, len(props_selected), 1):
		ids_props = str(props_selected[i]._id)
		name_props = props_selected[i]._name
		if len(name_props) <8:
			name_props_add_blank = name_props + '        '
			name_props_replace = name_props_add_blank[0:8]
		else:
			name_props_replace = name_props[0:8]
			
		if len(ids_props) <8:
			ids_props_add_blank = ids_props + '        '
			ids_props_replace = ids_props_add_blank[0:7]
		else:
			ids_props_replace = ids_props[0:7]
			
		infos_list_names.append(name_props_replace + ',')
		infos_list_ids_names.append(name_props_replace + ' ' + ids_props_replace)
		
		infos_list_string_panel.append('SET3     ' + ids_props_replace +'    PROP ' + ids_props_replace+'\n')
	
	return infos_list_names, infos_list_ids_names
			
#			infos_list_string_panel.append('$\n')
#			infos_list_string_panel.append('$------1-------2-------3-------4-------5-------6-------7-------8-------9-------0\n')
#			infos_list_string_panel.append('$\n')
############## Divide step load			
#			step_range = []
#			for k in range(0, len(infos_list_ids), 4):
#				step_range.append(k)
#			if max(step_range) < len(infos_list_ids):
#				step_range.append(len(infos_list_ids))
#			
#			infos_string_panel = []
#			for j in range(0, len(step_range)-1, 1):
#				infos_string_step_panel = []
#				for j1 in range(step_range[j], step_range[j+1], 1):
#					infos_string_step_panel.append('P'+str(infos_list_ids[j1])+' '+str(infos_list_ids[j1]))
#				if len(infos_string_step_panel)>0:
#					infos_string_panel.append(infos_string_step_panel)
#			
#			if len(infos_string_panel)>0:
#				if len(infos_string_panel) == 1:
#					infos_list_string_panel.append('PANEL   '+''.join(infos_string_panel[0])+'\n')
#				else:
#					infos_list_string_panel.append('PANEL   '+''.join(infos_string_panel[0])+'\n')
#					for w1 in range(1, len(infos_string_panel), 1):
#						infos_list_string_panel.append('        '+''.join(infos_string_panel[w1])+'\n')
#			
############## Write infos panel			
#			panel_text = open('D:/infos_panel_output.txt', 'w')
#			for w in range(0, len(infos_list_string_panel), 1):
#				panel_text.write(infos_list_string_panel[w])
#			
#			panel_text.close()
	
Create_Panel_Tool()

CreatePanelTool_1020



D:\Kyty180389\Script\99.Other

# PYTHON script
import os
import ansa
from ansa import *

def main():
	# Need some documentation? Run this with F5
	SelectSectionsBeam = base.PickEntities(constants.ABAQUS, ['BEAM_SECTION'])
	if SelectSectionsBeam != None:
		base.Or(SelectSectionsBeam)
		base.Neighb('1')
		ContraintOnBeam = base.CollectEntities(constants.ABAQUS, None, ['COUPLING', 'MPC', 'KINEMATIC COUPLING'], filter_visible = True)
	
		for i in range(0, len(SelectSectionsBeam), 1):
			GroupBeamsOnSectionBeam = base.IsolateConnectivityGroups(entities = SelectSectionsBeam[i], separate_at_blue_bounds = True, separate_at_pid_bounds = True)
			for KeyNameGroup, ElementBeamInGroup in GroupBeamsOnSectionBeam.items():
				NodesOnBeam = base.CollectEntities(constants.ABAQUS, ElementBeamInGroup, ['NODE'])	
				ListConstraintInBeam = []
				for w in range(0, len(ContraintOnBeam), 1):
					NodesContraintOnBeam = base.CollectEntities(constants.ABAQUS, ContraintOnBeam[w], ['NODE'])
					SetNodeContraintWithNodeBeam = set(NodesContraintOnBeam).intersection(NodesOnBeam)
					if len(SetNodeContraintWithNodeBeam) >0:
						ListConstraintInBeam.append(ContraintOnBeam[w])
			
				if len(ListConstraintInBeam) >0:
					ListNodesReferenContraint = base.CollectEntities(constants.ABAQUS, ListConstraintInBeam[0], ['NODE'])
					ListDifferenceNode = list(set(ListNodesReferenContraint).difference(NodesOnBeam))
					for j in range(0, len(ElementBeamInGroup), 1):
						base.SetEntityCardValues(constants.ABAQUS, ElementBeamInGroup[j], {'Orient': 'With Node - Y Axis', 'NODE3': ListDifferenceNode[0]._id})

if __name__ == '__main__':
	main()

ChangeVectorOfBeamAbaqus


# PYTHON script
import os
import ansa
from ansa import *

@session.defbutton('99_OTHER TOOL', 'CalculateWeightOfPart','Tính khối lượng của từng chi tiết')
def CalculateWeightOfPart():
	# Need some documentation? Run this with F5
	AllsProps = base.CollectEntities(constants.LSDYNA, None, ['__PROPERTIES__'], filter_visible = True)
	if len(AllsProps) >0:
		
		for i in range(0, len(AllsProps), 1):
			mass_info = base.CalcElementMass(AllsProps[i], deck = constants.NASTRAN)
			WeightOfParts = round(mass_info[0]*1000, 2)
			base.SetEntityCardValues(constants.LSDYNA, AllsProps[i], {'User/cad_thickness': WeightOfParts})
	
#CalculateWeightOfPart()

Caculate_Weight_Of_Parts





# PYTHON script
import os
import ansa
from ansa import *

deck_infos = base.CurrentDeck()
def main():
	# Need some documentation? Run this with F5
	path_csv = utils.SelectOpenFile(0, '*.csv')
	if len(path_csv) >0:
		infos_line_csv = ReadInfoCsvFunc(path_csv[0])
		if len(infos_line_csv) >0:
			infos_list_pid_origin = FindPropsDivideInCsvFunc(infos_line_csv)
			if len(infos_list_pid_origin) >0:
				infos_pids_weight_add_csv = CalculateWeightOfPartsFunc(infos_list_pid_origin)
				if len(infos_pids_weight_add_csv)>0:
					Write_Weight_of_Part_ToCsvFunc(infos_pids_weight_add_csv, infos_line_csv, path_csv)

def Write_Weight_of_Part_ToCsvFunc(infos_pids_weight_add_csv, infos_line_csv, path_csv):
	
	infos_csv_new = open(path_csv[0], 'w')
	for i in range(0, len(infos_line_csv), 1):
		tokens_string_csv = infos_line_csv[i].split(',')
		weight_infos_add = None
		for w in range(0, len(infos_pids_weight_add_csv), 1):
			if infos_pids_weight_add_csv[w][0] == tokens_string_csv[0]:
				weight_infos_add = infos_pids_weight_add_csv[w][1]
		
		if weight_infos_add == None:
			infos_csv_new.write(infos_line_csv[i] + '\n')
		else:
			infos_csv_new.write(infos_line_csv[i] + ',' + str(weight_infos_add) + '\n')
	
	infos_csv_new.close()
	
########## Tinh Khoi Luong Cua Cac Parts
def CalculateWeightOfPartsFunc(infos_list_pid_origin):
	
	infos_pids_weight_add_csv = []
	for i in range(0, len(infos_list_pid_origin), 1):
		infos_props_referen_ids = []
		for w in range(0, len(infos_list_pid_origin[i]), 1):
			props_referen = base.GetEntity(deck_infos, '__PROPERTIES__', int(infos_list_pid_origin[i][w]))
			if props_referen != None:
				infos_props_referen_ids.append(props_referen)
		
		if len(infos_props_referen_ids) >0:
			PartsConnect = CreateNewPartFunc(infos_list_pid_origin[i][0], '')
			ElemsOnProps = base.CollectEntities(deck_infos, infos_props_referen_ids, ['__ELEMENTS__'])
			base.SetEntityPart(ElemsOnProps, PartsConnect)
			mass_info = base.CalcElementMass(infos_props_referen_ids, deck = deck_infos)
			WeightOfParts = round(mass_info[0]*1000, 4)
			base.SetEntityCardValues(deck_infos, infos_props_referen_ids[0], {'Comment': WeightOfParts})
			infos_pids_weight_add_csv.append([infos_list_pid_origin[i][0], WeightOfParts])
	
	return infos_pids_weight_add_csv

########## Find Props Divide in model		
def FindPropsDivideInCsvFunc(infos_line_csv):
	
	list_pid_alls = []
	list_pid_origin_division = []
	list_pid_division = []
	
	infos_list_pid_origin = []
	for i in range(0, len(infos_line_csv), 1):
		split_string_line = infos_line_csv[i].split(',')
		list_pid_alls.append(split_string_line[0])
#		print(split_string_line)
		if split_string_line[24] != '':
			split_string_division = split_string_line[24].split(':')
			list_pid_origin_division.append(split_string_division[1])
			list_pid_division.append(split_string_line[0])
	
	infos_pid_not_divide = list(set(list_pid_alls).difference(list_pid_division))
	for j in range(0, len(infos_pid_not_divide), 1):
		infos_list_pid_origin.append([infos_pid_not_divide[j]])
	
	if len(list_pid_division) >0:
		list_pid_origin_remove_double = list(set(list_pid_origin_division))
		for k in range(0, len(list_pid_origin_remove_double), 1):
			infos_pid_origin_division = []
			infos_pid_origin_division.append(list_pid_origin_remove_double[k])
			for w in range(0, len(list_pid_origin_division), 1):
				if list_pid_origin_division[w] == list_pid_origin_remove_double[k]:
					infos_pid_origin_division.append(list_pid_division[w])
			
			if len(infos_pid_origin_division) >0:
				infos_list_pid_origin.append(infos_pid_origin_division)

	return infos_list_pid_origin

#	AllProps = base.CollectEntities(deck_infos, None, ['__PROPERTIES__'])
#	ListPropsConnected = []
#	for SingleProps in AllProps:
#		 PoscheckPID = FindEntityInListElementsFunc(SingleProps, ListPropsConnected)
#		 if PoscheckPID == None:
#		 	base.Or(SingleProps)
#		 	base.Neighb('ALL')
#		 	PropsVis = base.CollectEntities(deck_infos, None, ['__PROPERTIES__'], filter_visible = True)
#		 	if len(PropsVis) >0:
#		 		PropsWithMaxElems = FindPropOriginFunc(PropsVis)
#		 		ListPropsConnected.extend(PropsVis)
#		 		ElemsOnProps = base.CollectEntities(deck_infos, PropsVis, ['__ELEMENTS__'])
#		 		PartsConnect = base.NewPart(str(PropsWithMaxElems._id), '')
#		 		base.SetEntityPart(ElemsOnProps, PartsConnect)
#		 		
#		 		mass_info = base.CalcElementMass(PropsVis, deck = deck_infos)
#		 		WeightOfParts = round(mass_info[0]*1000, 3)
#		 		base.SetEntityCardValues(deck_infos, PropsWithMaxElems, {'Comment': WeightOfParts})
#		 		
#def FindPropOriginFunc(PropsVis):
#	
#	ListLenElemsCheck = []
#	for i in range(0, len(PropsVis), 1):
#		AllElemsInPropVis = base.CollectEntities(deck_infos, PropsVis[i], ['__ELEMENTS__'])
#		ListLenElemsCheck.append(len(AllElemsInPropVis))
#	
#	IndexMaxElems = ListLenElemsCheck.index(max(ListLenElemsCheck))
#	PropsWithMaxElems = PropsVis[IndexMaxElems]
#	
#	return PropsWithMaxElems
#	
#def FindEntityInListElementsFunc(EntityElement, ListElements):
#	
#	try:
#		Pos = ListElements.index(EntityElement)
#	except:
#		Pos = None
#	else:
#		Pos = Pos
#	
#	return Pos

def ReadInfoCsvFunc(PathCsv):
	
	OpenCSVFile = open(PathCsv)
	ReadLinesCSV = OpenCSVFile.readlines()
	
	ListLinesInCSV = []
	for i in range(0, len(ReadLinesCSV), 1):
		ListLinesInCSV.append(ReadLinesCSV[i].strip())

	OpenCSVFile.close()
	
	return ListLinesInCSV

def CreateNewPartFunc(NamePart, ModuleIdsPart):
	
	NewParts = base.NewPart(NamePart, ModuleIdsPart)
	if NewParts == None:
		EntityPart = base.NameToEnts(NamePart)
		
		NewParts = EntityPart[0]
	
	return NewParts	

if __name__ == '__main__':
	main()
Calculate_Weight_Of_PlasticParts








# PYTHON script
import os
import ansa
from ansa import *

@session.defbutton('99_OTHER TOOL', 'RemoveElemsOnConnection','Tách các phần tử trong Connection')
def RemoveElemsFromConnectionTool():

	EntityPick = base.PickEntities(constants.LSDYNA, ['__CONNECTIONS__'])
	if EntityPick != None:
		ElementInConnection = base.CollectEntities(constants.LSDYNA, EntityPick, ['__ELEMENTS__'])
		if len(ElementInConnection) >0:
			PartConnection = base.NewPart('Connection_Element', '')
			if PartConnection == None:
				EntityPart = base.NameToEnts('Connection_Element')
				PartConnection = EntityPart[0]
			else:
				PartConnection = PartConnection
		
			base.SetEntityPart(ElementInConnection, PartConnection)

RemoveElemsFromConnectionTool()

RemoveElemsOnConnection



# PYTHON script
import os
import meta
from meta import *

def SetupAnnotationOnPart():
	
#	utils.MetaCommand('explode center 1.5 all')
	
	parts_vis = parts.VisibleParts()
	model_id = 0
	
	utils.MetaCommand('annotation del all')
	for i in range(0, len(parts_vis), 1):
		NamePart = parts_vis[i].name
		ThicknessPart = parts_vis[i].shell_thick
		
		part_id = parts_vis[i].id
		part_type = parts_vis[i].type
#		part_type = constants.PSHELL
		
		part_materials = materials.MaterialsOfPart(model_id, part_type, part_id)
		MATName = part_materials[0].name
		
		part_mass = round(parts.MassOfPart(model_id, part_type, part_id)*1000, 2)
#		print(part_mass)
		
		StringCommand = 'annotation add onparts ' + str(part_id)+' '+ NamePart +"\n"+ 'Thickness: ' + str(ThicknessPart) +' mm' +"\n"+ 'Material  : '+ MATName +"\n" + 'Weight    : '+ str(part_mass) +' Kg'
#		print(StringCommand)
		
		utils.MetaCommand(StringCommand)
		
	utils.MetaCommand('annotation text all font "MS Shell Dlg 2,8,-1,5,75,0,0,0,0,0"')      
	utils.MetaCommand('annotation anchor all pointer 100.000000 100.000000')
	utils.MetaCommand('annotation background all color manual Orange')
	
SetupAnnotationOnPart()

SetUpAnnotationMetaPost




# PYTHON script
import os
import ansa
from ansa import *
deck_infos = constants.NASTRAN
def Change_Axis_Point_Tire():

##### Nhập tên cần tìm kiếm: Tire, hoặc .....
	input_name_search = 'Tire'
##### Chọn file cần chỉnh sửa thông tin	
	select_files = utils.SelectOpenFile(0, '*.bdf', '*.txt')
	if len(select_files)>0:
		lines_in_selected_file = open_entity_file_func(select_files[0])
		if len(lines_in_selected_file)>0:
			infos_locate_of_points = find_infos_points_in_source_file(input_name_search, lines_in_selected_file)
			if len(infos_locate_of_points)>0:
				
		


##### Lấy thông tin điểm point trong file
def find_infos_points_in_source_file(input_name_search, lines_in_selected_file):
	
	infos_location_name_points = find_location_of_name_points(input_name_search, lines_in_selected_file)
	if len(infos_location_name_points)>0:
#		print(infos_location_name_points)
		infos_locate_of_points = get_infos_location_points_in_files(infos_location_name_points, lines_in_selected_file)
#		print(infos_locate_of_points)
	else:
		print('Not found name of points')
	
	return infos_locate_of_points

########## Tìm tọa độ và tên điểm points trong file
def get_infos_location_points_in_files(infos_location_name_points, lines_in_selected_file):
	infos_locate_of_points= []
	########## Chia khoảng giữa các điểm points
	infos_range_name_points = []
	for i in range(0, len(infos_location_name_points)-1, 1):
		infos_range_name_points.append([infos_location_name_points[i], infos_location_name_points[i+1]])
	
	########## Giữa các tên của điểm point tìm tọa độ ORIGIN
	if len(infos_range_name_points)>0:
		for k in range(0, len(infos_range_name_points), 1):
			range_of_name_points = infos_range_name_points[k]
			infos_orgin_axis_points = []
			infos_loacte_points = []
			for w in range(range_of_name_points[0], range_of_name_points[1]):
				if lines_in_selected_file[w].find('ORIGIN') != -1:
					infos_orgin_axis_points.append(lines_in_selected_file[w])
					infos_loacte_points.append(w)
					
			if len(infos_orgin_axis_points) == 1:
				infos_locate_of_points.append([range_of_name_points[0], infos_loacte_points[0]])
#				tokens_axis_points = infos_orgin_axis_points[0].split('	')
#				print(tokens_axis_points)
#				new_points_origin = base.Newpoint(float(tokens_axis_points[1]), float(tokens_axis_points[2]), float(tokens_axis_points[3]))
#				base.SetEntityCardValues(deck_infos, new_points_origin, {'Name': lines_in_selected_file[range_of_name_points[0]]})
			else:
				print(lines_in_selected_file[range_of_name_points[0]] + 'Not found axis of points')
	
	return infos_locate_of_points
	
########## Tìm vị trí tên của điểm point trong file
def find_location_of_name_points(input_name_search, lines_in_selected_file):
	
	infos_location_name_req = []
	for i in range(0, len(lines_in_selected_file), 1):
		if lines_in_selected_file[i].find(input_name_search) != -1:
			infos_location_name_req.append(i)
	
	if len(infos_location_name_req)>0:
		infos_location_name_req.append(len(lines_in_selected_file))
	
	return infos_location_name_req

##### Mở file
def open_entity_file_func(path_entity_file):
	
	total_entity_lines_req = []
	open_entity_file = open(path_entity_file, 'r')
	lines_of_entity_file = open_entity_file.readlines()
	for i in range(0, len(lines_of_entity_file), 1):
		total_entity_lines_req.append(lines_of_entity_file[i].strip())
#		print(lines_of_entity_file[i].strip())
	open_entity_file.close()
	
	return total_entity_lines_req
	
Change_Axis_Point_Tire()
Change_Axis_Point_Tire




D:\Kyty180389\Script\02.Cad Assembly Tool


# PYTHON script
import ansa
from ansa import guitk
from ansa import constants
from ansa import base
from ansa import session
from ansa import utils

import os
from os import path
import shutil
 
def CADAssemblyTool():
	CVals_5 = ["CATPart To ANSA", "Auto Setup PID"]
	TopWindow = guitk.BCWindowCreate("CAD Assembly Tool version 1.0", guitk.constants.BCOnExitDestroy)
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Options Tool", guitk.constants.BCHorizontal)
	BCLabel_1 = guitk.BCLabelCreate(BCButtonGroup_1, "Options: ")
	BCComboBox_1 = guitk.BCComboBoxCreate(BCButtonGroup_1, CVals_5)
	
	BCButtonGroup_2 = guitk.BCButtonGroupCreate(TopWindow, "Select Path BOM", guitk.constants.BCHorizontal)
	BCLabel_2 = guitk.BCLabelCreate(BCButtonGroup_2, "Path BOM: ")
	BCLineEditPath_1 = guitk.BCLineEditPathCreate(BCButtonGroup_2, guitk.constants.BCHistoryFiles, "Folder BOM", guitk.constants.BCHistorySelect, "Select BOM")
	guitk.BCLineEditPathAddFilter(BCLineEditPath_1, "CSV File: ", 'csv')
	
	BCButtonGroup_3 = guitk.BCButtonGroupCreate(TopWindow, "Select Path CAD Data", guitk.constants.BCHorizontal)
	BCLabel_3 = guitk.BCLabelCreate(BCButtonGroup_3, "CAD Data: ")
	BCLineEditPath_2 = guitk.BCLineEditPathCreate(BCButtonGroup_3, guitk.constants.BCHistoryFolders, "Folder CAD", guitk.constants.BCHistorySelect, "Select CAD")
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_4 = guitk.BCLabelCreate(TopWindow, "")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	DataOnTopWin = [BCProgressBar_1, BCLabel_4, BCLineEditPath_2, BCLineEditPath_1, BCComboBox_1]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, DataOnTopWin)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, DataOnTopWin)
	
	guitk.BCShow(TopWindow)


def RejectFunc(TopWindow, DataOnTopWin):
	
	return 1

def AcceptFunc(TopWindow, DataOnTopWin):
	
	ProgBar = 	DataOnTopWin[0]
	StatusLabel = DataOnTopWin[1]
	LineEditPathCad = DataOnTopWin[2]
	LineEditPathBOM = DataOnTopWin[3]
	OptionsListTool = guitk.BCComboBoxCurrentText(DataOnTopWin[4])
	
	if OptionsListTool == "CATPart To ANSA":
		ConvertCATPartToANSATool(ProgBar, StatusLabel, LineEditPathBOM, LineEditPathCad)

def ConvertCATPartToANSATool(ProgBar, StatusLabel, LineEditPathBOM, LineEditPathCad):
	
	PathCADSelected = guitk.BCLineEditPathSelectedFilePaths(LineEditPathCad)
	PathBOMSelected = guitk.BCLineEditPathSelectedFilePaths(LineEditPathBOM)
	if PathBOMSelected != None and PathCADSelected != None:
		ListCATProductInBOM, ListCATPartInBOM, ListNameBOMLine, ListLevelBOMLine, ListLevelCATProductInBOM = GetInfoOfBOMListFunc(PathBOMSelected)
		if len(ListCATProductInBOM) >0:
	#		print(len(ListCATProductInBOM))
	#		print(len(ListLevelCATProductInBOM))
			
			AutoConvertCATIAToANSAFunc(ProgBar, StatusLabel, ListCATProductInBOM, ListCATPartInBOM, ListNameBOMLine, ListLevelBOMLine, ListLevelCATProductInBOM, PathCADSelected)

	else:
		guitk.UserError('Please select Path BOM or Path CAD')	
		return 0

#************************* Convert cad sang file ansa
def AutoConvertCATIAToANSAFunc(ProgBar, StatusLabel, ListCATProductInBOM, ListCATPartInBOM, ListNameBOMLine, ListLevelBOMLine, ListLevelCATProductInBOM, PathCADSelected):
	
	ListLinkFiles_NameCATProduct, ListLinkFiles_NameCATPart, ListNameFileTrimCATProduct, ListNameFileTrimCATPart = ReadInfoInPathCADFunc(PathCADSelected)
	if len(ListLinkFiles_NameCATProduct) >0:
#		print(len(ListLinkFiles_NameCATProduct))
		DictLevels_InfosCATIAProduct, ListLevelCATProductCompare = CompareInfosBOMWithFolderCadFunc(ListCATProductInBOM, ListLevelCATProductInBOM, ListLinkFiles_NameCATProduct, ListNameFileTrimCATProduct)
#		print(len(DictLevels_InfosCATIAProduct))
		if len(DictLevels_InfosCATIAProduct) >0:
			AutoTranslateToANSAFunc(ProgBar, StatusLabel, DictLevels_InfosCATIAProduct, ListLevelCATProductCompare, PathCADSelected)


def AutoTranslateToANSAFunc(ProgBar, StatusLabel, DictLevels_InfosCATIAProduct, ListLevelCATProductCompare, PathCADSelected):
	
	ListLevelCATIAProductReverse = sorted(list(set(ListLevelCATProductCompare)), reverse = True)
	
	guitk.BCProgressBarReset(ProgBar)
	guitk.BCProgressBarSetTotalSteps(ProgBar, len(ListLevelCATIAProductReverse))	
	for i in range(0, len(ListLevelCATIAProductReverse), 1):
		ValesInfosCATIAProduct = DictLevels_InfosCATIAProduct[ListLevelCATIAProductReverse[i]]
#		print(len(ValesInfosCATIAProduct))
		for k in range(0, len(ValesInfosCATIAProduct), 1):
			guitk.BCLabelSetText(StatusLabel, 'Import File: ' + ValesInfosCATIAProduct[k][1])
			
			TokenPathCAD = PathCADSelected.split('/')
			NameAssyCollect = TokenPathCAD[len(TokenPathCAD) - 1]
			
			PathFileCATIAProductImport = path.join(ValesInfosCATIAProduct[k][0], ValesInfosCATIAProduct[k][1])
#			print(ValesInfosCATIAProduct[k][1])
			FlagTranslate = AutoTranslateCADFunc(PathFileCATIAProductImport)
			if FlagTranslate != False:
				NameFolderANSA = 'ANSA'
				NameFileANSA = ValesInfosCATIAProduct[k][1] + '.ansa'
				PathNewFolderANSA = CreateNewFolderBaseOnLinkFunc(ValesInfosCATIAProduct[k][0], NameFolderANSA)
			
				if PathNewFolderANSA:
					PathFileCATIAProductNew = path.join(PathNewFolderANSA, ValesInfosCATIAProduct[k][1])
					shutil.move(PathFileCATIAProductImport,PathFileCATIAProductNew)
					
					SetupInfosCADPartFunc(NameAssyCollect)
					
					PathNewFileANSA = path.join(PathNewFolderANSA, NameFileANSA)
					base.SaveAs(PathNewFileANSA)
			
			else:
				print('Can not convert file CATIA')
		
		guitk.BCProgressBarSetProgress(ProgBar, i + 1)

def SetupInfosCADPartFunc(NameAssyCollect):
	
	AnsaPartsInfos = base.CollectEntities(constants.LSDYNA, None, ['ANSAPART'])
	if len(AnsaPartsInfos) >0:
		for i in range(0, len(AnsaPartsInfos), 1):
			ValsPartCollect = base.GetEntityCardValues(constants.LSDYNA, AnsaPartsInfos[i], ['Name', 'User/CAD/StringMetaData/Nomenclature', 'User/CAD/StringMetaData/ITEM_ID', 'User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]', 'User/CAD/StringParameterData/ParameterSet\Material'])
			
			TokensNameParts = ValsPartCollect['Name'].split('_')
			try:
				ThicknessPart = ValsPartCollect['User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]']
			except:
				ThicknessPart = 0.01
			else:
				if ThicknessPart != 0:
					ThicknessPart = ThicknessPart
				else:
					ThicknessPart = 0.01
	
			try:
				MatNamePart = ValsPartCollect['User/CAD/StringParameterData/ParameterSet\Material']
			except:
				MatNamePart = None
			else:
				MatNamePart = MatNamePart
	
			PropsInParts = base.CollectEntities(constants.LSDYNA, AnsaPartsInfos[i], '__PROPERTIES__', prop_from_entities = True)
			for k in range(0, len(PropsInParts), 1):
				ValsPropInPart = base.GetEntityCardValues(constants.LSDYNA, PropsInParts[k], ['Name', 'User/CAD/OriginalId'])
				base.SetEntityCardValues(constants.LSDYNA, PropsInParts[k], {'PID': ValsPropInPart['User/CAD/OriginalId'], 'Name': ValsPartCollect['User/CAD/StringMetaData/Nomenclature'], 'T1': ThicknessPart, 'NLOC': 1, 'Comment': TokensNameParts[0], 'User/original_name': NameAssyCollect})

##### Divide group cad
def DivideGroupCadOnPartFunc(AnsaPartsInfos, i):
	
	PropsDividePart = base.CollectEntities(constants.LSDYNA, AnsaPartsInfos[i], '__PROPERTIES__', prop_from_entities = True)
	for k in range(0, len(PropsDividePart), 1):
		DictGroupsOnProps = base.IsolateConnectivityGroups(PropsDividePart[k], separate_at_blue_bounds = 1, separate_at_pid_bounds = 1)
		if len(DictGroupsOnProps) >1:
			del DictGroupsOnProps['group_1']
			for DictGroupName, DictGroupItems in DictGroupsOnProps.items():
				PropsNewDivide = base.CopyEntity(None, PropsDividePart[k])
				base.SetEntityCardValues(constants.LSDYNA, PropsNewDivide, {'User/cad_thickness': PropsDividePart[k]._id})
				for w in range(0, len(DictGroupItems), 1):
					base.SetEntityCardValues(constants.LSDYNA, DictGroupItems[w], {'PID': PropsNewDivide._id})
	

def AutoTranslateCADFunc(PathFileTranslate):
	
	session.New('discard')
	FlagOpenCAD = base.Open(PathFileTranslate)
	
	if FlagOpenCAD == 0:
		EntityGeoOnPart = base.CollectEntities(constants.LSDYNA, None, ['FACE', 'CURVE', 'POINT'])
		if len(EntityGeoOnPart) >0:
			FlagTranslate = True
		else:
			FlagTranslate = False
	else:
		FlagTranslate = False
		
	return FlagTranslate

#************************** So sanh du lieu catproduct giua bom list va folder cad
def CompareInfosBOMWithFolderCadFunc(ListCATProductInBOM, ListLevelCATProductInBOM, ListLinkFiles_NameCATProduct, ListNameFileTrimCATProduct):
#	print(len(ListLinkFiles_NameCATProduct), len(ListNameFileTrimCATProduct))
	
	ListLevelCATProductCompare = []
	ListFile_LinkCATProductCompare = []
	
	for i in range(0, len(ListNameFileTrimCATProduct), 1):
		SingleFIleNameCATProduct = ListNameFileTrimCATProduct[i]
		PosSearchCATIAProductInBOM = FindEntityInListElementsFunc(SingleFIleNameCATProduct, ListCATProductInBOM)
		if PosSearchCATIAProductInBOM != None:
			IndexLevelCATProductInBOM = ListLevelCATProductInBOM[PosSearchCATIAProductInBOM]
			ListLevelCATProductCompare.append(IndexLevelCATProductInBOM)
			ListFile_LinkCATProductCompare.append(ListLinkFiles_NameCATProduct[i])			
#			ListLevelCATProductCompare.append(str(IndexLevelCATProductInBOM) + '_' + ListLinkFiles_NameCATProduct[i][0] + '_' + ListLinkFiles_NameCATProduct[i][1])

		
		else:
			print(ListNameFileTrimCATProduct[i])
	
	DictLevels_InfosCATIAProduct = {}
	if len(ListLevelCATProductCompare) >0:
		ListLevelCATIAProductSort = sorted(list(set(ListLevelCATProductCompare)), reverse = True)
		for k in range(0, len(ListLevelCATIAProductSort), 1):
			ListLink_FIleCATProductDuplicateLevel = []
			
			for w in range(0, len(ListLevelCATProductCompare), 1):
				if ListLevelCATProductCompare[w] == ListLevelCATIAProductSort[k]:
					ListLink_FIleCATProductDuplicateLevel.append(ListFile_LinkCATProductCompare[w])
			
			if len(ListLink_FIleCATProductDuplicateLevel)>0:
				DictLevels_InfosCATIAProduct[ListLevelCATIAProductSort[k]] = ListLink_FIleCATProductDuplicateLevel
#				print(ListLevelCATIAProductSort[k], ListLink_FIleCATProductDuplicateLevel)
	
	return DictLevels_InfosCATIAProduct, ListLevelCATProductCompare
	
def ReadInfoInPathCADFunc(PathCADSelected):
	
	ListLinkFiles_NameCATPart = []
	ListLinkFiles_NameCATProduct = []
	ListNameFileTrimCATProduct = []
	ListNameFileTrimCATPart = []
	
	ObjectInfosInPath = os.walk(PathCADSelected)
	for root, directories, files in ObjectInfosInPath:
		ListCATPartInFolder = []
		ListCATProductInFolder = []
		
		for i in range(0, len(files), 1):
			if files[i].endswith('.CATProduct'):
				ListCATProductInFolder.append(files[i])
				ListLinkFiles_NameCATProduct.append([root, files[i]])
				ListNameFileTrimCATProduct.append(files[i].split('_')[0])
#				ListNameFileTrimCATProduct.append(files[i][0 : len(files[i]) - len('.CATProduct')])
				
			elif files[i].endswith('.CATPart') or files[i].endswith('.model'):
				ListCATPartInFolder.append(files[i])
				ListLinkFiles_NameCATPart.append([root, files[i]])
				ListNameFileTrimCATPart.append(files[i].split('_')[0])
#				ListNameFileTrimCATPart.append(files[i][0 : len(files[i]) - len('.CATPart')])
			
			elif files[i].endswith('.model'):
				ListCATPartInFolder.append(files[i])
				ListLinkFiles_NameCATPart.append([root, files[i]])
				ListNameFileTrimCATPart.append(files[i].split('_')[0])
#				ListNameFileTrimCATPart.append(files[i][0 : len(files[i]) - len('.model')])

		if len(ListCATPartInFolder)>0 or len(ListCATProductInFolder)>0:
			continue
		
		else:
			if len(directories) == 0:
				print(root + 'Invalid CAD data')

	return ListLinkFiles_NameCATProduct, ListLinkFiles_NameCATPart, ListNameFileTrimCATProduct, ListNameFileTrimCATPart

#************************* Lay thong tin CATProcut va CATPart
def GetInfoOfBOMListFunc(PathBOMSelected):
	
	ListCATProductInBOM = []
	ListLevelCATProductInBOM = []
	ListCATPartInBOM = []	
	InfosLinesBOM = ReadInfoCsvFunc(PathBOMSelected)
	if len(InfosLinesBOM)>0:
		NumRow1st, ListNumnerColm = FindInfosOfRow1stFunc(InfosLinesBOM)
		
		if NumRow1st != None:
			ListNameBOMLine, ListLevelBOMLine = FindInfoCATIANameInBOMFunc(NumRow1st, ListNumnerColm, InfosLinesBOM, ListCATProductInBOM, ListCATPartInBOM, ListLevelCATProductInBOM)
	
	
	return ListCATProductInBOM, ListCATPartInBOM, ListNameBOMLine, ListLevelBOMLine, ListLevelCATProductInBOM

def FindInfoCATIANameInBOMFunc(NumRow1st, ListNumnerColm, InfosLinesBOM, ListCATProductInBOM, ListCATPartInBOM, ListLevelCATProductInBOM):
	
	ListLevelBOMLine = []
	ListNameBOMLine = []
	ListNameParentLine = []
	
	for i in range(NumRow1st + 1, len(InfosLinesBOM), 1):
		SplitBOMLines = InfosLinesBOM[i].split(',')
		if SplitBOMLines[ListNumnerColm[0]] != '':
			ListLevelBOMLine.append(int(SplitBOMLines[ListNumnerColm[0]]))
			ListNameBOMLine.append(SplitBOMLines[ListNumnerColm[1]])
#			ListNameBOMLine.append(SplitBOMLines[ListNumnerColm[1]].replace('/', '_').replace('-', '_'))
	
	if len(ListLevelBOMLine) >0:
		GetInfoLayerOfBOMFunc(ListLevelBOMLine, ListNameBOMLine, ListCATProductInBOM, ListCATPartInBOM, ListLevelCATProductInBOM)
	
	return ListNameBOMLine, ListLevelBOMLine
	
def GetInfoLayerOfBOMFunc(ListLevelBOMLine, ListNameBOMLine, ListCATProductInBOM, ListCATPartInBOM, ListLevelCATProductInBOM):
	
	for i in range(0, len(ListLevelBOMLine), 1):
		ValueIndexLevel = int(ListLevelBOMLine[i])
		try:
			ValueNextLevel = int(ListLevelBOMLine[i+1])
		except:
			ValueNextLevel = None
		else:
			ValueNextLevel = ValueNextLevel
		
		if ValueNextLevel != None:
			if ValueIndexLevel < ValueNextLevel:
#				print(ValueIndexLevel, ListNameBOMLine[i])
				ListCATProductInBOM.append(ListNameBOMLine[i].split('_')[0])
				ListLevelCATProductInBOM.append(ListLevelBOMLine[i])
#				ListCATProductInBOM.append(ListNameBOMLine[i])
			else:
				ListCATPartInBOM.append(ListNameBOMLine[i])		
		
		else:
			if ValueIndexLevel != int(ListLevelBOMLine[i-1]):
#				ListCATProductInBOM.append(ListNameBOMLine[i])
				ListCATProductInBOM.append(ListNameBOMLine[i].split('_')[0])
				ListLevelCATProductInBOM.append(ListLevelBOMLine[i])
			else:
				ListCATPartInBOM.append(ListNameBOMLine[i])			

def FindInfosOfRow1stFunc(InfosLinesBOM):
	
	for i in range(0, len(InfosLinesBOM), 1):
		if InfosLinesBOM[i].find('Level') != -1 and InfosLinesBOM[i].find('BOM Line') != -1:
			SplitBOMLines1st = InfosLinesBOM[i].split(',')
			ListNumnerColm = []
			for k in range(0, len(SplitBOMLines1st), 1):
				if SplitBOMLines1st[k] == 'Level':
					ListNumnerColm.append(k)
				if SplitBOMLines1st[k] == 'BOM Line':
					ListNumnerColm.append(k)
					
			return i, ListNumnerColm

#*********************** Help Funtions****************************
#*********************** Tao Folder Moi dua theo link va ten co san. Gia tri tra ve la link folder moi.

def CreateNewFolderBaseOnLinkFunc(FolderLink, FolderName):
	
	NewPathFolder = path.join(FolderLink, FolderName)
	if not path.exists(NewPathFolder):
		os.makedirs(NewPathFolder)
	
	else:
		NewPathFolder = NewPathFolder
	
	return NewPathFolder

def ReadInfoCsvFunc(PathCsv):
	
	OpenCSVFile = open(PathCsv)
	ReadLinesCSV = OpenCSVFile.readlines()
	
	ListLinesInCSV = []
	for i in range(0, len(ReadLinesCSV), 1):
		ListLinesInCSV.append(ReadLinesCSV[i].strip().replace('/', '_').replace('-', '_'))

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
	
CADAssemblyTool()
CadAssemblyTool_ver01_1807






# PYTHON script
import os
import ansa
from ansa import base
from ansa import constants

from os import path
import shutil

def MoveFuncAssyBaseOnBOM():
	# Need some documentation? Run this with F5

#	PathBOM = "E:/SUV_AWD/BOMlist-TOPVIU0010-001.004-VIRTUAL_VEHICLE_SUV_AWD.csv"
#	PathAssyTemplate = "E:/SUV_AWD/Group Assy Template.csv"
#	PathCADSelected = 'E:/SUV_AWD/CHASSIS'

	PathBOM = "E:\SUV_AWD\BOMlist-TOPVIU0010-001.004-VIRTUAL_VEHICLE_SUV_AWD.csv"
	PathCADSelected = 'E:\SUV_AWD\CHASSIS'
	
	
	InfosLinesBOM = ReadInfoCsvFunc(PathBOM)
	
	if len(InfosLinesBOM)>0:
		ListNameBOMLine, ListLevelBOMLine = GetInfoOfBOMListFunc(InfosLinesBOM)
		if len(ListLevelBOMLine) >0:
			ListAssyInBOMList, ListBOMLineReplace = GetInfoLayer_EntityElementsInBOMFunc(ListNameBOMLine, ListLevelBOMLine)
			if len(ListBOMLineReplace) >0:
#				print(ListBOMLineReplace)
				MoveGroupAssyBaseOnListTemplateFunc(ListAssyInBOMList, ListBOMLineReplace, PathCADSelected)

#************************** Move file theo tung folder assy
def MoveGroupAssyBaseOnListTemplateFunc(ListAssyInBOMList, ListBOMLineReplace, PathCADSelected):
	
		ListFilesExtensionCATIA, ListPathFileExtension, ListAllsFilesCATIAInFolder = ListAllFilesInFolderFunc(PathCADSelected)
		if len(ListAllsFilesCATIAInFolder) >0:
			for i in range(0, len(ListFilesExtensionCATIA), 1):
				PosSearchNameCATIA = FindEntityInListElementsFunc(ListFilesExtensionCATIA[i], ListBOMLineReplace)
	#			print(PosSearchNameCATIA)
				if PosSearchNameCATIA != None:
					NameFolderFuncAssy = ListAssyInBOMList[PosSearchNameCATIA]
					PathFolderAssyName = CreateNewFolderBaseOnLinkFunc(PathCADSelected, NameFolderFuncAssy)
					if PathFolderAssyName:
						PathFileCATIAOld = ListPathFileExtension[i]
						PathFileCATIANew = path.join(PathFolderAssyName, ListAllsFilesCATIAInFolder[i])
						shutil.move(PathFileCATIAOld, PathFileCATIANew)

def ListAllFilesInFolderFunc(PathCADSelected):
	
	ListFilesExtensionCATIA = []
	ListPathFileExtension = []
	ListAllsFilesCATIAInFolder = []
	
	ObjectInfosInPath = os.walk(PathCADSelected)
	for root, directories, files in ObjectInfosInPath:
		
		for i in range(0, len(files), 1):
			if files[i].endswith('.CATProduct'):
				ListPathFileExtension.append(path.join(root, files[i]))
				NameFileCATProduct = files[i][0 : len(files[i]) - len('.CATProduct')]
				ListAllsFilesCATIAInFolder.append(files[i])
				
				NameCATProductReplace = TrimNameBOMLineWithSpaceFunc(NameFileCATProduct)
				if NameCATProductReplace == '':
					NameCATProductReplace = NameFileCATProduct
				ListFilesExtensionCATIA.append(NameCATProductReplace)
				
			elif files[i].endswith('.model'):
				ListPathFileExtension.append(path.join(root, files[i]))
				NameFileCATModel = files[i][0 : len(files[i]) - len('.model')]
				ListAllsFilesCATIAInFolder.append(files[i])
				
				NameCATModelReplace = TrimNameBOMLineWithSpaceFunc(NameFileCATModel)
				if NameCATModelReplace == '':
					NameCATModelReplace = NameFileCATModel
				ListFilesExtensionCATIA.append(NameCATModelReplace)
				
			elif files[i].endswith('.CATPart'):
				ListPathFileExtension.append(path.join(root, files[i]))
				NameFileCATPart = files[i][0 : len(files[i]) - len('.CATPart')]
				ListAllsFilesCATIAInFolder.append(files[i])
				
				NameCATPartReplace = TrimNameBOMLineWithSpaceFunc(NameFileCATPart)
				if NameCATPartReplace == '':
					NameCATPartReplace = NameFileCATPart
				ListFilesExtensionCATIA.append(NameCATPartReplace)
	
	return ListFilesExtensionCATIA, ListPathFileExtension, ListAllsFilesCATIAInFolder	

#************************** Lay thong tin cac dong trong bom list
def GetInfoLayer_EntityElementsInBOMFunc(ListNameBOMLine, ListLevelBOMLine):
	
	ListAssyInBOMList = []
	ListBOMLineReplace = []
	
	ListElementInGroupBIW = FindEntityInGroupsBIWFunc(ListNameBOMLine, ListLevelBOMLine, ListAssyInBOMList, ListBOMLineReplace)
	
	FindEntityInOtherGroupsFunc(ListNameBOMLine, ListLevelBOMLine, ListAssyInBOMList, ListBOMLineReplace, ListElementInGroupBIW)
	
	return ListAssyInBOMList, ListBOMLineReplace
	
def FindEntityInOtherGroupsFunc(ListNameBOMLine, ListLevelBOMLine, ListAssyInBOMList, ListBOMLineReplace, ListElementInGroupBIW):
	
	ListStepOtherGroup = []
	for i in range(0, len(ListLevelBOMLine), 1):
		if ListLevelBOMLine[i] == 3:
			ListStepOtherGroup.append(i)
	
	if len(ListStepOtherGroup) >0:
		ListStepOtherGroup.append(len(ListLevelBOMLine))
		for k in range(0, len(ListStepOtherGroup) -1, 1):
			ListElementInOtherGroup = []
			for j in range(ListStepOtherGroup[k], ListStepOtherGroup[k+1], 1):
				NameElementInOtherGroup = ListNameBOMLine[j]
				LevelOfElemOtherGroup = int(ListLevelBOMLine[j])
				
				PosSearchInGroupBIW =  FindEntityInListElementsFunc(NameElementInOtherGroup, ListElementInGroupBIW)
				if PosSearchInGroupBIW == None:
					if LevelOfElemOtherGroup != 1 and LevelOfElemOtherGroup != 2:
						NameBOMOtherGroupReplace = TrimNameBOMLineWithSpaceFunc(NameElementInOtherGroup)
						if NameBOMOtherGroupReplace == '':
							NameBOMOtherGroupReplace = NameElementInOtherGroup
						ListElementInOtherGroup.append(NameBOMOtherGroupReplace)
			
			if len(ListElementInOtherGroup) >0:
				for w in range(0, len(ListElementInOtherGroup), 1):
					ListAssyInBOMList.append(ListElementInOtherGroup[0])
					ListBOMLineReplace.append(ListElementInOtherGroup[w])
#					print(ListElementInOtherGroup[0], ListElementInOtherGroup[w])
	
def FindEntityInGroupsBIWFunc(ListNameBOMLine, ListLevelBOMLine, ListAssyInBOMList, ListBOMLineReplace):
	
	ListElementInGroupBIW = []
	ListStepBIW = []
	for i in range(0, len(ListLevelBOMLine), 1):
		if ListLevelBOMLine[i] == 1:
			ListStepBIW.append(i)
			
	if len(ListStepBIW) >0:
		ListStepBIW.append(len(ListLevelBOMLine))
		
		for k in range(0, len(ListStepBIW) -1, 1):
			if ListNameBOMLine[ListStepBIW[k]].find('BODY_IN_WHITE') != -1 or ListNameBOMLine[ListStepBIW[k]].find('BIW') != -1:
#				print(ListStepBIW[k], ListStepBIW[k+1])
				NameAssyBIW = 'BIW'
				for j in range(ListStepBIW[k], ListStepBIW[k+1], 1):
					ListAssyInBOMList.append(NameAssyBIW)
					NameFileBOMBiwTrim = ListNameBOMLine[j]
					NameFileBIWRemoveSpace = TrimNameBOMLineWithSpaceFunc(NameFileBOMBiwTrim)
					if NameFileBIWRemoveSpace == '':
						NameFileBIWRemoveSpace = NameFileBOMBiwTrim
					
					ListBOMLineReplace.append(NameFileBIWRemoveSpace)
					
	#				print(NameFileBIWRemoveSpace,NameAssyBIW)
					
					ListElementInGroupBIW.append(ListNameBOMLine[j])
					
	return ListElementInGroupBIW

def TrimNameBOMLineWithSpaceFunc(NameFileNeedTrim):
	
	NameFileRemoveSpace = ''
	NameElementReplace = NameFileNeedTrim.replace('/', '_').replace('-', '_')
	TokenStringName = NameElementReplace.split('_')
	ListLenRemove = []
	ListStepDivideBySpace = []
	for i in range(0, len(TokenStringName), 1):
		if TokenStringName[i] == '':
			ListStepDivideBySpace.append(i)
	
	if len(ListStepDivideBySpace) >0:
		for k in range(0, min(ListStepDivideBySpace), 1):
			ListLenRemove.append(len(TokenStringName[k]))
#			print(TokenStringName[k], len(TokenStringName[k]), k)
	
	if len(ListLenRemove) >0:
		NameFileRemoveSpace = NameElementReplace[0: sum(ListLenRemove) + min(ListStepDivideBySpace) - 1]

	return NameFileRemoveSpace
	
#************************** Lay thong tin CATIA trong BOM List
def GetInfoOfBOMListFunc(InfosLinesBOM):
	
	NumRow1st, ListNumnerColm = FindInfosOfRow1stFunc(InfosLinesBOM)
		
	if NumRow1st != None:
		ListNameBOMLine, ListLevelBOMLine = FindInfoCATIANameInBOMFunc(NumRow1st, ListNumnerColm, InfosLinesBOM)
	
	return ListNameBOMLine, ListLevelBOMLine
	
def FindInfoCATIANameInBOMFunc(NumRow1st, ListNumnerColm, InfosLinesBOM):
	
	ListLevelBOMLine = []
	ListNameBOMLine = []
	ListNameParentLine = []
	
	for i in range(NumRow1st + 1, len(InfosLinesBOM), 1):
		SplitBOMLines = InfosLinesBOM[i].split(',')
		if SplitBOMLines[ListNumnerColm[0]] != '':
			ListLevelBOMLine.append(int(SplitBOMLines[ListNumnerColm[0]]))
			ListNameBOMLine.append(SplitBOMLines[ListNumnerColm[1]])
	
	return ListNameBOMLine, ListLevelBOMLine
			
def FindInfosOfRow1stFunc(InfosLinesBOM):
	
	for i in range(0, len(InfosLinesBOM), 1):
		if InfosLinesBOM[i].find('Level') != -1 and InfosLinesBOM[i].find('BOM Line') != -1:
			SplitBOMLines1st = InfosLinesBOM[i].split(',')
			ListNumnerColm = []
			for k in range(0, len(SplitBOMLines1st), 1):
				if SplitBOMLines1st[k] == 'Level':
					ListNumnerColm.append(k)
				if SplitBOMLines1st[k] == 'BOM Line':
					ListNumnerColm.append(k)	
					
			return i, ListNumnerColm

#******************************* Help Function
def FindEntityInListElementsFunc(EntityElement, ListElements):
	
	try:
		Pos = ListElements.index(EntityElement)
	except:
		Pos = None
	else:
		Pos = Pos
	
	return Pos		
	
def ReadInfoCsvFunc(PathCsv):

	OpenCSVFile = open(PathCsv)
	ReadLinesCSV = OpenCSVFile.readlines()
	
	ListLinesInCSV = []
	for i in range(0, len(ReadLinesCSV), 1):
		ListLinesInCSV.append(ReadLinesCSV[i].strip())

	OpenCSVFile.close()
	
	return ListLinesInCSV

#*********************** Tao Folder Moi dua theo link va ten co san. Gia tri tra ve la link folder moi
def CreateNewFolderBaseOnLinkFunc(FolderLink, FolderName):
	
	NewPathFolder = path.join(FolderLink, FolderName)
	if not path.exists(NewPathFolder):
		os.makedirs(NewPathFolder)
	
	else:
		NewPathFolder = NewPathFolder
	
	return NewPathFolder
	
MoveFuncAssyBaseOnBOM()

MoveFuncAssyBaseOnBOM_0715





# PYTHON script
import os
import ansa
from ansa import base
from ansa import constants

def main():
	# Need some documentation? Run this with F5
	
	ListPartSPOTs = []
	ListPartCONNECTIONs = []
	ListPartSEALING = []
	ListPartINSULs = []
	ListPartNeedCreate = []
	
	AnsaPartsInfos = base.CollectEntities(constants.LSDYNA, None, ['ANSAPART'])
	if len(AnsaPartsInfos)>0:
		for i in range(0, len(AnsaPartsInfos), 1):
#			PropsInParts = base.CollectEntities(constants.LSDYNA, AnsaPartsInfos[i], '__PROPERTIES__', prop_from_entities = True)
#			if len(PropsInParts)>0:
#				for k in range(0, len(PropsInParts), 1):
#					
#					DivideLeftRightPropsFunc(PropsInParts, k)
					
			DividePartNeedCreateFunc(AnsaPartsInfos, i, ListPartSPOTs, ListPartCONNECTIONs, ListPartSEALING, ListPartINSULs, ListPartNeedCreate)
	
	if len(ListPartSPOTs) >0:
		base.Or(ListPartSPOTs)
		base.NewGroupFromVisible('Groups SPOT', '')
	
	if len(ListPartCONNECTIONs) >0:
		base.Or(ListPartCONNECTIONs)
		base.NewGroupFromVisible('Groups CONNECTIONs', '')
	
	if len(ListPartSEALING) >0:
		base.Or(ListPartSEALING)
		base.NewGroupFromVisible('Groups SEAL', '')

	if len(ListPartINSULs) >0:
		base.Or(ListPartINSULs)
		base.NewGroupFromVisible('Groups INSUL', '')
	
	if len(ListPartNeedCreate) >0:
		base.Or(ListPartNeedCreate)
		base.NewGroupFromVisible('Groups NEED', '')

def DividePartNeedCreateFunc(AnsaPartsInfos, i, ListPartSPOTs, ListPartCONNECTIONs, ListPartSEALING, ListPartINSULs, ListPartNeedCreate):
	
	ValsPartCollect = base.GetEntityCardValues(constants.LSDYNA, AnsaPartsInfos[i], ['User/CAD/StringMetaData/PART_TYPE', 'User/CAD/StringMetaData/Nomenclature'])
	NomenClatureParts = ValsPartCollect['User/CAD/StringMetaData/Nomenclature']
	try:
		TypeSpot = ValsPartCollect['User/CAD/StringMetaData/PART_TYPE']
	except:
		TypeSpot = None
	else:
		TypeSpot = TypeSpot
		
	if NomenClatureParts.find('BOLT') != -1 or NomenClatureParts.find('NUT') != -1 or NomenClatureParts.find('SCREW') != -1 or NomenClatureParts.find('CLIP') != -1 or NomenClatureParts.find('STUD') != -1 or NomenClatureParts.find('PLUG') != -1:
		ListPartCONNECTIONs.append(AnsaPartsInfos[i])

	elif NomenClatureParts.find('SEAL') != -1:
		ListPartSEALING.append(AnsaPartsInfos[i])
	elif NomenClatureParts.find('INSUL') != -1:
		ListPartINSULs.append(AnsaPartsInfos[i])
	
	else:
		PropsOnOtherPart = base.CollectEntities(constants.LSDYNA, AnsaPartsInfos[i], '__PROPERTIES__', prop_from_entities = True)
		if len(PropsOnOtherPart) >0:
			for k in range(0, len(PropsOnOtherPart), 1):
				FacesInOtherProps = base.CollectEntities(constants.LSDYNA, PropsOnOtherPart[k], 'FACE')
				ValsPropsOtherPart = base.GetEntityCardValues(constants.LSDYNA, PropsOnOtherPart[k], ['Name', 'User/CAD/Name'])
				NamePropsOtherPart = ValsPropsOtherPart['User/CAD/Name']
				if NamePropsOtherPart.find('BOLT') != -1 or NamePropsOtherPart.find('NUT') != -1 or NamePropsOtherPart.find('SCREW') != -1 or NamePropsOtherPart.find('CLIP') != -1 or NamePropsOtherPart.find('STUD') != -1 or NamePropsOtherPart.find('FLUG') != -1 or NamePropsOtherPart.find('STD') != -1:
					NameConnection = 'CONNECTIONS_' + str(PropsOnOtherPart[k]._id)
					PartInfosConnection = CreateNewPartFunc(NameConnection)
					if PartInfosConnection != None:
						base.SetEntityPart(FacesInOtherProps, PartInfosConnection)
						ListPartCONNECTIONs.append(PartInfosConnection)
						
				elif NamePropsOtherPart.find('SEAL') != -1:
					NameSealing = 'SEAL_' + str(PropsOnOtherPart[k]._id)
					PartInfosSealing = CreateNewPartFunc(NameSealing)
					if PartInfosSealing != None:
						base.SetEntityPart(FacesInOtherProps, PartInfosSealing)
						ListPartSEALING.append(PartInfosSealing)
				elif NamePropsOtherPart.find('INSUL') != -1:
					NameInsul = 'INSUL_' + str(PropsOnOtherPart[k]._id)
					PartInfosInsul = CreateNewPartFunc(NameInsul)
					if PartInfosInsul != None:
						base.SetEntityPart(FacesInOtherProps, PartInfosInsul)
						ListPartINSULs.append(PartInfosInsul)
	
	if TypeSpot == 'JOINING':
		ListPartSPOTs.append(AnsaPartsInfos[i])		
	else:
		ListPartNeedCreate.append(AnsaPartsInfos[i])
			
def DivideLeftRightPropsFunc(PropsInParts, k):
	
	FacesInProps = base.CollectEntities(constants.LSDYNA, PropsInParts[k], 'FACE')
	ConsOnProps = base.CollectEntities(constants.LSDYNA, FacesInProps, 'CONS')
	HotPointsOnProps = base.CollectEntities(constants.LSDYNA, FacesInProps, 'HOT POINT')
					
	ListHotPoinsLH = []
	ListHotPoinsRH = []
	StatusDivide = ''
	for w in range(0, len(HotPointsOnProps), 1):
		ValsHotPoints = base.GetEntityCardValues(constants.LSDYNA, HotPointsOnProps[w], ['X', 'Y', 'Z'])
		if ValsHotPoints['Y'] <0:
			ListHotPoinsRH.append(HotPointsOnProps[w])
		else:
			ListHotPoinsLH.append(HotPointsOnProps[w])
			
	if len(ListHotPoinsRH) >0:
		base.SetEntityCardValues(constants.LSDYNA, PropsInParts[k], {'Labels': 'RH Part'})
	if len(ListHotPoinsLH) >0:
		base.SetEntityCardValues(constants.LSDYNA, PropsInParts[k], {'Labels': 'LH Part'})
	if len(ListHotPoinsRH) >0 and len(ListHotPoinsLH) >0:
		base.SetEntityCardValues(constants.LSDYNA, PropsInParts[k], {'Labels': 'Center Part'})


def CreateNewPartFunc(NamePart):
	
	NewParts = base.NewPart(NamePart, '')
	if NewParts == None:
		EntityPart = base.NameToEnts(NamePart)
		
		NewParts = EntityPart[0]
	
	return NewParts

if __name__ == '__main__':
	main()
MoveGroupAssy_0716



# PYTHON script
import os
import ansa
from ansa import base
from ansa import constants

def main():
	# Need some documentation? Run this with F5

	PartsCollect = base.CollectEntities(constants.LSDYNA, None, ['ANSAPART'])
	if len(PartsCollect) >0:
		
		for i in range(0, len(PartsCollect), 1):
			GetInfoOfPartsFunc(PartsCollect, i)


def GetInfoOfPartsFunc(PartsCollect, i):
	
	ValsPartCollect = base.GetEntityCardValues(constants.LSDYNA, PartsCollect[i], ['Name', 'User/CAD/StringMetaData/Nomenclature', 'User/CAD/StringMetaData/ITEM_ID', 'User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]', 'User/CAD/StringParameterData/ParameterSet\Material'])
#	print(ValsPartCollect['User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]'])
	
	try:
		ThicknessPart = ValsPartCollect['User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]']
	except:
		ThicknessPart = 0.001
	else:
		ThicknessPart = ThicknessPart
	
	try:
		MatNamePart = ValsPartCollect['User/CAD/StringParameterData/ParameterSet\Material']
	except:
		MatNamePart = None
	else:
		MatNamePart = MatNamePart
#	'User/original_name': NameAssyCollect,
	
	PropsInParts = base.CollectEntities(constants.LSDYNA, PartsCollect[i], '__PROPERTIES__', prop_from_entities = True)
	for k in range(0, len(PropsInParts), 1):
		ValsPropInPart = base.GetEntityCardValues(constants.LSDYNA, PropsInParts[k], ['Name', 'User/CAD/OriginalId'])
		base.SetEntityCardValues(constants.LSDYNA, PropsInParts[k], {'PID': ValsPropInPart['User/CAD/OriginalId'], 'Name': ValsPartCollect['User/CAD/StringMetaData/Nomenclature'], 'T1': ThicknessPart, 'NLOC': 1, 'Comment': ValsPartCollect['User/CAD/StringMetaData/ITEM_ID']})
		
	for j in range(0, len(PropsInParts), 1):
		DictGroupsOnProps = base.IsolateConnectivityGroups(PropsInParts[j], separate_at_blue_bounds = 1, separate_at_pid_bounds = 1)
		if len(DictGroupsOnProps) >1:
			del DictGroupsOnProps['group_1']
			for DictGroupName, DictGroupItems in DictGroupsOnProps.items():
				PropsNewDivide = base.CopyEntity(None, PropsInParts[j])
				base.SetEntityCardValues(constants.LSDYNA, PropsNewDivide, {'PID': ValsPropInPart['User/CAD/OriginalId'], 'Name': ValsPartCollect['User/CAD/StringMetaData/Nomenclature'], 'T1': ThicknessPart, 'NLOC': 1, 'Comment': ValsPartCollect['User/CAD/StringMetaData/ITEM_ID', 'User/cad_thickness': PropsInParts[j]._id]})
				for w in range(0, len(DictGroupItems), 1):
					base.SetEntityCardValues(constants.LSDYNA, DictGroupItems[w], {'PID': PropsNewDivide._id})
					

if __name__ == '__main__':
	main()


# PYTHON script
import os
import ansa
from ansa import base
from ansa import constants

def main():
	# Need some documentation? Run this with F5

	PartsCollect = base.CollectEntities(constants.LSDYNA, None, ['ANSAPART'])
	if len(PartsCollect) >0:
		
		for i in range(0, len(PartsCollect), 1):
			GetInfoOfPartsFunc(PartsCollect, i)


def GetInfoOfPartsFunc(PartsCollect, i):
	
	ValsPartCollect = base.GetEntityCardValues(constants.LSDYNA, PartsCollect[i], ['Name', 'User/CAD/StringMetaData/Nomenclature', 'User/CAD/StringMetaData/ITEM_ID', 'User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]', 'User/CAD/StringParameterData/ParameterSet\Material'])
#	print(ValsPartCollect['User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]'])
	
	try:
		ThicknessPart = ValsPartCollect['User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]']
	except:
		ThicknessPart = 0.001
	else:
		ThicknessPart = ThicknessPart
	
	try:
		MatNamePart = ValsPartCollect['User/CAD/StringParameterData/ParameterSet\Material']
	except:
		MatNamePart = None
	else:
		MatNamePart = MatNamePart
#	'User/original_name': NameAssyCollect,
	
	PropsInParts = base.CollectEntities(constants.LSDYNA, PartsCollect[i], '__PROPERTIES__', prop_from_entities = True)
	for k in range(0, len(PropsInParts), 1):
		ValsPropInPart = base.GetEntityCardValues(constants.LSDYNA, PropsInParts[k], ['Name', 'User/CAD/OriginalId'])
		base.SetEntityCardValues(constants.LSDYNA, PropsInParts[k], {'PID': ValsPropInPart['User/CAD/OriginalId'], 'Name': ValsPartCollect['User/CAD/StringMetaData/Nomenclature'], 'T1': ThicknessPart, 'NLOC': 1, 'Comment': ValsPartCollect['User/CAD/StringMetaData/ITEM_ID']})
		
	for j in range(0, len(PropsInParts), 1):
		DictGroupsOnProps = base.IsolateConnectivityGroups(PropsInParts[j], separate_at_blue_bounds = 1, separate_at_pid_bounds = 1)
		if len(DictGroupsOnProps) >1:
			del DictGroupsOnProps['group_1']
			for DictGroupName, DictGroupItems in DictGroupsOnProps.items():
				PropsNewDivide = base.CopyEntity(None, PropsInParts[j])
				base.SetEntityCardValues(constants.LSDYNA, PropsNewDivide, {'PID': ValsPropInPart['User/CAD/OriginalId'], 'Name': ValsPartCollect['User/CAD/StringMetaData/Nomenclature'], 'T1': ThicknessPart, 'NLOC': 1, 'Comment': ValsPartCollect['User/CAD/StringMetaData/ITEM_ID', 'User/cad_thickness': PropsInParts[j]._id]})
				for w in range(0, len(DictGroupItems), 1):
					base.SetEntityCardValues(constants.LSDYNA, DictGroupItems[w], {'PID': PropsNewDivide._id})
					

if __name__ == '__main__':
	main()


# PYTHON script
import os
import ansa
from ansa import base
from ansa import constants

def main():
	# Need some documentation? Run this with F5

	PartsCollect = base.CollectEntities(constants.LSDYNA, None, ['ANSAPART'])
	if len(PartsCollect) >0:
		
		for i in range(0, len(PartsCollect), 1):
			GetInfoOfPartsFunc(PartsCollect, i)


def GetInfoOfPartsFunc(PartsCollect, i):
	
	ValsPartCollect = base.GetEntityCardValues(constants.LSDYNA, PartsCollect[i], ['Name', 'User/CAD/StringMetaData/Nomenclature', 'User/CAD/StringMetaData/ITEM_ID', 'User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]', 'User/CAD/StringParameterData/ParameterSet\Material'])
#	print(ValsPartCollect['User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]'])
	
	try:
		ThicknessPart = ValsPartCollect['User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]']
	except:
		ThicknessPart = 0.001
	else:
		ThicknessPart = ThicknessPart
	
	try:
		MatNamePart = ValsPartCollect['User/CAD/StringParameterData/ParameterSet\Material']
	except:
		MatNamePart = None
	else:
		MatNamePart = MatNamePart
#	'User/original_name': NameAssyCollect,
	
	PropsInParts = base.CollectEntities(constants.LSDYNA, PartsCollect[i], '__PROPERTIES__', prop_from_entities = True)
	for k in range(0, len(PropsInParts), 1):
		ValsPropInPart = base.GetEntityCardValues(constants.LSDYNA, PropsInParts[k], ['Name', 'User/CAD/OriginalId'])
		base.SetEntityCardValues(constants.LSDYNA, PropsInParts[k], {'PID': ValsPropInPart['User/CAD/OriginalId'], 'Name': ValsPartCollect['User/CAD/StringMetaData/Nomenclature'], 'T1': ThicknessPart, 'NLOC': 1, 'Comment': ValsPartCollect['User/CAD/StringMetaData/ITEM_ID']})
		
	for j in range(0, len(PropsInParts), 1):
		DictGroupsOnProps = base.IsolateConnectivityGroups(PropsInParts[j], separate_at_blue_bounds = 1, separate_at_pid_bounds = 1)
		if len(DictGroupsOnProps) >1:
			del DictGroupsOnProps['group_1']
			for DictGroupName, DictGroupItems in DictGroupsOnProps.items():
				PropsNewDivide = base.CopyEntity(None, PropsInParts[j])
				base.SetEntityCardValues(constants.LSDYNA, PropsNewDivide, {'PID': ValsPropInPart['User/CAD/OriginalId'], 'Name': ValsPartCollect['User/CAD/StringMetaData/Nomenclature'], 'T1': ThicknessPart, 'NLOC': 1, 'Comment': ValsPartCollect['User/CAD/StringMetaData/ITEM_ID', 'User/cad_thickness': PropsInParts[j]._id]})
				for w in range(0, len(DictGroupItems), 1):
					base.SetEntityCardValues(constants.LSDYNA, DictGroupItems[w], {'PID': PropsNewDivide._id})
					

if __name__ == '__main__':
	main()



# PYTHON script
import os
import ansa
from ansa import base
from ansa import constants

def main():
	# Need some documentation? Run this with F5

	PartsCollect = base.CollectEntities(constants.LSDYNA, None, ['ANSAPART'])
	if len(PartsCollect) >0:
		
		for i in range(0, len(PartsCollect), 1):
			GetInfoOfPartsFunc(PartsCollect, i)


def GetInfoOfPartsFunc(PartsCollect, i):
	
	ValsPartCollect = base.GetEntityCardValues(constants.LSDYNA, PartsCollect[i], ['Name', 'User/CAD/StringMetaData/Nomenclature', 'User/CAD/StringMetaData/ITEM_ID', 'User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]', 'User/CAD/StringParameterData/ParameterSet\Material'])
#	print(ValsPartCollect['User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]'])
	
	try:
		ThicknessPart = ValsPartCollect['User/CAD/DoubleParameterData/ParameterSet\Thickness [mm]']
	except:
		ThicknessPart = 0.001
	else:
		ThicknessPart = ThicknessPart
	
	try:
		MatNamePart = ValsPartCollect['User/CAD/StringParameterData/ParameterSet\Material']
	except:
		MatNamePart = None
	else:
		MatNamePart = MatNamePart
#	'User/original_name': NameAssyCollect,
	
	PropsInParts = base.CollectEntities(constants.LSDYNA, PartsCollect[i], '__PROPERTIES__', prop_from_entities = True)
	for k in range(0, len(PropsInParts), 1):
		ValsPropInPart = base.GetEntityCardValues(constants.LSDYNA, PropsInParts[k], ['Name', 'User/CAD/OriginalId'])
		base.SetEntityCardValues(constants.LSDYNA, PropsInParts[k], {'PID': ValsPropInPart['User/CAD/OriginalId'], 'Name': ValsPartCollect['User/CAD/StringMetaData/Nomenclature'], 'T1': ThicknessPart, 'NLOC': 1, 'Comment': ValsPartCollect['User/CAD/StringMetaData/ITEM_ID']})
		
	for j in range(0, len(PropsInParts), 1):
		DictGroupsOnProps = base.IsolateConnectivityGroups(PropsInParts[j], separate_at_blue_bounds = 1, separate_at_pid_bounds = 1)
		if len(DictGroupsOnProps) >1:
			del DictGroupsOnProps['group_1']
			for DictGroupName, DictGroupItems in DictGroupsOnProps.items():
				PropsNewDivide = base.CopyEntity(None, PropsInParts[j])
				base.SetEntityCardValues(constants.LSDYNA, PropsNewDivide, {'PID': ValsPropInPart['User/CAD/OriginalId'], 'Name': ValsPartCollect['User/CAD/StringMetaData/Nomenclature'], 'T1': ThicknessPart, 'NLOC': 1, 'Comment': ValsPartCollect['User/CAD/StringMetaData/ITEM_ID', 'User/cad_thickness': PropsInParts[j]._id]})
				for w in range(0, len(DictGroupItems), 1):
					base.SetEntityCardValues(constants.LSDYNA, DictGroupItems[w], {'PID': PropsNewDivide._id})
					

if __name__ == '__main__':
	main()

SetupInfoCADPart_0716
D:\Kyty180389\Script\02.Cad Assembly Tool
