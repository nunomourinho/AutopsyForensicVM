

import jarray
import inspect
import os
import java.util.ArrayList as ArrayList
from java.lang import Class
from java.lang import System
from java.lang import ProcessBuilder
from java.io import File
from java.util.logging import Level
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

# Add filemanager capabilities
from org.sleuthkit.autopsy.casemodule.services import FileManager


# Factory that defines the name and details of the module and allows Autopsy
# to create instances of the modules that will do the analysis.
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


# Data Source-level ingest module.  One gets created per data source.
class RunVMIngestModule(DataSourceIngestModule):

    _logger = Logger.getLogger(MesiVMModuleFactory.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    def __init__(self):
        self.context = None

    # Where any setup and configuration is done
    # 'context' is an instance of org.sleuthkit.autopsy.ingest.IngestJobContext.
    # See: http://sleuthkit.org/autopsy/docs/api-docs/latest/classorg_1_1sleuthkit_1_1autopsy_1_1ingest_1_1_ingest_job_context.html
    def startUp(self, context):
        self.context = context
        
        # Get path to EXE based on where this script is run from.
        # Assumes EXE is in same folder as script
        # Verify it is there before any ingest starts
            
        bat_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mesi.bat")
        self.pathToBAT = File(bat_path)
        if not self.pathToBAT.exists():
            raise IngestModuleException("MESI.BAT was not found in module folder " + bat_path)
    
    def add_new_datasource(qcow_file_path):
        
        # Get the file manager
        file_manager = Case.getCurrentCase().getServices().getFileManager()
        
        # Create a new File object for the qcow2 file
        qcow_file = File(qcow_file_path)

        # Create a new file in the case for the QCOW file
        new_file = file_manager.addFile(qcow_file)

        # Set the file type to "Disk Image"
        ContentUtils.setFileType(new_file, ContentUtils.TYPE_DISK_IMAGE)
    
    
    # Where the analysis is done.
    # The 'dataSource' object being passed in is of type org.sleuthkit.datamodel.Content.
    # See: http://www.sleuthkit.org/sleuthkit/docs/jni-docs/latest/interfaceorg_1_1sleuthkit_1_1datamodel_1_1_content.html
    # 'progressBar' is of type org.sleuthkit.autopsy.ingest.DataSourceIngestModuleProgress
    # See: http://sleuthkit.org/autopsy/docs/api-docs/latest/classorg_1_1sleuthkit_1_1autopsy_1_1ingest_1_1_data_source_ingest_module_progress.html
    def process(self, dataSource, progressBar):
        
        # we don't know how much work there will be
        progressBar.switchToIndeterminate()
        # Example has only a Windows EXE, so bail if we aren't on Windows
        if not PlatformUtil.isWindowsOS(): 
            self.log(Level.INFO, "Ignoring data source.  Not running on Windows")
            return IngestModule.ProcessResult.OK

        # Verify we have a disk image and not a folder of files
        if not isinstance(dataSource, Image):
            self.log(Level.INFO, "Ignoring data source.  Not an image")
            return IngestModule.ProcessResult.OK

        # Get disk image paths            
        imagePaths = dataSource.getPaths()
        
        # We'll save our output to a file in the reports folder, named based on EXE and data source ID
        reportFile = File(Case.getCurrentCase().getCaseDirectory() + "\\Reports" + "\\img_stat-" + str(dataSource.getId()) + ".txt")

        # Test add datasource
        #self.add_new_datasource("D:/convertidos/MUS-CT19-DESKTOP.V2.qcow2-sda")
        
        # Run the EXE, saving output to reportFile
        # We use ExecUtil because it will deal with the user cancelling the job
        self.log(Level.INFO, "Running program on data source")
        cmd = ArrayList()
        # Add each argument in its own line.  I.e. "-f foo" would be two calls to .add()
        cmd.add(self.pathToBAT.toString())
        cmd.add(imagePaths[0])
        cmd.add(Case.getCurrentCase().getCaseDirectory())
        cmd.add(Case.getCurrentCase().getName())
        cmd.add(Case.getCurrentCase().getNumber())
        cmd.add(Case.getCurrentCase().getExaminer())
        #tags_manager = Case.getServices().getTagsManager()

        #all_tags = tags_manager.getAllContentTags()

        #for tag in all_tags:
            #content = tag.getContent()
            #tag_name = tag.getName().getDisplayName()
            #cmd.add(tag_name)
            #comment = tag.getComment()

        self.log(Level.INFO, imagePaths[0])
        self.log(Level.INFO, cmd.toString())
        processBuilder = ProcessBuilder(cmd);
        processBuilder.redirectOutput(reportFile)
        ExecUtil.execute(processBuilder, DataSourceIngestModuleProcessTerminator(self.context))
        
        
        # Add the report to the case, so it shows up in the tree
        # Do not add report to the case tree if the ingest is cancelled before finish.
        if not self.context.dataSourceIngestIsCancelled():
            #self.add_new_datasource("D:/convertidos/MUS-CT19-DESKTOP.V2.qcow2-sda")
            Case.getCurrentCase().addReport(reportFile.toString(), "Mesi VM", "Qemu output")
        else:
            if reportFile.exists():
                if not reportFile.delete():
                    self.log(LEVEL.warning,"Error deleting the incomplete report file")
            
        return IngestModule.ProcessResult.OK
