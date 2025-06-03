# PYTHON script
import os
import ansa
from ansa import *

DeckCurrent = constants.OPENFOAM
@session.defbutton('1_CAD ASSEMBLY', 'MiddleSkinTool','Get Middle Faces On Parts')
def MiddleSkinTool():
	# Need some documentation? Run this with F5
	PropsVisCollect = base.CollectEntities(DeckCurrent, None, ['__PROPERTIES__'], filter_visible = True)
	if len(PropsVisCollect) >0:
		ListErrorSkin = []
		for i in range(0, len(PropsVisCollect), 1):
			FacesOnPropsVis = base.CollectEntities(DeckCurrent, PropsVisCollect[i], ['FACE'])
			Status_Skin = base.Skin(apply_thickness = True,
							new_pid = False,
							offset_type = 3,
							ok_to_offset = True,
							max_thickness = 6,
							delete = True,
							entities = FacesOnPropsVis,
#							similarity,
							treat_chamfers = True,
							new_part = False,
#							part,
#							property,
							deviation = 2)
			
			if Status_Skin == 0:
				ListErrorSkin.append(PropsVisCollect[i])
		
		if len(ListErrorSkin) >0:
			base.Or(ListErrorSkin)
			base.NewGroupFromVisible('Skin Part Error_' + str(ListErrorSkin[0]._id), '', create_links = 'yes')	

#MiddleSkinTool()


