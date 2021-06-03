# -*- coding: utf-8 -*-
"""
Created on Sun May 30 22:24:08 2021

@author: benazzi
"""
import socket as sk
import threading as thr
import signal as sig
from sys import exit
from time import sleep, perf_counter_ns
import message_handler as msh

# flags
__stop_gateway = False

# for server connection
__server_ip = "10.10.10.10"  # 11 characters
__server_mac = "AA:BB:CC:DD:EE:C1"  # 17 characters
__server_port = 51_000

# connection towards clients
__gateway_client_ip = "192.168.1.1"  # 11 characters
__gateway_client_mac = "AA:BB:CC:DD:EE:B1"  # 17 characters
__udp_address = ("127.0.0.1", 50_000)

# connection towards server
__gateway_server_ip = "10.10.10.1"  # 10 characters
__gateway_server_mac = "AA:BB:CC:DD:EE:B2"  # 17 characters

# pairs of: (client IP address, client message)
__client_message_map = {
    "192.168.1.10": "",
    "192.168.1.20": "",
    "192.168.1.30": "",
    "192.168.1.40": "",
}
__clients_number = 4  # number of IoT client devices to serve

# lock used to limit access to __clients_served counter
__clients_lock = thr.Lock()
__clients_served = 0

# event to start the send_to_server thread
__send_wait = thr.Event()
# event to wait until send_to_server has sent the message
__send_end = thr.Event()

# adds source ip to message received from IoT device and stores
# it in __client_message_map
# if messages form all the clients have been received send them
def process_message(message, index):
    global __client_message_map
    global __clients_lock
    global __clients_served
    global __send_wait
    global __send_end
    # format message and save it in dictionary
    message = msh.unpack_message(message)
    to_save = ""
    with __clients_lock:
        # adds the source ip in each line of the message
        for line in message.splitlines():
            to_save += f"{index} - {line}\n"
        __client_message_map[index] = to_save
        # if dictionary contains 4 formatted messages launch send to server
        __clients_served += 1
        if __clients_served == __clients_number:
            print(f"received a message from all {__clients_number} clients")
            # send data to server
            __send_end.clear()  # prepare to wait for the send to complete
            __send_wait.set()  # unlocks the send_to_server thread
            __send_end.wait()  # wait for send to complete
            # restore counter and dictionary
            __clients_served = 0
            for key in __client_message_map:
                __client_message_map[key] = ""


# function wich listens for messages on UDP port
def receive_from_device(connection):
    try:
        # endless loop to receive messages
        while not __stop_gateway:
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
                thr.Thread(target=process_message, args=(message, source_ip,)).start()
    except:
        connection.close()


# sends the message to the server containing the values from the IoT clients
# stored in __client_message_map
def send_to_server():
    global __send_wait
    global __send_end
    while not __stop_gateway:
        __send_wait.wait()  # waits until the event is unlocked
        if __stop_gateway:  # check if program should stop
            return
        # create new TCP socket
        try:
            connection = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        except Exception:
            print("couldn't create TCP connection")
            __send_wait.clear()  # locks send event for next loop
            __send_end.set()  # unlocks calling thread
            continue
        # construct message and add "MAC" and "TCP" headers
        message = ""
        # concatenates the messages from clients
        for value in __client_message_map.values():
            message += value + "\n"
        # adds header to messages
        message = msh.make_message(
            message,
            (__gateway_server_mac, __server_mac),
            (__gateway_server_ip, __server_ip),
        ).encode("utf-8")
        print(message.decode("utf-8"))
        # connect to server and send message
        print("sending message to server")
        try:
            t1 = perf_counter_ns()
            connection.connect(("127.0.0.1", __server_port))
            connection.send(message)
            t2 = perf_counter_ns()
            print(f"message sent in {(t2 - t1)/(1000):0>3.0f} ms")
            connection.shutdown(sk.SHUT_RDWR)
        except Exception:
            print("couldn't send message to server")
        connection.close()
        __send_wait.clear()  # locks send event for next loop
        __send_end.set()  # unlocks calling thread


# handles SIGINT (ctrl+c from keyboard)
def signal_handler(signalnumber, frame):
    global __stop_gateway
    global __send_wait
    __stop_gateway = True
    __send_wait.set()  # unlock send thread to let it close
    print("stopping gateway (ctrl + c received)")


if __name__ == "__main__":
    print("starting gateway")
    udp_socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

    # prepare listening UDP socket
    try:
        udp_socket.bind(__udp_address)
        print("waiting for IoT devices on port: ", __udp_address[1])
    except IOError as e:
        print("an exception has occured while binding udp socket: ", e)
        exit()

    # create and strt thread for TCP connection
    send_thread = thr.Thread(target=send_to_server)
    # create and start thread for UDP socket listening
    receive_thread = thr.Thread(
        target=receive_from_device, args=(udp_socket,), daemon=True
    )

    # start send and receive threads
    send_thread.start()
    receive_thread.start()

    sig.signal(sig.SIGINT, signal_handler)
    # sig.pause() not working on Windows. replaced by sleep underneath
    while True:
        sleep(3)  # here to check for signals every 3 seconds
        if __stop_gateway:
            udp_socket.close()  # close receive socket
            # wait 3 more seconds if a thread is sending a message to the server
            exit()
