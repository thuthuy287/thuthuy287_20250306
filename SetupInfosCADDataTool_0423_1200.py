# PYTHON script
import os
import ansa
from ansa import *

#@session.defbutton('99_OTHER TOOL', 'Thickness00','Set độ dày của shell về giá trị 0')
deck_infos = constants.NASTRAN
def SetThickness00():
	AllsShellInModel = base.CollectEntities(deck_infos, None, ['SHELL'])
	if len(AllsShellInModel) >0:
		ListShellsErrorThickness = []
		for i in range(0, len(AllsShellInModel), 1):
			type_of_shells = AllsShellInModel[i].get_entity_values(deck_infos, ['type'])
			if type_of_shells['type'] == 'CTRIA3':
				AllsShellInModel[i].set_entity_values(deck_infos, {'T1': 0, 'T2': 0, 'T3': 0})
			if type_of_shells['type'] == 'CQUAD4':
				AllsShellInModel[i].set_entity_values(deck_infos, {'T1': 0, 'T2': 0, 'T3': 0, 'T4': 0})
	
	guitk.UserError('....Done.')
	

SetThickness00()


