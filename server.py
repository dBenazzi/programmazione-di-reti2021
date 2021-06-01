# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 11:32:45 2021

@author: benazzi
"""
import threading as thr
import socket as sk
import signal as sig

# import select as sel
from sys import exit
from time import sleep

# import message_handler as msh

# server address
__tcp_address = ("127.0.0.1", 51_000)


def receive_message(open_connection):
    print("ready to receive")
    message = open_connection.recv(4096)
    print(message.decode("utf-8"))
    open_connection.close()
    print("connection close")


def accept_connections(connection):
    connection_socket, address = connection.accept()
    print("new connection opened")
    thr.Thread(target=(receive_message), args=(connection_socket,)).start()


# handles SIGINT (ctrl+c from keyboard)
def signal_handler(signalnumber, frame):
    exit()  # placeholder


if __name__ == "__main__":
    # handler for ctrl+c
    sig.signal(sig.SIGINT, signal_handler)
    # open TCP socket
    tcp_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    try:
        tcp_socket.bind(__tcp_address)
        tcp_socket.listen(2)
    except Exception as e:
        print("couldn't bind tcp socket: \n", e)
        tcp_socket.close()
        exit(-1)

    connection_acceptor = thr.Thread(
        target=accept_connections, args=(tcp_socket,), daemon=True
    )
    connection_acceptor.start()

    # sig.pause() not working on Windows. replaced by sleep underneath
    while True:
        sleep(3)  # here to check for signals every 3 seconds
