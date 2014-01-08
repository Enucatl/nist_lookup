#!/usr/bin/env python

"""Functions to download and parse the NIST database table with the form
factors.

"""

import numpy as np
import scipy.constants as const
from scipy import interpolate
import urllib.request
import io
from bs4 import BeautifulSoup


class NistPageError(Exception):
    """Exception raised if the NIST website returns an error"""
    pass


def output_name(formula):
    """Get name for the output file."""
    return "nist_table_{0}".format(formula)


def download_page(formula, min_energy=10, max_energy=200):
    """Download HTML page from the NIST database."""
    url = "http://physics.nist.gov/cgi-bin/ffast/ffast.pl?\
Formula={formula}&gtype=4&range=S&lower={min_energy}\
&upper={max_energy}&density=&frames=no&htmltable=1".format(
        formula=formula,
        min_energy=min_energy,
        max_energy=max_energy)
    page = urllib.request.urlopen(url)
    text = page.read().decode()
    return text


def check_page(text):
    """Check if the page is valid."""
    if "Error" in text:
        print(text)
        raise NistPageError("""Website error, check that the formula is
        correct.""")


def get_density(text):
    """Return the number of atoms per unit volume (cm^3)"""
    for line in text.splitlines():
        if "Nominal density" in line:
            line = line.split()
            atomic_weight = float(line[0])
            density = float(line[-1])
            """convert to cm to be consistent with the other NIST tables"""
            atoms_per_unit_volume = const.N_A * density / atomic_weight
            break
    return atoms_per_unit_volume


def parse_table(text):
    """Parse the HTML table through the tags"""
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
            content = cell.find(text=True)
            table_row.append(content)
            table.append(table_row)
    return table


def calculate_coefficients(table, density):
    """print the scattering factors table for given
    element and energy range (keV)
    calculates delta and beta with formula (1) in section 1.7 of the xray
    data booklet http://xdb.lbl.gov/"""
    output_table = io.StringIO()
    print("""
#columns:
#energy (keV) (from NIST)
#f1 (e/atom) (from NIST)
#f2 (e/atom) (from NIST)
#wavelength (cm) (from NIST)
#delta (calculated)
#beta (calculated)
            """, file=output_table)
    #convert to cm to be consistent with the other NIST tables
    r_e = const.physical_constants["classical electron radius"][0] * 100
    factor = r_e / (2 * const.pi) * density
    for row in table:
        for column in row:
            print(float(column), end="\t", file=output_table)
        f1 = float(row[1])
        f2 = float(row[2])
        wavelength = float(row[3]) * 1e-7
        delta = factor * wavelength * wavelength * f1
        beta = factor * wavelength * wavelength * f2
        print(delta, end=" ", file=output_table)
        print(beta, file=output_table)
    return output_table.getvalue()


def get_formatted_table(material, min_energy=9, max_energy=210):
    """Compose the above functions."""
    text = download_page(material, min_energy, max_energy)
    check_page(text)
    table = parse_table(text)
    density = get_density(text)
    formatted_table = calculate_coefficients(table, density)
    return formatted_table


def get_graph_delta(table_raw):
    """return the interpolated delta"""
    table = np.loadtxt(table_raw)
    energies = table[:, 0]
    delta = table[:, 4]
    return interpolate.interp1d(energies, delta)


def get_graph_beta(table_raw):
    """return the interpolated beta"""
    table = np.loadtxt(table_raw)
    energies = table[:, 0]
    beta = table[:, 5]
    return interpolate.interp1d(energies, beta)
