# -*- coding: utf 8 -*-
"""
Unit implrementation using mod:`pint`.
"""

import numpy as np
import pint
import pint.unit

UndefinedUnitError = pint.UndefinedUnitError
DimensionalityError = pint.DimensionalityError

units = pint.UnitRegistry()

# Units not in the standard pint syntax
units.define('degrees_north = degree = degrees_N = degreesN = degree_north = degree_N = degreeN')
units.define('degrees_east = degree = degrees_E = degreesE = degree_east = degree_E = degreeE')
units.define('us_feet = usft = us_ft = 1200/3937 meters')
units.define('us_barrel = us_bbl = usbbl = 158,987294928 liter')
units.define('barrel = imperial_barrel = international_barrel = imp_bbl = bbl = 159,113159869818 liter')
units.define('bpd = bpod = barrel / day')
units.define('cf = cubic_feet = feet * feet * feet')
units.define('Mcfpd = Mcf / day')
units.define('boe = barrels_of_oil_equivalent = 6 Mcf')
units.define('BTU = british_thermal_unit = 1055.05585262 Joule')
units.define('percent = 0.01*count = %')
units.define('permille = 0.001*count = %')