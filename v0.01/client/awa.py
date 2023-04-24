import requests,time
stt=time.time()
print(requests.get("http://httpbin.org/ip",proxies={"http":"socks5://localhost:1080"}).text)
edt=time.time()
print((edt-stt)*1000)
stt=time.time()
print(requests.get("http://httpbin.org/ip").text)
edt=time.time()
print((edt-stt)*1000)