from java.util import ArrayList, List, UUID, logging
from org.sleuthkit.datamodel import AbstractFile, Content, Image, SleuthkitCase, TskCoreException, TskDataException
from org.sleuthkit.datamodel.SleuthkitJNI.CaseDbHandle import AddImageProcess

class Sample:

    @staticmethod
    def run(imagePath):
        try:
            sk = SleuthkitCase.newCase(imagePath + ".db")

            # initialize the case with an image
            timezone = ""
            process = sk.makeAddImageProcess(timezone, True, False, "")
            paths = ArrayList()
            paths.add(imagePath)
            try:
                process.run(UUID.randomUUID().toString(), paths.toArray([None] * paths.size()), 0)
            except TskDataException, ex:
                logging.Logger.getLogger(Sample.__name__).log(logging.Level.SEVERE, None, ex)

            # print out all the images found, and their children
            images = sk.getImages()
            for image in images:
                print "Found image: " + image.getName()
                print "There are " + str(image.getChildren().size()) + " children."
                for content in image.getChildren():
                    print '"' + content.getName() + '"' + " is a child of " + image.getName()

            # print out all .txt files found
            files = sk.findAllFilesWhere("LOWER(name) LIKE LOWER('%.txt')")
            for file in files:
                print "Found text file: " + file.getName()

        except TskCoreException, e:
            print "Exception caught: " + e.getMessage()
            Sample.usage(e.getMessage())

    @staticmethod
    def usage(error):
        print "Usage: ant -Dimage:{image string} run-sample"
        if "deleted first" in error:
            print "A database for the image already exists. Delete it to run this sample again."
        elif "unable to open database" in error:
            print 'Image must be encapsulated by double quotes. Ex: ant -Dimage="C:\\Users\\You\\image.E01" run-sample'

    @staticmethod
    def main(args):
        Sample.run(args[0])

if __name__ == '__main__':
    import sys
    Sample.main(sys.argv[1:])
