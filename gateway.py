# -*- coding: utf-8 -*-
"""
Created on Sun May 30 22:24:08 2021

@author: benazzi
"""
import socket as sk
import threading as thr
import message_handler as msh
from sys import exit

# flags
__stop = False

# connection towards clients
__gateway_client_ip = "192.168.1.01"  # 12 characters
__gateway_client_mac = "AA:BB:CC:DD:EE:B1"  # 17 characters
__udp_address = ("127.0.0.1", 50_000)

# connection towards server
__gateway_client_ip = "192.168.1.01"  # 12 characters
__gateway_client_mac = "AA:BB:CC:DD:EE:B1"  # 17 characters
__tcp_address = ("127.0.0.1", 51_000)


# pairs of: (client IP address, client message)
__client_message_map = {
    "192.168.1.10": "",
    "192.168.1.20": "",
    "192.168.1.30": "",
    "192.168.1.40": "",
}
__clients_served = 0
__clients_number = 1  # number of IoT client devices to serve


def process_message(message, index):
    # format message and save it in dictionary
    message = msh.unpack_message(message)
    to_save = ""
    # adds the source ip in each line of the message
    for line in message.splitlines():
        to_save += f"{index} - {line}\n"
    __client_message_map[index] = to_save
    print(__client_message_map)
    # if dictionary contains 4 formatted messages launch send to server


# function wich listens for messages on UDP port
def receive_from_device(connection):

    try:
        # endless loop to receive messages
        while True:
            # wait for a message
            print("ready for next message")
            message = connection.recv(4096).decode("utf-8")
            ip = msh.get_header(message)[1]  # extract the source IP address
            source_ip = ip[0:12]
            print("message received from: ", source_ip)
            # if IP address of device is registered schedule a thread
            # to process the message and store it
            if (
                source_ip in __client_message_map
                and __client_message_map[source_ip] == ""
            ):
                t = thr.Thread(target=process_message, args=(message, source_ip,))
                t.start()
    except Exception as e:
        print("an exception has occured: ", e)
    finally:
        connection.close()


def send_to_server(connection, message):
    pass


if __name__ == "__main__":
    udp_socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    tcp_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

    # prepare listening UDP socket
    try:
        udp_socket.bind(__udp_address)
        print("waiting for IoT devices on port: ", __udp_address[1])
    except Exception as e:
        print("an exception has occured: ", e)
        exit()

    # create and start thread for UDP socket
    receive_thread = thr.Thread(target=receive_from_device, args=(udp_socket,))
    try:
        receive_thread.start()
        receive_thread.join()
    except Exception as e:
        print("an exception has occured: ", e)
    finally:
        udp_socket.close()

    tcp_socket.close()
