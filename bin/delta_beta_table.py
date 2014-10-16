"""Run a lookup on the NIST database and print the table"""

import argparse

from nist_lookup.nist_lookup import get_formatted_table

if __name__ == '__main__':
    commandline_parser = argparse.ArgumentParser(
        description='''
        Download a table from the NIST
        for a material (only pure
        materials) and save it as a table with energy, f1, f2,
        wavelength, delta and beta.
        ''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    commandline_parser.add_argument('material', metavar='MATERIAL',
                                    nargs='?', default="Au",
                                    help='material (symbol)')
    commandline_parser.add_argument('--min_energy', metavar='MIN_ENERGY',
                                    nargs='?', type=float, default=10,
                                    help='minimum energy (keV)')
    commandline_parser.add_argument('--max_energy', metavar='MAX_ENERGY',
                                    nargs='?', type=float, default=200,
                                    help='maximum energy (keV)')
    args = commandline_parser.parse_args()
    table = get_formatted_table(args.material,
                                args.min_energy, args.max_energy)
    print(table)
