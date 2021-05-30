# -*- coding: utf-8 -*-
"""
Created on Sun May 30 22:38:26 2021

@author: benazzi
"""
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


def unpack_message(message: str) -> str:
    lines = message.splitlines()
    out = ""
    for line in lines:
        out += line + "\n"
    return out


# firts string contains MAC addresses
# second string contains IP addresses
def get_header(message: str) -> (str, str):
    lines = message.splitlines()
    return (lines[0], lines[1])
