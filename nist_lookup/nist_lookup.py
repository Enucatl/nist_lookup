#!/usr/bin/env python

from scipy.constants import N_A, physical_constants, pi
from string import Template
from bs4 import BeautifulSoup
import urllib.request


class NistPageError(Exception):
    pass


template_url = Template(
    "http://physics.nist.gov/cgi-bin/ffast/ffast.pl?\
Formula=$formula&gtype=4&range=S&lower=$min_energy\
&upper=$max_energy&density=&frames=no&htmltable=1")


def output_name(formula):
    return "nist_table_{0}".format(formula)


def download_page(formula, min_energy=10, max_energy=200):
    url = template_url.safe_substitute(formula=formula,
                                       min_energy=min_energy,
                                       max_energy=max_energy)
    page = urllib.request.urlopen(url)
    text = page.read().decode()
    return text


def check_page(text):
    if "Error" in text:
        print(text)
        raise NistPageError("""Website error, check that the formula is
        correct.""")


def get_density(text):
    for line in text.splitlines():
        if "Nominal density" in line:
            line = line.split()
            atomic_weight = float(line[0])
            density = float(line[-1])
            """convert to cm to be consistent with the other NIST tables"""
            atoms_per_unit_volume = N_A * density / atomic_weight
            break
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


def calculate_coefficients(table, density):
    """print the scattering factors table for given
    element and energy range (keV)
    calculates delta and beta with formula (1) in section 1.7 of the xray
    data booklet http://xdb.lbl.gov/"""
    print("""
            #columns:
            #energy (keV) (from NIST)
            #f1 (e/atom) (from NIST)
            #f2 (e/atom) (from NIST)
            #wavelength (cm) (from NIST)
            #delta (calculated)
            #beta (calculated)

            """)

    #convert to cm to be consistent with the other NIST tables
    r_e = physical_constants["classical electron radius"][0] * 1e2
    factor = r_e / (2 * pi) * density
    for row in table:
        for column in row:
            print(column, end=" ")
        f1 = float(row[1])
        f2 = float(row[2])
        wavelength = float(row[3]) * 1e-7
        delta = factor * wavelength * wavelength * f1
        beta = factor * wavelength * wavelength * f2
        print(delta, end=" ")
        print(beta)
