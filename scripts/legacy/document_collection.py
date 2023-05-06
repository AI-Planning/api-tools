# Script to add collections and benchmarks
# * Old method, updated to match https://github.com/ataitler/rddlrepository

import os, sys

current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)
sys.path.append(parent_directory)

import planning_domains_api as planning_api


def add_collection():

   # Request input for path of collection
   collectionpath = input("Path to collection folder: ")

   # If path isn't a directory, throw and error
   if not os.path.isdir(collectionpath):
      print("Provided path is not a valid directory.")
      return
   sys.path.append(collectionpath)
   from api import domains
   domain = domains[0]
   description = domain['description']
   ipc = domain['ipc']
   name = domain['name']
   problems = domain['problems']

   formalism = input("Formalism: ")
   # Call planning_domains_api.py function
   planning_api.create_collection(name, description, problems, ipc, formalism)
    
if __name__ == "__main__":
    """ Testing """
    add_collection()
