from branch.controller import Controller
from branch.display import Display
from branch.engine import Engine
from branch.git import Git


#
#   M A I N
#

if __name__ == "__main__":
    Engine(Git(), Display(), Controller()).run()
