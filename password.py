
from optparse import OptionParser
from werkzeug.security import generate_password_hash, check_password_hash

def main():

    # Command line
    options = parse_options()
    print("{0} -> [{1}]".format(options.password,  generate_password_hash(options.password)))


def parse_options():
    parser = OptionParser()
    parser.add_option("-p", "--password", dest="password",
                      help="password to hash")

    (options, args) = parser.parse_args()
    return options


if __name__ == '__main__':
    main()
