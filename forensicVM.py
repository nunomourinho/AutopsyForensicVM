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

# Add filemanager capabilities
from org.sleuthkit.autopsy.casemodule.services import FileManager


class MesiVMModuleFactory(IngestModuleFactoryAdapter):
    moduleName = "Forensic VM Client"

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

    def createDataSourceIngestModule(self, ingestOptions):
        return RunVMIngestModule()

    def getIngestJobSettingsPanel(self, settings):
        if not isinstance(settings, GenericIngestModuleJobSettings):
            raise IllegalArgumentException("Expected settings argument to be instanceof GenericIngestModuleJobSettings")
        self.settings = settings
        return MesiPanel(self.settings)


class RunVMIngestModule(DataSourceIngestModule):
    _logger = Logger.getLogger(MesiVMModuleFactory.moduleName)

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


class MesiPanel(IngestModuleIngestJobSettingsPanel):

    def __init__(self, settings):
        self.local_settings = settings
        self.initComponents()
        self.customizeComponents()

    # Code for event handling...

    def initComponents(self):
        self.setLayout(None)

        lblNewLabel_2 = JLabel("May take a while... Please be patient")
        lblNewLabel_2.setHorizontalAlignment(SwingConstants.LEFT)
        lblNewLabel_2.setFont(Font("Tahoma", Font.BOLD, 14))
        lblNewLabel_2.setBackground(Color.YELLOW)
        lblNewLabel_2.setBounds(10, 227, 347, 23)
        self.add(lblNewLabel_2)

        # Adding image to panel
        #image_path = "forensicVMClient.png"  # assuming this is the correct filename
        #image = ImageIO.read(File(image_path))
        #scaled_image = image.getScaledInstance(200, 200, Image.SCALE_SMOOTH)
        #image_label = JLabel(ImageIcon(scaled_image))
        #image_label.setBounds(10, 20, 200, 200)
        #self.add(image_label)

        # Adding multiline text
        multiline_text = "<html>Line1<br>Line2<br>Line3<br>Line4</html>"
        text_label = JLabel(multiline_text)
        text_label.setFont(Font("Tahoma", Font.BOLD | Font.ITALIC, 11))
        text_label.setHorizontalAlignment(SwingConstants.LEFT)
        text_label.setBounds(10, 250, 243, 60)
        self.add(text_label)

    def customizeComponents(self):
        pass
    # Return the settings used
    def getSettings(self):
        return self.local_settings
