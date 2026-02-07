'''
The setup.py file is an essential  part of packaging and
distributing Python projects. It is used by setuptools
(or distutils in older Python versions) to define the configuration
of your project , such as it's metadata , dependencies and more.
'''

from setuptools import find_packages , setup 
from typing import List 

def get_requirements()->List[str]:
    ''' 
    This function will return a list of requirements
    '''
    
    requirement_lst : List[str] = []
    try:
        with open('requirements.txt' , 'r') as file:
            #Read lines from the file 
            lines = file.readlines()
            #Process each line
            for line in lines:
                requirement = line.strip()
                #ignore empty lines and -e .
                if requirement and requirement!= '-e .':
                    requirement_lst.append(requirement) 
    except FileNotFoundError:
        print("requirements.txt file not found") 
        
    return requirement_lst   

print(get_requirements())

'''
Line 1: "numpy==1.24.0" → requirement = "numpy==1.24.0"
        if "numpy==1.24.0" and "numpy==1.24.0" != '-e .': 
        → True and True → ✅ Added to list
        
Line 2 : "" (empty line) → requirement = ""
        if "" and ... → False immediately → ❌ Skipped

Line 3 : "-e ."  → requirement = "-e ."
        if "-e ." and "-e ." != '-e .':
         → True and False → ❌ Skipped
                   
''' 
                        
setup(
    name = "NetworkSecurity" , 
    version = "0.0.1" , 
    author = "Manan Sharma" , 
    author_email = "mananofc24@gmail.com" , 
    packages = find_packages() , 
    install_requires = get_requirements()
    
)                
    
    
