import json
import socket
import threading

import requests

MYPORT = 7447
MYNAME = "omid"
MESSAGE_SIZE = 64
ENCODING = 'utf-8'

peer_address = (0, 0)
accepted_request = False

STATE = 0


def main():
    global STATE
    global MYPORT
    global MYNAME
    # global peer_address
    address = socket.gethostbyname(socket.gethostname())
    MYPORT = int(input("your_port: "))
    MYNAME = input("your_name: ")
    host = (address, MYPORT)
    print(host, "MyPort")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(host)

    res = adding_to_network()
    if res == "fail":
        return

    listen(s)

    while (True):
        STATE = 0
        inp = input("1)all_name_users 2)communicate\n")
        if int(inp) == 1:
            namePeers_GET()
        elif int(inp) == 2:
            communication(s)


def listen(server):
    t = threading.Thread(target=receive_messages, args=(server, None))
    t.start()


def adding_to_network():
    url = 'http://localhost:8000/api/data'
    data = {
        'id': MYNAME,
        'address': str(MYPORT) + '_' + socket.gethostbyname(socket.gethostname()),
    }

    headers = {'Content-type': 'application/json'}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        print('User stored successfully.')
        return "ok"
    else:
        print('Failed to store user. Error:', response.text)
        return "fail"


def namePeers_GET():
    url = 'http://localhost:8000/api/data'
    data = {

    }
    headers = {'Content-type': 'application/json'}
    response = requests.get(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        for name in response:
            print(name)


def communication(server):
    # t = threading.Thread(target=receive_messages, args=(server, None))
    # t.start()

    # request_connection(server)

    communicate(server)


def find_peerAddress(username):
    url = 'http://localhost:8000/api/data/address/'
    data = {
        'id': username,
    }
    headers = {'Content-type': 'application/json'}
    response = requests.get(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        data = response.content.decode()
        port = data.replace('"', '')
        port = port.split("_")
        # if isinstance(port[1], int):
    else:
        port = None
    return port[1], int(port[0])


def communicate(server):
    global STATE
    global peer_address
    # global accepted_request
    while True:
        STATE = 1
        con = input("send message? (y/n): ")
        if con == "y":
            break

    if not accepted_request:
        userName = input("User_name: ")
        peer_address = find_peerAddress(userName)
        print(peer_address, " peeradd")
        if not accepted_request:
            # peer_address = (socket.gethostbyname(socket.gethostname()), port)
            my_mess = "REQUEST"
            res=send_message(server, my_mess, peer_address)
            if res == "error":
                return
            # print('request sent')
            while not accepted_request:
                pass

    while True:
        STATE = 3
        my_mess = input("you: ")
        try:
            send_message(server, my_mess, peer_address)
        except:
            print("Error: Failed to send message. Please check your connection.")
            continue


def send_message(client, msg, server_address):
    message = msg.encode(ENCODING)

    msg_length = len(message)
    msg_length = str(msg_length).encode(ENCODING)
    msg_length += b' ' * (MESSAGE_SIZE - len(msg_length))

    try:
        client.sendto(message, server_address)
    except:
        print("Error: Failed to send message. Please check your connection.")
        return "error"


def receive_messages(server, nothing):
    global STATE
    global accepted_request
    global peer_address
    acceptCommunication = False
    while (True):

        message, address = server.recvfrom(MESSAGE_SIZE)
        msg = message.decode(ENCODING)
        if msg == "ACCEPTED":
            accepted_request = True
            acceptCommunication = True
            print("\nConnection is accepted from {}\n".format(address))
        elif msg == "REJECTED":
            print("\nConnection is rejected from {}\n".format(address))

        elif address[1] != peer_address[1] and peer_address[1] == 0 and msg == "REQUEST":
            # answer = input("do you accept {} (y,n)? ".format(address[1]))
            answer = 'y'
            if answer == 'y':
                send_message(server, "ACCEPTED", address)
                accepted_request = True
                acceptCommunication = True
                peer_address = address
            else:
                send_message(server, "REJECTED", address)
            # print('accepted')

        # if not acceptCommunication:
        while acceptCommunication:
            try:
                message, address = server.recvfrom(MESSAGE_SIZE)
            except:
                print("Error: Failed to receive message. Please check your connection.")
                continue
            print("\nConnection is started from {}".format(address))
            msg = message.decode(ENCODING)
            print("Message: {}".format(msg))
            if STATE == 0:
                print("1)all_name_users 2)communicate")
            elif STATE == 1:
                print("send message? (y/n): ", end='')
            else:
                print("you: ", end='')
            # if msg == "DISCONNECTED":
            #     server.close()


if __name__ == '__main__':
    main()
