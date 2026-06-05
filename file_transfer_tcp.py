import socket
import os
import sys
import argparse

def start_server(host, port, save_dir='.'):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"TCP Server listening on {host}:{port}")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        
        # Receive filename
        filename_len = int.from_bytes(client_socket.recv(4), 'big')
        filename = client_socket.recv(filename_len).decode('utf-8')
        
        # Receive file size
        file_size = int.from_bytes(client_socket.recv(8), 'big')
        
        # Receive file data
        with open(os.path.join(save_dir, filename), 'wb') as f:
            received = 0
            while received < file_size:
                data = client_socket.recv(4096)
                if not data:
                    break
                f.write(data)
                received += len(data)
        
        print(f"Received file: {filename} ({received} bytes)")
        client_socket.close()

def send_file(host, port, filepath):
    if not os.path.exists(filepath):
        print("File not found")
        return
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    
    # Send filename length and filename
    client_socket.send(len(filename).to_bytes(4, 'big'))
    client_socket.send(filename.encode('utf-8'))
    
    # Send file size
    client_socket.send(file_size.to_bytes(8, 'big'))
    
    # Send file data
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            client_socket.send(data)
    
    print(f"Sent file: {filename} ({file_size} bytes)")
    client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP File Transfer")
    parser.add_argument('--mode', choices=['server', 'client'], required=True)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=9999)
    parser.add_argument('--file', help='File to send (client mode)')
    parser.add_argument('--save_dir', default='.', help='Directory to save received files')
    args = parser.parse_args()
    
    if args.mode == 'server':
        start_server(args.host, args.port, args.save_dir)
    else:
        if not args.file:
            print("Please specify --file for client mode")
        else:
            send_file(args.host, args.port, args.file)
