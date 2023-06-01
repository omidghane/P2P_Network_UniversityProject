import json
import random
import socket
import threading

from PIL import Image
from PIL import *
import numpy as np
import requests

MYPORT = 7447
MYNAME = "omid"
MESSAGE_SIZE = 400
ENCODING = 'utf-8'

peer_address = (0, 0)
accepted_request = False
accepted_request2 = False
accepted_request3 = False

STATE = 0


def main():
    global STATE
    global MYPORT
    global MYNAME
    # global peer_address
    address = socket.gethostbyname(socket.gethostname())
    # MYPORT = int(input("your_port: "))
    MYPORT = random.randint(1,1000)
    MYNAME = input("your_name: ")
    # MYNAME = "qw"
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
        # inp = 2
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
    global accepted_request2
    # global accepted_request
    global accepted_request3
    while True:
        STATE = 1
        con = input("send message? (y/n): ")
        # con = "y"
        if con == "y":
            break

    if not accepted_request:
        userName = input("User_name: ")
        # userName = "as"
        peer_address = find_peerAddress(userName)
        # print(peer_address, " peeradd")
        if not accepted_request:
            # peer_address = (socket.gethostbyname(socket.gethostname()), port)
            my_mess = "REQUEST"
            res = send_message(server, my_mess, peer_address, 1)
            if res == "error":
                return
            # print('request sent')
            while not accepted_request:
                pass

    while True:
        STATE = 5
        choose = input("Data to send: 1)text 2)img\n")
        choose = int(choose)
        try:
            if choose == 1:
                res = send_message(server, "TEXT", peer_address, 1)
                while not accepted_request2:
                    # print("i waitttt")
                    pass
                STATE = 3
                my_mess = input("you: ")
                send_message_tcp(my_mess, peer_address)
            elif choose == 2:
                res = send_message(server, "IMG", peer_address, 1)
                while not accepted_request3:
                    # print("i waitttt")
                    pass
                # STATE = 6
            else:
                print("Invalid option")
        except:
            print("Error: Failed to send message. Please check your connection.")
            continue


def send_message(client, msg, server_address, mode):
    if mode == 1:
        message = msg.encode(ENCODING)
    else:
        message = msg

    try:
        client.sendto(message, server_address)
    except:
        print("(FUNC) Error: Failed to send message. Please check your connection.")
        return "error"


def send_message_tcp(msg, server_address):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        client_socket.sendall(msg.encode(ENCODING))
        client_socket.close()
    except:
        print("Error: Failed to send message. Please check your connection.")
        return "error"


def receive_messages(server, nothing):
    global STATE
    global accepted_request
    global peer_address
    global accepted_request2
    global accepted_request3
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
                send_message(server, "ACCEPTED", address, 1)
                accepted_request = True
                acceptCommunication = True
                peer_address = address
                # print("you accepted the request")
            else:
                send_message(server, "REJECTED", address, 1)
            # print('accepted')

        # if not acceptCommunication:
        while acceptCommunication:
            try:
                message, address = server.recvfrom(MESSAGE_SIZE)
                # print("new message: ", message)
                msg = message.decode(ENCODING)
                if msg == "TEXT":
                    # print("wait for text zzzzzz")
                    send_message(server, "ACCEPTED_TEXT", address, 1)
                    receive_messages_tcp(server, None)
                elif msg == "IMG":
                    send_message(server, "ACCEPTED_IMG", address, 1)
                    # message, address = server.recvfrom(MESSAGE_SIZE)
                    receive_image_udp(server)
                    print("I accepted")
                elif msg == "ACCEPTED_TEXT":
                    # print("he accepted the text")
                    accepted_request2 = True
                    continue
                elif msg == "ACCEPTED_IMG":
                    img_path = "r2zzMxBl_400x400.jpg"
                    img_matrix, width, height = image_to_matrix(img_path)
                    # print(img_matrix, " img_matrix")
                    send_image_udp(server, img_matrix, width, height, peer_address)
                    accepted_request3 = True
                    print("he accepted")
            except:
                print("UDP_Error: Failed to receive message. Please check your connection.")
                continue
            msg = message.decode(ENCODING)
            # print("Message: {}".format(msg))
            if STATE == 0:
                print("1)all_name_users 2)communicate")
                pass
            elif STATE == 1:
                print("send message? (y/n): ", end='')
                pass
            elif STATE == 4:
                print("you: ", end='')
            else:
                print("Data to send: 1)text 2)img")


def receive_messages_tcp(server, nothing):
    global STATE
    global accepted_request
    global peer_address
    global MYPORT

    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind((socket.gethostbyname(socket.gethostname()), MYPORT))
        tcp_socket.listen(1)
        # client_socket.connect(server_address)
        tcp_socket, client_address = tcp_socket.accept()

        msg = tcp_socket.recv(MESSAGE_SIZE).decode(ENCODING)
    except:
        print("Error: Failed to send message. Please check your connection.")
        return "error"
    # client_socket, client_address = server.accept()
    print("Message: {}".format(msg))
    tcp_socket.close()

from numpy import asarray
def image_to_matrix(image_path):

    try:
        image = Image.open(image_path)
        width, height = image.size  # Get the image size
        # matrix = image.convert("L").getdata()
        matrix = asarray(image)
        return matrix, width, height
    except Exception as e:
        print("Error: Failed to convert image to matrix.")
        print(e)
        return None


def receive_image_udp(server):
    message, address = server.recvfrom(MESSAGE_SIZE)
    # matrix_width = int(message.decode(ENCODING))
    m = message.decode(ENCODING)
    matrix_width, matrix_height = m.split("_")
    matrix_width, matrix_height = int(matrix_width), int(matrix_height)
    # print("size received qqqqqqq")

    received_data = b""
    # print(matrix_width * MESSAGE_SIZE, " amount ot receive eeeeeee")
    matrix = np.empty((matrix_width, matrix_height, 3), dtype=np.uint8)

    for i in range(matrix_width):
        print(i)
        chunk_data = b""
        while len(chunk_data) < matrix_height * 3:  # Assuming each pixel has 3 bytes (RGB)
            message, address = server.recvfrom(MESSAGE_SIZE)
            chunk_data += message
            send_message(server, "ACK", address, 1)

        chunk_array = np.frombuffer(chunk_data, dtype=np.uint8).reshape((matrix_height, 3))
        matrix[i] = chunk_array

        # received_data += chunk_data

        # chunk_data = np.frombuffer(received_data, dtype=np.uint8)
        # matrix[i] = chunk_data.reshape(matrix_width, -1)


    try:
        from PIL import Image
        image = Image.fromarray(matrix)
        image.save("received_image.jpg")
        image.show()
    except ImportError:
        print("Error: Pillow library is required to process the received image.")
        return


def send_image_udp(client, matrix, width, height, server_address):
    # matrix_width = width
    send_message(client, str(f"{width}_{height}"), server_address, 1)

    for i in range(0, width):
        for j in range(0, height, int(MESSAGE_SIZE/3)):
            if j+int(MESSAGE_SIZE/3) > height:
                chunk = matrix[i][j:height]
            else:
                chunk = matrix[i][j:j + int(MESSAGE_SIZE/3)]
            chunk_bytes = chunk.tobytes()  # Convert the NumPy array to bytes
            send_message(client, chunk_bytes, server_address, 2)
            response, _ = client.recvfrom(MESSAGE_SIZE)
            if response.decode(ENCODING) != "ACK":
                print("Error: Failed to send image data.")
                return



if __name__ == '__main__':
    main()
