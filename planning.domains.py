#!/usr/bin/python

from __future__ import print_function

import sys, os, pprint

import xml.etree.ElementTree as etree

import planning_domains_api as api

langAttribute = "{http://www.w3.org/XML/1998/namespace}lang"

domainPath = None
installationSettings = None
installationTree = None

defaultNamespace = "http://settings.planning.domains"

USAGE_STRING = """
No command-line options given.  Usage:

planning.domains.py update                            Update the local domain repository.

planning.domains.py find collections [string]          Find collections whose title/ID contains 'string'
planning.domains.py find domains [string]              Find domains whose title/ID contains 'string'
planning.domains.py find problems [string]             Find problems whose title/ID contains 'string'

planning.domains.py show collection [integer]         Find collections whose title/ID contains 'integer'
planning.domains.py show domain [integer]             Find domains whose title/ID contains 'integer'
planning.domains.py show problem [integer]            Find problems whose title/ID contains 'integer'
"""


def checkExists(pd_dir):
    """Check ~/.planning.domains exists, and is not a file"""

    if os.path.isfile(pd_dir):
        print("Fatal error: need to store settings in {0}, but there is a file with that name".format(pd_dir))
        exit(1)


    if not os.path.isdir(pd_dir):


        print("""
        == Pre-release client for planning.domains ==

 This is pre-release software, for accessing the content on
 api.planning.domains. It is released without warranty
 (including the implied warranties of merchantability
 or fitness for a particular purpose).

 Send bug reports to Andrew Coles (andrew.coles@kcl.ac.uk)
 or Christian Muise (christian.muise@gmail.com)

""")


        print("Making directory {0}...\n".format(pd_dir))
        try:
            os.mkdir(pd_dir)

        except OSError:
            print("Cannot make directory")
            exit(1)



def saveSettings():

    global installationTree

    settingsXML = os.path.join(pd_dir,"settings.xml")

    with open(settingsXML,"wb") as settingsFile:
        installationTree.write(settingsFile)



def fetchPlanningDomains(domainPath):
    try:
        resp = raw_input("Clone the domain repository (~50Mb download / ~1Gb uncompressed) to directory {0}? (y/n) ".format(domainPath))
        if 'y' == resp:
            os.system("git clone git@bitbucket.org:planning-tools/domains.git {0}".format(domainPath))
        else:
            print("Aborting fetching domains for the directory {0}".format(domainPath))
    except OSError:
        print("Cannot make directory {0}".format(domainPath))
        exit(1)



def loadSettings(home_dir,pd_dir):
    """Get the domain path from the settings.xml file in pd_dir.  If no domain path exists, ask for one."""

    settingsXML = os.path.join(pd_dir,"settings.xml")

    #print("Loading settings from {0}".format(settingsXML))

    global installationTree
    global installationSettings
    global domainPath

    if os.path.isfile(settingsXML):
        installationTree = etree.parse(settingsXML)
        installationSettings = installationTree.getroot()

        for child in installationSettings:
            if child.tag == "domain_path":
                domainPath = child.text

                if not os.path.isdir(domainPath):
                    fetchPlanningDomains(domainPath)

                return

    if installationSettings is None:
        installationSettings = etree.Element("{http://settings.planning.domains}settings")
        installationTree = etree.ElementTree(installationSettings)

    domainPath = raw_input("Enter path for installing files (or hit enter to use {0}): ".format(os.path.join(home_dir,"planning.domains")))

    domainPath = domainPath.lstrip()
    domainpath = domainPath.rstrip()

    if domainPath == "":
        domainPath = os.path.join(home_dir,"planning.domains")

    if os.path.isfile(domainPath):
        print("Fatal error: there is already a file called {0}".format(domainPath))
        exit(1)

    if not os.path.isdir(domainPath):
        fetchPlanningDomains(domainPath)

    etree.SubElement(installationSettings,"domain_path").text = domainPath

    saveSettings()


def find(sub, arg):
    """Find an object of type sub that matches argument arg."""

    if sub == 'collections':
        res = api.find_collections(arg)
    elif sub == 'domains':
        res = api.find_domains(arg)
    elif sub == 'problems':
        res = api.find_problems(arg)
    else:
        print("Error: Unrecognized sub-command, {0}".format(sub))
        exit(1)

    pprint.pprint(res)

def show(sub, arg):
    """Show an object of type sub that matches the id arg."""

    arg = int(arg)

    if sub == 'collection':
        res = api.get_collection(arg)
    elif sub == 'domain':
        res = api.get_domain(arg)
    elif sub == 'problem':
        res = api.get_problem(arg)
    else:
        print("Error: Unrecognized sub-command, {0}".format(sub))
        exit(1)

    pprint.pprint(res)


if __name__ == "__main__":

    home_dir = os.path.expanduser("~")

    pd_dir = os.path.join(home_dir,".planning.domains")

    checkExists(pd_dir)

    loadSettings(home_dir, pd_dir)

    if installationSettings is None:
        print("Fatal error: could not establish installation settings")
        exit(1)


    if len(sys.argv) == 1:
        print(USAGE_STRING)
        exit(0)


    root = None

    i = 1

    while i < len(sys.argv):
        if sys.argv[i] == "update":
            if api.checkForDomainPath():
                print("Updating...")
                os.system("cd {0}; git pull -u".format(api.DOMAIN_PATH))
            else:
                print("Error: Domain path is not set.")

            i += 1

        else:

            command = sys.argv[i]
            i += 1

            if i == len(sys.argv):
                print("Error: expected a sub-command after {0}".format(command))
                exit(1)

            subcommand = sys.argv[i]
            i += 1

            if i == len(sys.argv):
                print("Error: expected an argument after {0}".format(subcommand))
                exit(1)

            argument = sys.argv[i]
            i += 1

            argument = argument.rstrip()
            argument = argument.lstrip()

            if len(argument) == 0:
                print("Warning: expected non-empty argument after {0}".format(command))
                continue

            if command == "find":
                find(subcommand, argument)
            elif command == "show":
                show(subcommand, argument)
            else:
                print("Error: unknown command {0}".format(command))
                exit(1)



