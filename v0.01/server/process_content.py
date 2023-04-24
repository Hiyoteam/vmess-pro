import hashlib,time,json,base64,logging,socket,threading
def doubleProcess(cli,add,target):
    logging.info(f"Connecting to: {target['target']}:{target['port']}")
    ser=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        #if the connect failed, whole the serving process will crash so we add a 'try' segment
        ser.connect((target['target'],target['port']))
    except:
        #connect failed...
        logging.info(f"Connecting to: {target['target']}:{target['port']} failed.")
        cli.send("VMESSPRO: CONN FAILED".encode("utf-8"))
        return
    #woa, successed lets start the processes -.-
    logging.info(f"Connecting to: {target['target']}:{target['port']} successed.")
    cli.send("VMESSPRO: CONN SUCCESSED".encode("utf-8"))
    #start the process of receiving data from the server and sending
    threading.Thread(target=ser2cli,args=(cli,add,ser,target)).start()
    threading.Thread(target=cli2ser,args=(cli,add,ser,target)).start()

def cli2ser(cli,add,ser,target):
    logging.info(f"ClientToServer data transfering process for {add} started")
    while 1:
        try:
            data=cli.recv(65535)
        except:
            logging.debug("Force-closed, closeing")
            return
        if not data:
            ser.close()
            break
        try:
            data=data.decode("utf-8")
        except:
            logging.info("Got an invaild data from client")
            ser.close()
            cli.close()
            break
        #prase command
        if data.split("??")[0] == "VMESSPRO: SENDTHESEBELOW":
            #send the data to server
            ser.send(base64.b64decode(data.split("??")[1]))
def ser2cli(cli,add,ser,target):
    logging.info(f"ServerToClient data transfering process for {add} started")
    while 1:
        try:
            data=ser.recv(65535)
        except:
            logging.debug("Force-closed, exiting")
            return
        if not data:
            cli.close()
            break
        payload="VMESSPRO: NEWPACKAGE??"+base64.b64encode(data).decode("ascii")
        cli.send(payload.encode("utf-8"))
def decodePackage(pack:bytes,pwd:str,add,cli):
    logging.info(f"Accepted new connection request from {add}")
    # decode the package content
    try:
        pack=json.loads(base64.b64decode(pack.decode('utf-8')).decode("utf-8"))
    except:
        return False  # Cannot got the pack content
    content={}
    try:
        content.update({"target":pack["target"]})
        content.update({"port":pack['port']})
        pack["key"]
    except:
        return False #has no the key
    # check the content is valid
    if content['target']=='' or content['port']=='':
        return False # the content is invalid
    if type(content['port']) != int:
        return False #invaild port
    if content['port']<1 or content['port']>65535:
        return False #invaild port
    #check the key
    if pwd != pack["key"]:
        return False #Invaild key
    logging.info("New connection to %s:%d"%(content['target'],content['port']))
    doubleProcess(cli,add,content)
    return True
    
def newConn(cli,add,pwd):
    data=cli.recv(65535)
    if not data:
        cli.close()
    if not decodePackage(data,pwd,add,cli):
        cli.close()