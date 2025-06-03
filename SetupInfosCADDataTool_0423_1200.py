# PYTHON script
import os
import ansa
from ansa import *

#@session.defbutton('99_OTHER TOOL', 'Thickness00','Set độ dày của shell về giá trị 0')
def SetThickness00():
	# Need some documentation? Run this with F5

	AllsShellInModel = base.CollectEntities(constants.PAMCRASH, None, ['SHELL'])
	if len(AllsShellInModel) >0:
		ListShellsErrorThickness = []
		for i in range(0, len(AllsShellInModel), 1):
			ValsShellCheck = base.GetEntityCardValues(constants.PAMCRASH, AllsShellInModel[i], ['h'])
			print(AllsShellInModel[i]._id, ValsShellCheck['h'])
			if ValsShellCheck['h'] != 0 and ValsShellCheck['h'] != '':
				ListShellsErrorThickness.append(AllsShellInModel[i])
		
		if len(ListShellsErrorThickness) >0:
			for k in range(0, len(ListShellsErrorThickness), 1):
				base.SetEntityCardValues(constants.PAMCRASH, ListShellsErrorThickness[k], {'h': 0})
	
	guitk.UserError('....Done.')
	

SetThickness00()


