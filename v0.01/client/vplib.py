import socket,threading,json,base64,logging
def URLdecoder(url):
    try:
        return json.loads(base64.b64decode(url.replace("vmessp://","")).decode("utf-8"))
    except:
        raise RuntimeError("Invaild VMESSP address")
class Connection:
    def __init__(self,sock):
        self.sock=sock
        self.status="WAITING"
    def recv(self,size=65535):
        data=self.sock.recv(size)
        logging.debug(f"Recived message")
        if not data:
            self.status="CLOSED"
            logging.debug(f"Socket closed")
            return None
        logging.debug(f"Pack content: {data.decode('utf-8').replace('VMESSPRO: NEWPACKAGE??','')}")
        return base64.b64decode(data.decode("utf-8").replace("VMESSPRO: NEWPACKAGE??",""))
    def send(self,content:bytes):
        if self.status!="OPEN":
            raise RuntimeError("Socket operation at a closed socket")
        self.sock.send(("VMESSPRO: SENDTHESEBELOW??"+base64.b64encode(content).decode("utf-8")).encode("utf-8"))
    def connect(self,host,port,password):
        connpayload={"target":host,"port":port,"key":password}
        connpayload=base64.b64encode(json.dumps(connpayload).encode("utf-8")).decode("utf-8").encode("utf-8")
        self.sock.send(connpayload)
        reslt=self.sock.recv(65535)
        reslt=reslt.decode("utf-8")
        if reslt == "VMESSPRO: CONN SUCCESSED":
            self.status="OPEN"
            return True
        else:
            self.status="CLOSED"
            return False
    def fileno(self):
        return self.sock.fileno()
    def close(self):
        self.sock.close()
    def sendall(self,content):
        self.send(content)
class VmessPro:
    def __init__(self,url):
        self.config=URLdecoder(url)
    def connect(self):
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((self.config["host"],self.config["port"]))
        return Connection(sock)

