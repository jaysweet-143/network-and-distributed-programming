import socket
import os
import sys
import argparse

CHUNK_SIZE = 4096
TIMEOUT = 5  # seconds for unreliable feel, but we'll add simple ACK

def start_server(host, port, save_dir='.'):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"UDP Server listening on {host}:{port}")
    
    while True:
        # Receive filename
        data, addr = server_socket.recvfrom(CHUNK_SIZE)
        filename = data.decode('utf-8')
        print(f"Receiving file: {filename} from {addr}")
        
        # Send ACK for filename
        server_socket.sendto(b'ACK', addr)
        
        # Receive file size
        data, addr = server_socket.recvfrom(CHUNK_SIZE)
        file_size = int(data.decode('utf-8'))
        server_socket.sendto(b'ACK', addr)
        
        # Receive file data
        with open(os.path.join(save_dir, filename), 'wb') as f:
            received = 0
            while received < file_size:
                data, addr = server_socket.recvfrom(CHUNK_SIZE)
                if data == b'END':
                    break
                f.write(data)
                received += len(data)
                server_socket.sendto(b'ACK', addr)  # Simple ACK
        
        print(f"Received file: {filename} ({received} bytes)")
        
def send_file(host, port, filepath):
    if not os.path.exists(filepath):
        print("File not found")
        return
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    
    # Send filename
    client_socket.sendto(filename.encode('utf-8'), (host, port))
    # Wait for ACK
    client_socket.settimeout(TIMEOUT)
    try:
        data, addr = client_socket.recvfrom(CHUNK_SIZE)
    except socket.timeout:
        print("Timeout on filename ACK")
        return
    
    # Send file size
    client_socket.sendto(str(file_size).encode('utf-8'), (host, port))
    try:
        data, addr = client_socket.recvfrom(CHUNK_SIZE)
    except socket.timeout:
        print("Timeout on size ACK")
        return
    
    # Send file data
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
            client_socket.sendto(data, (host, port))
            try:
                ack, addr = client_socket.recvfrom(CHUNK_SIZE)
            except socket.timeout:
                print("Timeout on chunk ACK, retrying...")
                # Simple retry once
                client_socket.sendto(data, (host, port))
    
    # Send END
    client_socket.sendto(b'END', (host, port))
    print(f"Sent file: {filename} ({file_size} bytes)")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP File Transfer")
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
