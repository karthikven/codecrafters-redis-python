import socket


def main():

    HOST = "localhost"
    PORT = 6379
    
    with socket.create_server((HOST, PORT), reuse_port=True) as server_socket:
        conn, _ = server_socket.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(b"+PONG\r\n")

        
        
if __name__ == "__main__":
    main()
