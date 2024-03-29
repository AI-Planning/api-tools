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


def find(sub, arg, form):
    """Find an object of type sub that matches argument arg."""

    if sub == 'collections':
        res = api.find_collections(arg, form)
    elif sub == 'domains':
        res = api.find_domains(arg, form)
    elif sub == 'problems':
        res = api.find_problems(arg, form)
    else:
        print("Error: Unrecognized sub-command, {0}".format(sub))
        exit(1)

    pprint.pprint(res, sort_dicts=False)

def show(sub, arg, form):
    """Show an object of type sub that matches the id arg."""

    arg = int(arg)

    if sub == 'plan':
        print(api.get_plan(arg, form))
        return

    if sub == 'collection':
        res = api.get_collection(arg, form)
    elif sub == 'domain':
        res = api.get_domain(arg, form)
    elif sub == 'problem':
        res = api.get_problem(arg, form)
    else:
        print("Error: Unrecognized sub-command, {0}".format(sub))
        exit(1)

    pprint.pprint(res, sort_dicts=False)

def submit_plan(pid, pfile, formalism):
    with open(pfile) as f:
        plan = f.read()
    api.submit_plan(pid, plan, formalism)

def cache(cid, outdir, formalism, include_data = False):

    print("Caching collection %d to [%s] (data included = %s)..." % (cid, outdir, str(include_data)))

    if os.path.exists(outdir):
        print("Error: Output directory already exists.")
        exit(1)
    else:
        os.mkdir(outdir)

    domains = {}
    problem_data = {}
    domain_data = api.get_domains(cid, formalism)
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
        probs = [api.localize(p) for p in api.get_problems(dom['domain_id'], formalism)]

        # Copy the domain and problem files to their appropriate directory
        for i in range(len(probs)):
            dpath = os.path.join(dname, "domain_%.2d.pddl" % (i+1))
            ppath = os.path.join(dname, "prob_%.2d.pddl" % (i+1))

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
    find_parser.add_argument("--query", help="String to search for in the titles/IDs.")
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
    submit_plan_parser = subparsers.add_parser("submit-plan", help="Submit the provided plan for validation and possible storage.")
    submit_plan_parser.add_argument("--id", type=int, help="Problem ID for which the plan is provided.")
    submit_plan_parser.add_argument("--plan", type=argparse.FileType("r"), help="File containing the plan to submit.")
    add_formalism_argument(submit_plan_parser)

    # Cache
    cache_parser = subparsers.add_parser("cache", help="Collect all of the domains in a collection into a specified folder.")
    cache_parser.add_argument("--id", type=int, help="Collection ID to cache.")
    cache_parser.add_argument("--folder", help="Folder to store the cached collection.")
    add_formalism_argument(cache_parser)

    # Cache-all
    cache_all_parser = subparsers.add_parser("cache-all", help="Collect all domains in a collection into a specified folder, including problem data and statistics.")
    cache_all_parser.add_argument("--id", type=int, help="Collection ID to cache.")
    cache_all_parser.add_argument("--folder", help="Folder to store the cached collection and problem data/statistics.")
    add_formalism_argument(cache_all_parser)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        exit(0)

    # update
    if args.command == "update":
        if api.checkForDomainPath():
            print("Updating...")
            os.system("cd {0}; git pull".format(api.DOMAIN_PATH))
        else:
            print("Error: Domain path is not set.")

    # cache
    elif args.command == "cache":
        if args.id is None or args.folder is None:
            print("Error: Must provide a collection ID and folder name.")
            exit(1)
        cache(args.id, args.folder, args.formalism)

    # cache-all
    elif args.command == "cache-all":
        if args.id is None or args.folder is None:
            print("Error: Must provide a collection ID and folder name.")
            exit(1)
        cache(args.id, args.folder, args.formalism, True)


    # register
    elif args.command == "register":
        register()

    # submit
    elif args.command == "submit-plan":
        if args.id is None or args.plan is None:
            print("Error: Must provide a problem ID and plan file.")
            exit(1)
        submit_plan(args.id, args.plan, args.formalism)

    # list
    elif args.command == "list":
        if args.type is None:
            print("Error: Must provide a list type.")
            exit(1)
        if args.type == "tags":
            print("{0}\t{1}\n".format('Tag Name'.rjust(26), 'Description'))
            tags = api.get_tags(args.formalism)
            for t in sorted(tags.keys()):
                print("{0}\t{1}".format(t.rjust(26), tags[t]))
            print()
        elif args.type == "collections":
            cols = {c['collection_id']: c for c in api.get_collections(args.formalism)}
            for cid in sorted(cols.keys()):
                c = cols[cid]
                print()
                print("         ID: {0}".format(c['collection_id']))
                print("       Name: {0}".format(c['collection_name']))
                print("      #Doms: {0}".format(len(c['domain_set'])))
                print("Description: {0}".format(c['description']))
            print()
        elif args.type == "null-attribute":
            if args.attribute is None:
                print("Error: Must provide an attribute name.")
                exit(1)
            nullprobs = api.get_null_attribute_problems(args.attribute, args.formalism)
            if len(nullprobs) < 25:
                pprint.pprint(nullprobs)
            else:
                print("{0} problems have {1} set to null. 10 examples:\n".format(len(nullprobs), args.attribute))
                print('\n'.join([" - {0}: {1}".format(i, nullprobs[i]) for i in list(nullprobs.keys())[:10]]))
                print(' - ...')
        else:
            print("Error: Unknown list type.")
            exit(1)

    # find
    elif args.command == "find":
        if args.type is None or args.query is None:
            print("Error: Must provide a search type and query.")
            exit(1)
        find(args.type, args.query, args.formalism)

    # show
    elif args.command == "show":
        if args.type is None or args.id is None:
            print("Error: Must provide a show type and ID.")
            exit(1)
        show(args.type, args.id, args.formalism)

    # tag
    elif args.command == "tag":
        if args.type is None or args.id is None or args.tag is None:
            print("Error: Must provide a tag type, ID, and tag name.")
            exit(1)

        if args.type == "collection":
            api.tag_collection(args.id, args.tag, args.formalism)
        elif args.type == "domain":
            api.tag_domain(args.id, args.tag, args.formalism)
        elif args.type == "problem":
            api.tag_problem(args.id, args.tag, args.formalism)
        else:
            print("Error: Can only tag a collection, domain, or problem.")
            exit(1)

    # untag
    elif args.command == "untag":
        if args.type is None or args.id is None or args.tag is None:
            print("Error: Must provide an untag type, ID, and tag name.")
            exit(1)
        if args.type == "collection":
            api.untag_collection(args.id, args.tag, args.formalism)
        elif args.type == "domain":
            api.untag_domain(args.id, args.tag, args.formalism)
        elif args.type == "problem":
            api.untag_problem(args.id, args.tag, args.formalism)
        else:
            print("Error: Can only untag a collection, domain, or problem.")
            exit(1)

    else:
        parser.print_help()
        exit(0)
    print()


