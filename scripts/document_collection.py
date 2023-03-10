# Script to add collections and benchmarks
""" Script to add a new collection"""

import os, sys

current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)
sys.path.append(parent_directory)

import planning_domains_api as api


def add_collection():

   # Request input for path of collection
   collectionpath = input("Path to collection folder: ")

   # If path isn't a directory, throw and error
   if not os.path.isdir(collectionpath):
      print("Provided path is not a valid directory.")
      return
    
   # Open file and strip information
   api_file = open(collectionpath + "\\api.py")
   description = ""
   ipc = ""
   name = ""
   domains = ""
   for line in api_file:
      if 'domains' in line:
         pass
      elif 'description' in line:
         description += line[20:-2]
      elif 'ipc' in line:
         ipc += line[10:-2]
      elif 'name' in line:
         name += line[11:-2]
      else:
         domains += line
   # Clean up domain string
   domains = domains[15:-3]

   # Call planning_domains_api.py function
   api.create_collection(name, description, domains, ipc)
    
if __name__ == "__main__":
    """ Testing """
    add_collection()
