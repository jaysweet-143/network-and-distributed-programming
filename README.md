# Simple File Transfer Application

This project implements a basic file transfer application using Python sockets for the Network and Distributed Programming course.

## Features
- TCP-based reliable file transfer
- UDP-based (with simple reliability via ACKs) file transfer
- Command-line interface for server and client modes

## Files
- `file_transfer_tcp.py`: TCP version for reliable transfer
- `file_transfer_udp.py`: UDP version 
- `test_file.txt`: Sample file

## Usage

### TCP
**Start Server:**
```bash
python3 file_transfer_tcp.py --mode server --port 9999
```

**Send File (in another terminal):**
```bash
python3 file_transfer_tcp.py --mode client --port 9999 --file test_file.txt
```

### UDP
**Start Server:**
```bash
python3 file_transfer_udp.py --mode server --port 9999
```

**Send File:**
```bash
python3 file_transfer_udp.py --mode client --port 9999 --file test_file.txt
```

Files are saved in the current directory on the server side.

## Notes
- For TCP: Uses stream sockets for reliable, ordered delivery.
- For UDP: Datagram sockets with basic acknowledgments to simulate somewhat reliable but demonstrates unreliability potential (e.g., remove ACKs for pure unreliable).
- Run on different machines by changing host IP.
- Synchronization topic can be discussed in context of concurrent file handling if extended to multi-client.

