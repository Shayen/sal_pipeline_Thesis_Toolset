#
# ===== Maya Application template =====
# 

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as apiUI
import shiboken

from functools import partial
import os, sys, subprocess, time, datetime, shutil

# ============ Will change to qt.py ============
try:
	from PySide2.QtCore import *
	from PySide2.QtGui import *
	from PySide2.QtWidgets import *
	from PySide2.QtUiTools import *
	from PySide2 import __version__
	import shiboken2 as shiboken

except ImportError:
	from PySide.QtCore import *
	from PySide.QtGui import *
	from PySide.QtUiTools import *
	from PySide import __version__
	import shiboken

# project libs import
from sal_pipeline.src import env
from sal_pipeline.src import utils
reload(utils)
reload(env)

# tool libs import
import mayaGlobalPublisher_core 
reload(mayaGlobalPublisher_core)

core = mayaGlobalPublisher_core.mayaGlobalPublisher_core()
getEnv 	= env.getEnv()
modulepath = getEnv.modulePath()

__app_version__ = '0.1'
# V0.1

try:
	myInfo = env.getInfo()
	myInfo.get_task()
except IndexError :
	e_msg = "## This file is not in pipeline. please check your file. ##\n"
	print('_'*64)
	print(e_msg)

	raise IOError(e_msg)

class mayaGlobalPublisher( QMainWindow ):

	def __init__(self, parent=None):
		""" Description """
		QMainWindow.__init__(self, parent)

		_uiFilename_ = 'Maya_GlobalPublish.ui'
		_uiFilePath_ = modulepath + '/ui/' + _uiFilename_		

		# Check is ui file exists?
		if not os.path.isfile( _uiFilePath_ ):
			cmds.error( 'File ui not found.' )

		# ---- LoadUI -----
		loader = QUiLoader()
		currentDir = os.path.dirname(__file__)
		file = QFile( _uiFilePath_ )
		file.open(QFile.ReadOnly)
		self.ui = loader.load(file, parentWidget=self)
		file.close()
		# -----------------

		self.ui.setWindowTitle('Maya global publisher v.' + str(__app_version__))

		self._initUI()
		self._initConnect()
		self.ui.show()

	def _initUI(self):
		self.ui.lineEdit_publisher.setText( myInfo.getUsername() )
		self.ui.label_pubFileName.setText(  myInfo.get_pubName() )
		self.ui.label_filePath.setText( cmds.file(q=True, sn=True) )
		self.ui.label_dateTime.setText( str(time.strftime("%d/%m/%Y %H:%M %p",time.localtime())))

		# FUTURE : Query configyration from config file.
		self.ui.comboBox_pipelineStep.addItem("model")

		# capture viewport
		self.setThumbnail( core.captureViewport() )

	def _initConnect(self):
		self.ui.pushButton_cancel.clicked.connect(self.closeWindow)
		self.ui.pushButton_publish.clicked.connect(self._doPublish)

	def setThumbnail(self, imagePath):

		if not os.path.exists(imagePath):
			imagePath = ''
			self.pixmap_Placeholder.setText(imagePath)
			return

		pixmap = QPixmap( imagePath )
		pixmap = pixmap.scaledToWidth(240)
		self.ui.label_imagePlaceHolder.setPixmap(pixmap)

	def _doPublish(self):
		''' publish file '''

		self.ui.listWidget_allStatus.clear()
		is_postToFacebook = False 
		# Check save state::
		is_modifiedFile = cmds.file(q=True, modified=True)

		# // When file have some change, Save in new version.
		if is_modifiedFile :

			#  save Increment
			core.saveIncrement()
			self.update_Status("save increment.")

		# save to Hero file
		core.creat_HeroFile()
		self.update_Status("Create hero file.")

		# export Publish data via JSON
		core.export_pubData()
		self.update_Status("Create publish metadata.")

		if is_postToFacebook :
			# post to FB group
			# -- !!warning!! : user must be admin to group.
			data = {}
			post_result = core.post_toFacebook(data = data)

	def update_Status(self, message):
		item = QListWidgetItem(message)
		self.ui.listWidget_allStatus.addItem(item)

	def closeWindow(self):
		clearUI()

#####################################################################

def openExplorer(filePath):
	"""Open File explorer after finish."""
	win_publishPath = filePath.replace('/', '\\')
	subprocess.Popen('explorer \/select,\"%s\"' % win_publishPath)

def getMayaWindow():
	"""
	Get the main Maya window as a QMainWindow instance
	@return: QMainWindow instance of the top level Maya windows
	"""
	ptr = apiUI.MQtUtil.mainWindow()
	if ptr is not None:
		return shiboken.wrapInstance(long(ptr), QWidget)

def clearUI():
	if cmds.window('sal_globalPublisher',exists=True):
		cmds.deleteUI('sal_globalPublisher')
		clearUI()

def run():
	clearUI()
	app = mayaGlobalPublisher( getMayaWindow() )
	# pass

if __name__ == '__main__':
	run()