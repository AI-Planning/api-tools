
# Documents new collections *Formatted for incoming RDDL collections on 2023-03-29
# https://github.com/ataitler/rddlrepository


import os, sys, glob

def add_collection():
    # Request input for path of collection
    collectionpath = input("Path to collection folder: \n")

    # If path isn't a directory, throw and error
    if not os.path.isdir(collectionpath):
        print("Provided path is not a valid directory.")
        return
    sys.path.append(collectionpath)

    try:
        from __init__ import info
    except ImportError:
        print("ERROR: __init__.py file is most likely empty, unable to parse given directory.")
        return
    name = info['name']
    description = info['description']
    ipc = info['context']
    tags = info['tags']
    viz = info['viz']

    instance_list = glob.glob(collectionpath + "/instance*")
    if len(instance_list) < 2:
        print("There needs to be more than 1 instance.rddl file")
        return
    # Make sure its greater than one for instance list as well
    domain_file = glob.glob(collectionpath + "/domain*.rddl")
    if len(domain_file) > 1:
        print("There cannot be more than 1 domain file for RDDL collections")
        return
    else:
        domain_file = domain_file[0]


    formalism = input("Formalism: \n").lower()

    # Call planning_domains_api.py function
    current = os.path.dirname(os.path.realpath(__file__))
    parent_directory = os.path.dirname(current)
    sys.path.append(parent_directory)

    import planning_domains_api as planning_api
    # planning_api.create_collection(name, description, tags, ipc, formalism)

if __name__ == "__main__":
    """ Testing """
    add_collection()
