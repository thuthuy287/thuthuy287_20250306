# PYTHON script
import os
import ansa
from ansa import *

deck_infos = constants.NASTRAN
RUN_DIR = '//10.128.10.55/ati$/13.INSTITUTES/01.ATI/05.CAE_Center/01.MOD/00.Common/100.Member/3576613_N.HIEP/Script_data'
def DivideArcWeldFemSiteTool(RUN_DIR):
	# Need some documentation? Run this with F5
	path_image_femsite = os.path.join(RUN_DIR, '97-Image')
	TopWindow = guitk.BCWindowCreate("Setup Infos for Welding Props Tool ver02", guitk.constants.BCOnExitDestroy)
	
	BCButtonGroup_1 = guitk.BCButtonGroupCreate(TopWindow, "Select Type Of FEMSITE", guitk.constants.BCVertical)
	BCButtonGroup_2 = guitk.BCButtonGroupCreate(BCButtonGroup_1, "Options With SHELL-SHELL", guitk.constants.BCHorizontal)
	BCCheckBox_1 = guitk.BCCheckBoxCreate(BCButtonGroup_2, "Overlap-joints")
	BCCheckBox_2 = guitk.BCCheckBoxCreate(BCButtonGroup_2, "Edge-joints")
	BCCheckBox_3 = guitk.BCCheckBoxCreate(BCButtonGroup_2, "Y-joints")
	
	guitk.BCAddToolTipImage(BCCheckBox_1, os.path.join(path_image_femsite, 'Overlap_joints.png'))
	guitk.BCAddToolTipImage(BCCheckBox_2, os.path.join(path_image_femsite, 'Edge_joint.png'))
	guitk.BCAddToolTipImage(BCCheckBox_3, os.path.join(path_image_femsite, 'Y-joints.png'))
	
	BCButtonGroup_3 = guitk.BCButtonGroupCreate(BCButtonGroup_1, "Options With SHELL-SOLID", guitk.constants.BCHorizontal)
	BCCheckBox_4 = guitk.BCCheckBoxCreate(BCButtonGroup_3, "Haz joints 1 Layer")
	BCCheckBox_5 = guitk.BCCheckBoxCreate(BCButtonGroup_3, "Haz joints 2 Layer")
	BCCheckBox_6 = guitk.BCCheckBoxCreate(BCButtonGroup_3, "Buttjoint_partial")
	
	guitk.BCAddToolTipImage(BCCheckBox_4, os.path.join(path_image_femsite, 'Haz_joints_one_layer.png'))
	guitk.BCAddToolTipImage(BCCheckBox_5, os.path.join(path_image_femsite, 'Haz_joints_two_layer.png'))
	guitk.BCAddToolTipImage(BCCheckBox_6, os.path.join(path_image_femsite, 'Buttjoint_partial.png'))
	
	BCButtonGroup_4 = guitk.BCButtonGroupCreate(BCButtonGroup_1, "Options With SOLID-SOLID", guitk.constants.BCHorizontal)
	BCCheckBox_7 = guitk.BCCheckBoxCreate(BCButtonGroup_4, "Lap joints")
	BCCheckBox_8 = guitk.BCCheckBoxCreate(BCButtonGroup_4, "T-joints")
	BCCheckBox_9 = guitk.BCCheckBoxCreate(BCButtonGroup_4, "Buttjoint_full_pene")
	
	guitk.BCAddToolTipImage(BCCheckBox_7, os.path.join(path_image_femsite, 'Lap_joints.png'))
	guitk.BCAddToolTipImage(BCCheckBox_8, os.path.join(path_image_femsite, 'T_joints.png'))
	guitk.BCAddToolTipImage(BCCheckBox_9, os.path.join(path_image_femsite, 'Buttjoint_full_pene.png'))
	
	BCProgressBar_1 = guitk.BCProgressBarCreate(TopWindow, 100)
	BCLabel_1 = guitk.BCLabelCreate(TopWindow, " ")
	BCDialogButtonBox_1 = guitk.BCDialogButtonBoxCreate(TopWindow)
	
	_window = [BCProgressBar_1, BCLabel_1, BCCheckBox_1, BCCheckBox_2, BCCheckBox_3, BCCheckBox_4, BCCheckBox_5, BCCheckBox_6, BCCheckBox_7, BCCheckBox_8, BCCheckBox_9]
	
	guitk.BCWindowSetRejectFunction(TopWindow, RejectFunc, _window)
	guitk.BCWindowSetAcceptFunction(TopWindow, AcceptFunc, _window)
	
	guitk.BCCheckBoxSetToggledFunction(BCCheckBox_1, CheckBox1Func, _window)
	guitk.BCCheckBoxSetToggledFunction(BCCheckBox_2, CheckBox2Func, _window)
	guitk.BCCheckBoxSetToggledFunction(BCCheckBox_3, CheckBox3Func, _window)
	guitk.BCCheckBoxSetToggledFunction(BCCheckBox_4, CheckBox4Func, _window)
	guitk.BCCheckBoxSetToggledFunction(BCCheckBox_5, CheckBox5Func, _window)
	guitk.BCCheckBoxSetToggledFunction(BCCheckBox_6, CheckBox6Func, _window)
	guitk.BCCheckBoxSetToggledFunction(BCCheckBox_7, CheckBox7Func, _window)
	guitk.BCCheckBoxSetToggledFunction(BCCheckBox_8, CheckBox8Func, _window)
	guitk.BCCheckBoxSetToggledFunction(BCCheckBox_9, CheckBox9Func, _window)
	
	guitk.BCShow(TopWindow)

def RejectFunc(TopWindow, _window):
	return 1

#***************** Khoi dong giao dien nguoi dung
def AcceptFunc(TopWindow, _window):
	
	ProbarStatus = _window[0]
	LabelStatus = _window[1]
####### SHELL vs SHELL	
	Overlap_joints_status = guitk.BCCheckBoxIsChecked(_window[2])
	Edge_joints_status = guitk.BCCheckBoxIsChecked(_window[3])
	Y_joints_status = guitk.BCCheckBoxIsChecked(_window[4])
####### SHELL vs SOLID
	Joints1LayerStatus = guitk.BCCheckBoxIsChecked(_window[5])
	Joints2LayerStatus = guitk.BCCheckBoxIsChecked(_window[6])
	ButtjointPartialStatus = guitk.BCCheckBoxIsChecked(_window[7])
####### SOLID vs SOLID
	LapJointsStatus = guitk.BCCheckBoxIsChecked(_window[8])
	T_jointsStatus = guitk.BCCheckBoxIsChecked(_window[9])
	Buttjoint_FullPene_Status = guitk.BCCheckBoxIsChecked(_window[10])
	
	for i in range(0, 50, 1):
		guitk.BCLabelSetText(LabelStatus, 'Select Arcweld Elements.....')
		base.SetPickMethod(base.constants.PID_REGION_SELECTION)
		ElemsWeldSelect = base.PickEntities(deck_infos, ['SHELL'])
		if ElemsWeldSelect != None:
			if Overlap_joints_status == True:
				OverlapJointsFunc(ElemsWeldSelect, LabelStatus)
			if Edge_joints_status == True:
				Edge_jointsFunc(ElemsWeldSelect, LabelStatus)
			if Y_joints_status == True:
				Y_jointsFunc(ElemsWeldSelect, LabelStatus)
			if Joints1LayerStatus == True:
				HazJoints1LayerFunc(ElemsWeldSelect, LabelStatus)
			if Joints2LayerStatus == True:
				HazJoints2LayerFunc(ElemsWeldSelect, LabelStatus)

		else:
			return 0

#######*********************** Haz joints one layer status **********************######
def HazJoints2LayerFunc(ElemsWeldSelect, LabelStatus):
	
	guitk.BCLabelSetText(LabelStatus, 'Select one props referens.....')
	Joints2Layer_props = base.PickEntities(deck_infos, ['PSHELL'])
	if Joints2Layer_props != None:
		if len(Joints2Layer_props) == 1:
			base.Or(ElemsWeldSelect)
			base.Neighb('2')
			Status_HazJoints2Layer = False
			DividePropsOfWeld_ZoneFunc(ElemsWeldSelect, Joints2Layer_props[0])
			DividePropsOfSolid_HAZ_ZoneFunc(ElemsWeldSelect, Status_HazJoints2Layer, Joints2Layer_props[0])
		
		else:
			guitk.UserError('Select two props.....')
			return 1

#######*********************** Haz joints one layer status **********************######
def HazJoints1LayerFunc(ElemsWeldSelect, LabelStatus):
	
	guitk.BCLabelSetText(LabelStatus, 'Select one props referens.....')
	Joints1Layer_props = base.PickEntities(deck_infos, ['PSHELL'])
	if Joints1Layer_props != None:
		if len(Joints1Layer_props) == 1:
			base.Or(ElemsWeldSelect)
			base.Neighb('2')
			Status_HazJoints1Layer = True
			DividePropsOfWeld_ZoneFunc(ElemsWeldSelect, Joints1Layer_props[0])
			DividePropsOfSolid_HAZ_ZoneFunc(ElemsWeldSelect, Status_HazJoints1Layer, Joints1Layer_props[0])
		
		else:
			guitk.UserError('Select two props.....')
			return 1
	

#######*********************** Y joints Status **********************######	
def Y_jointsFunc(ElemsWeldSelect, LabelStatus):
	
	guitk.BCLabelSetText(LabelStatus, 'Select two props referens.....')
	Yjoints_props = base.PickEntities(deck_infos, ['PSHELL'])
	if Yjoints_props != None:
		if len(Yjoints_props) == 2:
			base.Or(ElemsWeldSelect)
			base.Neighb('1')
			
			infos_thickness_all_props = []
			for w in range(0, len(Yjoints_props), 1):
				ValsThickness = Yjoints_props[w].get_entity_values(deck_infos, ['T'])
				infos_thickness_all_props.append(ValsThickness['T'])
				
			IndexMinThicknessProps = infos_thickness_all_props.index(min(infos_thickness_all_props))
			infos_props_Yjoints = Yjoints_props[IndexMinThicknessProps]
			
			Status_Yjoints = True
			DividePropsOfWeld_ZoneFunc(ElemsWeldSelect, infos_props_Yjoints)
			DividePropsOfHAZ_ZoneFunc(ElemsWeldSelect, Status_Yjoints)
			
		else:
			guitk.UserError('Select two props.....')
			return 1

#######*********************** Overlap joints Status **********************######	
def OverlapJointsFunc(ElemsWeldSelect, LabelStatus):
	
	guitk.BCLabelSetText(LabelStatus, 'Select only props referens.....')
	Overlap_props = base.PickEntities(deck_infos, ['PSHELL'])
	if Overlap_props != None:
		if len(Overlap_props) == 1:
			base.Or(ElemsWeldSelect)
			base.Neighb('1')
			
			Status_Overlap_joints = False
			DividePropsOfWeld_ZoneFunc(ElemsWeldSelect, Overlap_props[0])
			DividePropsOfHAZ_ZoneFunc(ElemsWeldSelect, Status_Overlap_joints)
	
		else:
			guitk.UserError('Select one props.....')
			return 1

#######*********************** Edge joints Status **********************######	
def Edge_jointsFunc(ElemsWeldSelect, LabelStatus):
	guitk.BCLabelSetText(LabelStatus, 'Select two props referens.....')
	Edge_props = base.PickEntities(deck_infos, ['PSHELL'])
	if Edge_props != None:
		if len(Edge_props) == 2:
			base.Or(ElemsWeldSelect)
			base.Neighb('1')
			
			for i in range(0, len(Edge_props), 1):
				infos_edge_props = Edge_props[i].get_entity_values(deck_infos, ['T'])
				Elems_edge_joints_vis = base.CollectEntities(deck_infos, Edge_props[i], ['SHELL'], filter_visible = True)
				Nodes_edge_joints = base.CollectEntities(deck_infos, Elems_edge_joints_vis, ['GRID'])
				
				infos_elems_edgeweld_common,  infos_elems_edgeweld_double= FindElemsCommonNodesFunc(Elems_edge_joints_vis, ElemsWeldSelect)
				if len(infos_elems_edgeweld_common)>0:
					infos_elems_edgeweld_single = infos_elems_edgeweld_common + infos_elems_edgeweld_double
					string_end_weld_edge_joint = '09'
					string_name_weld_edge_joint = 'ArcWeld'
					string_status_props_edge_joints = 'PSHELL'
					infos_thickness_props_edge_joints = infos_edge_props['T']
#					print(infos_elems_edgeweld_single)
					SetupInfosPropSolidsWeldFunc(infos_elems_edgeweld_single, Edge_props[i], string_end_weld_edge_joint, string_name_weld_edge_joint, string_status_props_edge_joints, infos_thickness_props_edge_joints)
					
					infos_elems_edgeweld_common,  infos_elems_edgeweld_double= FindElemsCommonNodesFunc(infos_elems_edgeweld_single, Elems_edge_joints_vis)
					if len(infos_elems_edgeweld_common)>0:
						infos_elems_around_edgeweld = infos_elems_edgeweld_common + infos_elems_edgeweld_double
						string_end_haz_edge_joint = '02'
						string_name_haz_edge_joint = 'HAZ_ZONE'
						SetupInfosPropSolidsWeldFunc(infos_elems_around_edgeweld, Edge_props[i], string_end_haz_edge_joint, string_name_haz_edge_joint, string_status_props_edge_joints, infos_thickness_props_edge_joints)
			
		else:
			guitk.UserError('Select two props.....')
			return 1


#######*********************** Divide props of elems weld  **********************######		
def DividePropsOfWeld_ZoneFunc(ElemsWeldSelect, props_reference):
	
	infos_props_referen = props_reference.get_entity_values(deck_infos, ['T'])
	string_end_weld_joint = '09'
	string_name_weld_joint = 'ArcWeld'
	string_status_weld_joints = 'PSHELL'
	infos_thickness_props_joints = infos_props_referen['T']
	SetupInfosPropSolidsWeldFunc(ElemsWeldSelect, props_reference, string_end_weld_joint, string_name_weld_joint, string_status_weld_joints, infos_thickness_props_joints)

#######*********************** Divide haz zone with shells elems  **********************######		
def DividePropsOfHAZ_ZoneFunc(ElemsWeldSelect, Status_add_weld):

	props_haz_joints_vis = base.CollectEntities(deck_infos, None, ['PSHELL', 'PSOLID'], filter_visible = True)
	if len(props_haz_joints_vis)>0:
		props_around_haz_joints = RemovePropsArcOnListPropsVisVisFunc(props_haz_joints_vis, ElemsWeldSelect)
		if len(props_around_haz_joints)>0:
			for i in range(0, len(props_around_haz_joints), 1):
				infos_haz_joints = props_around_haz_joints[i].get_entity_values(deck_infos, ['T', '__type__'])
				if infos_haz_joints['__type__'] == 'PSHELL':
					infos_thickness_haz_joins = infos_haz_joints['T']
				else:
					infos_thickness_haz_joins = 'N'
						
				elems_haz_joint_vis = base.CollectEntities(deck_infos, props_around_haz_joints[i], ['SHELL', 'SOLID'], filter_visible = True)
				if len(elems_haz_joint_vis)>0:
					infos_elems_haz_joints, infos_elems_double_weld = FindElemsCommonNodesFunc(ElemsWeldSelect, elems_haz_joint_vis)
					if len(infos_elems_haz_joints)>0:
						string_end_haz_joint = '02'
						string_name_haz_joint = 'HAZ_ZONE'
						string_status_haz_joints = infos_haz_joints['__type__']
						SetupInfosPropSolidsWeldFunc(infos_elems_haz_joints, props_around_haz_joints[i], string_end_haz_joint, string_name_haz_joint, string_status_haz_joints, infos_thickness_haz_joins)
					if Status_add_weld == True and len(infos_elems_double_weld) >0:
						DividePropsOfWeld_ZoneFunc(infos_elems_double_weld, props_around_haz_joints[i])

#######*********************** Divide haz zone with solid elems  **********************######	
def DividePropsOfSolid_HAZ_ZoneFunc(ElemsWeldSelect, StatusZoneLayer, props_solid_weld_referen):
	
	infos_props_vis = base.CollectEntities(deck_infos, None, ['PSHELL', 'PSOLID'], filter_visible = True)
	if len(infos_props_vis) >0:
		infos_props_divide_vis = RemovePropsArcOnListPropsVisVisFunc(infos_props_vis, ElemsWeldSelect)
		if len(infos_props_divide_vis)>0:
			for i in range(0, len(infos_props_divide_vis), 1):
				infos_props_divide = infos_props_divide_vis[i].get_entity_values(deck_infos, ['T', '__type__'])
				if infos_props_divide['__type__'] == 'PSHELL':
					infos_shells_vis = base.CollectEntities(deck_infos, infos_props_divide_vis[i], ['SHELL'], filter_visible = True)
					if len(infos_shells_vis)>0:
						infos_shells_haz_zone, infos_shell_double_weld = FindElemsCommonNodesFunc(ElemsWeldSelect, infos_shells_vis)
						if len(infos_shells_haz_zone)>0:
							string_end_haz_shell = '02'
							string_name_haz_shell = 'HAZ_ZONE'
							string_status_haz_shell = infos_props_divide['__type__']
							SetupInfosPropSolidsWeldFunc(infos_shells_haz_zone, infos_props_divide_vis[i], string_end_haz_shell, string_name_haz_shell, string_status_haz_shell, infos_props_divide['T'])
				else:
					infos_solids_vis = base.CollectEntities(deck_infos, infos_props_divide_vis[i], ['SOLID'], filter_visible = True)
					if len(infos_solids_vis)>0:
						infos_type_solid = infos_solids_vis[0].get_entity_values(deck_infos, ['type'])
						infos_elems_one_nodes, infos_elems_two_nodes, infos_elem_solid_other = FindSolidsCommonNodesWeldFunc(ElemsWeldSelect, infos_solids_vis)
						infos_solids_haz_zone_1st = infos_elems_one_nodes + infos_elems_two_nodes
						if len(infos_solids_haz_zone_1st)>0:
							string_end_haz_solid_1st = '01'
							string_name_haz_solid_1st = 'HAZ_ZONE_1st'
							string_status_haz_solid_1st = 'PSOLID'
							infos_thickness_haz_zone_1st = 'N'
							SetupInfosPropSolidsWeldFunc(infos_solids_haz_zone_1st, infos_props_divide_vis[i], string_end_haz_solid_1st, string_name_haz_solid_1st, string_status_haz_solid_1st, infos_thickness_haz_zone_1st)
							SetInfosNullShellOfSolidsFunc(infos_props_divide_vis[i], infos_solids_haz_zone_1st, ElemsWeldSelect, StatusZoneLayer, props_solid_weld_referen, infos_solids_vis)

#######*********************** Create Vol shell skin around solid  **********************######	
def SetInfosNullShellOfSolidsFunc(infos_props_haz_zone_referen, infos_haz_zone_solids, ElemsWeldSelect, StatusZoneLayer, props_solid_weld_referen, infos_solids_vis):
	
	infos_VolShells_skin = base.CreateShellsFromSolidFacets(option = "skin", ret_ents = True, solids = infos_solids_vis)
	if len(infos_VolShells_skin)>0:
		infos_nullshells_one_nodes, infos_nullshells_twonodes, infos_nullshells_other = FindSolidsCommonNodesWeldFunc(ElemsWeldSelect, infos_VolShells_skin)
		if len(infos_nullshells_other)>0:
			base.DeleteEntity(infos_nullshells_other, True)
			
		infos_nullshells_skin = infos_nullshells_one_nodes + infos_nullshells_twonodes
		CreatePropsOfNullShellsFunc(infos_nullshells_skin, infos_props_haz_zone_referen, props_solid_weld_referen)
		if StatusZoneLayer == False:
			if len(infos_nullshells_twonodes)>0:
				infos_solids_remove_zone_1st = list(set(infos_solids_vis).difference(infos_haz_zone_solids))
				infos_solids_zone_2nd_common, infos_solids_zone_2nd_one_nodes, infos_other_solid_zone = FindSolidsCommonNodesWeldFunc(infos_nullshells_twonodes, infos_solids_remove_zone_1st)
				infos_solid_zone_2nd_referen = infos_solids_zone_2nd_common + infos_solids_zone_2nd_one_nodes
				if len(infos_solid_zone_2nd_referen)>0:
					string_end_haz_solid_2nd = '02'
					string_name_haz_solid_2nd = 'HAZ_ZONE_1st'
					string_status_haz_2nd = 'PSOLID'
					infos_thickness_haz_zone_2nd = 'N'
					SetupInfosPropSolidsWeldFunc(infos_solid_zone_2nd_referen, infos_props_haz_zone_referen, string_end_haz_solid_2nd, string_end_haz_solid_2nd, string_status_haz_2nd, infos_thickness_haz_zone_2nd)

#######*********************** Find solid elems common nodes  **********************######	
def FindSolidsCommonNodesWeldFunc(infos_solids_source, infos_solids_target):
	
	infos_solids_common = []
	infos_solids_onenodes =[]
	infos_solids_other = []
	
	nodes_solids_source = base.CollectEntities(deck_infos, infos_solids_source, ['GRID'])
	for i in range(0, len(infos_solids_target), 1):
		nodes_solids_target = base.CollectEntities(deck_infos, infos_solids_target[i], ['GRID'])
		infos_nodes_solids_common = list(set(nodes_solids_source).intersection(nodes_solids_target))
		if len(infos_nodes_solids_common)>0:
			if len(infos_nodes_solids_common) == 1:
				infos_solids_onenodes.append(infos_solids_target[i])
			else:
				infos_solids_common.append(infos_solids_target[i])
		else:
			infos_solids_other.append(infos_solids_target[i])
		
	return infos_solids_onenodes, infos_solids_common, infos_solids_other
										
#######*********************** Find element common nodes  **********************######	
def FindElemsCommonNodesFunc(infos_elems_source, infos_elems_target):
	
	infos_elems_common = []
	infos_elems_double_weld = []
	nodes_elems_source = base.CollectEntities(deck_infos, infos_elems_source, ['GRID'])
	for k in range(0, len(infos_elems_target), 1):
		nodes_elems_target = base.CollectEntities(deck_infos, infos_elems_target[k], ['GRID'])
		infos_nodes_common = list(set(nodes_elems_source).intersection(nodes_elems_target))
		if len(infos_nodes_common)>0:
			infos_elems_common.append(infos_elems_target[k])
			if len(infos_nodes_common) == len(nodes_elems_target):
				infos_elems_double_weld.append(infos_elems_target[k])
				
	return infos_elems_common, infos_elems_double_weld


#######*********************** Thiet dinh thong tin properties cho null shell skin **********************######
def CreatePropsOfNullShellsFunc(infos_nullshells_skin, infos_props_haz_zone_referen, props_solid_weld_referen):
	
	infos_props_zone_referen = infos_props_haz_zone_referen.get_entity_values(deck_infos, ['MID'])
	infos_mat_origin_of_props_zone = infos_props_zone_referen['MID']
	infos_new_IdMat_nullshells = int(str(infos_mat_origin_of_props_zone._id)[0:6]+'09')
	infos_mat_nullshell_referen = base.GetEntity(deck_infos, '__MATERIALS__', int(infos_new_IdMat_nullshells))
	if infos_mat_nullshell_referen == None:
		infos_new_mat_nullshells = base.CopyEntity(None, infos_mat_origin_of_props_zone)
		infos_new_mat_nullshells.set_entity_values(deck_infos, {'MID': infos_new_IdMat_nullshells})
	
	vals_props_weld_solid = props_solid_weld_referen.get_entity_values(deck_infos, ['T'])
	
	infos_props_nullshells_referen = None
	for i in range(0, 9, 1):
		id_of_props_nullshells = infos_props_haz_zone_referen._id + (i*10 + 7)
		props_nullshells_07 = base.GetEntity(deck_infos, 'PSHELL', id_of_props_nullshells)
#		print(props_nullshells_07)
		if props_nullshells_07 != None:
			vals_props_nullshells_07 = props_nullshells_07.get_entity_values(deck_infos, ['T'])
#			print(vals_props_nullshells_07 ['T'])
#			print(vals_props_weld_solid['T']/2)
			if vals_props_nullshells_07 ['T'] == vals_props_weld_solid['T']/2:
				infos_props_nullshells_referen = props_nullshells_07
				break
			else:
				continue
		else:
			infos_props_nullshells_referen = base.CreateEntity(deck_infos, 'PSHELL', {'PID': id_of_props_nullshells, 'Name': 'Null_of_HAZ_Zone_1st_' + str(vals_props_weld_solid['T']/2) + 'mm', 'T': vals_props_weld_solid['T']/2, 'MID1': infos_new_IdMat_nullshells, 'MID2': infos_new_IdMat_nullshells, 'MID3': infos_new_IdMat_nullshells})
			break
	
	if infos_props_nullshells_referen != None:
		for k in range(0, len(infos_nullshells_skin), 1):
			infos_nullshells_skin[k].set_entity_values(deck_infos, {'PID': infos_props_nullshells_referen._id})
	
#######*********************** Thiet dinh thong tin properties cho cac part **********************######
def SetupInfosPropSolidsWeldFunc(InfosElemsDivideProps, PropsInfosOrigin, EntityStringEndHeatZone, EntityNameHeatZone, StatusProps, InfosThickness):
	
	type_props_origin = PropsInfosOrigin.get_entity_values(deck_infos, ['__type__', 'MID', 'MID1'])
	if type_props_origin['__type__'] == 'PSHELL':
		InfosMatsOrigin = type_props_origin['MID1']
	else:
		InfosMatsOrigin = type_props_origin['MID']
	
	MatIdsOnNewProps = int(str(InfosMatsOrigin._id)[0:6]+EntityStringEndHeatZone)
	MatsEntityReferenIds = base.GetEntity(deck_infos, '__MATERIALS__', int(MatIdsOnNewProps))
	if MatsEntityReferenIds == None:
		NewMatsOnPropsReferen = base.CopyEntity(None, InfosMatsOrigin)
		NewMatsOnPropsReferen.set_entity_values(deck_infos, {'MID': MatIdsOnNewProps})
	
	NewIdsOnSolidsProps = int(str(PropsInfosOrigin._id)[0:5]+EntityStringEndHeatZone)
	if StatusProps == 'PSOLID':
		PropsSolidsReferenIds = base.GetEntity(deck_infos, 'PSOLID', int(NewIdsOnSolidsProps))
		PropsSolidsReferenIds = base.GetEntity(deck_infos, 'PSOLID', int(NewIdsOnSolidsProps))
		if PropsSolidsReferenIds != None:
			PropsSolidsReferenIds.set_entity_values(deck_infos, {'MID': MatIdsOnNewProps})
		else:
			NewPropsSolidsElems = base.CopyEntity(None, PropsInfosOrigin)
			NewPropsSolidsElems.set_entity_values(deck_infos, {'PID': NewIdsOnSolidsProps, 'Name': EntityNameHeatZone + '_' + InfosThickness, 'MID': MatIdsOnNewProps})
	
	elif StatusProps == 'PSHELL':
		PropsShellsReferenIds = base.GetEntity(deck_infos, 'PSHELL', int(NewIdsOnSolidsProps))
		if PropsShellsReferenIds != None:
			PropsShellsReferenIds.set_entity_values(deck_infos, {'MID1': MatIdsOnNewProps, 'MID2': MatIdsOnNewProps, 'MID3': MatIdsOnNewProps})
		else:
			NewPropsShellsElems = base.CreateEntity(deck_infos, 'PSHELL', {'PID': NewIdsOnSolidsProps, 'Name': EntityNameHeatZone + '_' + str(InfosThickness) + 'mm', 'T': InfosThickness, 'MID1': MatIdsOnNewProps, 'MID2': MatIdsOnNewProps, 'MID3': MatIdsOnNewProps})
		
	for i in range(0, len(InfosElemsDivideProps), 1):
		InfosElemsDivideProps[i].set_entity_values(deck_infos, {'PID': NewIdsOnSolidsProps})

#######*********************** Loai bo cac PID khong co duoi la 00 **********************######
def RemovePropsArcOnListPropsVisVisFunc(AllsPropsVisible, ListElemsArcWeld):
	
	ListPropsVisAroundArc = []
	for i in range(0, len(AllsPropsVisible), 1):
		if len(str(AllsPropsVisible[i]._id)) == 7:
			vals_props_vis = AllsPropsVisible[i].get_entity_values(deck_infos, ['__type__'])
			if vals_props_vis['__type__'] == 'PSHELL':
				if str(AllsPropsVisible[i]._id).endswith('00') or str(AllsPropsVisible[i]._id).endswith('02'):
					ElemsOnPropVis = base.CollectEntities(deck_infos, AllsPropsVisible[i], ['SHELL', 'SOLID'], filter_visible = True)
					ListCommonShellArc = list(set(ListElemsArcWeld).intersection(ElemsOnPropVis))
					if len(ListCommonShellArc) == 0:
						ListPropsVisAroundArc.append(AllsPropsVisible[i])
			else:
				ListPropsVisAroundArc.append(AllsPropsVisible[i])
			
	return ListPropsVisAroundArc

#######*********************** Set infos window button **********************######
def CheckBox1Func(CheckBox_1, state, _window):
	if guitk.BCCheckBoxIsChecked(CheckBox_1):
		guitk.BCCheckBoxSetChecked(_window[3], False); guitk.BCCheckBoxSetChecked(_window[4], False); guitk.BCCheckBoxSetChecked(_window[5], False)
		guitk.BCCheckBoxSetChecked(_window[6], False); guitk.BCCheckBoxSetChecked(_window[7], False)	; guitk.BCCheckBoxSetChecked(_window[8], False)
		guitk.BCCheckBoxSetChecked(_window[9], False); guitk.BCCheckBoxSetChecked(_window[10], False)
	
def CheckBox2Func(CheckBox_2, state, _window):
	if guitk.BCCheckBoxIsChecked(CheckBox_2):
		guitk.BCCheckBoxSetChecked(_window[2], False); guitk.BCCheckBoxSetChecked(_window[4], False); guitk.BCCheckBoxSetChecked(_window[5], False)
		guitk.BCCheckBoxSetChecked(_window[6], False); guitk.BCCheckBoxSetChecked(_window[7], False)	; guitk.BCCheckBoxSetChecked(_window[8], False)
		guitk.BCCheckBoxSetChecked(_window[9], False); guitk.BCCheckBoxSetChecked(_window[10], False)

def CheckBox3Func(CheckBox_3, state, _window):
	if guitk.BCCheckBoxIsChecked(CheckBox_3):
		guitk.BCCheckBoxSetChecked(_window[2], False); guitk.BCCheckBoxSetChecked(_window[3], False); guitk.BCCheckBoxSetChecked(_window[5], False)
		guitk.BCCheckBoxSetChecked(_window[6], False); guitk.BCCheckBoxSetChecked(_window[7], False)	; guitk.BCCheckBoxSetChecked(_window[8], False)
		guitk.BCCheckBoxSetChecked(_window[9], False); guitk.BCCheckBoxSetChecked(_window[10], False)	

def CheckBox4Func(CheckBox_4, state, _window):
	if guitk.BCCheckBoxIsChecked(CheckBox_4):
		guitk.BCCheckBoxSetChecked(_window[2], False); guitk.BCCheckBoxSetChecked(_window[3], False); guitk.BCCheckBoxSetChecked(_window[4], False)
		guitk.BCCheckBoxSetChecked(_window[6], False); guitk.BCCheckBoxSetChecked(_window[7], False)	; guitk.BCCheckBoxSetChecked(_window[8], False)
		guitk.BCCheckBoxSetChecked(_window[9], False); guitk.BCCheckBoxSetChecked(_window[10], False)

def CheckBox5Func(CheckBox_5, state, _window):
	if guitk.BCCheckBoxIsChecked(CheckBox_5):
		guitk.BCCheckBoxSetChecked(_window[2], False); guitk.BCCheckBoxSetChecked(_window[3], False); guitk.BCCheckBoxSetChecked(_window[4], False)
		guitk.BCCheckBoxSetChecked(_window[5], False); guitk.BCCheckBoxSetChecked(_window[7], False)	; guitk.BCCheckBoxSetChecked(_window[8], False)
		guitk.BCCheckBoxSetChecked(_window[9], False); guitk.BCCheckBoxSetChecked(_window[10], False)	

def CheckBox6Func(CheckBox_6, state, _window):
	if guitk.BCCheckBoxIsChecked(CheckBox_6):
		guitk.BCCheckBoxSetChecked(_window[2], False); guitk.BCCheckBoxSetChecked(_window[3], False); guitk.BCCheckBoxSetChecked(_window[4], False)
		guitk.BCCheckBoxSetChecked(_window[5], False); guitk.BCCheckBoxSetChecked(_window[6], False)	; guitk.BCCheckBoxSetChecked(_window[8], False)
		guitk.BCCheckBoxSetChecked(_window[9], False); guitk.BCCheckBoxSetChecked(_window[10], False)

def CheckBox7Func(CheckBox_7, state, _window):
	if guitk.BCCheckBoxIsChecked(CheckBox_7):
		guitk.BCCheckBoxSetChecked(_window[2], False); guitk.BCCheckBoxSetChecked(_window[3], False); guitk.BCCheckBoxSetChecked(_window[4], False)
		guitk.BCCheckBoxSetChecked(_window[5], False); guitk.BCCheckBoxSetChecked(_window[6], False)	; guitk.BCCheckBoxSetChecked(_window[7], False)
		guitk.BCCheckBoxSetChecked(_window[9], False); guitk.BCCheckBoxSetChecked(_window[10], False)

def CheckBox8Func(CheckBox_8, state, _window):
	if guitk.BCCheckBoxIsChecked(CheckBox_8):
		guitk.BCCheckBoxSetChecked(_window[2], False); guitk.BCCheckBoxSetChecked(_window[3], False); guitk.BCCheckBoxSetChecked(_window[4], False)
		guitk.BCCheckBoxSetChecked(_window[5], False); guitk.BCCheckBoxSetChecked(_window[6], False)	; guitk.BCCheckBoxSetChecked(_window[7], False)
		guitk.BCCheckBoxSetChecked(_window[8], False); guitk.BCCheckBoxSetChecked(_window[10], False)

def CheckBox9Func(CheckBox_9, state, _window):
	if guitk.BCCheckBoxIsChecked(CheckBox_9):
		guitk.BCCheckBoxSetChecked(_window[2], False); guitk.BCCheckBoxSetChecked(_window[3], False); guitk.BCCheckBoxSetChecked(_window[4], False)
		guitk.BCCheckBoxSetChecked(_window[5], False); guitk.BCCheckBoxSetChecked(_window[6], False)	; guitk.BCCheckBoxSetChecked(_window[7], False)
		guitk.BCCheckBoxSetChecked(_window[8], False); guitk.BCCheckBoxSetChecked(_window[9], False)
	
DivideArcWeldFemSiteTool(RUN_DIR)
