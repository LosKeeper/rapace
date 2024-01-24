from src.equipment.meta_controller import MetaController
import argparse

USER_INPUT = 'topology' # file name without extension input of the user            

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Import user-input logical topology into physical topology')
    parser.add_argument('--no-compile', action='store_false', help='Do not compile P4 programs if they are already compiled')
    args = parser.parse_args()
    
    meta_controller = MetaController(USER_INPUT, args.no_compile)
    meta_controller.Import()
    meta_controller.list_controllers()