from branch.controller import Controller
from branch.display import Display
from branch.display import Message
from branch.engine import Engine
from branch.git import Git


#
#   M A I N
#

if __name__ == "__main__":
    try:
        Engine(Git(), Display(), Controller()).run()

    except Exception as e:
        # Display().message('Operation failed:\n  ' + str(e), type=Message.error)
        raise
