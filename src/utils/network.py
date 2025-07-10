import socket


def sendPing(host,port,timeout=2):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #presumably 
    sock.settimeout(timeout)
    try:
        sock.connect((host,port))
    except:
        return False
    else:
        sock.close()
        return True

def get_host_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "127.0.0.1"