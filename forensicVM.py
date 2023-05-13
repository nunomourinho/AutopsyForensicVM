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

# Add filemanager capabilities
from org.sleuthkit.autopsy.casemodule.services import FileManager


class MesiVMModuleFactory(IngestModuleFactoryAdapter):
    moduleName = "Forensic VM"

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Virtualize datasource."

    def getModuleVersionNumber(self):
        return "1.0"

    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, ingestOptions):
        return RunVMIngestModule()


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
