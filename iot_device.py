# -*- coding: utf-8 -*-
"""
Created on Sun May 30 18:08:04 2021

@author: benazzi
"""
import generate_values as val

# for gateway connection
__gateway_ip = "192.168.1.1"
__gateway_mac = "AA:BB:CC:DD:EE:B1"
__gateway_port = 50_000

# registered values for a day
def create_values_for_a_day() -> str:
    values_string = ""
    for i in range(24):
        values_string += f"{i:02d}:00 - {val.generate_temperature():0>5.2f} - {val.generate_humidity():0>5.2f}\n"
    return values_string


if __name__ == "__main__":
    pass
