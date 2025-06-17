# PYTHON script
import os
import ansa
from ansa import *

import math

def CreateMorphingBoxFunc():
	# Need some documentation? Run this with F5
	AllsFaces = base.PickEntities(constants.LSDYNA, ['FACE'])
	if AllsFaces != None:
		DictIsolateFaceConnect = base.IsolateConnectivityGroups(entities = AllsFaces, separate_at_blue_bounds = False, separate_at_pid_bounds = True)
		if DictIsolateFaceConnect != None:
			for KeyNameGroupFace, FacesSelect in DictIsolateFaceConnect.items():
				NewHexaBoxs = mesh.HexaBoxOrtho(loaded_elements = FacesSelect, min_flag = True)
				if NewHexaBoxs != 0:
					HexaBoxFaces = base.CollectEntities(constants.LSDYNA, NewHexaBoxs, ['HEXA_BOX_FACE'])
					if len(HexaBoxFaces) >0:
						ListBoxFaceDouble = FindBoxFaceDoubleVecsFunc(HexaBoxFaces)
						if len(ListBoxFaceDouble) >0:
							DictSingleBoxFace_ListEntity = FindEntityOnBoxFacesFunc(ListBoxFaceDouble, FacesSelect)
							if len(DictSingleBoxFace_ListEntity) >0:
								AlignBoxFaceToCadFunc(DictSingleBoxFace_ListEntity)
					
			base.RedrawAll()

###-------------------------------- Align box ve cad----------------------------------------
def AlignBoxFaceToCadFunc(DictSingleBoxFace_ListEntity):
	
	for SingleBoxConnect, ListEntityFaceConnect in DictSingleBoxFace_ListEntity.items():
		ListFaceExtends = ExtendsFacesOnMorphFunc(ListEntityFaceConnect)
		if len(ListFaceExtends) >0:
			ValsBoxFaceConnect = base.GetEntityCardValues(constants.LSDYNA, SingleBoxConnect, ['Name', 'Comment'])
			TokensNameBoxConnect = ValsBoxFaceConnect['Name'].split('_')
			VecsOfBoxConnect = [float(TokensNameBoxConnect[0]), float(TokensNameBoxConnect[1]), float(TokensNameBoxConnect[2])]
			mesh.AssociateBoxFacesToSurfs(box_faces = [SingleBoxConnect], surface_ents = ListFaceExtends, user_projection_mode_vector = VecsOfBoxConnect, remove_points = False)
		
			base.DeleteEntity(ListFaceExtends, True)
		
####-------------------------------- Mo rong cac faces voi khoang cach la 10 ----------------------------------------	
def ExtendsFacesOnMorphFunc(ListEntityFaceConnect):
	
	ListFaceExtends = []
	for i in range(0, len(ListEntityFaceConnect), 1):
		ElemsFaceExtend = base.SurfaceExtend(face = ListEntityFaceConnect[i], extend_value = 10, untrim = True, delete_original_face = False)
		if ElemsFaceExtend != None:
			ListFaceExtends.append(ElemsFaceExtend)
	
	return ListFaceExtends		

###-------------------------------- Tim cac face cad cung vector voi morph faces----------------------------------------			
def FindEntityOnBoxFacesFunc(ListBoxFaceDouble, FacesSelect):
	
	DictSingleBoxFace_ListEntity = {}
	for i in range(0, len(ListBoxFaceDouble), 1):
		ListEntityOnBoxFace = CheckVecsOfBoxWithVecsOfFacesSelectFunc(ListBoxFaceDouble[i], FacesSelect)
		if len(ListEntityOnBoxFace) >0:
			FindFacesNearestBoxFunc(ListBoxFaceDouble[i], ListEntityOnBoxFace, DictSingleBoxFace_ListEntity)
	
	return DictSingleBoxFace_ListEntity
#	if len(DictSingleBoxFace_ListEntity) >0:
#		for aa, bb in DictSingleBoxFace_ListEntity.items():
#			setFace = base.CreateEntity(constants.LSDYNA, 'SET')
#			base.AddToSet(setFace, bb)		

####-------------------------------- Check khoang cach cua face toi tung box face----------------------------------------
def FindFacesNearestBoxFunc(ListBoxFaceDistance, ListEntityOnBoxFace, DictSingleBoxFace_ListEntity):
	
	DictIsolateGroupFace = base.IsolateConnectivityGroups(entities = ListEntityOnBoxFace, separate_at_blue_bounds = False, separate_at_pid_bounds = True)
	if DictIsolateGroupFace != None:
		for i in range(0, len(ListBoxFaceDistance), 1):
			ValsBoxFaceDistance = base.GetEntityCardValues(constants.LSDYNA, ListBoxFaceDistance[i], ['Name', 'Comment'])
			TokensCommentBoxDistance = ValsBoxFaceDistance['Comment'].split('_')
			AxisCogOfBoxFace = [float(TokensCommentBoxDistance[0]), float(TokensCommentBoxDistance[1]), float(TokensCommentBoxDistance[2])]
			
			ListDistanceCalculate = []
			ListFacesConnect = []
			for KeyGroupIsolate, ListFacesIsolate in DictIsolateGroupFace.items():
				ProjContainerResult = calc.ProjectPointToContainer(AxisCogOfBoxFace, ListFacesIsolate)
				ListDistanceCalculate.append(ProjContainerResult[1])
				ListFacesConnect.append(ListFacesIsolate)
			
			if len(ListDistanceCalculate) >0:
				IndexMinDistance = ListDistanceCalculate.index(min(ListDistanceCalculate))
				DictSingleBoxFace_ListEntity[ListBoxFaceDistance[i]] = ListFacesConnect[IndexMinDistance]

####-------------------------------- Check vector cua face trung voi vector cua tung box face----------------------------------------
def CheckVecsOfBoxWithVecsOfFacesSelectFunc(ListBoxFacesDefine, FacesSelect):
	
	ListEntityOnBoxFace = []
	for i in range(0, len(ListBoxFacesDefine), 1):
#		print(ListBoxFacesDefine[i]._id)
		ValsBoxFaceDefine = base.GetEntityCardValues(constants.LSDYNA, ListBoxFacesDefine[i], ['Name', 'Comment'])
		TokensNameBoxDefine = ValsBoxFaceDefine['Name'].split('_')
		VecsOfBoxFaceDefine = [float(TokensNameBoxDefine[0]), float(TokensNameBoxDefine[1]), float(TokensNameBoxDefine[2])]
		if len(VecsOfBoxFaceDefine) >0:
			for k in range(0, len(FacesSelect), 1):
				OrientsVecOfFace = base.GetFaceOrientation(FacesSelect[k])
				AngleTwoVecs = math.degrees(calc.CalcAngleOfVectors(VecsOfBoxFaceDefine, OrientsVecOfFace))
				if AngleTwoVecs < 5 or AngleTwoVecs > 175:
#					print(FacesSelect[k]._id)
					ListEntityOnBoxFace.append(FacesSelect[k])
	
	return ListEntityOnBoxFace
	
###-------------------------------- Tim cac hexa box face co vector trung nhau----------------------------------------	
def FindBoxFaceDoubleVecsFunc(HexaBoxFaces):
	
	ListBoxFaceDouble = []
	GetVectorOfMorphFacesFunc(HexaBoxFaces)
	
	ListHexaBoxFacesCheck = []
	for i in range(0, len(HexaBoxFaces), 1):
		PosSeachBoxFace1st = FindEntityInListElemsFunc(HexaBoxFaces[i], ListHexaBoxFacesCheck)
		if PosSeachBoxFace1st == None:
			ValsBoxFace1st = base.GetEntityCardValues(constants.LSDYNA, HexaBoxFaces[i], ['Name', 'Comment'])
			TokensNameBox1st = ValsBoxFace1st['Name'].split('_')
			VecsOfBoxFace1st = [float(TokensNameBox1st[0]), float(TokensNameBox1st[1]), float(TokensNameBox1st[2])]
			for k in range(0, len(HexaBoxFaces), 1):
				if HexaBoxFaces[k] != HexaBoxFaces[i]:
					ValsBoxFace2nd = base.GetEntityCardValues(constants.LSDYNA, HexaBoxFaces[k], ['Name', 'Comment'])
					TokensNameBox2nd = ValsBoxFace2nd['Name'].split('_')
					VecsOfBoxFace2nd = [float(TokensNameBox2nd[0]), float(TokensNameBox2nd[1]), float(TokensNameBox2nd[2])]
					
					Angle2Vecs = math.degrees(calc.CalcAngleOfVectors(VecsOfBoxFace1st, VecsOfBoxFace2nd))
					if Angle2Vecs < 5 or Angle2Vecs >175:
						ListHexaBoxFacesCheck.append(HexaBoxFaces[k])
						ListBoxFaceDouble.append([HexaBoxFaces[i], HexaBoxFaces[k]])
	
	return ListBoxFaceDouble

#####-------------------------------- Tim vector cua morph faces----------------------------------------		
def GetVectorOfMorphFacesFunc(HexaBoxFaces):
	
	for k in range(0, len(HexaBoxFaces), 1):
		HexaBoxEdges = base.CollectEntities(constants.LSDYNA, HexaBoxFaces[k], ['HEXA_BOX_EDGE'])
		CurveOnHexaBoxEdges = base.CurvesFromEntities(entities = HexaBoxEdges, connect_curves = [0.05, 45])
		if len(CurveOnHexaBoxEdges) >0:
			ListAxisPointOnCurveEdge = []
			for i in range(0, len(CurveOnHexaBoxEdges), 1):
				ValsCurveHexaBoxEdge = base.GetEntityCardValues(constants.LSDYNA, CurveOnHexaBoxEdges[i], ['Start X', 'Start Y', 'Start Z', 'End X', 'End Y', 'End Z'])
				CogNodesOfCurve = [(ValsCurveHexaBoxEdge['Start X'] + ValsCurveHexaBoxEdge['End X'])/2, (ValsCurveHexaBoxEdge['Start Y'] + ValsCurveHexaBoxEdge['End Y'])/2, (ValsCurveHexaBoxEdge['Start Z'] + ValsCurveHexaBoxEdge['End Z'])/2]
				ListAxisPointOnCurveEdge.append(CogNodesOfCurve)
			
			if len(ListAxisPointOnCurveEdge) >0:
				AxisNodesCurve1st = ListAxisPointOnCurveEdge[0]
				AxisNodesCurve2nd = ListAxisPointOnCurveEdge[1]
				AxisNodesCurve3rd = ListAxisPointOnCurveEdge[2]
				NormalDirection = CreatePlaneOnThreePointsFunc(AxisNodesCurve1st, AxisNodesCurve2nd, AxisNodesCurve3rd)
				ListCogPoints = CreateCogPointsFunc(ListAxisPointOnCurveEdge)
				base.SetEntityCardValues(constants.LSDYNA, HexaBoxFaces[k], {'Name': str(NormalDirection[0]) + '_' + str(NormalDirection[1]) + '_' + str(NormalDirection[2]), 'Comment': str(ListCogPoints[0]) + '_' + str(ListCogPoints[1]) + '_' + str(ListCogPoints[2])})
			
		base.DeleteEntity(CurveOnHexaBoxEdges, True)

########################### Help Function ##################################
#####-------------------------------- Tao Cog cua list point----------------------------------------	
def CreateCogPointsFunc(ListAxisPoints):
	
	ListAxisX = []
	ListAxisY = []
	ListAxisZ = []
	for i in range(0, len(ListAxisPoints), 1):
		ListAxisX.append(ListAxisPoints[i][0])
		ListAxisY.append(ListAxisPoints[i][1])
		ListAxisZ.append(ListAxisPoints[i][2])
	
	AxisPointsCog = [sum(ListAxisX)/len(ListAxisX), sum(ListAxisY)/len(ListAxisY), sum(ListAxisZ)/len(ListAxisZ)]
	
	return AxisPointsCog

#####-------------------------------- Tao mat phang di qua 3 diem cho truoc----------------------------------------			
def CreatePlaneOnThreePointsFunc(A, B, C):
	# Tinh vector AB
	AB = [B[0] - A[0], B[1] - A[1], B[2] - A[2]]
	# Tinh vector AC
	AC = [C[0] - A[0], C[1] - A[1], C[2] - A[2]]
	# Tinh tich co huong cua hai vector (tim vector phap tuyen cua mat phang) a=(a1;a2;a3 ) và b=(b1;b2;b3 )
	#				[a, b] = (a2b3 - a3b2, a3b1 - a1b3, a1b2 - a2b1)							
	NormalDirection = [AB[1]*AC[2] - AB[2]*AC[1], AB[2]*AC[0] - AB[0]*AC[2], AB[0]*AC[1] - AB[1]*AC[0]]
	
	return NormalDirection

#####--------------------------------- Tim phan tu trong 1 list------------------------------------------------------------
def FindEntityInListElemsFunc(EntitySearch, ListElems):
	
	try:
		Pos = ListElems.index(EntitySearch)
	except:
		Pos = None
	else:
		Pos = Pos
	
	return Pos
	
CreateMorphingBoxFunc()
