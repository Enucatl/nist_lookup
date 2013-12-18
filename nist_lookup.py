#!/usr/bin/env python

from scipy.constants import N_A, physical_constants, pi
from string import Template
from BeautifulSoup import BeautifulSoup
import os
import urllib
import math

template_url = Template("http://physics.nist.gov/cgi-bin/ffast/ffast.pl?Formula=$formula&gtype=4&range=S&lower=$min_energy&upper=$max_energy &density=&frames=no&htmltable=1")


def output_name(formula):
    return "nist_table_{0}".format(formula)


def download_page(formula, min_energy=10, max_energy=200):
    url = template_url.safe_substitute(formula=formula,
                                       min_energy=min_energy,
                                       max_energy=max_energy)
    page = urllib.urlopen(url)
    text = page.read()
    return text


def get_density(text):
    atoms_per_unit_volume = get_density(text)
    return atoms_per_unit_volume


def parse_table(text):
    soup = BeautifulSoup(text)
    table = soup.find("table")
    rows = table.findAll("tr")
    table = []
    for row in rows:
        cols = row.findAll("td")
        if not cols:
            continue
        cols = cols[:3] + [cols[-1]]
        table_row = []
        for cell in cols:
            content = cell.find(text=True).replace("&nbsp;", "")
            table_row.append(content)
            table.append(table_row)
    return table


class ScatteringFactorTable(object):
    """get and save the scattering factors table for given
    element and energy range (keV)
    calculates delta and beta with formula (1) in section 1.7 of the xray
    data booklet http://xdb.lbl.gov/"""

    def __init__(self, element_Z, min_energy=10, max_energy=200,
                 folder="nist"):
        super(ScatteringFactorTable, self).__init__()
        self.element_Z = element_Z
        self.min_energy = min_energy
        self.max_energy = max_energy
        if not os.path.exists(folder):
            os.makedirs(folder)
        elif os.path.exists(folder) and not os.path.isdir(folder):
            raise OSError("{0} is a file, not a folder!".format(
                folder))
        self.file_name = os.path.join(folder,
                                      "refraction_index_{0}_{1}_{2}".format(
                                              self.element_Z,
                                              self.min_energy,
                                              self.max_energy))
        self.url = template_url.safe_substitute(
                Z=element_Z,
                lower_energy=min_energy,
                upper_energy=max_energy
        )

    def get_density(self, text):
        for line in text.split("\n"):
            if "Nominal density" in line:
                line = line.split()
                atomic_weight = float(line[0])
                density = float(line[-1])
                """convert to cm to be consistent with the other NIST tables"""
                self.atoms_per_unit_volume = N_A * density / atomic_weight
                break

    def get_table(self):
        page = urllib2.urlopen(self.url)
        text = page.read()
        soup = BeautifulSoup(text)
        table = soup.find("table")
        rows = table.findAll("tr")
        self.table = []
        for row in rows:
            cols = row.findAll("td")
            if not cols: continue
            cols = cols[:3] + [cols[-1]]
            table_row = []
            for cell in cols:
                content = cell.find(text=True).replace("&nbsp;", "")
                table_row.append(content)
                self.table.append(table_row)
                self.get_density(text)

    def save_table(self):
        self.get_table()
        with open(self.file_name, "w") as out_file:
            print("""
                  #columns:
                  #energy (keV) (from NIST)
                  #f1 (e/atom) (from NIST)
                  #f2 (e/atom) (from NIST)
                  #wavelength (cm) (from NIST)
                  #delta (calculated)
                  #beta (calculated)

                  """, file=out_file)

            """convert to cm to be consistent with the other NIST tables"""
            r_e = physical_constants["classical electron radius"][0] * 1e2
            factor = r_e / (2 * pi) * self.atoms_per_unit_volume
            for row in self.table:
                for column in row:
                    print(column, end=" ", file=out_file)
                    f1 = float(row[1])
                    f2 = float(row[2])
                    wavelength = float(row[3]) * 1e-7
                    delta = factor * wavelength * wavelength * f1
                    beta = factor * wavelength * wavelength * f2
                    print(delta, end=" ", file=out_file)
                    print(beta, file=out_file)

if __name__ == '__main__':
    import sys
    import periodic_table
    import argparse

    commandline_parser = argparse.ArgumentParser(description='''
                                                 Download a table from the NIST for a material (only pure
                                                 materials) and save it as a table with energy, f1, f2,
                                                 wavelength, delta and beta.
                                                 ''',
                                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    commandline_parser.add_argument('--folder', '-f', metavar='FOLDER',
                                    nargs='?', default="nist", help='''folder where the nist database
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
    a = ScatteringFactorTable(args.material.capitalize(),
                              args.min_energy,
                              args.max_energy,
                              args.folder)
    a.save_table()
