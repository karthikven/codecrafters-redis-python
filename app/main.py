import socket


def main():

    HOST = "localhost"
    PORT = 6379
    server_socket = socket.create_server((HOST, PORT))
    conn, addr = server_socket.accept()
    conn.send(b"+PONG\r\n")
    conn.close()
        
    # server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    # conn, addr = server_socket.accept() # wait for client
    # print("connected to a client")

    # data = conn.recv(1024)
    # print("Received from client", data.decode())
    # conn.send()

    # conn.close()

if __name__ == "__main__":
    main()
