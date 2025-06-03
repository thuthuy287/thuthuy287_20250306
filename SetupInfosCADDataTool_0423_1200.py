100. Help Function

# PYTHON script
import math

def CalculateDistance2PointsFunc(Points1st, Points2nd):
	
	VecsAB = [Points2nd[0] - Points1st[0], Points2nd[1] - Points1st[1], Points2nd[2] - Points1st[2]]
	LenVecsAB = math.sqrt((VecsAB[0]*VecsAB[0]) + (VecsAB[1]*VecsAB[1]) + (VecsAB[2]*VecsAB[2]))
	
	return LenVecsAB



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

def CreateNewGroupsFunc(NameGroup):
	
	NewGroups = base.NewGroup(NameGroup, '')
#	if NewGroups == None:
#		EntityGroup = base.NameToEnts(NewGroups)
#		
#		NewGroups = EntityGroup[0]
	
	return NewGroups



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
		ListLinesInCSV.append(ReadLinesCSV[i].strip().replace('/', '_').replace('-', '_'))

	OpenCSVFile.close()
	
	return ListLinesInCSV





#SetUpGroupPart.py
# PYTHON script
import os
import ansa
from ansa import *

def main():
	# Need some documentation? Run this with F5

#	AllSets = base.CollectEntities(constants.LSDYNA, None, 'SET')
#	for i in range(0, len(AllSets), 1):
#		ValsSet = AllSets[i].get_entity_values(constants.LSDYNA, ['Name'])
#		PropsInSet = base.CollectEntities(constants.LSDYNA, AllSets[i], ['__PROPERTIES__'])
#		if len(PropsInSet) >0:
#			for k in range(0, len(PropsInSet), 1):
#				PropsInSet[k].set_entity_values(constants.LSDYNA, {'Comment': ValsSet['Name']})

	PathCsv = 'D:/1.csv'
	InfosLinesInCsv = ReadInfoCsvFunc(PathCsv)
	for i in range(0, len(InfosLinesInCsv), 1):
		TokensLinesCsv = InfosLinesInCsv[i].split(',')
		IDPart = TokensLinesCsv[0]
		NameSet = TokensLinesCsv[1]
		
		PropReference = base.GetEntity(constants.LSDYNA, 'SECTION_SHELL', int(IDPart))
		if PropReference != None:
			
			SetGroupAssy = base.CreateEntity(constants.LSDYNA, 'SET', {'Name': NameSet})
			if SetGroupAssy == None:
				SetReferreneByName = base.NameToEnts(NameSet)
				SetGroupAssy = SetReferreneByName[0]
			
#			print(SetGroupAssy)
			base.AddToSet(SetGroupAssy, PropReference)
		
		else:
			print(IDPart)
	
def ReadInfoCsvFunc(PathCsv):
	
	OpenCSVFile = open(PathCsv)
	ReadLinesCSV = OpenCSVFile.readlines()
	
	ListLinesInCSV = []
	for i in range(0, len(ReadLinesCSV), 1):
		ListLinesInCSV.append(ReadLinesCSV[i].strip())

	OpenCSVFile.close()
	
	return ListLinesInCSV

if __name__ == '__main__':
	main()





21.ConvertCadToSpot
# PYTHON script
import os
import ansa
from ansa import *

import math

deck = constants.LSDYNA
@session.defbutton('5_SPOT-WELD', 'ConvertCadToSpotWeldTool','Tạo Spot Connection từ cad data ....')
def ConvertCadToSpotWeldTool():
	
	TopWindow = guitk.BCWindowCreate("Convert Cad To Spot Connection", guitk.constants.BCOnExitDestroy)
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Options: ", guitk.constants.BCHorizontal)
	BCRadioButton_1 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Convert Cad To Spot", None, 0)
	BCRadioButton_2 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Auto Connectivity", None, 0)
	guitk.BCRadioButtonSetChecked(BCRadioButton_1, True)
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_1 = guitk.BCLabelCreate(TopWindow, "")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	_win = [BCProgressBar_1, BCLabel_1, BCRadioButton_1, BCRadioButton_2]
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
	
	if guitk.BCRadioButtonIsChecked(_win[2]):
		ConvertCadToSpotConnectionFunc(ProBar, LabelStatus)
	
	if guitk.BCRadioButtonIsChecked(_win[3]):
		AutoConnectivityBoltConnectionFunc(ProBar, LabelStatus)


def AutoConnectivityBoltConnectionFunc(ProBar, LabelStatus):
	
	AllsConnections = base.PickEntities(deck, ['__CONNECTIONS__'])
	if len(AllsConnections) >0:
		guitk.BCProgressBarReset(ProBar)
		guitk.BCProgressBarSetTotalSteps(ProBar, len(AllsConnections))
		for i in range(0, len(AllsConnections), 1):
			base.Or(AllsConnections[i])
			base.Near(radius=10.)
			guitk.BCLabelSetText(LabelStatus, 'Auto Connectivity Spot Connection...........' + str(AllsConnections[i]._id))
			ValsOfBoltConnection = AllsConnections[i].get_entity_values(deck, ['Comment', 'X', 'Y', 'Z', 'DX', 'DY', 'DZ', 'Length', 'Num of Parts'])
			PropsVisible = base.CollectEntities(deck, None, ['SECTION_SHELL'], filter_visible = True)
			if len(PropsVisible) >0:
				ListIdPartsAddConnection = []
				for k in range(0, len(PropsVisible), 1):
					FacesOnPropVis = base.CollectEntities(deck, PropsVisible[k], ['FACE'], filter_visible = True)
					if len(FacesOnPropVis) >0:
						ProjConnectionToFaceVis = base.ProjectPointDirectional(target = FacesOnPropVis, point_x = ValsOfBoltConnection['X'], point_y = ValsOfBoltConnection['Y'], point_z = ValsOfBoltConnection['Z'], vec_x = ValsOfBoltConnection['DX'], vec_y = ValsOfBoltConnection['DY'], vec_z = ValsOfBoltConnection['DZ'], tolerance = ValsOfBoltConnection['Length'], project_on = 'faces')
						if ProjConnectionToFaceVis != None:
							ListIdPartsAddConnection.append('#' + str(PropsVisible[k]._id))
				if len(ListIdPartsAddConnection) >0:
					for j in range(0, ValsOfBoltConnection['Num of Parts'], 1):
						AllsConnections[i].set_entity_values(deck, {'P1': ''})
					for w in range(0, len(ListIdPartsAddConnection), 1):
						AllsConnections[i].set_entity_values(deck, {'P' + str(w+1): ListIdPartsAddConnection[w]})
					
					if str(len(ListIdPartsAddConnection)) != ValsOfBoltConnection['Comment']:
						base.Newpoint(ValsOfBoltConnection['X'], ValsOfBoltConnection['Y'], ValsOfBoltConnection['Z'])
					
			guitk.BCProgressBarSetProgress(ProBar, i +1)

def ConvertCadToSpotConnectionFunc(ProBar, LabelStatus):
#	AllsProps = base.CollectEntities(deck, None, ['SECTION_SHELL'])
	AllsProps = base.PickEntities(deck, ['SECTION_SHELL'])
	if len(AllsProps) >0:
		ListPairsGroupsFace, IsolateGroupFace = FindAllsGroupsSpotCadFunc(AllsProps, ProBar, LabelStatus)
		if len(ListPairsGroupsFace) >0:
			CreateNewConnectionPointsFunc(ListPairsGroupsFace, IsolateGroupFace, ProBar, LabelStatus)

def CreateNewConnectionPointsFunc(ListPairsGroupsFace, IsolateGroupFace, ProBar, LabelStatus):
	
	guitk.BCProgressBarReset(ProBar)
	guitk.BCProgressBarSetTotalSteps(ProBar, len(ListPairsGroupsFace))
	
	for i in range(0, len(ListPairsGroupsFace), 1):
		guitk.BCLabelSetText(LabelStatus, 'Converting Spot...........' + str(i))
		print('Converting Spot..' + str(i) + '/' + str(len(ListPairsGroupsFace)))
		ListGroupPairsFaces = []
		for k in range(0, len(ListPairsGroupsFace[i]), 1):
			ListGroupPairsFaces.extend(IsolateGroupFace[ListPairsGroupsFace[i][k]])
		if len(ListGroupPairsFaces) >0:
#			print(ListGroupPairsFaces)
			base.Or(ListGroupPairsFaces)
			ListCommentAddConnection = DivideTypeOfSpotCadFunc()
			if len(ListCommentAddConnection) >1:
				ListCommentAddConnection.append('Double')
				ListCommentAddConnection.reverse()
				
			CogOnPairsFace, VecsOnPairsFace = CreateCogOnSinglePropsFunc(ListGroupPairsFaces)
#			base.Newpoint(CogOnPairsFace[0], CogOnPairsFace[1], CogOnPairsFace[2])
			ProjPointToPairsFaceStatus = base.ProjectPointDirectional(target = ListGroupPairsFaces, point_x = CogOnPairsFace[0], point_y = CogOnPairsFace[1], point_z = CogOnPairsFace[2], vec_x = VecsOnPairsFace[0], vec_y = VecsOnPairsFace[1], vec_z = VecsOnPairsFace[2], tolerance = 10, project_on = 'faces')
			if ProjPointToPairsFaceStatus != None:
				DistanceCogPairsFace = CalculateDistance2PointsFunc(CogOnPairsFace, ProjPointToPairsFaceStatus)	
				BoltConnection = connections.CreateConnectionPoint(type = 'Bolt_Type', position = CogOnPairsFace)
				BoltConnection.set_entity_values(deck, {'DX': VecsOnPairsFace[0], 'DY': VecsOnPairsFace[1], 'DZ': VecsOnPairsFace[2], 'Length': DistanceCogPairsFace, 'FE Rep Type': 'BOLT', 'Search Dist': 5, 'Search On Direction': 'yes'})
				BoltConnection.set_entity_values(deck, {'Comment': ''})
				
				for w in range(0, len(ListCommentAddConnection), 1):
					ValsCommentBoltConnection = BoltConnection.get_entity_values(deck, ['Comment'])
					if ValsCommentBoltConnection['Comment'] == '':
						BoltConnection.set_entity_values(deck, {'Comment': ListCommentAddConnection[w]})
					else:
						BoltConnection.set_entity_values(deck, {'Comment': ValsCommentBoltConnection['Comment'] + ',' + ListCommentAddConnection[w]})
		
		guitk.BCProgressBarSetProgress(ProBar, i +1)

def FindAllsGroupsSpotCadFunc(AllsProps, ProBar, LabelStatus):
	
	ListPairsGroupsFace = []
	IsolateGroupFace = {}
	
	AllsFaceOnProps = base.CollectEntities(deck, AllsProps, ['FACE'])
	if len(AllsFaceOnProps) >0:
		IsolateGroupFace = base.IsolateConnectivityGroups(entities = AllsFaceOnProps, separate_at_blue_bounds = False, separate_at_pid_bounds = False)
		if IsolateGroupFace != None:
			ListGroupFaceCheck = []
			guitk.BCProgressBarReset(ProBar)
			guitk.BCProgressBarSetTotalSteps(ProBar, len(IsolateGroupFace))
			StepGroup1st = 0
			for NameGroup1st, GroupsFace1st in IsolateGroupFace.items():
				guitk.BCLabelSetText(LabelStatus, 'Loading...........' + NameGroup1st)
				print('Find group spot..' + str(StepGroup1st) + '/' + str(len(IsolateGroupFace)))
				PosSearchGroupCheck = FindEntityInListElementsFunc(NameGroup1st,ListGroupFaceCheck)
				if PosSearchGroupCheck == None:
					AxisCogOfFace, VecsOfFaces = CreateCogOnSinglePropsFunc(GroupsFace1st)
#					base.Newpoint(AxisCogOfFace[0], AxisCogOfFace[1], AxisCogOfFace[2])
					ListGroupNameDouble = []
					for NameGroup2nd, GroupsFace2nd in IsolateGroupFace.items():
						if NameGroup2nd != NameGroup1st:
							ProjPointToFaceStatus = base.ProjectPointDirectional(target = GroupsFace2nd, point_x = AxisCogOfFace[0], point_y = AxisCogOfFace[1], point_z = AxisCogOfFace[2], vec_x = VecsOfFaces[0], vec_y = VecsOfFaces[1], vec_z = VecsOfFaces[2], tolerance = 10, project_on = 'faces')
#							print(len(GroupsFace2nd), ProjPointToFaceStatus)
							if ProjPointToFaceStatus != None:
								ListGroupFaceCheck.append(NameGroup1st)
								ListGroupFaceCheck.append(NameGroup2nd)
								ListGroupNameDouble.append(NameGroup2nd)

					if len(ListGroupNameDouble)>0:
						ListGroupNameDouble.append(NameGroup1st)
						ListPairsGroupsFace.append(ListGroupNameDouble)
					else:
						base.Newpoint(AxisCogOfFace[0], AxisCogOfFace[1], AxisCogOfFace[2])
				
				StepGroup1st += 1
				guitk.BCProgressBarSetProgress(ProBar, StepGroup1st +1)
	
	return ListPairsGroupsFace, IsolateGroupFace					

def DivideTypeOfSpotCadFunc():
	
	ListCommentReq = []
	PropVisible = base.CollectEntities(deck, None, ['SECTION_SHELL'], filter_visible = True)
	if len(PropVisible) >0:
		for i in range(0, len(PropVisible), 1):
			ValsProps = PropVisible[i].get_entity_values(deck, ['COLOR_R', 'COLOR_G', 'COLOR_B'])
			if ValsProps['COLOR_R'] == 0 and ValsProps['COLOR_G'] == 255 and ValsProps['COLOR_B'] == 0:
				ListCommentReq.append('2')
#				PropVisible[i].set_entity_values(deck, {'Comment': 2})
			elif ValsProps['COLOR_R'] == 255 and ValsProps['COLOR_G'] == 255 and ValsProps['COLOR_B'] == 0:
				ListCommentReq.append('3')
#				PropVisible[i].set_entity_values(deck, {'Comment': 3})
			else:
				ListCommentReq.append('ReCheck,2')
#				PropVisible[i].set_entity_values(deck, {'Comment': '2_ReCheck'})
	
	ListCommentRemoveDouble = list(set(ListCommentReq))
	
	return ListCommentRemoveDouble

def CreateCogOnSinglePropsFunc(ListFacesImport):
	
	#### Create Cog On Group Face
	HotPointsOnFace = base.CollectEntities(deck, ListFacesImport, ['HOT POINT'])
	AxisPointsX = []
	AxisPointsY = []
	AxisPointsZ = []
	for i in range(0, len(HotPointsOnFace), 1):
		ValsHotPoints = HotPointsOnFace[i].get_entity_values(deck, ['X', 'Y', 'Z'])
		AxisPointsX.append(ValsHotPoints['X'])
		AxisPointsY.append(ValsHotPoints['Y'])
		AxisPointsZ.append(ValsHotPoints['Z'])
			
	AxisCogOfFace = [sum(AxisPointsX)/len(AxisPointsX), sum(AxisPointsY)/len(AxisPointsY), sum(AxisPointsZ)/len(AxisPointsZ)]
	
	#### Find Vector Project
	VecsOfFaces = []
	ConsOnFace = base.CollectEntities(deck, ListFacesImport, ['CONS'])
	for k in range(0, len(ConsOnFace), 1):
		ValsOfCons = ConsOnFace[k].get_entity_values(deck, ['Min Radius', 'Start Vector'])
		if ValsOfCons['Min Radius'] >1000:
			TokensStartVecs = ValsOfCons['Start Vector'].split(',')
			VecsOfFaces = [float(TokensStartVecs[0]), float(TokensStartVecs[1]), float(TokensStartVecs[2])]
			break
			
	return AxisCogOfFace, VecsOfFaces


def FindEntityInListElementsFunc(EntityElement, ListElements):
	
	try:
		Pos = ListElements.index(EntityElement)
	except:
		Pos = None
	else:
		Pos = Pos
	
	return Pos

def CalculateDistance2PointsFunc(Points1st, Points2nd):
	
	VecsAB = [Points2nd[0] - Points1st[0], Points2nd[1] - Points1st[1], Points2nd[2] - Points1st[2]]
	LenVecsAB = math.sqrt((VecsAB[0]*VecsAB[0]) + (VecsAB[1]*VecsAB[1]) + (VecsAB[2]*VecsAB[2]))
	
	return LenVecsAB
					
#ConvertCadToSpotWeldTool()










22.CreateBeamTool
# PYTHON script
import ansa
from ansa import *

deck = constants.LSDYNA
@session.defbutton('2-MESH', 'CreateBeamTool','Tạo Beam....')
def CreateBeamTool():
	CVals_21 = ["1HL_Tubul_1D", "1HL_Tubul_2D"]
	TopWindow = guitk.BCWindowCreate("Create Beam Tool ver01", guitk.constants.BCOnExitDestroy)
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Type Of Beam", guitk.constants.BCHorizontal)
	BCLabel_1 = guitk.BCLabelCreate(BCButtonGroup_1, "Type: ")
	BCComboBox_1 = guitk.BCComboBoxCreate(BCButtonGroup_1, CVals_21)
	
	BCButtonGroup_2 = guitk.BCButtonGroupCreate(TopWindow, "Options: ", guitk.constants.BCVertical)
	BCBoxLayout_1 = guitk.BCBoxLayoutCreate(BCButtonGroup_2, guitk.constants.BCHorizontal)
	BCLabel_2 = guitk.BCLabelCreate(BCBoxLayout_1, "Lenght Of Beam: ")
	BCLineEdit_1 = guitk.BCLineEditCreate(BCBoxLayout_1, "5")
	BCBoxLayout_2 = guitk.BCBoxLayoutCreate(BCButtonGroup_2, guitk.constants.BCHorizontal)
	BCLabel_3 = guitk.BCLabelCreate(BCBoxLayout_2, "Diameter:           ")
	BCLineEdit_2 = guitk.BCLineEditCreate(BCBoxLayout_2, "2")
	
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	_window = [BCComboBox_1, BCLineEdit_1, BCLineEdit_2]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, _window)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, _window)
	
	guitk.BCShow(TopWindow)

def RejectFunc(TopWindow, _window):
	
	return 1
#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, _window):
	
	TypeBeam = guitk.BCComboBoxCurrentText(_window[0])
	LenOfBeam = guitk.BCLineEditGetText(_window[1])
	DiamBeam = guitk.BCLineEditGetText(_window[2])
	
	CurveData = base.PickEntities(deck, ['CURVE'])
	if CurveData != None:
		for i in range(0, len(CurveData), 1):
			vals_curve = CurveData[i].get_entity_values(deck, ['Length'])
			ListAxisPointsEvaluate = DividePointsOnCurvesFunc(CurveData[i], vals_curve, LenOfBeam)
			if len(ListAxisPointsEvaluate) >0:
				CreateInfosBeamFunc(ListAxisPointsEvaluate, DiamBeam, TypeBeam)
				
	base.RedrawAll()

#################################
def CreateInfosBeamFunc(ListAxisPointsEvaluate, DiamBeam, TypeBeam):
	
	NewPropsBeam = CreateNewPropsOfBeamFunc(TypeBeam, DiamBeam)
	NodeOrient = base.CreateEntity(deck, 'NODE', {'X': ListAxisPointsEvaluate[0][0]+5, 'Y': ListAxisPointsEvaluate[0][1]+5, 'Z': ListAxisPointsEvaluate[0][2]+5})

	for i in range(0, len(ListAxisPointsEvaluate)-1, 1):
		Node1st = base.CreateEntity(deck, 'NODE', {'X': ListAxisPointsEvaluate[i][0], 'Y': ListAxisPointsEvaluate[i][1], 'Z': ListAxisPointsEvaluate[i][2]})
		Node2nd = base.CreateEntity(deck, 'NODE', {'X': ListAxisPointsEvaluate[i+1][0], 'Y': ListAxisPointsEvaluate[i+1][1], 'Z': ListAxisPointsEvaluate[i+1][2]})
		base.CreateEntity(deck, 'ELEMENT_BEAM_ELFORM_1', {'N1': Node1st._id, 'N2': Node2nd._id, 'PID': NewPropsBeam._id, 'Orient': 'With Node - Y Axis', 'N3': NodeOrient._id})
	
	mesh.AutoPaste(visible = True, project_on_geometry = False, move_to = "average pos", distance = 0.2)
	
#################################
def CreateNewPropsOfBeamFunc(TypeBeam, DiamBeam):
	
	if TypeBeam == '1HL_Tubul_1D':
		PidOfBeam = int(str(90000)+DiamBeam)
		NewPropsBeam = base.CreateEntity(deck, 'SECTION_BEAM_ELFORM_1', {'PID': PidOfBeam, 'Name': 'PBEAM D=' + DiamBeam + 'mm', 'ELFORM': '1 H-L', 'CST': '1 tubul.', 'TS1': DiamBeam, 'TS2': DiamBeam})
		if NewPropsBeam == None:
			NewPropsBeam = base.GetEntity(deck, 'SECTION_BEAM_ELFORM_1', PidOfBeam)
	
	return NewPropsBeam
	
#################################
def DividePointsOnCurvesFunc(CurveImport, vals_curve, LenOfBeam):
	
	ListAxisPointsEvaluate = []
	
	StepDivide = int(vals_curve['Length']/int(LenOfBeam))
	for i in range(0, StepDivide+1, 1):
		AxisPointsEvaluate = base.EvaluateCurvePoint(CurveImport, i/StepDivide)
#		base.Newpoint(AxisPointsEvaluate[0], AxisPointsEvaluate[1], AxisPointsEvaluate[2])
		ListAxisPointsEvaluate.append([AxisPointsEvaluate[0], AxisPointsEvaluate[1], AxisPointsEvaluate[2]])
	
	return ListAxisPointsEvaluate
		
#CreateBeamTool()












27.RealizeConnectionTool
# PYTHON script
import os
import ansa
from ansa import *

deck_infos = base.CurrentDeck()

#@session.defbutton('6_CONNECTION', 'RealizeConnectionTool',' Tự động aplly connection cho model....')
def RealizeConnectionTool():
	# Need some documentation? Run this with F5
	TopWindow = guitk.BCWindowCreate("Realize Connection Tool ver 1.0", guitk.constants.BCOnExitDestroy)
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select type of model", guitk.constants.BCHorizontal)
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
	
	Select_Connections = base.PickEntities(deck_infos, ['__CONNECTIONS__'], 'CONNECTION')
	if Select_Connections != None:
		infos_connection_spot, infos_connection_mastic, infos_connection_arcweld, infos_conection_glass_adhensive, infos_connection_glue_adhensive, infos_connection_error_comment = DivideTypeOfConnectionsFunc(Select_Connections)
		
		if len(infos_connection_spot) >0:
			RelizeSpotsConnectionFunc(infos_connection_spot, NVH_ModelStatus, Crash_ModelStatus, LabelStatus)
		if len(infos_connection_mastic) >0:
			RelizeMasticsConnectionFunc(infos_connection_mastic, NVH_ModelStatus, Crash_ModelStatus, LabelStatus)
		if len(infos_connection_arcweld) >0:
			RelizeArcWeldsConnectionFunc(infos_connection_arcweld, NVH_ModelStatus, Crash_ModelStatus, LabelStatus)		

############## Realize connection ArcWelds
def RelizeArcWeldsConnectionFunc(infos_connection_arcweld, NVH_ModelStatus, Crash_ModelStatus, LabelStatus):
	
	if NVH_ModelStatus == True:
		infos_arcweld_alumi = []
		infos_arcweld_steel = []
		
		for i in range(0, len(infos_connection_arcweld), 1):
			infos_connection_arcweld[i].set_entity_values(deck_infos, {'FE Rep Type': 'RBE3-HEXA-RBE3',
																								'PSOLID ID': 250000,
																								'Step Length': 5,		
																								'Height': 2,
																								'Num of Stripes': 1,
																								'Num of Layers': 1,
																								'Orient On P1': 'yes',
																								'Orient On P2': 'no',				
																								'RBE3 Pinflags': 123,
																								'Separate RefC Pinflags': 'no',
																								'Keep All Branches': 'yes',
																								'Feature Angle': 20,
																								'RBE3 Diam' : 10,
																								'Insert RBE2': 'no',
																								'Shrink Width': 'no',
																								'Distribution': 'Uniform',													
																							})
			type_of_arcweld = FindPropsConnectivityInConnectionFunc(infos_connection_arcweld[i])
			if type_of_arcweld == 'Alumi':
				infos_arcweld_alumi.append(infos_connection_arcweld[i])
			else:
				infos_arcweld_steel.append(infos_connection_arcweld[i])
		
		connections.ReApplyConnections(connections = infos_connection_mastic)
		if len(infos_arcweld_alumi) >0:
			elems_arc_alumi = base.CollectEntities(deck_infos, infos_arcweld_alumi, ['SOLID'])
			if len(elems_arc_alumi) >0:
				
				
	


def FindPropsConnectivityInConnectionFunc(SingleConnectionSeam):
	
	ListIdsPropsConnectivity = []
	type_of_arcweld = None
	dict_connectivity_connection = connections.GroupConnectionsByConnectivity(SingleConnectionSeam)
	if len(dict_connectivity_connection) >0:
		for string_connectivity, infos_connection in dict_connectivity_connection.items():
			if string_connectivity.find('#') != -1:
				string_props_connect = string_connectivity.replace('#', '')
			else:
				string_props_connect = string_connectivity
					
		ListIdsPropsConnectivity = string_props_connect.split(',')
	
	if len(ListIdsPropsConnectivity) >0:
		for i in range(0, len(ListIdsPropsConnectivity), 1):
			props_referen_ids  = base.GetEntity(deck_infos, '__PROPERTIES__', int(ListIdsPropsConnectivity[i]))
			if props_referen_ids != None:
				mats_referen = base.CollectEntities(deck_infos, props_referen_ids, '__MATERIALS__', recursive = True)
				vals_of_mats_props = mats_referen[0].get_entity_values(deck_infos, ['E', 'NU', 'RHO'])
				if vals_of_mats_props['E'] == 210000 and vals_of_mats_props['NU'] == 0.3 and vals_of_mats_props['RHO'] == 7.85E-9:
					type_of_arcweld = 'Steel'
					SingleConnectionSeam.set_entity_values(deck_infos, {'Comment': 'ARC_Steel'})
				elif vals_of_mats_props['E'] == 70000 and vals_of_mats_props['NU'] == 0.34 and vals_of_mats_props['RHO'] == 2.70E-09:
					type_of_arcweld = 'Alumi'
					SingleConnectionSeam.set_entity_values(deck_infos, {'Comment': 'ARC_Alumi'})
				else:
					type_of_arcweld = None
					SingleConnectionSeam.set_entity_values(deck_infos, {'Comment': 'ARC_Other'})
				
	return type_of_arcweld

############## Realize connection spotwelds
def RelizeMasticsConnectionFunc(infos_connection_mastic, NVH_ModelStatus, Crash_ModelStatus, LabelStatus)	:
	
	if NVH_ModelStatus == True:
		for i in range(0, len(infos_connection_mastic), 1):
			infos_connection_mastic[i].set_entity_values(deck_infos, {'FE Rep Type': 'RBE3-HEXA-RBE3',
																								'PSOLID ID': 730000,									
																								'RBE3 Pinflags': 123,
																								'Separate RefC Pinflags': 'no',
																								'Keep All Branches': 'yes',
																								'Feature Angle': 20,
																								'RBE3 Diam' : 10,
																								'Insert RBE2': 'no',
																								'Num of Layers': 1,
																								'Fix Hexa Quality': 'no',
																								'Force Gap': 'no',
																								'Generation Method': 'Projectional',
																							})
		collector_props_mastic = base.CollectNewModelEntities(deck_infos, ['PSOLID'])																					
		connections.ReApplyConnections(connections = infos_connection_mastic)
		new_props_mastic = collector_props_mastic.report()
		del collector_props_mastic
		if len(new_props_mastic) >0:
			mats_mastic = base.GetEntity(deck_infos, 'MAT1', 10004900)
			if mats_mastic == None:
				mats_mastic = base.CreateEntity(deck_infos, 'MAT1', {'MID': 10004900})
			
			mats_mastic.set_entity_values(deck_infos, {'Name': 'MASTIC-DOOR-ROOF', 'E': 5.96, 'NU': 0.49, 'RHO': 1.00E-09, 'DEFINED': 'YES'})
			new_props_mastic[0].set_entity_values(deck_infos, {'Name': 'MASTIC-DOOR-ROOF', 'MID': 10004900})
	
	if Crash_ModelStatus == True:
		Ids_mats_mastic = 10000490
		Name_props_mastic = 'MASTIC_SEALER'
		RealizeConnectionAdhesivesOfCrashModelFunc(infos_connection_mastic, Ids_mats_mastic, Name_props_mastic)
	
################# Realize Connection Adhensive for Crash model		
def RealizeConnectionAdhesivesOfCrashModelFunc(Infos_Connections, IdsMatElemsCons, NamePropsElemsCons):
	
	for i in range(0, len(Infos_Connections), 1):
		Infos_Connections[i].set_entity_values(deck_infos, {'FE Rep Type': 'HEXA-CONTACT',
																								'Contact': 'yes',
																								'Single Contact': 'yes',																								
																								'Num of Layers': 1,
																								'Specify Gap': 0.01,
																								'Force Gap': 'no',
																							})
	collector_props_cons= base.CollectNewModelEntities(deck_infos, ['SECTION_SOLID'])
	collector_sets_cons = base.CollectNewModelEntities(deck_infos, ['SET'])
	collector_contacts_cons = base.CollectNewModelEntities(deck_infos, ['CONTACT'])
	connections.ReApplyConnections(connections = Infos_Connections)
	new_props_cons = collector_props_cons.report()
	new_sets_cons = collector_sets_cons.report()
	new_contacts_cons = collector_contacts_cons.report()
	if len(new_props_cons) >0:
		mats_elems_cons = base.GetEntity(deck_infos, 'MAT1 MAT_ELASTIC', IdsMatElemsCons)
		if mats_elems_cons == None:
			mats_elems_cons = base.CreateEntity(deck_infos, 'MAT1 MAT_ELASTIC', {'MID': IdsMatElemsCons})
				
		mats_elems_cons.set_entity_values(deck_infos, {'Name': NamePropsElemsCons, 'E': 210000, 'PR': 0.3, 'RO': 7.83E-9, 'DEFINED': 'NO'})
			
		sections_elems_cons = base.GetEntity(deck_infos, 'DYNA_SECTION_SOLID', 50200001)
		if sections_elems_cons == None:
			sections_elems_cons = base.CreateEntity(deck_infos, 'DYNA_SECTION_SOLID', {'ID': 50200001, 'ELFORM': 2})
		
		new_props_cons[0].set_entity_values(deck_infos, {'Name': NamePropsElemsCons, 'MID': IdsMatElemsCons, 'USER_SECID': 'SECTION', 'SECID': sections_elems_cons._id})
			
		new_contacts_cons[0].set_entity_values(deck_infos, {'Name': '*CONTACT_' + NamePropsElemsCons, 'FROZEN_DELETE': 'YES', 'TYPE': 'TIED_SHELL_EDGE_TO_SURFACE_OFFSET', 'FS': 0.2, 'FD': 0.2, 'OPTIONAL CARDS A,B,C,D,E': 'NONE'})
		vals_infos_contact_mastic = new_contacts_cons[0].get_entity_values(deck_infos, ['SSID', 'MSID'])
		vals_infos_contact_mastic['SSID'].set_entity_values(deck_infos, {'Name': 'SLAVE PARTs_CONTACT_' + NamePropsElemsCons, 'FROZEN_DELETE': 'YES'})
		vals_infos_contact_mastic['MSID'].set_entity_values(deck_infos, {'Name': 'MASTER PARTs_CONTACT_' + NamePropsElemsCons, 'FROZEN_DELETE': 'YES'})

################### Tao vol shell skin			
		ElemsSolidOfConnection = base.CollectEntities(deck_infos, new_props_cons, ['__ELEMENTS__'])
		ElemsVolumeShells = mesh.CreateShellsOnSolidsPidSkin(ElemsSolidOfConnection, True)
		vals_elems_volume = ElemsVolumeShells[0].get_entity_values(deck_infos, ['PID'])
		base.RemoveFromSet(vals_infos_contact_mastic['SSID'], new_props_cons)
		base.AddToSet(vals_infos_contact_mastic['SSID'], vals_elems_volume['PID'])
			
################### Tao thong tin cho properties of vol shell
		sections_shell_skin = base.GetEntity(deck_infos, 'DYNA_SECTION_SHELL', 10230010)
		if sections_shell_skin == None:
			sections_shell_skin = base.CreateEntity(deck_infos, 'DYNA_SECTION_SHELL', {'SECID': 10230010, 'ELFORM': 2, 'T1': 0.1, 'SHRF': 0.833, 'NIP': 3})
		
		hourglass_shell_skin = base.GetEntity(deck_infos, 'HOURGLASS', 180009)
		if hourglass_shell_skin == None:
			hourglass_shell_skin = base.CreateEntity(deck_infos, 'HOURGLASS', {'HGID': 180009})
			
		vals_elems_volume['PID'].set_entity_values(deck_infos, {'MID': 19000000, 'USER_SECID': 'SECTION', 'SECID': sections_shell_skin._id, 'HGID': hourglass_shell_skin._id, '_CONTACT': 'CONTACT', 'OPTT': 0.7})			

############## Realize connection spotwelds
def RelizeSpotsConnectionFunc(infos_connection_spot, NVH_ModelStatus, Crash_ModelStatus, LabelStatus):
	
	if NVH_ModelStatus == True:
		for i in range(0, len(infos_connection_spot), 1):
			infos_connection_spot[i].set_entity_values(deck_infos, {'FE Rep Type': 'RBE3-HEXA-RBE3',
																								'PSOLID ID': 500000,
																								'Duplicate hexas': 'no',
																								'Do Not Move': 'yes',
																								'Force Ortho Solids': 'yes',
																								'Use Thickness as Height': 'yes',
																								'Specify Height': 'no',
																								'RBE3 Pinflags': 123,
																								'Separate RefC Pinflags': 'no',
																								'Feature Angle': 20,
																								'RBE3 Diam' : 10,
																								'Avoid Feature Lines': 'no',
																								'Cut off Adhesives': 'no'
																							})
		collector_props_spot = base.CollectNewModelEntities(deck_infos, ['PSOLID'])																					
		connections.ReApplyConnections(connections = infos_connection_spot)
		new_props_spots = collector_props_spot.report()
		del collector_props_spot
		if len(new_props_spots) >0:
			mats_spot = base.GetEntity(deck_infos, 'MAT1', 10350400)
			if mats_spot == None:
				mats_spot = base.CreateEntity(deck_infos, 'MAT1', {'MID': 10350400})
			
			mats_spot.set_entity_values(deck_infos, {'Name': 'SPOT-HEXA', 'E': 210000, 'NU': 0.3, 'RHO': '', 'DEFINED': 'YES'})
			new_props_spots[0].set_entity_values(deck_infos, {'Name': 'SPOT-HEXA', 'MID': 10350400})
		
	if Crash_ModelStatus == True:
		for i in range(0, len(infos_connection_spot), 1):
			infos_connection_spot[i].set_entity_values(deck_infos, {'FE Rep Type': 'DYNA SPOT WELD',
																								'Property': 'PSOLID',
																								'Use LS DYNA Mat100': 'yes',
																								'Do Not Move': 'yes',
																								'Create Spotweld Cluster': 'no',
																								'Number of hexas': 1,																																
																								'Use Thickness to Diameter': 'yes',
																								'Connect To Mesh': 'no',
																								'Contact': 'yes',
																								'Single Contact': 'yes',																								
																								'Cut off Adhesives': 'yes'
																							})
		collector_props_spot = base.CollectNewModelEntities(deck_infos, ['SECTION_SOLID'])
		collector_sets_spot = base.CollectNewModelEntities(deck_infos, ['SET'])
		collector_contacts_spot = base.CollectNewModelEntities(deck_infos, ['CONTACT'])
		connections.ReApplyConnections(connections = infos_connection_spot)
		new_props_spots = collector_props_spot.report()
		new_sets_spots = collector_sets_spot.report()
		new_contacts_spots = collector_contacts_spot.report()
		
		if len(new_props_spots) >0:
			mats_spot = base.GetEntity(deck_infos, 'MAT1 MAT_ELASTIC', 10048041)
			if mats_spot == None:
				mats_spot = base.CreateEntity(deck_infos, 'MAT1 MAT_ELASTIC', {'MID': 10048041})
				
			mats_spot.set_entity_values(deck_infos, {'Name': 'SPOTWELD_SOLID', 'E': 210000, 'PR': 0.3, 'RO': 7.83E-9, 'DEFINED': 'NO'})
			
			sections_spot = base.GetEntity(deck_infos, 'DYNA_SECTION_SOLID', 50200001)
			if sections_spot == None:
				sections_spot = base.CreateEntity(deck_infos, 'DYNA_SECTION_SOLID', {'ID': 50200001, 'ELFORM': 2})
			
			new_props_spots[0].set_entity_values(deck_infos, {'Name': 'SPOTWELD_SOLID', 'MID': 10048041, 'USER_SECID': 'SECTION', 'SECID': sections_spot._id})
			
			new_contacts_spots[0].set_entity_values(deck_infos, {'Name': '*CONTACT_SPOTWELD', 'FROZEN_DELETE': 'YES', 'TYPE': 'TIED_SHELL_EDGE_TO_SURFACE_OFFSET', 'FS': 0.2, 'FD': 0.2, 'OPTIONAL CARDS A,B,C,D,E': 'NONE'})
			vals_infos_contact = new_contacts_spots[0].get_entity_values(deck_infos, ['SSID', 'MSID'])
			vals_infos_contact['SSID'].set_entity_values(deck_infos, {'Name': 'SLAVE PARTs_CONTACT SPOTWELD', 'FROZEN_DELETE': 'YES'})
			vals_infos_contact['MSID'].set_entity_values(deck_infos, {'Name': 'MASTER PARTs_CONTACT SPOTWELD', 'FROZEN_DELETE': 'YES'})
		
############## Divide connection base on comment in connection
def DivideTypeOfConnectionsFunc(Select_Connections):
	
	infos_connection_spot = []
	infos_connection_mastic = []
	infos_connection_arcweld = []
	infos_conection_glass_adhensive = []
	infos_connection_glue_adhensive = []
	infos_connection_error_comment = []
	
	for i in range(0, len(Select_Connections), 1):
		vals_connection = 	Select_Connections[i].get_entity_values(deck_infos, ['Comment'])
		if vals_connection['Comment'] == 'SPOT':
			infos_connection_spot.append(Select_Connections[i])
		elif vals_connection['Comment'] == 'MASTIC':
			infos_connection_mastic.append(Select_Connections[i])
		elif vals_connection['Comment'] == 'ARC':
			infos_connection_arcweld.append(Select_Connections[i])
		elif vals_connection['Comment'] == 'GLASS':
			infos_conection_glass_adhensive.append(Select_Connections[i])
		elif vals_connection['Comment'] == 'GLUE':
			infos_connection_glue_adhensive.append(Select_Connections[i])
		else:
			infos_connection_error_comment.append(Select_Connections[i])
	
	return infos_connection_spot, infos_connection_mastic, infos_connection_arcweld, infos_conection_glass_adhensive, infos_connection_glue_adhensive, infos_connection_error_comment			
		 
RealizeConnectionTool()






10. Create Cnodes
# PYTHON script
import os
import ansa
from ansa import *

#@session.defbutton('3_FULL ASSEMBLY', 'CreateCnodeTool','Create connections between any groups')
def CreateCnodeTool():
	# Need some documentation? Run this with F5
	TopWindow = guitk.BCWindowCreate("Create Cnode Tool version 1.0", guitk.constants.BCOnExitDestroy)
	
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Status", guitk.constants.BCHorizontal)
	BCRadioButton_1 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "All Model", None, 0)
	BCRadioButton_2 = guitk.BCRadioButtonCreate(BCButtonGroup_1, "Visible Model", None, 0)
	guitk.BCRadioButtonSetChecked(BCRadioButton_2, True)
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_1 = guitk.BCLabelCreate(TopWindow, "")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)

	DataOnTop = [BCProgressBar_1, BCLabel_1, BCRadioButton_1, BCRadioButton_2]
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, DataOnTop)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, DataOnTop)
	
	guitk.BCShow(TopWindow)

def RejectFunc(TopWindow, DataOnTop):
	
	return 1

#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, DataOnTop):
	
	ProBar = DataOnTop[0]
	BCLabel = DataOnTop[1]
	AllModelStatus = DataOnTop[2]
	VisibleModelStatus = DataOnTop[3]
	
	if guitk.BCRadioButtonIsChecked(VisibleModelStatus) == True:
		AnsaGroupCollect = base.CollectEntities(constants.LSDYNA, None, 'ANSAGROUP', filter_visible = True)
	if guitk.BCRadioButtonIsChecked(AllModelStatus) == True:
		AnsaGroupCollect = base.CollectEntities(constants.LSDYNA, None, 'ANSAGROUP')
	
	if len(AnsaGroupCollect) >0:	
		ListGroupCollect = FindGroupOutsidePartManagerFunc(AnsaGroupCollect)
		if len(ListGroupCollect) >0:
			CreateCnodeForGroupCollectFunc(ListGroupCollect, ProBar, BCLabel, AllModelStatus, VisibleModelStatus)
			base.Compress('')

##***************** Tạo Cnode giữa các group ngoài cùng part manager
def CreateCnodeForGroupCollectFunc(ListGroupCollect, ProBar, BCLabel, AllModelStatus, VisibleModelStatus):
	
	guitk.BCProgressBarReset(ProBar)
	guitk.BCProgressBarSetTotalSteps(ProBar, len(ListGroupCollect))
	
	MatOnPropsOffset = base.CreateEntity(constants.LSDYNA, 'MAT20 MAT_RIGID', {'MID': 91000002})
	for i in range(0, len(ListGroupCollect), 1):
		ValsGroupCollect = base.GetEntityCardValues(constants.LSDYNA, ListGroupCollect[i], ['Name'])
		guitk.BCLabelSetText(BCLabel, 'Create Cnodes In Group: ' + ValsGroupCollect['Name'])
		base.Or(ListGroupCollect[i])
		DictRigidsBody_GroupsElemsConnect, ListNodesUnConnectRigidBody, ListElemShellVolSkin = FindRigidsCollectOtherGroupFunc(ListGroupCollect, i)
		ListElemsCreateContrained = []
		if len(DictRigidsBody_GroupsElemsConnect) >0:
			CreateConstrainRigidBodyForGroupFunc(DictRigidsBody_GroupsElemsConnect, ListElemsCreateContrained)
		
		if len(ListNodesUnConnectRigidBody) >0:
			RelativePointOnShellUnConnectFunc(ListNodesUnConnectRigidBody)
		
#		print(ListElemsCreateContrained)
		if len(ListElemShellVolSkin) >0:
			ListElemsVolSkinNeedRemove = list(set(ListElemShellVolSkin).difference(ListElemsCreateContrained))
#			aa = base.CreateEntity(constants.NASTRAN, "SET")
#			base.AddToSet(aa, ListElemsVolSkinNeedRemove)
			base.DeleteEntity(ListElemsVolSkinNeedRemove, True)
			
		guitk.BCProgressBarSetProgress(ProBar, i+1)

##***************** Tạo point tại các vị trí bắt liên kết bị lỗi
def RelativePointOnShellUnConnectFunc(ListNodesUnConnectRigidBody):
	
	ListPointsUnConnectRigids = []
	for i in range(0, len(ListNodesUnConnectRigidBody), 1):
		ValsNodesUnconnect = base.GetEntityCardValues(constants.LSDYNA, ListNodesUnConnectRigidBody[i], ['X', 'Y', 'Z'])
		ListPointsUnConnectRigids.append(base.Newpoint(ValsNodesUnconnect['X'], ValsNodesUnconnect['Y'], ValsNodesUnconnect['Z']))
	
	if len(ListPointsUnConnectRigids) >0:
		NamePointUnconnect = 'Part Unconnect Rigids Body'
		ModuleIdPointUnconnect = ''
		PartPointsUnconnect = CreateNewPartFunc(NamePointUnconnect, ModuleIdPointUnconnect)
		base.SetEntityPart(ListPointsUnConnectRigids, PartPointsUnconnect)

##***************** Tạo các Rigids liên kết với các group khác
def CreateConstrainRigidBodyForGroupFunc(DictRigidsBody_GroupsElemsConnect, ListElemsCreateContrained):
	
	for KeyRigidsBody, ListGroupElemsCollect in DictRigidsBody_GroupsElemsConnect.items():
		ListPropsConnectElemsOffset = DivideGroupShellsOnSingleGroupFunc(ListGroupElemsCollect, KeyRigidsBody)
		if len(ListPropsConnectElemsOffset) >0:
			CreateNewConstrainBodyFunc(KeyRigidsBody, ListPropsConnectElemsOffset)
			base.DeleteEntity(KeyRigidsBody, True)
			
			ListElemsCreateContrained.extend(base.CollectEntities(constants.LSDYNA, ListPropsConnectElemsOffset, ['ELEMENT_SHELL']))

####***************** Tạo constrain rigids body
def CreateNewConstrainBodyFunc(KeyRigidsBody, ListPropsConnectElemsOffset):
	
	PartRigidsConnect = base.GetEntityPart(KeyRigidsBody)
	ValsPartRigids = base.GetEntityCardValues(constants.LSDYNA, PartRigidsConnect, ['Hierarchy'])
	TokensLinkPartRigids = ValsPartRigids['Hierarchy'].split('/')
	GroupPartRigidsConnect = base.GetPartFromName(TokensLinkPartRigids[0])
	##### Tạo part chứa các constrain rigid body cho từng groups
	NamePartContrainBody = 'Part Constrain Rigids_' + TokensLinkPartRigids[0]
	ModuleIdsPartContrainBody = ''
	PartConstrainBody = CreateNewPartFunc(NamePartContrainBody, ModuleIdsPartContrainBody)
	
	for i in range(0, len(ListPropsConnectElemsOffset), 1):
		if ListPropsConnectElemsOffset[i] != ListPropsConnectElemsOffset[0]:
			ElemsConstrainBody = base.CreateEntity(constants.LSDYNA, 'CONSTRAINED_RIGID_BODIES', {'PIDM': ListPropsConnectElemsOffset[0]._id, 'PIDS': ListPropsConnectElemsOffset[i]._id, 'FROZEN_DELETE': 'YES', 'IFLAG': 0})
			base.SetEntityPart(ElemsConstrainBody, PartConstrainBody)
	
	base.SetEntityPart(PartConstrainBody, GroupPartRigidsConnect)

####***************** Chia các element tương ứng với từng groups
def DivideGroupShellsOnSingleGroupFunc(ListGroupElemsCollect, KeyRigidsBody):
	
	ListNameGroupConnect = []
	ListElementOffset = []
	ListPropsConnectElemsOffset = []
	
	for i in range(0, len(ListGroupElemsCollect), 1):
		PartShellsConnect = base.GetEntityPart(ListGroupElemsCollect[i][0])
		ValsPartConnect = base.GetEntityCardValues(constants.LSDYNA, PartShellsConnect, ['Hierarchy'])
		TokensLinkPart = ValsPartConnect['Hierarchy'].split('/')
#		GroupPartConnect = base.GetPartFromName(TokensLinkPart[0])
				
		DiameterFillHole = FindElementFillHoleInGroupShellFunc(ListGroupElemsCollect[i])
		if DiameterFillHole != None:
			base.Or(ListGroupElemsCollect[i])
			ListMeshFillHole = mesh.FillHole(diameter = round(DiameterFillHole, 2) + 0.2, point_on_center = False, convert_to_spot = False, create_curve = False, zones_num = 0)
			if len(ListMeshFillHole) >0:
				ListElementOffset.append(ListMeshFillHole)
				ListNameGroupConnect.append(TokensLinkPart[0])
			
		else:
			ListElementOffset.append(ListGroupElemsCollect[i])
			ListNameGroupConnect.append(TokensLinkPart[0])

	if len(ListNameGroupConnect) >0:
		ListNameGroupRemoveDuplicate = list(set(ListNameGroupConnect))
		if len(ListNameGroupRemoveDuplicate) >1:
			AllsPropsReport = SetupInfosToElemetOffsetFunc(ListNameGroupRemoveDuplicate, ListNameGroupConnect, ListElementOffset)
			ListPropsConnectElemsOffset.extend(AllsPropsReport)
		
		else:
			ListNameGroupNotRemove = ListNameGroupConnect
			AllsPropsReport = SetupInfosToElemetOffsetFunc(ListNameGroupNotRemove, ListNameGroupConnect, ListElementOffset)
	
	return ListPropsConnectElemsOffset						

def FindElementFillHoleInGroupShellFunc(ListElemsCheckFillHole):
	
	DiameterFillHole = None
	
	ValsElemsFillHole = base.GetEntityCardValues(constants.LSDYNA, ListElemsCheckFillHole[0], ['PID'])
	PropsOnShellFillHole = base.GetEntity(constants.LSDYNA, '__PROPERTIES__', ValsElemsFillHole['PID'])
	if PropsOnShellFillHole != None:
		object_BoundaryGroupShells = base.CollectBoundaryNodes(container = ListElemsCheckFillHole, include_second_order_nodes = False)
		object_BoundaryPropsShells = base.CollectBoundaryNodes(container = PropsOnShellFillHole, include_second_order_nodes = False)
		
		ListDiameterOfBoundaryProps = []
		for SingleDiameterOfBoundary in object_BoundaryPropsShells.diameters:
			ListDiameterOfBoundaryProps.append(SingleDiameterOfBoundary)
		
		if len(ListDiameterOfBoundaryProps) >0:
			for ListNodesBoundaryOnGroupShell in object_BoundaryGroupShells.perimeters:
				i = 0
				for ListsBoundaryNodesOnProps in object_BoundaryPropsShells.perimeters:
					if object_BoundaryPropsShells.diameters[i] != max(ListDiameterOfBoundaryProps):
						ListNodesBoundaryGroupWithProps = set(ListNodesBoundaryOnGroupShell).intersection(ListsBoundaryNodesOnProps)
						if len(ListNodesBoundaryGroupWithProps) >0:
							DiameterFillHole = object_BoundaryPropsShells.diameters[i]
					i += 1
		else:
			DiameterFillHole = None	
	
	return DiameterFillHole
		
def SetupInfosToElemetOffsetFunc(NameGroupReference, ListNameGroupConnect, ListElementOffset):
	
	AllsPropsReport = []
	for SingleNameGroupDuplicate in NameGroupReference:
		PartOffset, PropsOffset = CreateInfosElementOffsetFunc(SingleNameGroupDuplicate)
		AllsPropsReport.append(PropsOffset)
		for k in range(0, len(ListNameGroupConnect), 1):
			if ListNameGroupConnect[k] == SingleNameGroupDuplicate:
				base.SetEntityPart(ListElementOffset[k], PartOffset)
				for j in range(0, len(ListElementOffset[k]), 1):
					base.SetEntityCardValues(constants.LSDYNA, ListElementOffset[k][j], {'PID': PropsOffset._id})
	
	return AllsPropsReport	
		
####***************** Tạo part và properties, group chứa các element offset
def CreateInfosElementOffsetFunc(SingleNameGroupDuplicate):
			
	GroupPartConnect = base.GetPartFromName(SingleNameGroupDuplicate)
	PropsOffset = base.CreateEntity(constants.LSDYNA, 'SECTION_SHELL', {'Name': 'NULL_' + SingleNameGroupDuplicate, 'T1': 0.1, 'NLOC': 0, 'MID': 91000002})
	##### Tạo part chứa các element offset cho từng groups
	NamePartOffset = 'NULL_' + SingleNameGroupDuplicate + '_' + str(PropsOffset._id)
	ModuleIdsPartOffset = str(PropsOffset._id)
#	print(ModuleIdsPartOffset)
	PartOffset = CreateNewPartFunc(NamePartOffset, ModuleIdsPartOffset)
#	print(PartOffset)
	##### Tạo Group chứa các element offset cho từng groups
	NameGroupOffset = 'Part Null_' + SingleNameGroupDuplicate
	ModuleIdsGroupOffset = 'Part Null_' + SingleNameGroupDuplicate
	GroupsOffset = CreateNewGroupsFunc(NameGroupOffset, ModuleIdsGroupOffset)
	
	base.SetEntityPart(PartOffset, GroupsOffset)
	base.SetEntityPart(GroupsOffset, GroupPartConnect)
	
	return PartOffset, PropsOffset
	
##***************** Tìm các Rigids liên kết với các group khác
def FindRigidsCollectOtherGroupFunc(ListGroupCollect, i):
	
	DictRigidsBody_GroupsElemsConnect = {}
	ListNodesUnConnectRigidBody = []
	ListElemShellVolSkin = []
	#####***************** Lọc ra các rbody nào đang bị free
	DictRigidCollect_InfosNodes = {}
	RigidOnSingleGroups = base.CollectEntities(constants.LSDYNA, None, 'CONSTRAINED_NODAL_RIGID_BODY', filter_visible = True)
#	print(len(RigidOnSingleGroups))
	free_nodes = base.CheckFree('visible')
	if free_nodes !=0:
		for i in range(0, len(RigidOnSingleGroups), 1):
			NodesOnRigids = base.CollectEntities(constants.LSDYNA, RigidOnSingleGroups[i], 'NODE')
			ListNodeRigidsFree = set(NodesOnRigids).intersection(set(free_nodes))
			if len(ListNodeRigidsFree) >0:
				DictRigidCollect_InfosNodes[RigidOnSingleGroups[i]] = NodesOnRigids
				
	#####***************** Tìm các shell gắn với các rbody free
	if len(DictRigidCollect_InfosNodes) >0:
		FindElemsShellCollectWithRigidsFreeFunc(DictRigidCollect_InfosNodes, DictRigidsBody_GroupsElemsConnect, ListNodesUnConnectRigidBody, ListElemShellVolSkin)
	
	return DictRigidsBody_GroupsElemsConnect, ListNodesUnConnectRigidBody, ListElemShellVolSkin

##***************** Tìm các element shell gắn với các rigids body free
def FindElemsShellCollectWithRigidsFreeFunc(DictRigidCollect_InfosNodes, DictRigidsBody_GroupsElemsConnect, ListNodesUnConnectRigidBody, ListElemShellVolSkin):
	
	base.Or(DictRigidCollect_InfosNodes)
	base.Neighb('1')
	ListShellConvertFromSolid = []
	PropsSolidVisible = base.CollectEntities(constants.LSDYNA, None, 'SECTION_SOLID', filter_visible = True)
	if len(PropsSolidVisible) >0:
		for w in range(0, len(PropsSolidVisible), 1):
			SolidsVisible = base.CollectEntities(constants.LSDYNA, PropsSolidVisible[w], 'ELEMENT_SOLID', filter_visible = True)
			PartOnSolid = base.GetEntityPart(SolidsVisible[0])
			ListShellConvertFromSolid = mesh.CreateShellsOnSolidsPidSkin(SolidsVisible, True)
			ListElemShellVolSkin.extend(ListShellConvertFromSolid)
			base.SetEntityPart(ListShellConvertFromSolid, PartOnSolid)

	ElemsShellVisible = base.CollectEntities(constants.LSDYNA, None, 'ELEMENT_SHELL', filter_visible = True)
	if len(ElemsShellVisible) >0:
		GroupsElemsIsolate = base.IsolateConnectivityGroups(ElemsShellVisible, separate_at_blue_bounds = 1, separate_at_pid_bounds = 0, feature_angle = 0, feature_type = 'convex_and_concave')
		for KeyRigidsCollect, InfosNodesRigids in DictRigidCollect_InfosNodes.items():
			ListGroupsShellsCollect = []
			for NameGroupIsolate, GroupItemsIsolate in GroupsElemsIsolate.items():
				ValueCompareNode = FindBoundaryNodesInGroupElemsShellFunc(GroupItemsIsolate, InfosNodesRigids)
				ListShellsCollectRigids = []
				FlagCollectRigid = True
				for i in range(0, len(GroupItemsIsolate), 1):
					NodesOnElemShell = base.CollectEntities(constants.LSDYNA, GroupItemsIsolate[i], 'NODE')
					DuplicateNodeShell_NodeRigids = set(NodesOnElemShell).intersection(InfosNodesRigids)
					if len(DuplicateNodeShell_NodeRigids) >0:
						if ValueCompareNode == 1:
							if len(DuplicateNodeShell_NodeRigids) <= 2:
								ListShellsCollectRigids.append(GroupItemsIsolate[i])
							else:
								FlagCollectRigid = False
						else:
							if len(DuplicateNodeShell_NodeRigids) == len(NodesOnElemShell):
								ListShellsCollectRigids.append(GroupItemsIsolate[i])
							else:
								FlagCollectRigid = False
				
				if len(ListShellsCollectRigids) >0:
					ListGroupsShellsCollect.append(ListShellsCollectRigids)
				else:
					if FlagCollectRigid == False:
						NodesOnGroupItemIsolate = base.CollectEntities(constants.LSDYNA, GroupItemsIsolate, 'NODE')
						ListNodesUnConnectRigidBody.extend(NodesOnGroupItemIsolate)
			
			if len(ListGroupsShellsCollect) >0:
				DictRigidsBody_GroupsElemsConnect[KeyRigidsCollect] = ListGroupsShellsCollect
	
####***************** Tìm group ngoài cùng part manager							
def FindBoundaryNodesInGroupElemsShellFunc(GroupItemsIsolate, InfosNodesRigids):
	
	ListBoundaryNodes = []
	ValueCompareNode = None
	
	ObjectBoundareNodes = base.CollectBoundaryNodes(GroupItemsIsolate, include_second_order_nodes = False)
	if ObjectBoundareNodes != None:
		for prt_node_chains in ObjectBoundareNodes.perimeters:
			ListBoundaryNodes.extend(prt_node_chains)
	
	if len(ListBoundaryNodes) >0:
		DuplicateBoundaryNode_RigidsNodes = set(InfosNodesRigids).intersection(ListBoundaryNodes)
		if len(DuplicateBoundaryNode_RigidsNodes) >0:
			if len(DuplicateBoundaryNode_RigidsNodes) == 4:
				ValueCompareNode = 1
			else:
				ValueCompareNode = None
	return ValueCompareNode		

##***************** Tìm group ngoài cùng part manager
def FindGroupOutsidePartManagerFunc(AnsaGroupCollect):
	
	ListGroupCollect = []
	for i in range(0, len(AnsaGroupCollect), 1):
		ValsGroupCollect = base.GetEntityCardValues(constants.LSDYNA, AnsaGroupCollect[i], ['Name', 'Hierarchy'])
		if ValsGroupCollect['Hierarchy'] == '':
#			print(ValsGroupCollect['Name'])
			ListGroupCollect.append(AnsaGroupCollect[i])
	
	return ListGroupCollect

#######################
def CreateNewPartFunc(NamePart, ModuleIdsPart):
	
	NewParts = base.NewPart(NamePart, ModuleIdsPart)
	if NewParts == None:
		EntityPart = base.NameToEnts(NamePart)
		
		NewParts = EntityPart[0]
	
	return NewParts	

def CreateNewGroupsFunc(NameGroup, ModuleIdsGroup):
	NewGroups = base.NewGroup(NameGroup, ModuleIdsGroup)
	if NewGroups == None:
		EntityGroups = base.GetPartFromModuleId(ModuleIdsGroup)
		
		NewGroups = EntityGroups
	
	return NewGroups	
	
CreateCnodeTool()
