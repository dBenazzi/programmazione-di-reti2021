# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 11:32:45 2021

@author: benazzi
"""
import threading as thr
import socket as sk
import signal as sig
import selectors as sel
from sys import exit
from time import sleep
import message_handler as msh

# flag
__stop_server = False

# gateway address
__gateway_ip = "10.10.10.1"  # 10 characters
__gateway_mac = "AA:BB:CC:DD:EE:B2"  # 17 characters

# socket address
__tcp_address = ("127.0.0.1", 51_000)

# lock to wait for accepting connections
__accept_wait = thr.Event()

# reads data from the given connection and prints it.
# if more than 10 seconds pass after starting the function
# socket is closed and data is not read
def receive_message(open_connection):
    # selector to check if data is ready on the socket
    selector = sel.DefaultSelector()
    selector.register(open_connection, sel.EVENT_READ)
    print("ready to receive")
    # wait for 10 seconds or whenever there is data to read from socket
    connection_ready = selector.select(10)
    if connection_ready:  # check if data is ready to be read
        try:
            message = open_connection.recv(4096).decode("utf-8")  # read from socket
            header = msh.get_header(message)
            source_ip = header[1][0:10]
            if source_ip != __gateway_ip:  # check if source is gateway
                print("message source is not gateway")
            else:
                # print message containing values
                print(f"message received from gateway ({source_ip}) containing:\n")
                print(msh.unpack_message(message))
        except IOError as e:
            print("error during read:\n", e)
            selector.close()
            open_connection.close()
            return
    else:
        print("connection timeout. no data received")
    selector.close()
    open_connection.close()
    print("connection close")


# accepts a new TCP connection and creates a new thread to handle it
def accept_connections(connection):
    global __accept_wait
    while not __stop_server:
        __accept_wait.wait()  # hold until clients attempt connection
        connection_socket, address = connection.accept()
        print("new connection opened")
        thr.Thread(target=(receive_message), args=(connection_socket,)).start()
        __accept_wait.clear()  # restore for next client request


# monitors (using selectors) tcp_socket and unlocks accept_wait
# if a new request is ready to be served.
def connection_request_notifier(connection):
    global __accept_wait
    selector = sel.DefaultSelector()
    selector.register(connection, sel.EVENT_READ)
    while not __stop_server:
        accept_ready = selector.select(5)
        if accept_ready:
            __accept_wait.set()
    selector.close()


# handles SIGINT (ctrl+c from keyboard)
def signal_handler(signalnumber, frame):
    global __stop_server
    __stop_server = True
    print("stopping server (ctrl + c received)")


if __name__ == "__main__":
    print("starting server")
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

    # start thread accepting connection and its notifier
    thr.Thread(target=accept_connections, args=(tcp_socket,), daemon=True).start()
    connection_notifier = thr.Thread(
        target=connection_request_notifier, args=(tcp_socket,)
    )
    connection_notifier.start()

    print("server ready")
    # sig.pause() not working on Windows. replaced by sleep underneath
    while True:
        sleep(3)  # here to check for signals every 3 seconds
        if __stop_server:
            # close socket only if not acecpting a connection
            if not __accept_wait.is_set():
                connection_notifier
                tcp_socket.close()
            exit()
