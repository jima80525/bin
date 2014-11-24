#!/usr/bin/python
from git import *
import os
repo = Repo(os.getcwd())
print repo.working_tree_dir
