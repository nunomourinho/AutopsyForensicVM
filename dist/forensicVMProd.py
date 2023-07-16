from __builtin__ import str
from java.awt import Panel, BorderLayout, EventQueue, GridLayout, GridBagLayout, GridBagConstraints, Font, Color      
from java.awt.event import ActionListener, ActionEvent 
from java.lang import IllegalArgumentException
from java.lang import System
from java.util.logging import Level
from javax.swing import BoxLayout
from javax.swing import JCheckBox
from javax.swing import JFrame, JLabel, JButton, JTextField, JComboBox, JTextField, JProgressBar, JMenuBar, JMenuItem, JTabbedPane, JPasswordField, JCheckBox, SwingConstants, BoxLayout, JPanel
from javax.swing.border import TitledBorder, EtchedBorder, EmptyBorder
from mailbox import _PartialFile
import traceback
import jarray
import inspect
import os
import java.util.ArrayList as ArrayList
from java.util import ArrayList, List, UUID, logging
from java.lang import Class
from java.lang import System
from java.lang import ProcessBuilder
from java.io import File
from java.util.logging import Level
from org.sleuthkit.datamodel import AbstractFile, Content, Image, SleuthkitCase, TskCoreException, TskDataException
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.datamodel import Image
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestJobContext
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import DataSourceIngestModuleProcessTerminator
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.coreutils import PlatformUtil
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.datamodel import ContentUtils
from org.sleuthkit.autopsy.coreutils import ExecUtil
from java.io import FileWriter
from org.json.simple import JSONArray, JSONObject
from org.sleuthkit.datamodel import SleuthkitCase

from org.sleuthkit.autopsy.ingest import IngestModuleGlobalSettingsPanel
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel
import java.awt.image.BufferedImage
from javax.imageio import ImageIO
from java.net import URL
from javax.swing import ImageIcon
from java.io import File
from __builtin__ import str
from java.awt import Panel, BorderLayout, EventQueue, GridLayout, GridBagLayout, GridBagConstraints, Font, Color      
from java.awt.event import ActionListener, ActionEvent 
from java.lang import IllegalArgumentException
from java.lang import System
from java.util.logging import Level
from javax.swing import BoxLayout
from javax.swing import JCheckBox
from javax.swing import JFrame, JLabel, JButton, JTextField, JComboBox, JTextField, JProgressBar, JMenuBar, JMenuItem, JTabbedPane, JPasswordField, JCheckBox, SwingConstants, BoxLayout, JPanel
from javax.swing.border import TitledBorder, EtchedBorder, EmptyBorder
from mailbox import _PartialFile
from org.apache.commons.codec.digest import DigestUtils
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Blackboard
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import FileIngestModule
from org.sleuthkit.autopsy.ingest import GenericIngestModuleJobSettings

from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import IngestModuleGlobalSettingsPanel
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.datamodel import AbstractFile, TskData
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import SleuthkitCase
from java.awt import SystemColor
import _hashlib
import inspect
import jarray
# Add filemanager capabilities
from org.sleuthkit.autopsy.casemodule.services import FileManager


class MesiVMModuleFactoryProd(IngestModuleFactoryAdapter):
    moduleName = "ForensicVM Client 2023"

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Virtualization of forensic images"
        #return "The ForensicVM client plugin in Autopsy enables the virtualization of forensic images, simplifying the "\
        #       "analysis of digital evidence. It provides control over the virtualized environment, ensuring a "\
        #       "smooth and efficient investigation process. Its synergistic operation with the ForensicVM server "\
        #       "offers a powerful toolset for forensic investigations, facilitating meticulous scrutiny of forensic "\
        #       "images in a virtualized context."

    def getModuleVersionNumber(self):
        return "1.0"

    def isDataSourceIngestModuleFactory(self):
        return True

    def getDefaultIngestJobSettings(self):
        return GenericIngestModuleJobSettings()
   
    def hasIngestJobSettingsPanel(self):
        return False
    
    def getIngestJobSettingsPanel(self, settings):
        if not isinstance(settings, GenericIngestModuleJobSettings):
            raise IllegalArgumentException("MESI: Expected settings argument to be instanceof GenericIngestModuleJobSettings")
        self.settings = settings
        return MesiVMPanelProd(self.settings)
        
    def createDataSourceIngestModule(self, ingestOptions):
        return RunVMIngestModuleProd()


class RunVMIngestModuleProd(DataSourceIngestModule):
    _logger = Logger.getLogger(MesiVMModuleFactoryProd.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    def __init__(self):
        self.context = None

    def startUp(self, context):
        self.context = context

        # Get path to EXE based on where this script is run from.
        # Assumes EXE is in same folder as script
        # Verify it is there before any ingest starts
       
        bat_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mesi-debug.bat")
        self.pathToBAT = File(bat_path)
        if not self.pathToBAT.exists():
            bat_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "forensicVmClient.exe")
            self.pathToBAT = File(bat_path)
            if not self.pathToBAT.exists():
                raise IngestModuleException("MESI.BAT was not found in module folder " + bat_path)


    def add_tags_to_json(self, case_path):
        tagsManager = Case.getCurrentCase().getServices().getTagsManager()

        # Get all existing tag names
        tag_names = tagsManager.getAllTagNames()

        tag_info_arr = JSONArray()

        for tag_name in tag_names:
            tag_dict = JSONObject()
            tag_dict.put("name", tag_name.getDisplayName() if tag_name.getDisplayName() else "")

            tags_arr = JSONArray()

            tag_info_arr.add(tag_dict)

        json_file = FileWriter(case_path)
        json_file.write(tag_info_arr.toJSONString())
        json_file.close()

    def process(self, dataSource, progressBar):

        if not PlatformUtil.isWindowsOS():
            self.log(Level.INFO, "Ignoring data source.  Not running on Windows")
            return IngestModule.ProcessResult.OK

        if not isinstance(dataSource, Image):
            self.log(Level.INFO, "Ignoring data source.  Not an image")
            return IngestModule.ProcessResult.OK

        imagePaths = dataSource.getPaths()

        reportFile = File(
            Case.getCurrentCase().getCaseDirectory() + "\\Reports" + "\\img_stat-" + str(dataSource.getId()) + ".txt")

        self.log(Level.INFO, "Running program on data source")
        cmd = ArrayList()

        cmd.add("cmd")
        cmd.add("/c")
        cmd.add("start")
        cmd.add(self.pathToBAT.toString())
        cmd.add(imagePaths[0])
        cmd.add(Case.getCurrentCase().getCaseDirectory())
        cmd.add(Case.getCurrentCase().getName())
        cmd.add(Case.getCurrentCase().getNumber())
        cmd.add(Case.getCurrentCase().getExaminer())

        try:
           self.add_tags_to_json(Case.getCurrentCase().getCaseDirectory() + "/case_tags.json")
        except Exception as e:
            self.log(Level.WARNING, "Error adding tags to json")
            self.log(Level.WARNING, str(e))
            self.log(Level.WARNING, traceback.format_exc())

        self.log(Level.INFO, imagePaths[0])
        self.log(Level.INFO, cmd.toString())
        processBuilder = ProcessBuilder(cmd);
        processBuilder.redirectOutput(reportFile)
        ExecUtil.execute(processBuilder, DataSourceIngestModuleProcessTerminator(self.context))

        if not self.context.dataSourceIngestIsCancelled():

            Case.getCurrentCase().addReport(reportFile.toString(), "Mesi VM", "Qemu output")
        else:
            if reportFile.exists():
                if not reportFile.delete():
                    self.log(LEVEL.warning, "Error deleting the incomplete report file")

        return IngestModule.ProcessResult.OK


class MesiVMPanelProd(IngestModuleIngestJobSettingsPanel):
    # Note, we can't use a self.settings instance variable.
    # Rather, self.local_settings is used.
    # https://wiki.python.org/jython/UserGuide#javabean-properties
    # Jython Introspector generates a property - 'settings' on the basis
    # of getSettings() defined in this class. Since only getter function
    # is present, it creates a read-only 'settings' property. This auto-
    # generated read-only property overshadows the instance-variable -
    # 'settings'

    # We get passed in a previous version of the settings so that we can
    # prepopulate the UI
    # TODO: Update this for your UI
    def __init__(self, settings):
        self.local_settings = settings
        self.initComponents()
        self.customizeComponents()

    # TODO: Update this for your UI
    def cMD5Event(self, event):
        if self.cMD5.isSelected():
            self.local_settings.setSetting("md5", "true")
        else:
            self.local_settings.setSetting("md5", "false")

# TODO: Update this for your UI
    def cSHA1Event(self, event):
        if self.cSHA1.isSelected():
            self.local_settings.setSetting("sha1", "true")
        else:
            self.local_settings.setSetting("Sha1", "false")

    def cSHA256Event(self, event):
        if self.cSHA256.isSelected():
            self.local_settings.setSetting("sha256", "true")
        else:
            self.local_settings.setSetting("Sha256", "false")


    def cSHA384Event(self, event):
        if self.cSHA384.isSelected():
            self.local_settings.setSetting("sha384", "true")
        else:
            self.local_settings.setSetting("Sha384", "false")


    def cSHA512Event(self, event):
        if self.cSHA512.isSelected():
            self.local_settings.setSetting("sha512", "true")
        else:
            self.local_settings.setSetting("Sha512", "false")

    def cTAGGED_FILESEvent(self, event):
        if self.cSHA512.isSelected():
            self.local_settings.setSetting("tagged_files", "true")
        else:
            self.local_settings.setSetting("tagget_files", "false")
   
    
    # TODO: Update this for your UI
    def initComponents(self):
                
        self.setLayout(None)
                
        lblNewLabel = JLabel("GPL 3.0 Source: https://github.com/mesi2020/autopsy")
        lblNewLabel.setForeground(SystemColor.textHighlight);
        lblNewLabel.setBounds(10, 281, 317, 14)
        self.add(lblNewLabel)
   
   

       
    # TODO: Update this for your UI
    def customizeComponents(self):
        try:
            self.cSHA1.setSelected(self.local_settings.getSettings("sha1") == "true")
            self.cMD5.setSelected(self.local_settings.getSetting("md5") == "true")                                    
        except:
            pass
    

    # Return the settings used
    def getSettings(self):
        return self.local_settings
