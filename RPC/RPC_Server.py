import argparse
from concurrent.futures import ThreadPoolExecutor
import inspect
import ipaddress
import json
from socket import *
import threading
import time
from Server_Function import *
from Data_Handle import Message_deserialization,Message_serialization

def server_start():
    parse = argparse.ArgumentParser(description= "SERVER_HELP")     #帮助参数设定
    
    #-l，服务端监听的 ip 地址，需要同时支持 IPv4 和 IPv6，可以为空，默认监听所有 ip 地址，即 0.0.0.0
    parse.add_argument('-l', '--listen', help='服务端监听的 ip 地址，同时支持 IPv4 和 IPv6，默认监听0.0.0.0', default= '0.0.0.0')
    
    #-p，服务端监听的端口号，不得为空
    parse.add_argument('-p', '--port', help='服务端监听的端口号，不得为空', required=True)
    
    return parse.parse_args()

class RPC_Server:
    def __init__(self, ip , prot, register_host = 'localhost', register_port = 5000, max = 10):
        self.register_address = (register_host, register_port)
        self.max =ThreadPoolExecutor(max)
        self.func = {}
        self.address = (ip, prot)
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        #在这里加是不是IPv6的判断
        self.server_socket.bind(self.address)
        self.server_socket.listen(5)


        
    def server_register(self, function):    #服务注册，将服务在服务器上注册，使得客户端可以调用该方法
        self.func[function.__name__] = function
        args = [(param.name, param.annotation.__name__ if param.annotation != inspect.Parameter.empty else 'str')
                for param in inspect.signature(function).parameters.values()]
        self.server_running(Message_serialization({'type' : 'register','service_name':function.__name__, 'args':args, 'ip':self.address[0], 'port':self.address[1]}))
        threading.Thread(target=self.start_heartbeat, args=(function.__name__,), daemon=True).start()


    def start_heartbeat(self, func):         
        while True:
            print(f"{func}发送心跳包")
            self.server_running(Message_serialization({'type':'heartbeat','service_name': func ,'ip':self.address[0], 'port':self.address[1]}))
            time.sleep(10)

        
    
    def server_for_client(self, socket):
        socket.settimeout(5)
        try:
            message = socket.recv(1024)

        except TimeoutError:
            print("请求超时！马上将关闭连接")
            socket.close()
        except Exception as e:
            print("服务器请求数据失败！{}".format(e))
            socket.close()

        if not message:
            socket.close()
            return
        
        len = int.from_bytes(message[:4], byteorder='big')
        mesg = Message_deserialization(message[4:4+len])
        function = mesg['func']
        args = mesg['args']
        result = '调用{};结果为{}'.format(function, self.func[function](*args))

        try:
            rlt = Message_serialization({'result':result})
            socket.sendall(len(rlt).to_bytes(4, byteorder='big') + rlt)

        except timeout:
            print("发送数据超时！")
            socket.close()
        except Exception as e:
            print("服务器发送数据超时！{}".format(e))
            socket.close()


    def server_running(self, message):
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)           #设置端口重用
        serverSocket.connect(self.register_address)
        try:
            serverSocket.sendall(message)
            respone = serverSocket.recv(1024)
            if respone:
                try:
                    res = Message_deserialization(respone)
                    print(res)
                except json.JSONDecodeError as e:
                    print("注册中心返回数据错误！{}".format(e))
            #self.server_for_client(clientSocket)
            else:
                print("注册中心返回数据为空")
        except IOError:
            serverSocket.close()
        except KeyboardInterrupt:
            serverSocket.close()
            print("强制关闭服务器")

    def start(self):
        while True:
            clientSocket, addr = self.server_socket.accept()
            self.max.submit(self.server_for_client, clientSocket)



if __name__ =='__main__':
    # args = server_start()
    # ip = args.listen
    # port = args.port ip, int(port)

    server = RPC_Server('172.27.19.243', 5000)
    server.server_register(Add)
    server.server_register(Mul)
    server.server_register(Minus)
    server.server_register(Square)
    server.server_register(Cube)
    server.server_register(Takeover)
    server.server_register(Division)
    server.server_register(Sum)
    server.server_register(Max)
    server.server_register(Sort)

    server.start()
