# -*- coding: utf-8 -*-
"""
Created on Sun May 30 17:36:43 2021

@author: benazzi
"""
from random import uniform as uf

# absolute umidity between 7 and 20 g/m^3
__humidity_min = 7.0
__humidity_max = 20
# temperatures between 0 and 25 °C
__temp_min = 0.0
__temp_max = 30.0


def generate_temperature() -> float:
    return round(uf(__temp_min, __temp_max), 2)


def generate_humidity() -> float:
    return round(uf(__humidity_min, __humidity_max), 2)
