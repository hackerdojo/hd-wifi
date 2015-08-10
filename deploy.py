#!/usr/bin/python


""" Deploys and unit tests the app. """


import subprocess

# Initialize the submodules first.
subprocess.call(["git", "submodule", "init"])
subprocess.call(["git", "submodule", "update"])

# Run the shared deploy code.
from shared import deploy
deploy.run()
