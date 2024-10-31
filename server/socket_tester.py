import socket

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("localhost", 6779))
        while True:
            command = input("Enter command: ")
            if command == "quit":
                break
            if command == "recv":
                print(s.recv(1024).decode())
            else:
                s.sendall(command.encode())
