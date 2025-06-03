# PYTHON script
import os
import ansa
from ansa import *
import math

deck_infos = constants.LSDYNA
@session.defbutton('6_CONNECTION', 'ConvertCADToConnectionBoltTool','Convert cad sang điểm connection points ....')
def ConvertCADToConnectionBoltTool():
	# Need some documentation? Run this with F5

	TopWindow = guitk.BCWindowCreate("Convert Cad To Connections Tool version 1.0", guitk.constants.BCOnExitDestroy)
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Action", guitk.constants.BCVertical)
	BCRadioButton_2 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Convert Cad To Connection", None, 0)
	guitk.BCRadioButtonSetChecked(BCRadioButton_2, True)
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_1 = guitk.BCLabelCreate(TopWindow, "")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	_window = [BCProgressBar_1, BCLabel_1, BCRadioButton_2]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, _window)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, _window)
	
	guitk.BCShow(TopWindow)

def RejectFunc(TopWindow, _window):
	
	return 1

#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, _window):
	
	ProgBar = _window[0]
	IndexLabel = _window[1]
	IndexConvertCad = _window[2]
	
	PartBoltCad = base.CollectEntities(deck_infos, None, ['ANSAPART'], filter_visible = True)
	if len(PartBoltCad) >0:
		StepRun = 0
		DictSimilarPartsReq = FindSimilarGroupsCadFunc(PartBoltCad)
		if len(DictSimilarPartsReq) >0:
			guitk.BCProgressBarSetTotalSteps(ProgBar, len(DictSimilarPartsReq))
			for Similar_status,  ListInfosPartsConnect in DictSimilarPartsReq.items():
				if Similar_status.find('similar_group') != -1:
					CreateConnectionOnSimilarGroupFunc(ListInfosPartsConnect, Similar_status, ProgBar)
				
				else:
					CreateConnectionOnOtherGroupFunc(ListInfosPartsConnect, Similar_status, ProgBar)
			
				guitk.BCProgressBarSetProgress(ProgBar, StepRun+1)
				StepRun +=1

######******************* Tạo điểm connection point của những part giống nhau ****************************
def CreateConnectionOnOtherGroupFunc(ListInfosOtherParts, Similar_status, ProgBar):
	
	for SingleOtherParts in ListInfosOtherParts:
#		print(SingleOtherParts._id)
		CreateConnectionOnSimilarGroupFunc([SingleOtherParts], Similar_status, ProgBar)


######******************* Tạo điểm connection point của những part giống nhau ****************************
def CreateConnectionOnSimilarGroupFunc(ListInfosPartsConnect, Similar_status, ProgBar):
	base.Or(ListInfosPartsConnect)
#	print(ListInfosPartsConnect[0]._id)
	FacesOnPartsSimilar = base.CollectEntities(deck_infos, ListInfosPartsConnect[0], ['FACE'])
	ListConsOnPartsSimilar = base.CollectEntities(deck_infos, FacesOnPartsSimilar, ['CONS'])
	
	ValsPartsSimilar = ListInfosPartsConnect[0].get_entity_values(deck_infos, ['COG x', 'COG y', 'COG z', 'Size max', 'User/CAD/DoubleParameterData/ParameterSet\d [mm]', 'User/CAD/DoubleParameterData/ParameterSet\D [mm]'])
	AxisCogPartsSimilar = [ValsPartsSimilar['COG x'], ValsPartsSimilar['COG y'], ValsPartsSimilar['COG z']]
	InfosMaxDistanceOfParts = FindMaxSizeOfPartsBoltFunc(FacesOnPartsSimilar)
#	InfosMaxDistanceOfParts = ValsPartsSimilar['Size max']
#	print(InfosMaxDistanceOfParts)
	ListAxisVecsOfParts, InfosAxisPointsProj, StatusTypeOfParts, ListConsAddVecsOfNut = FindVecsInConnectionFunc(ListConsOnPartsSimilar, FacesOnPartsSimilar, AxisCogPartsSimilar, InfosMaxDistanceOfParts)

#	print(InfosAxisPointsProj)
	if len(ListAxisVecsOfParts) >0:
		if StatusTypeOfParts == 'BOLT':
			SizeOfBoltParts = ValsPartsSimilar['User/CAD/DoubleParameterData/ParameterSet\d [mm]']
			if SizeOfBoltParts == '' or SizeOfBoltParts == None:
				SizeOfBoltParts = CalculateDiameterOfBoltPartsFunc(AxisCogPartsSimilar, InfosAxisPointsProj, ListConsOnPartsSimilar, ListInfosPartsConnect)
			
			CreateInfosConnectionBoltToSimilarPartsFunc(AxisCogPartsSimilar, ListAxisVecsOfParts, SizeOfBoltParts, ListInfosPartsConnect, InfosMaxDistanceOfParts, Similar_status, StatusTypeOfParts)
		
		if StatusTypeOfParts == 'NUT':
			SizeOfNutParts = ValsPartsSimilar['User/CAD/DoubleParameterData/ParameterSet\D [mm]']
			if SizeOfNutParts == '' or SizeOfNutParts == None:
				SizeOfNutParts = CalculateDiameterOfNutPartsFunc(AxisCogPartsSimilar, ListConsOnPartsSimilar, ListInfosPartsConnect, ListAxisVecsOfParts, ListConsAddVecsOfNut)

			InfosMaxDistanceOfParts = ValsPartsSimilar['Size max']
			CreateInfosConnectionBoltToSimilarPartsFunc(AxisCogPartsSimilar, ListAxisVecsOfParts, SizeOfNutParts, ListInfosPartsConnect, InfosMaxDistanceOfParts, Similar_status, StatusTypeOfParts)

######### ******************* Tao connection cho cac part bolt similar ****************************
def CreateInfosConnectionBoltToSimilarPartsFunc(AxisCogPartsSimilar, ListAxisVecsOfParts, SizeOfBoltParts, ListInfosPartsConnect, InfosMaxDistanceOfParts, Similar_status, StatusTypeOfParts):
#	print(SizeOfBoltParts)
	RoundSizeConnection = round(float(SizeOfBoltParts), 0)
	ConnectionOfPart = connections.CreateConnectionPoint(type = 'Bolt_Type', position = AxisCogPartsSimilar)
	base.SetEntityCardValues(constants.LSDYNA, ConnectionOfPart, {'DX': ListAxisVecsOfParts[0], 'DY': ListAxisVecsOfParts[1], 'DZ': ListAxisVecsOfParts[2], 'Length': InfosMaxDistanceOfParts*2/3, 'D': RoundSizeConnection, 'Washer': RoundSizeConnection})
	base.SetEntityPart(ConnectionOfPart, ListInfosPartsConnect[0])
	SetupInfosPropsPartsConnectionFunc(ListInfosPartsConnect, RoundSizeConnection, StatusTypeOfParts)
	
	if Similar_status.find('similar_group') != -1:
		base.BreakPartInstances(ListInfosPartsConnect)
		MasterPartsInstances = ListInfosPartsConnect[0]
		for i in range(1, len(ListInfosPartsConnect), 1):
			print('Create Part Instances ' + str(i+1) + '/' + str(len(ListInfosPartsConnect)))
			SlavePartsInstances = ListInfosPartsConnect[i]
			base.ConnectPartInstances(MasterPartsInstances, SlavePartsInstances)
	
		dm.SyncRepresentation(ListInfosPartsConnect)
		print('Next Step....')

######### ******************* Thiet dinh pid va part cho cac part cung duong kinh bolt ****************************
def SetupInfosPropsPartsConnectionFunc(ListInfosPartsConnect, RoundSizeConnection, StatusTypeOfParts):
	
	
	NameProps = StatusTypeOfParts + '-M' + str(int(RoundSizeConnection))
	PropsIds = int(str(int(RoundSizeConnection))+str(int(RoundSizeConnection))+str(int(RoundSizeConnection)))
	
	NewPropsConnection = base.CreateEntity(deck_infos, 'SECTION_SHELL', {'Name':  NameProps, 'PID': PropsIds})
	if NewPropsConnection == None:
		NewPropsConnection = base.GetEntity(deck_infos, 'SECTION_SHELL', PropsIds)

	AllsFacesOnParts = FacesOnPartsSimilar = base.CollectEntities(deck_infos, ListInfosPartsConnect, ['FACE'])
	for i in range(0, len(AllsFacesOnParts), 1):
		base.SetEntityCardValues(deck_infos, AllsFacesOnParts[i], {'PID': PropsIds})

######### ******************* Do duong kinh cua NUT ****************************
def CalculateDiameterOfNutPartsFunc(AxisCogPartsSimilar, ListConsOnPartsSimilar, ListInfosPartsConnect, ListAxisVecsOfParts, ListConsAddVecsOfNut):
	
	ListDiaHotPointToMiddleCurve = []
	InfosNewCurveNUT = CreateCurveOnNUTPartsFunc(AxisCogPartsSimilar, ListAxisVecsOfParts)
	if InfosNewCurveNUT != None:
		ConsWithMinDistanceReq = FindConsWithMinDistanceToCOGFunc(InfosNewCurveNUT, ListConsAddVecsOfNut)
		if ConsWithMinDistanceReq != None:
			ListHotPointsCalculateDiaReq = FindHotPointsCaculateDiameterOfNUTFunc(ConsWithMinDistanceReq, ListAxisVecsOfParts)
			if len(ListHotPointsCalculateDiaReq) >0:
				for i in range(0, len(ListHotPointsCalculateDiaReq), 1):
					ProjHotPointToMiddleCurve = base.ProjectPoint(float(ListHotPointsCalculateDiaReq[i][0]), float(ListHotPointsCalculateDiaReq[i][1]), float(ListHotPointsCalculateDiaReq[i][2]), InfosNewCurveNUT)
					AxisPointsProjHotPointsToCurves = [ProjHotPointToMiddleCurve[1], ProjHotPointToMiddleCurve[2], ProjHotPointToMiddleCurve[3]]
					ListDiaHotPointToMiddleCurve.append(CalculateDistance2PointsFunc(ListHotPointsCalculateDiaReq[i], AxisPointsProjHotPointsToCurves))
			
	base.DeleteEntity(InfosNewCurveNUT, True)
	return max(ListDiaHotPointToMiddleCurve)*2

############# ******************* Tim cac diem Hot point khong dong phang voi cac diem hot point thuoc duong cons nho nhat ****************************	
def FindHotPointsCaculateDiameterOfNUTFunc(ConsWithMinDistanceReq, ListAxisVecsOfParts):
	
	ListHotPointsCalculateDiaReq = []
#	print(ConsWithMinDistanceReq._id)
	HotPointsOnConsMinReq = base.CollectEntities(deck_infos, ConsWithMinDistanceReq, ['HOT POINT'])
	FacesOnConsMinReq = base.GetFacesOfCons(ConsWithMinDistanceReq)
	for i in range(0, len(HotPointsOnConsMinReq), 1):
		AxisHotPointsOnConsMin = HotPointsOnConsMinReq[i].position
		InfosFacesReferenHotPointMin = base.GetFacesOfHotPoints(HotPointsOnConsMinReq[i])
		InfosFaceOnHotPoints = list( set(InfosFacesReferenHotPointMin).difference(FacesOnConsMinReq))
		HotPointsOnFaceReferen = base.CollectEntities(deck_infos, InfosFaceOnHotPoints, ['HOT POINT'])
		HotPointsOnFaceReferen.remove(HotPointsOnConsMinReq[i])
#		aaaa = base.CreateEntity(constants.NASTRAN, "SET")	
#		base.AddToSet(aaaa, HotPointsOnFaceReferen)
		for k in range(0, len(HotPointsOnFaceReferen), 1):
			AxisHotPointsOnFacesReferen = HotPointsOnFaceReferen[k].position
			ProjHPointsReferenToConsMin = base.ProjectPoint(AxisHotPointsOnFacesReferen[0], AxisHotPointsOnFacesReferen[1], AxisHotPointsOnFacesReferen[2], ConsWithMinDistanceReq)
			if ProjHPointsReferenToConsMin[0] ==2:
				AxisProjHPointsReferenResult = [ProjHPointsReferenToConsMin[1], ProjHPointsReferenToConsMin[2], ProjHPointsReferenToConsMin[3]]
				DistanceAxisProjPointResultToHPointMin = CalculateDistance2PointsFunc(AxisProjHPointsReferenResult, AxisHotPointsOnConsMin)
#				print(DistanceAxisProjPointResultToHPointMin)
				if round(DistanceAxisProjPointResultToHPointMin,6) != 0:
					ListHotPointsCalculateDiaReq.append(AxisHotPointsOnFacesReferen)
	
	return ListHotPointsCalculateDiaReq
		
############# ******************* Do khoang cach tu cac duong cons toi tam part va tim ra duong cons co khoang cach nho nhat ****************************
def FindConsWithMinDistanceToCOGFunc(InfosNewCurveNUT, ListConsAddVecsOfNut):
	ListDistanceConsToMiddleCurves = []
	
	for i in range(0, len(ListConsAddVecsOfNut), 1):
		ValsConsNUT = base.GetEntityCardValues(deck_infos, ListConsAddVecsOfNut[i], ['End Point', 'Start Point'])
		AxisStartPointOfConsNUT = ValsConsNUT['Start Point'].split(',')
		AxisStartPointOfConsReq = [float(AxisStartPointOfConsNUT[0]), float(AxisStartPointOfConsNUT[1]), float(AxisStartPointOfConsNUT[2])]
		ProjStartPointToMiddleCurves = base.ProjectPoint(float(AxisStartPointOfConsNUT[0]), float(AxisStartPointOfConsNUT[1]), float(AxisStartPointOfConsNUT[2]), InfosNewCurveNUT)
		CoordinatesOfResultProj = [ProjStartPointToMiddleCurves[1], ProjStartPointToMiddleCurves[2], ProjStartPointToMiddleCurves[3]]
		ListDistanceConsToMiddleCurves.append(CalculateDistance2PointsFunc(AxisStartPointOfConsReq, CoordinatesOfResultProj))
	
	if len(ListDistanceConsToMiddleCurves) >0:
		IndexMinDistanceToCOGParts = ListDistanceConsToMiddleCurves.index(min(ListDistanceConsToMiddleCurves))
		ConsWithMinDistanceReq = ListConsAddVecsOfNut[IndexMinDistanceToCOGParts]
	else:
		ConsWithMinDistanceReq = None
		
	return ConsWithMinDistanceReq

############# ******************* Tao curve tu tam va theo vector cua part nut ****************************
def CreateCurveOnNUTPartsFunc(AxisCogPartsSimilar, ListAxisVecsOfParts):
	
	NewAxisRelativePoints = [ListAxisVecsOfParts[0] + AxisCogPartsSimilar[0], ListAxisVecsOfParts[1] + AxisCogPartsSimilar[1], ListAxisVecsOfParts[2] + AxisCogPartsSimilar[2]]
	
	InfosCoordNUT_X = [AxisCogPartsSimilar[0], NewAxisRelativePoints[0]]
	InfosCoordNUT_Y = [AxisCogPartsSimilar[1], NewAxisRelativePoints[1]]
	InfosCoordNUT_Z = [AxisCogPartsSimilar[2], NewAxisRelativePoints[2]]
	InfosNewCurveNUT = base.CreateCurve(len(InfosCoordNUT_X), InfosCoordNUT_X, InfosCoordNUT_Y, InfosCoordNUT_Z)
	
	return InfosNewCurveNUT

######### ******************* Do duong kinh cua BOLT ****************************
def CalculateDiameterOfBoltPartsFunc(AxisCogPartsSimilar, InfosAxisPointsProj, ListConsOnPartsSimilar, ListInfosPartsConnect):
	
	DistanceProjToCurves = []
	
	InfosCoordCurve_X = [AxisCogPartsSimilar[0], InfosAxisPointsProj[0]]
	InfosCoordCurve_Y = [AxisCogPartsSimilar[1], InfosAxisPointsProj[1]]
	InfosCoordCurve_Z = [AxisCogPartsSimilar[2], InfosAxisPointsProj[2]]
	InfosNewCurveParts = base.CreateCurve(len(InfosCoordCurve_X), InfosCoordCurve_X, InfosCoordCurve_Y, InfosCoordCurve_Z)
	
	HotPointsOnPartsBolt = base.CollectEntities(deck_infos, ListConsOnPartsSimilar, ['HOT POINT'])
	for i in range(0, len(HotPointsOnPartsBolt), 1):
		AxisOfHotPoints = HotPointsOnPartsBolt[i].position
		ProjPointToCurveParts = base.ProjectPoint(AxisOfHotPoints[0], AxisOfHotPoints[1], AxisOfHotPoints[2], InfosNewCurveParts)
		if ProjPointToCurveParts[0] == 1:
			AxisPointProjToCurveReq = [ProjPointToCurveParts[1], ProjPointToCurveParts[2], ProjPointToCurveParts[3]]
			DistanceProjToCurves.append(CalculateDistance2PointsFunc(AxisOfHotPoints, AxisPointProjToCurveReq))
	
	DiamterOfBoltParts = round(max(DistanceProjToCurves)*2, 0)
	base.DeleteEntity(InfosNewCurveParts, True)
	
	return DiamterOfBoltParts

######### ******************* Tim kich co lon nhat cua part bolt ****************************
def FindMaxSizeOfPartsBoltFunc(InfosFaceConnect):
	ListFacesConnectChecked = []
	ListMaxDistanceParts = []
	for SingleFace1st in InfosFaceConnect:
		CogOfFace1st = base.Cog(SingleFace1st)
		VecsOfFaces1st = base.GetFaceOrientation(SingleFace1st)
		for SingleFace2nd in InfosFaceConnect:
			if SingleFace2nd != SingleFace1st:
				ProjCogFaces1st = base.ProjectPointDirectional(target = SingleFace2nd,
																					point_x = CogOfFace1st[0],
																					point_y = CogOfFace1st[1],
																					point_z = CogOfFace1st[2],
																					vec_x = VecsOfFaces1st[0],
																					vec_y = VecsOfFaces1st[1],
																					vec_z = VecsOfFaces1st[2],
																					tolerance = 1000,
																					project_on = 'faces')
				if ProjCogFaces1st != None:
#					base.Newpoint(ProjCogFaces1st[0], ProjCogFaces1st[1], ProjCogFaces1st[2])
					ListMaxDistanceParts.append(CalculateDistance2PointsFunc(CogOfFace1st, ProjCogFaces1st))
					
	return max(ListMaxDistanceParts)

######### ******************* Tim vector cua connection ****************************
def FindVecsInConnectionFunc(ListConsImport, InfosFacesImport, InfosAxisCogParts, InfosMaxSizePartsSimilar):
	
	InfosAxisVecsReq = []
	AxisPointsWithMaxDistanceProj = []
	StatusTypeOfParts = None
	ListConsAddVecsOfNut = []
	ListConsMaxRadius = FindConsWithMaxRadiusFunc(ListConsImport)
	
	if len(ListConsMaxRadius) >0:
		DictConsMaxR_InfosProject = {}
		DictConsMaxR_InfosStatusProject = {}
		for i in range(0, len(ListConsMaxRadius), 1):
			ValsConsMaxR = base.GetEntityCardValues(deck_infos, ListConsMaxRadius[i], ['End Point', 'Start Point'])
			AxisStartConsMaxR = ValsConsMaxR['Start Point'].split(',')
			AxisEndConsMaxR = ValsConsMaxR['End Point'].split(',')
			VecsOfConsMaxR = [float(AxisStartConsMaxR[0]) - float(AxisEndConsMaxR[0]), float(AxisStartConsMaxR[1]) - float(AxisEndConsMaxR[1]), float(AxisStartConsMaxR[2]) - float(AxisEndConsMaxR[2])]
			
			ListPointsProjected, InfosDistanceProjected = ProjectCogPartToSingleFaceOnPartsFunc(InfosFacesImport, InfosAxisCogParts, VecsOfConsMaxR)
			if len(ListPointsProjected) >0:
				DictConsMaxR_InfosProject[ListConsMaxRadius[i]] = [ListPointsProjected, InfosDistanceProjected]
			else:
				ListConsAddVecsOfNut.append(ListConsMaxRadius[i])
				DictConsMaxR_InfosStatusProject[ListConsMaxRadius[i]]= ListPointsProjected
		
#		print(len(DictConsMaxR_InfosProject), len(ListConsMaxRadius))
		if len(DictConsMaxR_InfosProject) == len(ListConsMaxRadius):
			StatusTypeOfParts = 'BOLT'
			ListVecsCalculated, ListAxisPointsMaxRCalculated = FindConsWithMaxDistanceProjectFunc(DictConsMaxR_InfosProject, InfosAxisCogParts, InfosMaxSizePartsSimilar, AxisPointsWithMaxDistanceProj, InfosAxisVecsReq)
			if len(ListVecsCalculated) >0:
				InfosAxisVecsReq = ListVecsCalculated
				AxisPointsWithMaxDistanceProj = ListAxisPointsMaxRCalculated
		else:
			StatusTypeOfParts = 'NUT'
#			print(StatusTypeOfParts)
			for KeyConsMaxR, ValsStatusProject in DictConsMaxR_InfosStatusProject.items():
				if len(ValsStatusProject) == 0:
					ValsConsOfNUT = base.GetEntityCardValues(deck_infos, KeyConsMaxR, ['End Point', 'Start Point'])
					AxisStartConsNUT = ValsConsOfNUT['Start Point'].split(',')
					AxisEndConsNUT = ValsConsOfNUT['End Point'].split(',')
					InfosAxisVecsReq = [float(AxisStartConsNUT[0]) - float(AxisEndConsNUT[0]), float(AxisStartConsNUT[1]) - float(AxisEndConsNUT[1]), float(AxisStartConsNUT[2]) - float(AxisEndConsNUT[2])]
					break
			
	return InfosAxisVecsReq, AxisPointsWithMaxDistanceProj, StatusTypeOfParts, ListConsAddVecsOfNut

def FindConsWithMaxDistanceProjectFunc(DictConsMaxR_InfosProject, InfosAxisCogParts, InfosMaxSizePartsSimilar, AxisPointsWithMaxDistanceProj, InfosAxisVecsReq):
	
	ListVecsCalculated = []
	ListAxisPointsMaxRCalculated = []
	
	for KeysConsMaxR, ValsInfosProjected in DictConsMaxR_InfosProject.items():
		InfosDistanceCalculate = FindMaxDistanceOnListPointsFunc(ValsInfosProjected[0])
		if max(InfosDistanceCalculate) > InfosMaxSizePartsSimilar:
			InfosCheckMaxDistance = max(InfosDistanceCalculate) - InfosMaxSizePartsSimilar
		else:
			InfosCheckMaxDistance = InfosMaxSizePartsSimilar - max(InfosDistanceCalculate)
		
#		print(max(InfosDistanceCalculate), InfosMaxSizePartsSimilar, InfosCheckMaxDistance)
		if InfosCheckMaxDistance <=0.1:
			IndexMaxDistanceProj = ValsInfosProjected[1].index(max(ValsInfosProjected[1]))
			ListAxisPointsMaxRCalculated = ValsInfosProjected[0][IndexMaxDistanceProj]
			ListVecsCalculated = [ListAxisPointsMaxRCalculated[0] - InfosAxisCogParts[0], ListAxisPointsMaxRCalculated[1] - InfosAxisCogParts[1], ListAxisPointsMaxRCalculated[2] - InfosAxisCogParts[2]]
#			base.Newpoint(ListAxisPointsMaxRCalculated[0], ListAxisPointsMaxRCalculated[1], ListAxisPointsMaxRCalculated[2])
			break
			
	return ListVecsCalculated, ListAxisPointsMaxRCalculated

########### ******************* Do khoang cach giua cac diem point project to face ****************************
def FindMaxDistanceOnListPointsFunc(InfosPointsCalculate):
	
	ListInfosPointsChecked = []
	ListDistancePointsCalculate = []
	for SinglePoints1st in InfosPointsCalculate:
		for SinglePoints2nd in InfosPointsCalculate:
			PosSearchPoints2nd = FindEntityInListElementsFunc(SinglePoints2nd, ListInfosPointsChecked)
			if PosSearchPoints2nd == None:
				DistancePoints1stToPoints2nd = CalculateDistance2PointsFunc(SinglePoints1st, SinglePoints2nd)
				ListDistancePointsCalculate.append(DistancePoints1stToPoints2nd)
	
	return ListDistancePointsCalculate					

########## ******************* Tu toa do diem tam cua part, project toi cac face trong part, ket qua tra ve la list toa do diem point project va list cons khong project duoc ****************************
def ProjectCogPartToSingleFaceOnPartsFunc(InfosFacesImport, InfosAxisCogParts, VecsOfConsMaxR):
	
	InfosPointsProjected = []
	InfosDistanceProjected = []
	for k in range(0, len(InfosFacesImport), 1):
		ProjDirectionStatus = base.ProjectPointDirectional(target = InfosFacesImport[k],
																					point_x = InfosAxisCogParts[0],
																					point_y = InfosAxisCogParts[1],
																					point_z = InfosAxisCogParts[2],
																					vec_x = VecsOfConsMaxR[0],
																					vec_y = VecsOfConsMaxR[1],
																					vec_z = VecsOfConsMaxR[2],
																					tolerance = 100,
																					project_on = 'faces')
#		print(ProjDirectionStatus)		
		if ProjDirectionStatus != None:
			InfosPointsProjected.append(ProjDirectionStatus)
			InfosDistanceProjected.append(CalculateDistance2PointsFunc(InfosAxisCogParts, ProjDirectionStatus))
#			base.Newpoint(ProjDirectionStatus[0], ProjDirectionStatus[1], ProjDirectionStatus[2])
	return InfosPointsProjected, InfosDistanceProjected	
	
######### ******************* Tim các đường Cons có độ dài > 1000 (đường thẳng) ****************************
def FindConsWithMaxRadiusFunc(ListConsImport):
	
	ListConsMaxRadius = []
	for i in range(0, len(ListConsImport), 1):
		ValsConsMaxRadius = base.GetEntityCardValues(deck_infos, ListConsImport[i], ['Min Radius', 'Start Vector', 'Length'])
		if float(ValsConsMaxRadius['Min Radius']) >1000:
			ListConsMaxRadius.append(ListConsImport[i])
	
	return ListConsMaxRadius

####******************* Find Similar group cad****************************
def FindSimilarGroupsCadFunc(PartBoltCad):
	
	FacesCollect = base.CollectEntities(deck_infos, PartBoltCad, ['FACE'])
	DictSimilarPartsReq = {}
	ListPartsFacesSimilar = []
	if len(FacesCollect) >0:
		DictSimilarGroup = base.IsolateSimilarGroups(entities = FacesCollect,
																			separate_at_blue_bounds = 0,
																			separate_at_pid_bounds = 0,
																			similarity_factor = 95,
																			distance = 0.2)
		if DictSimilarGroup != None:
			for SimilarGroupName, DictConnectivityGroups in DictSimilarGroup.items():
				PartsConnectivity = []
				for ConnectivityGroupName, ListConnectFace in DictConnectivityGroups.items():
					PartsFaceReferen = base.GetEntityPart(ListConnectFace[0])
					if PartsFaceReferen != None:
						ListPartsFacesSimilar.append(PartsFaceReferen)
						PartsConnectivity.append(PartsFaceReferen)
				
				if len(PartsConnectivity) >0:	
					DictSimilarPartsReq[SimilarGroupName] = PartsConnectivity
					
	ListPartsFacesDifference = list(set(PartBoltCad).difference(ListPartsFacesSimilar))
	ListFacesDifference = base.CollectEntities(deck_infos, ListPartsFacesDifference, ['FACE'])
	if len(ListFacesDifference) >0:
		DictIsolateFaceDiff = base.IsolateConnectivityGroups(entities = ListFacesDifference, separate_at_blue_bounds = False, separate_at_pid_bounds = False)
		if DictIsolateFaceDiff != None:
			ListInfosPartsDiff = []
			for KeyNameGroupDiff, InfosFacesDiff in DictIsolateFaceDiff.items():
				PartsDiffReferen = base.GetEntityPart(InfosFacesDiff[0])
				if PartsDiffReferen != None:
					ListInfosPartsDiff.append(PartsDiffReferen)
					
			if len(ListInfosPartsDiff) >0:	
				DictSimilarPartsReq['Not_Similar'] = ListInfosPartsDiff
	
	return DictSimilarPartsReq

#******************* Help Function****************************
def CreateNewGroupsFunc(NameNewGroup):
	
	NewsGroup = base.NewGroup(NameNewGroup, '')
	if NewsGroup == None:
		EntityGroup = base.NameToEnts(pattern = NameNewGroup, deck = deck_infos, match = constants.ENM_EXACT)
		NewsGroup = EntityGroup[0]
	
	return NewsGroup

def FindEntityInListElementsFunc(EntityElement, ListElements):
	
	try:
		Pos = ListElements.index(EntityElement)
	except:
		Pos = None
	else:
		Pos = Pos
	
	return Pos

def CalculateAngleTwoVectorFunc(Vecs1st, Vecs2nd):
	
	AngleVecs1st_2nd = math.degrees(calc.CalcAngleOfVectors(Vecs1st, Vecs2nd))
#	print(AngleVecs1st_2nd)
	return AngleVecs1st_2nd

def CalculateDistance2PointsFunc(InfosPoints1st, InfosPoints2nd):
	
	Vecs2Points = [InfosPoints2nd[0] - InfosPoints1st[0], InfosPoints2nd[1] - InfosPoints1st[1], InfosPoints2nd[2] - InfosPoints1st[2]]
	LensOfVecs = math.sqrt(Vecs2Points[0]*Vecs2Points[0] + Vecs2Points[1]*Vecs2Points[1] + Vecs2Points[2]*Vecs2Points[2])
	
	return LensOfVecs

#ConvertCADToConnectionBoltTool()
