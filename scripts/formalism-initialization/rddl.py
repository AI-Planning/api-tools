
# Documents new collections *Formatted for incoming RDDL collections on 2023-03-29
# https://github.com/ataitler/rddlrepository


import os, sys, glob

import importlib.util

def add_IPPC_instances(rootdir):
    # Use glob to get IPPC directories, ignoring __init__.py
    ippc_folders = glob.glob(f"{rootdir}/*/")

    assert len(ippc_folders) == 3, "There should be 3 IPPC folders"

    # Handle IPPC2011 and IPPC2014 first
    for ippc_name in ['IPPC2011', 'IPPC2014']:
        # Get the domain folders
        domain_folders = glob.glob(f"{rootdir}/{ippc_name}/*/")

        # Assert each domain folder has MDP and POMDP folders
        for domain_folder in domain_folders:
            assert os.path.isdir(f"{domain_folder}MDP/"), f"{domain_folder} does not have MDP folder"
            assert os.path.isdir(f"{domain_folder}POMDP/"), f"{domain_folder} does not have POMDP folder"

            for style in ['MDP', 'POMDP']:
                # folder with the instances
                instance_folder = f"{domain_folder}{style}/"

                # import the __init__.py file
                spec = importlib.util.spec_from_file_location("module_name", f"{instance_folder}/__init__.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                domain_info = module.info

                # Get the instances and domain file
                instance_list = glob.glob(f"{instance_folder}/instance*")
                domain_file = glob.glob(f"{instance_folder}/domain*.rddl")

                # Make sure there is only one domain file
                assert len(domain_file) == 1, f"{instance_folder} has more than one domain file"

                # Make sure there is more than one instance
                assert len(instance_list) > 1, f"{instance_folder} has less than two instances"

                # TODO: Work with the info, domain, and instances to create the collection, domain, and problems


        print(f'{ippc_name}: {len(domain_folders)} domains')

    # Handle IPPC2018
    ippc_name = 'IPPC2018'
    # Get the domain folders
    domain_folders = glob.glob(f"{rootdir}/{ippc_name}/*/")
    print(f'{ippc_name}: {len(domain_folders)} domains')

def add_standalone_instances(rootdir):
    pass

topdir = input("Path to top-level directory: ")

if not os.path.isdir(topdir):
    print("Provided path is not a valid directory.")
    sys.exit(1)

add_IPPC_instances(topdir)
# add_standalone_instances(topdir)

exit(0)

    name = info['name']
    description = info['description']
    ipc = info['context']
    tags = info['tags']
    viz = info['viz']

    # Call planning_domains_api.py function
    current = os.path.dirname(os.path.realpath(__file__))
    parent_directory = os.path.dirname(current)
    sys.path.append(parent_directory)

    import planning_domains_api as planning_api
    planning_api.create_collection(name, description, tags, ipc, formalism)
