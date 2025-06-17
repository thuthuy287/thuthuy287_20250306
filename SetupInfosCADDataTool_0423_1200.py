import ansa
from ansa import *
import math

#@session.defbutton('2-MESH', 'SupportCreateArcTool','Support quá trình tạo Arc từ CAD Data') 
def SupportCreateArcTool():
	TopWindow = guitk.BCWindowCreate("Support Create Arc Cad Tool version 1.0", guitk.constants.BCOnExitDestroy)
	
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Options: ", guitk.constants.BCVertical)
	BCRadioButton_1 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Project Cons To Cons", None, 0)
	BCRadioButton_2 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Project Cons To Faces", None, 0)
	guitk.BCRadioButtonSetChecked(BCRadioButton_2, True)
	
	BCButtonGroup_2 = guitk.BCButtonGroupCreate(TopWindow, "Select Type: ", guitk.constants.BCVertical)
	BCCheckBox_1 = guitk.BCCheckBoxCreate(BCButtonGroup_2, "Mark Hot Points")
	BCCheckBox_2 = guitk.BCCheckBoxCreate(BCButtonGroup_2, "Create Connect Faces")
	BCCheckBox_3 = guitk.BCCheckBoxCreate(BCButtonGroup_2, "Plane Cut Faces")
	guitk.BCCheckBoxSetChecked(BCCheckBox_2, True)
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_1 = guitk.BCLabelCreate(TopWindow, "")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	DataOnTop = [BCProgressBar_1, BCLabel_1, BCRadioButton_1, BCRadioButton_2, BCCheckBox_3, BCCheckBox_1, BCCheckBox_2]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, DataOnTop)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, DataOnTop)
	
	guitk.BCShow(TopWindow)

def RejectFunc(TopWindow, DataOnTop):
	
	return 1
#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, DataOnTop):
	
	ProBar = DataOnTop[0]
	StatusLabel = DataOnTop[1]
	StatusConsToCons = DataOnTop[2]
	StatusConsToFaces = DataOnTop[3]
	StatusPlaneCut = DataOnTop[4]
	StatusMarkPoint = DataOnTop[5]
	StatusConnectFaces = DataOnTop[6]
	
	for i in range(0, 1000, 1):
		SelectConsSource = base.PickEntities(constants.LSDYNA, ['CONS'])
		if SelectConsSource != None:
			if guitk.BCRadioButtonIsChecked(StatusConsToCons) == True:
				SelectConsTarget = base.PickEntities(constants.LSDYNA, ['CONS'])
				if SelectConsTarget != None:
					ProjectConsToConsFunc(StatusMarkPoint, StatusConnectFaces, SelectConsSource, SelectConsTarget)
			
			if guitk.BCRadioButtonIsChecked(StatusConsToFaces) == True:
				SelectFacesTarget = base.PickEntities(constants.LSDYNA, ['FACE'])
				if SelectFacesTarget != None:
					ProjectConsToFacesFunc(StatusMarkPoint, StatusConnectFaces, StatusPlaneCut, SelectConsSource, SelectFacesTarget)
			
		else:
			return 0

#***************** Tạo Arc Weld giữa Cons với Faces ***********************************
def ProjectConsToFacesFunc(StatusMarkPoint, StatusConnectFaces, StatusPlaneCut, SelectConsSource, SelectFacesTarget):

	ProjConsToFaceResult = base.ConsProjectNormal(entities = SelectConsSource, faces_array = SelectFacesTarget, max_distance = 10, split_original = True, connect_with_faces = True, nearest_target = True, delete_faces = False)
	if ProjConsToFaceResult != None:
		ListNewConsProjResult = ProjConsToFaceResult[0]
		ListNewFacesProjResult = ProjConsToFaceResult[1]
		ValsConsSource = base.GetEntityCardValues(constants.LSDYNA, SelectConsSource[0], ['Elem.Length'])
		ListPartsFacesCoonsReport = []
		CreateInfoForFacesCoonsFunc(ListNewFacesProjResult, ListPartsFacesCoonsReport)

		ListConsNeedJoint, ListConsTargetInNewFaces = SetInfosForConsOfFacesProjectFunc(ListNewFacesProjResult, ListNewConsProjResult)
		
		if len(ListConsTargetInNewFaces) >0:
			CreateNewSeamLinesConnection(ListConsTargetInNewFaces, ListPartsFacesCoonsReport, SelectFacesTarget)
			if guitk.BCCheckBoxIsChecked(StatusPlaneCut) == True:
				PlaneCutPropsOnFacesSelectFunc(ListNewFacesProjResult, SelectFacesTarget)
				
			if guitk.BCCheckBoxIsChecked(StatusConnectFaces) == True and guitk.BCCheckBoxIsChecked(StatusMarkPoint) == True:
				MarkPointsOnFacesFunc(ListConsTargetInNewFaces, ValsConsSource['Elem.Length'], ListNewFacesProjResult, ListPartsFacesCoonsReport)
				MarkPointsOnFacesFunc(ListNewConsProjResult, ValsConsSource['Elem.Length'], ListNewFacesProjResult, ListPartsFacesCoonsReport)
				if len(ListConsNeedJoint) >0:
					mesh.JoinMacros(entities = ListConsNeedJoint, keep_mesh = True, auto_delete_hot_points = True)
			
			elif guitk.BCCheckBoxIsChecked(StatusMarkPoint) == True:
				MarkPointsOnFacesFunc(ListConsTargetInNewFaces, ValsConsSource['Elem.Length'], ListNewFacesProjResult, ListPartsFacesCoonsReport)
				MarkPointsOnFacesFunc(ListNewConsProjResult, ValsConsSource['Elem.Length'], ListNewFacesProjResult, ListPartsFacesCoonsReport)
				if len(ListConsNeedJoint) >0:
					mesh.JoinMacros(entities = ListConsNeedJoint, keep_mesh = True, auto_delete_hot_points = True)
				base.DeleteEntity(ListPartsFacesCoonsReport, True)
			
			

############ Create New Seamlines Connection
def CreateNewSeamLinesConnection(ListConsTargetInNewFaces, ListPartsFacesCoonsReport, SelectFacesTarget):
	
	CurveOnCoonsConvert = base.ConsToCurves(ListConsTargetInNewFaces)
	ListMiddleCurves = base.CurvesConnectMulti(curves = CurveOnCoonsConvert, tolerance = 0.5, angle = 90, ret_ents = True)
	
	if ListMiddleCurves !=None:
		ListCurveImportConnection = ListMiddleCurves
	else:
		ListCurveImportConnection = CurveOnCoonsConvert
	
	MaxIdConnection = FindMaxConnectionIdsInModelFunc()
	
	FacesOnCoonsTarget = base.GetFacesOfCons(ListConsTargetInNewFaces)
	if len(FacesOnCoonsTarget) >0:
		ListFaceCoonsCheck = base.CollectEntities(constants.LSDYNA, ListPartsFacesCoonsReport, ['FACE'])
		ListFaceSourceAddConnection = list(set(FacesOnCoonsTarget).difference(ListFaceCoonsCheck))
		
		ValsFacesSource = base.GetEntityCardValues(constants.LSDYNA, SelectFacesTarget[0], ['PID'])
		ValsFacesTarget = base.GetEntityCardValues(constants.LSDYNA, ListFaceSourceAddConnection[0], ['PID'])
	
		ListPartConnectConnection = [str(ValsFacesSource['PID']), str(ValsFacesTarget['PID'])]
		connections.CreateConnectionLine(type = 'SeamLine_Type', curves = ListCurveImportConnection, id = MaxIdConnection, connectivity = ListPartConnectConnection)

## ---------------------- Tao mat cat cho cac face -------------------------
def PlaneCutPropsOnFacesSelectFunc(ListNewFacesProjResult, SelectFacesTarget):
	
	for i in range(0, len(ListNewFacesProjResult), 1):
		ListAxisPointsPlaneCut = GetAxisPointPlaneCutFunc(ListNewFacesProjResult[i])
		if len(ListAxisPointsPlaneCut) >0:
			ListFaceConnectPlaneCut = GetListFacesPlaneCutFunc(SelectFacesTarget)
			if len(ListFaceConnectPlaneCut) >0:
				base.FacesPlaneCut(working_plane = ListAxisPointsPlaneCut, entities = ListFaceConnectPlaneCut, produce_plane_faces = False, perform_topology = True)

#####-------------------- Tim cac face cung pid voi faces select
def GetListFacesPlaneCutFunc(SelectFacesTarget):
	
	ListFaceConnectPlaneCut = []
	for i in range(0, len(SelectFacesTarget), 1):
		ValseFacesSelect1st = base.GetEntityCardValues(constants.LSDYNA, SelectFacesTarget[i], ['PID'])
		PropsOnFaceSelect = base.GetEntity(constants.LSDYNA, '__PROPERTIES__', ValseFacesSelect1st['PID'])
		if PropsOnFaceSelect != None:
			ListFaceConnectPlaneCut.extend(base.CollectEntities(constants.LSDYNA, PropsOnFaceSelect, ['FACE']))
	
	return ListFaceConnectPlaneCut

#####-------------------- Tim 3 diem de tao mat cat
def GetAxisPointPlaneCutFunc(ListFaceGetAxisPlane):
	ListAxisPointsPlaneCut = []
	HotPointsOnFaces = base.CollectEntities(constants.LSDYNA, ListFaceGetAxisPlane, ['HOT POINT'])
	for i in range(0, 3, 1):
		ValsHPoints = base.GetEntityCardValues(constants.LSDYNA, HotPointsOnFaces[i], ['X', 'Y', 'Z'])
		ListAxisPointsPlaneCut.append([ValsHPoints['X'], ValsHPoints['Y'], ValsHPoints['Z']])
	
	return ListAxisPointsPlaneCut
	
## ---------------------- Mark point vao cac duong cons tren faces voi khoang cach la length cua cons -------------------------
def MarkPointsOnFacesFunc(ListConsNeedMark, StepLengthOfCons, ListNewFacesProjResult, ListPartsFacesCoonsReport):
	
	CurvesOnConsNeedMark = base.ConsToCurves(ListConsNeedMark)
	ListCurvesConnectMulti = base.CurvesConnectMulti(curves = CurvesOnConsNeedMark, tolerance = 0.2, angle = 45, ret_ents = True)
	if ListCurvesConnectMulti != None:
		ListCurvesConnectMulti = ListCurvesConnectMulti
	else:
		ListCurvesConnectMulti = CurvesOnConsNeedMark
		
	ListAxisEvaluePointOnCurves = []
	for i in range(0, len(ListCurvesConnectMulti), 1):
		ValsCurveConnect = base.GetEntityCardValues(constants.LSDYNA, ListCurvesConnectMulti[i], ['Length'])
		ListAxisEvaluePointReport = DivideCurveBaseOnStepLengthFunc(StepLengthOfCons, ValsCurveConnect['Length'], ListCurvesConnectMulti[i])
		if len(ListAxisEvaluePointReport) >0:
#			for w in range(0, len(ListAxisEvaluePointReport), 1):
#				base.Newpoint(ListAxisEvaluePointReport[w][0], ListAxisEvaluePointReport[w][1], ListAxisEvaluePointReport[w][2])
			ListAxisEvaluePointOnCurves.extend(ListAxisEvaluePointReport)
		
	base.DeleteEntity(ListCurvesConnectMulti, True)
	if len(ListAxisEvaluePointOnCurves) >0:
		base.ProjectAndMarkPoints(points_coordinates = ListAxisEvaluePointOnCurves, projection_tolerance = 1, parts = ListPartsFacesCoonsReport)		
			
## ---------------------- Thiết định ID Faces vào comment của đường CONs -------------------------
def SetInfosForConsOfFacesProjectFunc(ListNewFacesProjResult, ListNewConsProjResult):
	
	### Thiết định ID face vào comment của cons
	DictNewFace_ConsFacesProj = {}
	for i in range(0, len(ListNewFacesProjResult), 1):
		ConsOfNewFacesProj = base.CollectEntities(constants.LSDYNA, ListNewFacesProjResult[i], ['CONS'])
		for k in range(0, len(ConsOfNewFacesProj), 1):
			ValsConsFacesProj = base.GetEntityCardValues(constants.LSDYNA, ConsOfNewFacesProj[k], ['Comment'])
			base.SetEntityCardValues(constants.LSDYNA, ConsOfNewFacesProj[k], {'Comment': str(ListNewFacesProjResult[i]._id) + ',' + ValsConsFacesProj['Comment']})
		
		DictNewFace_ConsFacesProj[ListNewFacesProjResult[i]] = ConsOfNewFacesProj	
	### Lọc ra các đường CONs cần join và đường CONs đối xứng.
	ListConsNeedJoint = []
	ListConsTargetInNewFaces = []
	if len(DictNewFace_ConsFacesProj) >0:
		for KeysNewFace, ListConsFacesProj in DictNewFace_ConsFacesProj.items():
			for w in range(0, len(ListConsFacesProj), 1):
				ValsSingleConsProj = base.GetEntityCardValues(constants.LSDYNA, ListConsFacesProj[w], ['Comment', 'Number of Pasted Cons'])
				TokensCommentSingleCons = ValsSingleConsProj['Comment'].split(',')
#				print(len(TokensCommentSingleCons))
				if len(TokensCommentSingleCons) >2:
					ListConsNeedJoint.append(ListConsFacesProj[w])
				else:
					if ValsSingleConsProj['Number of Pasted Cons'] != 1:
						PosSearchNewConsFace = FindEntityInListElementFunc(ListConsFacesProj[w], ListNewConsProjResult)
						if PosSearchNewConsFace == None:
							ListConsTargetInNewFaces.append(ListConsFacesProj[w])
	
#	print(ListConsTargetInNewFaces)
	return ListConsNeedJoint, ListConsTargetInNewFaces
			
#***************** Tạo Arc Weld giữa 2 cons với nhau ***********************************
def ProjectConsToConsFunc(StatusMarkPoint, StatusConnectFaces, SelectConsSource, SelectConsTarget):
	
	HotPointsOnConsSource = base.CollectEntities(constants.LSDYNA, SelectConsSource, ['HOT POINT'])
	ProjectPointToConsTargetFunc(SelectConsTarget, HotPointsOnConsSource)
	if len(SelectConsTarget) >0:
		ListPairsConsReport = FindPairsConsProjectFunc(SelectConsSource, SelectConsTarget)
#		print(ListPairsConsReport)
		if len(ListPairsConsReport) >0:
			CreateArcCadForListPairsConsFunc(ListPairsConsReport, StatusMarkPoint, StatusConnectFaces)

## ---------------------- Tạo các arc cad dựa trên các cặp cons tìm được -------------------------
def CreateArcCadForListPairsConsFunc(ListPairsConsReport, StatusMarkPoint, StatusConnectFaces):
	
	for i in range(0, len(ListPairsConsReport), 1):
		CurvesOnConsSource = base.ConsToCurves(ListPairsConsReport[i][0])
		ValsConsSource = base.GetEntityCardValues(constants.LSDYNA, ListPairsConsReport[i][0], ['Elem.Length', 'Length', 'Start Point', 'Start Vector', 'End Point', 'End Vector'])
		
		ListAxisEvaluatePoints = DivideCurveBaseOnStepLengthFunc(ValsConsSource['Elem.Length'], ValsConsSource['Length'], CurvesOnConsSource[0])
		base.DeleteEntity(CurvesOnConsSource, True)	
		
		ListPartsFacesCoonsReport, ListFacesCoonsReport = CreateFacesForPairsConsFunc(ListPairsConsReport[i])
		if len(ListPartsFacesCoonsReport) >0:
			if guitk.BCCheckBoxIsChecked(StatusConnectFaces) == True and guitk.BCCheckBoxIsChecked(StatusMarkPoint) == True:
				MarkPointsOnConsFunc(ListAxisEvaluatePoints, ListFacesCoonsReport)
			elif guitk.BCCheckBoxIsChecked(StatusMarkPoint) == True:
				MarkPointsOnConsFunc(ListAxisEvaluatePoints, ListFacesCoonsReport)
				base.DeleteEntity(ListPartsFacesCoonsReport, True)

## ---------------------- Mark các nodes trên đường Cons -------------------------
def MarkPointsOnConsFunc(ListAxisEvaluatePoints, ListFacesCoonsReport):
	
	ListConsOnFacesCoonsReport = base.CollectEntities(constants.LSDYNA, ListFacesCoonsReport, ['CONS'])
	for i in range(0, len(ListConsOnFacesCoonsReport), 1):
		ListAxisPointProjectToPart = []
		ListPartProjectTarget = [base.GetEntityPart(ListConsOnFacesCoonsReport[i])]
		for k in range(0, len(ListAxisEvaluatePoints), 1):
			ProjectPointToPairCons = base.ProjectPoint(ListAxisEvaluatePoints[k][0], ListAxisEvaluatePoints[k][1], ListAxisEvaluatePoints[k][2], ListConsOnFacesCoonsReport[i])
			if ProjectPointToPairCons[0] == 1:
#				base.Newpoint(ProjectPointToPairCons[1], ProjectPointToPairCons[2], ProjectPointToPairCons[3])
				ListAxisPointProjectToPart.append([ProjectPointToPairCons[1], ProjectPointToPairCons[2], ProjectPointToPairCons[3]])
					
		if len(ListAxisPointProjectToPart) >0:
			base.ProjectAndMarkPoints(points_coordinates = ListAxisPointProjectToPart, projection_tolerance = 1, parts = ListPartProjectTarget)

## ---------------------- Tạo faces giữa các đường cons ------------------------- 
def CreateFacesForPairsConsFunc(ListPairsConsCreateFace):
	
#	print(ListPairsConsCreateFace)
	ListPartsFacesCoonsReport = []
	ListFacesCoonsReport = []
	ListCurveOnPairCons = base.ConsToCurves(ListPairsConsCreateFace)
	FacesCoons = base.SurfsCoons(faces_array = ListCurveOnPairCons, join_perimeters = False, respect_user_selection = False, ret_ents = True)
	if FacesCoons != None:
		ConsOnFacesReport = base.CollectEntities(constants.LSDYNA, FacesCoons, ['CONS'])
		ListConsTopo = ConsOnFacesReport + ListPairsConsCreateFace
		base.Topo(cons = ListConsTopo, paste_with_frozen_faces = True, paste_different_pids = True)
		ListFacesCoonsReport.extend(FacesCoons)
		CreateInfoForFacesCoonsFunc(FacesCoons, ListPartsFacesCoonsReport)
	
	base.DeleteEntity(ListCurveOnPairCons, True)
	
	return ListPartsFacesCoonsReport, ListFacesCoonsReport

## ---------------------- Tạo thông tin properties và thông tin part cho faces coons ------------------------- 
def CreateInfoForFacesCoonsFunc(FacesCoons, ListPartsFacesCoonsReport):
	
	###------------- Tạo Part
	NamePartFacesCoons = 'Surface Coons Result_' + str(FacesCoons[0]._id)
	ModuleIdPartFacesCoons = ''
	PartFacesCoonsReport = CreateNewPartFunc(NamePartFacesCoons, ModuleIdPartFacesCoons)
	
	base.SetEntityPart(FacesCoons, PartFacesCoonsReport)
	
	ListPartsFacesCoonsReport.append(PartFacesCoonsReport)
	###------------- Tạo Props
	NewPropsFaces = base.CreateEntity(constants.LSDYNA, 'SECTION_SHELL')
	for i in range(0, len(FacesCoons), 1):
		base.SetEntityCardValues(constants.LSDYNA, FacesCoons[i], {'PID': NewPropsFaces._id})
		
## ---------------------- Tìm đường cons mới sinh ra khi project hot point -------------------------
def FindPairsConsProjectFunc(SelectConsSource, SelectConsTarget):
	
	ListPairsConsReport = []
	for i in range(0, len(SelectConsSource), 1):
		DictStringIdsHotPoint_ConsTarget = {}
		for k in range(0, len(SelectConsTarget), 1):
			HotPointOnConsTarget = base.CollectEntities(constants.LSDYNA, SelectConsTarget[k], ['HOT POINT'])
			ListHotPointTargetConnect = []
			for w in range(0, len(HotPointOnConsTarget), 1):
				ValsHotPointTarget = base.GetEntityCardValues(constants.LSDYNA, HotPointOnConsTarget[w], ['X', 'Y', 'Z'])
				StatusProjPointToCons = base.ProjectPoint(ValsHotPointTarget['X'], ValsHotPointTarget['Y'], ValsHotPointTarget['Z'], SelectConsSource[i])
#				print(StatusProjPointToCons[0])
				if StatusProjPointToCons[0] == 1:
					ListHotPointTargetConnect.append(HotPointOnConsTarget[w])
#				elif StatusProjPointToCons[0] == 2:
#					PointsProjectResult = [StatusProjPointToCons[1], StatusProjPointToCons[2], StatusProjPointToCons[3]]
#					SnapPointProject = [StatusProjPointToCons[1], StatusProjPointToCons[2], StatusProjPointToCons[3]]
#					DistanceSnapToPointProject = CalculateDistanceTwoPointsFunc(PointsProjectResult, SnapPointProject)
#					if DistanceSnapToPointProject < 1.1:
#						ListHotPointTargetConnect.append(HotPointOnConsTarget[w])
#					base.Newpoint(StatusProjPointToCons[4], StatusProjPointToCons[5], StatusProjPointToCons[6])
#					base.Newpoint(StatusProjPointToCons[1], StatusProjPointToCons[2], StatusProjPointToCons[3])
#			print(len(ListHotPointTargetConnect))		
			if len(ListHotPointTargetConnect) == 2:
				ListIdsHotPointTarget = [ListHotPointTargetConnect[0]._id, ListHotPointTargetConnect[1]._id]
				ListIdsHotPointTarget.sort()
				DictStringIdsHotPoint_ConsTarget[str(ListIdsHotPointTarget[0]) + '_' + str(ListIdsHotPointTarget[1])] = SelectConsTarget[k]
						
		if len(DictStringIdsHotPoint_ConsTarget) >0:
			ListConsAddToSurfFaces = []
			ListConsAddToSurfFaces.append(SelectConsSource[i])
			RemoveDuplicateOfConsTargetFunc(DictStringIdsHotPoint_ConsTarget, ListConsAddToSurfFaces)
			if len(ListConsAddToSurfFaces) >1:
				ListPairsConsReport.append(ListConsAddToSurfFaces)
#				print(ListConsAddToSurfFaces)
#			FacesCoons = base.SurfsCoons(faces_array = ListConsAddToSurfFaces, join_perimeters = False, respect_user_selection = False, ret_ents = True)
			
	return ListPairsConsReport

## ---------------------- Lọc ra va remove các đường cons bị trùng nhau -------------------------
def RemoveDuplicateOfConsTargetFunc(DictStringIdsHotPoint_ConsTarget, ListConsAddToSurfFaces):
	
	for KeyStringIdsHotPoints, SingleConsTarget in DictStringIdsHotPoint_ConsTarget.items():
		ListConsAddToSurfFaces.append(SingleConsTarget)

## ---------------------- Project hot point tới đường cons được chọn -------------------------
def ProjectPointToConsTargetFunc(SelectConsTarget, HotPointsOnConsSource):
	
	for k in range(0, len(HotPointsOnConsSource), 1):
		collector_HotPointProjResult = base.CollectNewModelEntities(constants.LSDYNA, ['CONS'])
		ValsHotPointSource = base.GetEntityCardValues(constants.LSDYNA, HotPointsOnConsSource[k], ['X', 'Y', 'Z'])
		base.HotPointsProject(ValsHotPointSource['X'], ValsHotPointSource['Y'], ValsHotPointSource['Z'], SelectConsTarget, remesh = True)
		collector_HotPointProjReport = collector_HotPointProjResult.report()
		del collector_HotPointProjResult
		
		if len(collector_HotPointProjReport) >0:
			SelectConsTarget.extend(collector_HotPointProjReport)
		
#************************ Help Functions **************************
#####------------------Chia curve theo step length
def DivideCurveBaseOnStepLengthFunc(LengthTarget, LengthOfCurve, InputCurve):
	
	ListAxisEvaluatePoints = []
	StepLengthOnCurve = int(round((LengthOfCurve/LengthTarget), 0))
#	print(StepLengthOnCurve)
	if StepLengthOnCurve == 0:
		StepLengthOnCurve = 1
		
	for i in range(0, StepLengthOnCurve + 1, 1):
		AxisPointDivideByStep = base.EvaluateCurvePoint(InputCurve, i/StepLengthOnCurve)
		ListAxisEvaluatePoints.append(AxisPointDivideByStep)
#		base.Newpoint(AxisPointDivideByStep[0], AxisPointDivideByStep[1], AxisPointDivideByStep[2])

	return ListAxisEvaluatePoints		

##### ---------------- Tim cac phan tu trong list
def FindEntityInListElementFunc(EntityElem, ListElements):
	
	try:
		Pos = ListElements.index(EntityElem)
	except:
		Pos = None
	else:
		Pos = Pos
	
	return Pos		

##### ---------------- Tính khoảng cách giữa hai điểm points
def CalculateDistanceTwoPointsFunc(Points1st, Points2nd):
	
	VecsPoints1st_2nd = [Points2nd[0] - Points1st[0], Points2nd[1] - Points1st[1], Points2nd[2] - Points1st[2]]
	LensVecs2Points = math.sqrt(VecsPoints1st_2nd[0]*VecsPoints1st_2nd[0] + VecsPoints1st_2nd[1]*VecsPoints1st_2nd[1] + VecsPoints1st_2nd[2]*VecsPoints1st_2nd[2])
	
	return LensVecs2Points

##### ---------------- Tạo Part mới
def CreateNewPartFunc(NamePartEntity, ModulePartEntity):
	
	NewPartEntity = base.NewPart(NamePartEntity, ModulePartEntity)
	if NewPartEntity == None:
		EntityPartReference = base.NameToEnts(NamePartEntity)
		NewPartEntity = EntityPartReference[0]
	
	else:
		NewPartEntity = NewPartEntity
	
	return NewPartEntity
	
##### ---------------- Tim khoang id lon nhat trong model
def FindMaxConnectionIdsInModelFunc():
	
	EntityConnections = base.CollectEntities(constants.LSDYNA, None, ['__CONNECTIONS__'])
	ListIdsConnection = []
	if len(EntityConnections) >0:
		for i in range(0, len(EntityConnections), 1):
			ListIdsConnection.append(EntityConnections[i]._id)
	
	if len(ListIdsConnection) >0:
		MaxIdConnection = max(ListIdsConnection) +1
	
	else:
		MaxIdConnection = 100
	
	return MaxIdConnection
	
SupportCreateArcTool()
