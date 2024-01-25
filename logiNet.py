import argparse

from src.equipment.meta_controller import MetaController
from src.api import Api

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Import user-input logical topology into physical topology')
    parser.add_argument('--input', type=str, help='Yaml file of the logical topology')
    parser.add_argument('--no-compile', action='store_false', help='Do not compile P4 programs if they are already compiled')
    parser.add_argument('--compile', type=str, help='Compile only a specific file')
    parser.add_argument('--no-cli', action='store_false', help='Do not start the CLI for the API')
    args = parser.parse_args()
    
    meta_controller = MetaController(args.input, args.compile, args.no_compile)
    if args.no_cli:
        api = Api(meta_controller)
        api.cmdloop()
    