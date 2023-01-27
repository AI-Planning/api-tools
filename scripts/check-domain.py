import os, sys

current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)
sys.path.append(parent_directory)

import planning_domains_api as api

if __name__ == "__main__":
    user_input = 0

    # Using system arguments 
    try:
        user_input = int(input("What domain would you like to check: "))
        domain = api.get_domain(user_input)
    except:
        print("Input is not a number")
    
    print(domain)