#!/usr/bin/python

import argparse, os, pprint, sys

import xml.etree.ElementTree as etree

import planning_domains_api as api

langAttribute = "{http://www.w3.org/XML/1998/namespace}lang"

domainPath = None
installationSettings = None
installationTree = None
userEmail = None
userToken = None

defaultNamespace = "http://settings.planning.domains"

USAGE_STRING = """
No command-line options given.  Usage:

planning.domains.py update                                Update the local domain repository.

planning.domains.py register                              Register your email and token for making API edits

planning.domains.py find collections [string]             Find collections whose title/ID contains 'string'
planning.domains.py find domains [string]                 Find domains whose title/ID contains 'string'
planning.domains.py find problems [string]                Find problems whose title/ID contains 'string'

planning.domains.py show collection [integer]             Find collections whose title/ID contains 'integer'
planning.domains.py show domain [integer]                 Find domains whose title/ID contains 'integer'
planning.domains.py show problem [integer]                Find problems whose title/ID contains 'integer'
planning.domains.py show plan [integer]                   Show the plan (if any) matching the given problem ID

planning.domains.py list collections                      Lists all of the collections.
planning.domains.py list tags                             Lists all of the available tags.
planning.domains.py list null-attribute [string]          Lists all of the problems that have a null attribute setting (string)

planning.domains.py tag collection [integer] [string]     Tags the specified collection (integer) with a tag (string)
planning.domains.py tag domain [integer] [string]         Tags the specified domain (integer) with a tag (string)
planning.domains.py tag problem [integer] [string]        Tags the specified problem (integer) with a tag (string)
planning.domains.py untag collection [integer] [string]   Un-tags the specified collection (integer) with a tag (string)
planning.domains.py untag domain [integer] [string]       Un-tags the specified domain (integer) with a tag (string)
planning.domains.py untag problem [integer] [string]      Un-tags the specified problem (integer) with a tag (string)

planning.domains.py submit plan [integer] [plan file]     Submit the provided plan for validation and possible storage

planning.domains.py cache [integer] [string]              Collect all of the domains in a collection (integer) into a specified folder (string)
planning.domains.py cache-all [integer] [string]          Same as previous, but also includes the problem data / statistics
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
        resp = input("Clone the domain repository (~50Mb download / ~1Gb uncompressed) to directory {0}? (y/n) ".format(domainPath))
        if 'y' == resp:
            os.system("git clone https://github.com/AI-Planning/classical-domains.git {0}".format(domainPath))
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
    global userEmail
    global userToken

    if os.path.isfile(settingsXML):
        installationTree = etree.parse(settingsXML)
        installationSettings = installationTree.getroot()

        for child in installationSettings:
            if child.tag == "domain_path":
                domainPath = child.text

                if not os.path.isdir(domainPath):
                    fetchPlanningDomains(domainPath)

            if child.tag == "email":
                userEmail = child.text

            if child.tag == "token":
                userToken = child.text

        return

    if installationSettings is None:
        installationSettings = etree.Element("{http://settings.planning.domains}settings")
        installationTree = etree.ElementTree(installationSettings)

    domainPath = input("Enter path for installing files (or hit enter to use {0}): ".format(os.path.join(home_dir,"planning.domains")))

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

    userEmail = input("Enter email for API updates: ")
    userToken = input("Enter token for API updates (leave blank if none provided): ")

    etree.SubElement(installationSettings,"email").text = userEmail
    etree.SubElement(installationSettings,"token").text = userToken

    saveSettings()


def register():
    global userEmail
    global userToken

    userEmail = input("Enter email for API updates (leave blank for %s): " % userEmail) or userEmail
    userToken = input("Enter token for API updates (leave blank for %s): " % userToken) or userToken

    list(filter(lambda x: x.tag == 'email', installationSettings))[0].text = userEmail
    list(filter(lambda x: x.tag == 'token', installationSettings))[0].text = userToken

    saveSettings()

    print("Email and token settings saved!\n")


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

    pprint.pprint(res, sort_dicts=False)

def show(sub, arg):
    """Show an object of type sub that matches the id arg."""

    arg = int(arg)

    if sub == 'plan':
        print(api.get_plan(arg))
        return

    if sub == 'collection':
        res = api.get_collection(arg)
    elif sub == 'domain':
        res = api.get_domain(arg)
    elif sub == 'problem':
        res = api.get_problem(arg)
    else:
        print("Error: Unrecognized sub-command, {0}".format(sub))
        exit(1)

    pprint.pprint(res, sort_dicts=False)

def submit_plan(pid, pfile):
    with open(pfile) as f:
        plan = f.read()
    api.submit_plan(pid, plan)

def cache(cid, outdir, include_data = False):

    print("Caching collection %d to [%s] (data included = %s)..." % (cid, outdir, str(include_data)))

    if os.path.exists(outdir):
        print("Error: Output directory already exists.")
        exit(1)
    else:
        os.mkdir(outdir)

    domains = {}
    problem_data = {}
    domain_data = api.get_domains(cid)
    domain_names = [dom['domain_name'] for dom in domain_data]
    assert len(set(domain_names)) == len(domain_names), "Error: It appears as though the collection has repeated domain names."

    for dom in domain_data:

        dname = dom['domain_name']

        # Map the domain name to the list of domain-problem pairs and problem data
        domains[dname] = []
        problem_data[dname] = []

        # Make the directory for the domain
        os.mkdir(os.path.join(outdir, dname))

        # Turn the links into relative paths for this machine
        probs = map(api.localize, api.get_problems(dom['domain_id']))

        # Copy the domain and problem files to their appropriate directory
        for i in range(len(probs)):
            dpath = os.path.join(dname, "domain_%.2d.pddl" % (i+1))
            ppath = os.path.join(dname, "%.2d.pddl" % (i+1))

            os.system("cp %s %s" % (probs[i]['domain_path'], os.path.join(outdir,dpath)))
            os.system("cp %s %s" % (probs[i]['problem_path'], os.path.join(outdir,ppath)))

            domains[dname].append((dpath,ppath))

            if include_data:
                problem_data[dname].append(probs[i])
                problem_data[dname][-1]['domain_path'] = os.path.abspath(os.path.join(outdir,dpath))
                problem_data[dname][-1]['problem_path'] = os.path.abspath(os.path.join(outdir,ppath))

    with open(os.path.join(outdir, "domains.py"), 'w') as f:
        f.write('\n# Use "from domains import DOMAINS" to get the benchmark set\n')
        if include_data:
            f.write('\n# Use "from domains import DATA" to get the problem data (aligns with the DOMAINS list)\n')
        f.write('\nDOMAINS = ')
        f.write(pprint.pformat(domains))
        if include_data:
            f.write('\n\nDATA = ')
            f.write(pprint.pformat(problem_data))
        f.write('\n')

    print("Done!\n")

if __name__ == "__main__":

    home_dir = os.path.expanduser("~")

    pd_dir = os.path.join(home_dir,".planning.domains")

    checkExists(pd_dir)

    loadSettings(home_dir, pd_dir)

    if installationSettings is None:
        print("Fatal error: could not establish installation settings")
        exit(1)


    parser = argparse.ArgumentParser(description="Planning Domains CLI")
    subparsers = parser.add_subparsers(dest="command")

    def add_formalism_argument(subparser):
        subparser.add_argument("--formalism", choices=["classical", "rddl"], default="classical", help="Specify the formalism for the command.")

    # Update
    update_parser = subparsers.add_parser("update", help="Update the local domain repository.")

    # Register
    register_parser = subparsers.add_parser("register", help="Register your email and token for making API edits.")

    # Find
    find_parser = subparsers.add_parser("find", help="Find collections, domains, or problems whose title/ID contains a string.")
    find_parser.add_argument("--type", choices=["collections", "domains", "problems"], help="Type of item to find.")
    find_parser.add_argument("string", help="String to search for in the titles/IDs.")
    add_formalism_argument(find_parser)

    # Show
    show_parser = subparsers.add_parser("show", help="Find and show collections, domains, problems, or plans with a specific ID.")
    show_parser.add_argument("--type", choices=["collection", "domain", "problem", "plan"], help="Type of item to show.")
    show_parser.add_argument("--id", type=int, help="ID of the item to show.")
    add_formalism_argument(show_parser)

    # List
    list_parser = subparsers.add_parser("list", help="Lists collections, tags, or problems with a null attribute setting.")
    list_parser.add_argument("--type", choices=["collections", "tags", "null-attribute"], help="Type of items to list.")
    list_parser.add_argument("--attribute", nargs="?", default=None, help="Attribute setting to search for (only for null-attribute).")
    add_formalism_argument(list_parser)

    # Tag
    tag_parser = subparsers.add_parser("tag", help="Tag a collection, domain, or problem with a specific tag.")
    tag_parser.add_argument("--type", choices=["collection", "domain", "problem"], help="Type of item to tag.")
    tag_parser.add_argument("--id", type=int, help="ID of the item to tag.")
    tag_parser.add_argument("--tag", help="Tag to add to the item.")
    add_formalism_argument(tag_parser)

    # Untag
    untag_parser = subparsers.add_parser("untag", help="Untag a collection, domain, or problem with a specific tag.")
    untag_parser.add_argument("--type", choices=["collection", "domain", "problem"], help="Type of item to untag.")
    untag_parser.add_argument("--id", type=int, help="ID of the item to untag.")
    untag_parser.add_argument("--tag", help="Tag to remove from the item.")
    add_formalism_argument(untag_parser)

    # Submit plan
    submit_plan_parser = subparsers.add_parser("submit_plan", help="Submit the provided plan for validation and possible storage.")
    submit_plan_parser.add_argument("--id", type=int, help="Problem ID for which the plan is provided.")
    submit_plan_parser.add_argument("--plan", type=argparse.FileType("r"), help="File containing the plan to submit.")
    add_formalism_argument(submit_plan_parser)

    # Cache
    cache_parser = subparsers.add_parser("cache", help="Collect all of the domains in a collection into a specified folder.")
    cache_parser.add_argument("--id", type=int, help="Collection ID to cache.")
    cache_parser.add_argument("--folder", help="Folder to store the cached collection.")

    # Cache-all
    cache_all_parser = subparsers.add_parser("cache_all", help="Collect all domains in a collection into a specified folder, including problem data and statistics.")
    cache_all_parser.add_argument("--id", type=int, help="Collection ID to cache.")
    cache_all_parser.add_argument("--folder", help="Folder to store the cached collection and problem data/statistics.")

    args = parser.parse_args()

    print("Parsing details:")
    print(args)
    exit(0)


    if len(sys.argv) == 1:
        print(USAGE_STRING)
        exit(0)


    root = None

    i = 1

    while i < len(sys.argv):
        if sys.argv[i] == "update":
            if api.checkForDomainPath():
                print("Updating...")
                os.system("cd {0}; git pull".format(api.DOMAIN_PATH))
            else:
                print("Error: Domain path is not set.")

            i += 1

        elif sys.argv[i] == 'cache':
            i += 1

            try:
                cid = int(sys.argv[i].strip())
                i += 1
                outdir = sys.argv[i].strip()
                i += 1
            except:
                print("Must provide a valid collection ID and filename.")
                exit(1)

            cache(cid, outdir)

        elif sys.argv[i] == 'cache-all':
            i += 1

            try:
                cid = int(sys.argv[i].strip())
                i += 1
                outdir = sys.argv[i].strip()
                i += 1
            except:
                print("Must provide a valid collection ID and filename.")
                exit(1)

            cache(cid, outdir, True)

        elif sys.argv[i] == 'register':
            register()
            i += 1

        elif sys.argv[i] == 'submit':
            i += 1

            sub = sys.argv[i].strip()
            i += 1

            if sub == 'plan':

                pid = int(sys.argv[i].strip())
                i += 1

                pfile = sys.argv[i].strip()
                i += 1

                submit_plan(pid, pfile)
            else:
                print("Error: unknown submission type {0}".format(sub))

        elif sys.argv[i] == 'list':
            i += 1

            sub = sys.argv[i].strip()
            i += 1

            if sub == 'tags':
                print("{0}\t{1}\n".format('Tag Name'.rjust(26), 'Description'))
                tags = api.get_tags()
                for t in sorted(tags.keys()):
                    print("{0}\t{1}".format(t.rjust(26), tags[t]))
                print()
            elif sub == 'collections':
                cols = {c['collection_id']: c for c in api.get_collections()}
                for cid in sorted(cols.keys()):
                    c = cols[cid]
                    print()
                    print("         ID: {0}".format(c['collection_id']))
                    print("       Name: {0}".format(c['collection_name']))
                    print("      #Doms: {0}".format(len(c['domain_set'])))
                    print("Description: {0}".format(c['description']))
                print()
            elif sub == 'null-attribute':
                attribute = sys.argv[i].strip()
                i += 1
                nullprobs = api.get_null_attribute_problems(attribute)
                if len(nullprobs) < 25:
                    pprint.pprint(nullprobs)
                else:
                    print("{0} problems have {1} set to null. 10 examples:\n".format(len(nullprobs), attribute))
                    print('\n'.join([" - {0}: {1}".format(i, nullprobs[i]) for i in list(nullprobs.keys())[:10]]))
                    print(' - ...')
            else:
                print("Error: unknown list type {0}".format(sub))
                exit(1)
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
            elif command in ["tag", "untag"]:

                iid = int(argument)

                if i == len(sys.argv):
                    print("Error: expected a tag name")
                    exit(1)
                tag = sys.argv[i]
                i += 1

                if 'tag' == command and 'collection' == subcommand:
                    api.tag_collection(iid, tag)
                elif 'tag' == command and 'domain' == subcommand:
                    api.tag_domain(iid, tag)
                elif 'tag' == command and 'problem' == subcommand:
                    api.tag_problem(iid, tag)
                elif 'untag' == command and 'collection' == subcommand:
                    api.untag_collection(iid, tag)
                elif 'untag' == command and 'domain' == subcommand:
                    api.untag_domain(iid, tag)
                elif 'untag' == command and 'problem' == subcommand:
                    api.untag_problem(iid, tag)
                else:
                    print("Error: can only (un)tag a collection, domain, or problem")
                    exit(1)
            else:
                print("Error: unknown command {0}".format(command))
                exit(1)
    print()


