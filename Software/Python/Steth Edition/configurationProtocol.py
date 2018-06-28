"""
Stethoscope Configuration Protocol

The following module contains functions used to link resources to the main device scripts

Fluvio L Lobo Fenoglietto 11/15/2017
"""

from    os.path import expanduser
import  sys


# ======================================= #
# Define Paths
#
# Define and insert paths to directories
# with required documentation for the
# device scripts
#
# Fluvio L Lobo Fenoglietto 11/15/2017
# ======================================= #
def definePaths(device):
    baseDir = expanduser("~")                                                                   # get main/root or base directory for the operating system in use
    rootDir = "/root"                                                                           # root directory for Linux - Raspbian
    if baseDir == rootDir:
        homeDir = "/home/pi"
        pythonDir = homeDir + "/pd3d/csec/repos/ControlSystem/Software/Python"
        deviceDir = pythonDir + "/" + device + "/"
    else:
        homeDir = "/home/pi"
        pythonDir = 0
        deviceDir = 0
    print deviceDir
    return homeDir, pythonDir, deviceDir

# ======================================= #
# Insert Paths
#
# Insert defined directory paths into the
# python directory
#
# Fluvio L Lobo Fenoglietto 11/15/2017
# ======================================= #
def addPaths(paths):
    if isinstance(paths, list):
        Npaths = len(paths)
        for i in range(0, Npaths):
            sys.path.insert(0, paths[i])
        response = True
    else:
        sys.path.insert(0, paths)
        response = False
    return response
        
    
