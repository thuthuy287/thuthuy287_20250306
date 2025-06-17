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

















