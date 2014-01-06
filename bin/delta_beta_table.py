"""Run a lookup on the NIST database"""

import argparse

from nist_lookup import download_page
from nist_lookup import check_page
from nist_lookup import parse_table
from nist_lookup import get_density
from nist_lookup import calculate_coefficients

if __name__ == '__main__':
    commandline_parser = argparse.ArgumentParser(
        description='''
        Download a table from the NIST
        for a material (only pure
        materials) and save it as a table with energy, f1, f2,
        wavelength, delta and beta.
        ''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    commandline_parser.add_argument('--folder', '-f', metavar='FOLDER',
                                    nargs='?', default="nist",
                                    help='''folder where the nist database
                                    files will be stored''')
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
    text = download_page(args.material)
    check_page(text)
    table = parse_table(text)
    density = get_density(text)
    calculate_coefficients(table, density)
