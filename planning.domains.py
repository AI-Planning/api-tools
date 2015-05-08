#!/usr/bin/python3

import sys
import os
import datetime
import gzip
import zipfile
import copy

from os.path import isfile, isdir, join

import xml.etree.ElementTree as etree

import urllib.request
import urllib.parse

langAttribute = "{http://www.w3.org/XML/1998/namespace}lang"

domainPath = None
installationSettings = None
installationTree = None

defaultNamespace = "http://settings.planning.domains"

def checkExists(pd_dir):
    """Check ~/.planning.domains exists, and is not a file"""

    if isfile("pd_dir"):
        print("Fatal error: need to store settings in {0}, but there is a file with that name".format(pd_dir))
        exit(1)


    if not isdir(pd_dir):


        print("""== Pre-release client for planning.domains ==

This is pre-release software, for accessing the content on planning.domains.  The backend of the site is undergoing heavy revision,
so do not distribute this software: it may stop working in the future.  Note it is released without warranty (including the implied
warranties of merchantability or fitness for a particular purpose).  Send bug reports to Andrew Coles.

""")




        print("Making directory {0}".format(pd_dir))
        try:
            os.mkdir(pd_dir)

        except OSError:
            print("Cannot make directory")
            exit(1)

def saveSettings():

    global installationTree

    settingsXML = join(pd_dir,"settings.xml")

    with open(settingsXML,"wb") as settingsFile:
        installationTree.write(settingsFile)





def loadSettings(home_dir,pd_dir):
    """Get the domain path from the settings.xml file in pd_dir.  If no domain path exists, ask for one."""

    settingsXML = join(pd_dir,"settings.xml")

    #print("Loading settings from {0}".format(settingsXML))

    global installationTree
    global installationSettings
    global domainPath

    if isfile(settingsXML):
        installationTree = etree.parse(settingsXML)
        installationSettings = installationTree.getroot()

        for child in installationSettings:
            if child.tag == "domain_path":
                domainPath = child.text

                if isdir(domainPath):
                    return
                else:
                    try:
                        os.mkdir(domainPath)
                    except OSError:
                        print("Error in settings.xml: domains directory {0} does not exist, and cannot be made".format(domainPath))
                        exit(1)

                    print("Warning when reading settings.xml: domains directory {0} did not exist, but it was created".format(domainPath))

                    return

    if installationSettings is None:
        installationSettings = etree.Element("{http://settings.planning.domains}settings")
        installationTree = etree.ElementTree(installationSettings)

    domainPath = input("Enter path for installing files (or hit enter to use {0}): ".format(join(home_dir,"planning.domains")))

    domainPath = domainPath.lstrip()
    domainpath = domainPath.rstrip()

    if domainPath == "":
        domainPath = join(home_dir,"planning.domains")

    if isfile(domainPath):
        print("Fatal error: there is already a file called {0}".format(domainPath))
        exit(1)

    if not isdir(domainPath):
        try:
            os.mkdir(domainPath)
        except OSError:
            print("Cannot make directory {0}".format(domainPath))
            exit(1)

    etree.SubElement(installationSettings,"domain_path").text = domainPath

    saveSettings()





def update(packagesPath):
    """Download the latest package list"""
    urllib.request.urlretrieve("http://raw.planning.domains/packages.xml.gz",packagesPath)







def find(root,argument):
    """Search for packages whose title or ID contains the given argument"""
    matchingIDs = []

    for child in root:
        if child.tag == "domain":
            if child.attrib is None:
                print("Fatal error: found a domain without an ID");
                exit(1)

            if 'id' not in child.attrib:
                print("Fatal error: found a domain without an ID");
                exit(1)

            thisID = child.attrib['id']

            matches = False
            thisTitle = None
            titleLanguage = None

            if argument in thisID:
                matches = True

            for innerchild in child:
                if innerchild.tag == "title":
                    if argument in innerchild.text:
                        matches = True

                    if thisTitle is None:
                        #note the first title found
                        thisTitle = innerchild.text
                        titleLanguage = innerchild.attrib[langAttribute]
                    else:
                        #if the first title isn't in English...
                        if titleLanguage != "en" and innerchild.attrib[langAttribute] == en:
                            thisTitle = innerchild.text
                            titleLanguage = "en"

            if matches:
                matchingIDs.append((thisID,thisTitle))

    if len(matchingIDs) == 0:
        print("Cannot find a title or ID containing {0}".format(argument))

    else:
        print("Domains with title or ID containing {0}:".format(argument))
        for (x,y) in matchingIDs:
            print("ID: {0} , Title: {1}".format(x,y))

def getDateFromDomain(domainNode,dateTag):
    for child in domainNode:
        if child.tag == dateTag:
            return child.text

    raise LookupError

def downloadIfNew(child,dateTag,fileTag):

    thisID = child.attrib['id']
    latestDate = getDateFromDomain(child,dateTag)

    global installationSettings

    filesToRemove = []
    dirsToRemove = []

    installedTag = "installed_{0}".format(fileTag)

    for installed in installationSettings:
        if installed.tag == installedTag:
            if installed.attrib['ref'] == thisID:
                innerchild = installed[0]

                if innerchild.tag != "date":
                    print("Malformed settings.xml file, cannot continue: expect to find 'date' as the first child of {0}".format(installedTag))
                    exit(1)

                if innerchild.text >= latestDate:
                    print("{1} for {0} is already the latest version".format(thisID,fileTag))
                    return False, [], []

                else:

                    for innerchild in installed[1:]:
                        if innerchild.tag == "file":
                            filesToRemove.append(innerchild.text)
                        elif innerchild.tag == "dir":
                            dirsToRemove.append(innerchild.text)

                installationSettings.remove(installed)

                break

    data = {}
    data['id'] = thisID
    data['type'] = fileTag
    parameters = urllib.parse.urlencode(data)

    print("Downloading {1} for {0}...".format(thisID,fileTag))
    urllib.request.urlretrieve("http://raw.planning.domains/fetch.php?{0}".format(parameters),\
                                join(pd_dir,"{0}.zip".format(fileTag))                           )

    return True, filesToRemove, dirsToRemove


def downloadDomainAndProblemsIfNew(child):
    return downloadIfNew(child,"files_last_modified","domain_and_problems")


def downloadMetadataIfNew(child):
    return downloadIfNew(child,"metadata_last_modified","metadata")


def install(root,argument,pd_dir):
    global domainPath
    global installationSettings

    """Install the package with the given ID, to the given domain path"""
    for child in root:
        if child.tag == "domain":
            if child.attrib is None:
                print("Fatal error: found a domain without an ID");
                exit(1)

            if 'id' not in child.attrib:
                print("Fatal error: found a domain without an ID");
                exit(1)

            thisID = child.attrib['id']

            if thisID == argument:

                needMetadata, metadataFiles, metadataDirs = downloadMetadataIfNew(child)
                needDomain,   domainFiles, domainDirs     = downloadDomainAndProblemsIfNew(child)

                if not needMetadata and not needDomain:
                    print("{0} is already the latest version".format(thisID))
                    continue


                if needMetadata:

                    if len(metadataFiles) > 0:
                        print("Removing old metadata for {0}".format(thisID))

                        for f in metadataFiles:
                            """Removing a metadata file"""
                            os.remove(join(domainPath,f))

                        print("Installing new metadata for {0}".format(thisID))
                    else:
                        print("Installing metadata for {0}".format(thisID))


                    with zipfile.ZipFile(join(pd_dir,"metadata.zip"),'r') as metadataZip:
                        metadataZip.extractall(domainPath)

                        newDetailsRoot = etree.SubElement(installationSettings,"installed_metadata", attrib={'ref':thisID})
                        etree.SubElement(newDetailsRoot, "date").text = getDateFromDomain(child,"metadata_last_modified")

                        for info in metadataZip.infolist():
                            etree.SubElement(newDetailsRoot,"file").text = info.filename
                            #print(info.filename)

                    os.remove(join(pd_dir,"metadata.zip"))

                if needDomain:

                    if len(domainFiles) > 0:
                        print("Removing old domain and problems for {0}".format(thisID))

                        for f in domainFiles:
                            """Removing a domain/problem file"""
                            os.remove(join(domainPath,f))

                        print("Installing new domain and probelms for {0}".format(thisID))
                    else:
                        print("Installing domain and problems for {0}".format(thisID))


                    with zipfile.ZipFile(join(pd_dir,"domain_and_problems.zip"),'r') as problemsZip:
                        problemsZip.extractall(domainPath)

                        newDetailsRoot = etree.SubElement(installationSettings,"installed_domain_and_problems", attrib={'ref':thisID})
                        etree.SubElement(newDetailsRoot, "date").text = getDateFromDomain(child,"files_last_modified")

                        for info in problemsZip.infolist():
                            etree.SubElement(newDetailsRoot,"file").text = info.filename
                            #print(info.filename)

                    os.remove(join(pd_dir,"domain_and_problems.zip"))

                print("Updating settings.xml")
                saveSettings()




def upgrade(packageList,pd_dir):
    """Update any installed packages to newer versions, according to date-stamps"""

    global domainPath
    global installationSettings

    with gzip.open(packageList,'rb') as packagesFile:
        tree = etree.parse(packagesFile)
        root = tree.getroot()

        latestMetadataDates = {}
        latestFilesDates = {}

        for child in root:
            if child.tag == "domain":
                id = child.attrib['id']
                for timechild in child:
                    if timechild.tag == "files_last_modified":
                        latestFilesDates[id] = timechild.text

                    elif timechild.tag == "metadata_last_modified":
                        latestMetadataDates[id] = timechild.text

        toUpdate = {}

        for installed in installationSettings:
            if installed.tag == "installed_metadata":
                id = installed.attrib['ref']

                if id not in latestMetadataDates:
                    print("Warning: metadata is installed for {0}, but it is no longer on the package list".format(id))
                    continue

                innerchild = installed[0]

                if innerchild.tag != "date":
                    print("Malformed settings.xml file, cannot continue: expect to find 'date' as the first child of 'installed_metadata'")
                    exit(1)

                if latestMetadataDates[id] > innerchild.text:
                    toUpdate[id] = (True,False)

        for installed in installationSettings:
            if installed.tag == "installed_domain_and_problems":
                id = installed.attrib['ref']

                if id not in latestFilesDates:
                    print("Warning: domain and problem files are installed for {0}, but it is no longer on the package list".format(id))
                    continue

                innerchild = installed[0]

                if innerchild.tag != "date":
                    print("Malformed settings.xml file, cannot continue: expect to find 'date' as the first child of 'installed_domain_and_problems'")
                    exit(1)

                if latestFilesDates[id] > innerchild.text:
                    toUpdate[id] = (True,True)


        for id in toUpdate:
            if toUpdate[id] == (True,True):
                print("Updating metadata and domain/problems for {0}".format(id))
            else:
                print("Updating metadata for {0}".format(id))

            install(root,id,pd_dir)

    print("All up to date")

if __name__ == "__main__":

    home_dir = os.path.expanduser("~")

    pd_dir = join(home_dir,".planning.domains")

    checkExists(pd_dir)

    loadSettings(home_dir, pd_dir)

    if installationSettings is None:
        print("Fatal error: could not establish installation settings")
        exit(1)

    #don't download the package list twice, if the script is ran with the update option, but packages.xml was missing
    downloadedPackageList = False
    packageList = join(pd_dir,"packages.xml.gz")

    if not isfile(packageList):
        print("No package list found, downloading it")
        update(packageList)
        downloadedPackageList = True


    if len(sys.argv) == 1:
        print("""No command-line options given.  Usage:

planning.domains.py update                     Update the packages.xml list to the latest version
planning.domains.py upgrade                    Upgrade installed packages (and/or their metadata) to the latest version
planning.domains.py find [string]              Find packages whose title/ID contains 'string'
planning.domains.py install [id] [id] ...      Install the packages with the IDs given""")

        exit(0)


    root = None

    i = 1

    while i < len(sys.argv):
        if sys.argv[i] == "update":
            if downloadedPackageList:
                print("Already downloaded package list")
            else:
                print("Downloading package list")
                update(packageList)
                downloadedPackageList = True

            i += 1

        elif sys.argv[i] == "upgrade":

            upgrade(packageList,pd_dir)
            i += 1

        else:

            command = sys.argv[i]
            i += 1

            if i == len(sys.argv):
                print("Error: expected an argument after {0}".format(command))
                exit(1)

            while i < len(sys.argv):
                argument = sys.argv[i]
                i += 1

                argument = argument.rstrip()
                argument = argument.lstrip()

                if len(argument) == 0:
                    print("Warning: expected non-empty argument after {0}".format(command))
                    continue


                if root is None:
                    with gzip.open(packageList,'rb') as packagesFile:
                        tree = etree.parse(packagesFile)
                        root = tree.getroot()

                if command == "find":
                    find(root,argument)

                elif command == "install":
                    install(root,argument,pd_dir)


