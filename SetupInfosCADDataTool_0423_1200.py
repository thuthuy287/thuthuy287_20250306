# PYTHON script
import os
import ansa
from ansa import *
from os import path

DeckCurrent = constants.OPENFOAM
PathQuality = 'V:/13.INSTITUTES/01.ATI/05.CAE_Center/01.MOD/00.Common/100.Member/3576613_N.HIEP/'
### Đọc thông tin quality và parameter của Vinfast
@session.defbutton('98_QUALITY_PARAMETER', '10mm_CRASH_VF','Read infos quality and paramerter')
def ReadInfos10mm_Crash():
	mesh.ReadMeshParams(path.join(PathQuality, "Script_data/99-Param_Qual/VINFAST/10mm_Param_Crash_VINFAST.ansa_mpar"))
	mesh.ReadQualityCriteria(path.join(PathQuality, "Script_data/99-Param_Qual/VINFAST/10mm_Qual_Crash_VINFAST.ansa_qual"))

	base.SetViewButton({'HIDDEN': 'on'})

@session.defbutton('98_QUALITY_PARAMETER', '10mm_NASTRAN_VF','Read infos quality and paramerter')
def ReadInfos10mm_Nas():
	mesh.ReadMeshParams(path.join(PathQuality, "Script_data/99-Param_Qual/VINFAST/10mm_Param_NAS_VINFAST.ansa_mpar"))
	mesh.ReadQualityCriteria(path.join(PathQuality, "Script_data/99-Param_Qual/VINFAST/10mm_Qual_Nastran_VINFAST.ansa_qual"))

	base.SetViewButton({'HIDDEN': 'on'})	

@session.defbutton('98_QUALITY_PARAMETER', '5mm_CRASH_VF','Read infos quality and paramerter')
def ReadInfos5mm_Crash():
	mesh.ReadMeshParams(path.join(PathQuality, "Script_data/99-Param_Qual/VINFAST/5mm_Param_Crash_VINFAST.ansa_mpar"))
	mesh.ReadQualityCriteria(path.join(PathQuality, "Script_data/99-Param_Qual/VINFAST/5mm_Qual_Crash_VINFAST.ansa_qual"))

	base.SetViewButton({'HIDDEN': 'on'})		
	
@session.defbutton('98_QUALITY_PARAMETER', '5mm_NASTRAN_VF','Read infos quality and paramerter')
def ReadInfos5mm_Nas():
	mesh.ReadMeshParams(path.join(PathQuality, "Script_data/99-Param_Qual/VINFAST/5mm_Param_VINFAST_NASTRAN.ansa_mpar"))
	mesh.ReadQualityCriteria(path.join(PathQuality, "Script_data/99-Param_Qual/VINFAST/5mm_Qual_Nastran_VINFAST.ansa_qual"))

	base.SetViewButton({'HIDDEN': 'on'})




