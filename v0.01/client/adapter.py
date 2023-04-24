import socket,select,vplib
def handle_request(client,url):
    # 接受客户端发来的数据，即请求头
    header = client.recv(1024)
    # 解析请求头
    version = header[0]
    if version != 5:
        return
    n_methods = header[1]
    methods = header[2:]
    if 0 not in methods:
        return
    # 向客户端发送响应，选择支持的验证方式为0，即无需验证
    response = b'\x05\x00'
    client.sendall(response)
    # 接受客户端发来的连接请求，即连接头
    header = client.recv(1024)
    # 解析连接头
    version, cmd, _, address_type = header[:4]
    if version != 5:
        return
    if cmd != 1:
        return
    if address_type == 1:  # IPv4地址
        address = socket.inet_ntoa(header[4:8])
        port = int.from_bytes(header[8:10], byteorder='big')
    elif address_type == 3:  # 域名
        address_length = header[4]
        address = header[5:5+address_length].decode()
        port = int.from_bytes(header[5+address_length:7+address_length], byteorder='big')
    else:
        return
    # 向客户端发送响应，表示连接成功
    response = b'\x05\x00\x00\x01' + socket.inet_aton('0.0.0.0') + b'\x00\x00'
    client.sendall(response)
    # 连接目标主机
    serverr = vplib.VmessPro(url)
    server=serverr.connect()
    server.connect(address, port,"")
    # 开始转发数据
    while True:
        r, w, e = select.select([client, server], [], [])
        if client in r:
            data = client.recv(4096)
            if not data:
                break
            server.sendall(data)
        if server in r:
            data = server.recv(4096)
            if not data:
                break
            client.sendall(data)
    # 关闭连接
    client.close()
    server.close()

def run_server(url,host='localhost', port=1080):
    # 创建服务器套接字
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(128)
    print(f'Listening VMESSPRO Client on {host}:{port}...')
    # 循环接受连接请求
    while True:
        client, address = server.accept()
        print(f'Accepted connection from {address}')
        handle_request(client,url)


