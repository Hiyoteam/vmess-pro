import socket,threading,process_content,base64,logging,json
pwd=""
logging.basicConfig(level=logging.DEBUG)
logger=logging.getLogger("VmessPro")
logger.setLevel(logging.DEBUG)
def serve(h,p):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(("0.0.0.0",p))
    s.listen(5)
    logger.info(f"VmessPro Core v3.0 Started at {h}:{p}")
    logger.info("Use the URL following to connect.")
    url="vmessp://"
    data={"host":h,"port":p,"password":pwd,"protocol":"core"}
    url+=base64.b64encode(json.dumps(data).encode("utf-8")).decode("ascii")
    logger.info(url)
    while 1:
        cli,add=s.accept()
        threading.Thread(target=process_content.newConn,args=(cli,add,pwd)).start()
        
serve("127.0.0.1",8069)