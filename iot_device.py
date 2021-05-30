# -*- coding: utf-8 -*-
"""
Created on Sun May 30 18:08:04 2021

@author: benazzi
"""
import generate_values as val
import socket as sk
from time import sleep

# flags
__seconds_to_next_send = 86_400

# for gateway connection
__gateway_ip = "192.168.1.01"  # 12 characters
__gateway_mac = "AA:BB:CC:DD:EE:B1"  # 17 characters
__gateway_port = 50_000

# generate registered values for a day
# values format is:
# -------------------------------------------------
# | hh:mm - temperature value - humidity value \n |
# | ....                                          |
# | hh:mm - temperature value - humidity value \n |
# -------------------------------------------------
def create_values_for_a_day() -> str:
    values_string = ""
    for i in range(24):
        values_string += f"{i:02d}:00 - {val.generate_temperature():0>5.2f} - {val.generate_humidity():0>5.2f}\n"
    return values_string


# creates the message to sendo to the gateway by appending the given message
# to source and destination addresses
# the message format is:
# ------------------------------------------------
# | source MAC address | destination MAC address |
# | source IP address  | destination IP address  |
# ------------------------------------------------
# | ...               message                ... |
# ------------------------------------------------
def make_message(message: str, mac_addresses: tuple, ip_addresses: tuple) -> str:
    out_message = (
        f"{mac_addresses[0]}{mac_addresses[1]}\n{ip_addresses[0]}{ip_addresses[1]}\n"
    )
    return out_message + message


# function which simulates the IoT device's behavior
def device():
    out = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    sleep(
        __seconds_to_next_send
    )  # waits for 24 hours and the sends data to the gateway
    message = create_values_for_a_day()
    message = make_message(
        message, ("AA:BB:CC:DD:EE:A1", __gateway_mac), ("192.168.1.10", __gateway_ip)
    )
    out.sendto(message.encode("utf-8"), ("127.0.0.1", __gateway_port))
    out.close()


if __name__ == "__main__":
    device()
