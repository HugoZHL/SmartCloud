from argparse import ArgumentParser
from util import register

if __name__ == '__main__':

    parser = ArgumentParser(description="Add User")
    parser.add_argument('-u', '--username', type=str, required=True)
    parser.add_argument('-p', '--password', type=str, required=True)

    args = parser.parse_args()

    error = register(args.username, args.password)

    if error:
        print('Error: ' + error)
