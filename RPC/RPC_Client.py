import argparse
import inspect
import ipaddress
import socket
from Data_Handle import Message_serialization,Message_deserialization

def client_start():
    note = argparse.ArgumentParser(description= "Client_HELP")     #帮助参数设定
    
    #-i,客户端需要连接的注册中心的 ip 地址，需要同时支持 IPv4 和 IPv6
    note.add_argument('-i', '--ip', help='客户端需要连接的注册中心的 ip 地址，同时支持 IPv4 和 IPv6，不得为空', default= '0.0.0.0')
    
    #-p，客户端需要连接的注册中心的端口号，不得为空
    note.add_argument('-p', '--port', help='客户端需要连接的注册中心的端口号，不得为空', required=True)
    
    args = note.parse_args()
    return args


class RPC_Client(object):
    def __init__(self, registry_host = 'localhost', registry_port = 5000):             #客户端的初始化函数，这里传入了服务器的IP和端口号
        self.register_address = (registry_host, registry_port)
        self.local_func_map = {}  

    def find_service(self, func, args):
        if func in self.local_func_map:
            return self.local_func_map[func]

        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect(self.register_address)
        try:
            print("连接注册中心成功")
            clientSocket.sendall(Message_serialization({'type': 'FindServices', 'service_name' : func, 'args' : args}))
            response = clientSocket.recv(1024)
            clientSocket.close()
            if not response:
                print("未收到有效的数据响应！")
                return None
            else:
                res = Message_deserialization(response)

            if res == 'Failed!':
                print(f"Service {func} not found!")
                return None
            else:        
                server_ip = res['ip']
                server_port = res['port']
                server_address = (server_ip, int(server_port)) 
                self.local_func_map[func] = server_address
                return server_address
        except IOError:
            print("连接注册中心失败！")
            clientSocket.close()
        except KeyboardInterrupt:
            print("强制关闭客户端！")
            clientSocket.close()  

    def client_call_service(self, func, args):
        target_address = self.find_service(func, args)
        if not target_address:
            return None
        #要实现socket既支持IPv4，也支持IPv6操作
        try:
            if ipaddress.ip_address(target_address[0]).version == 4:
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
                clientSocket.connect(target_address)                      #建立TCP连接
            else:
                ipv6 = ipaddress.IPv6Address(target_address[0]).compressed
                clientSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                clientSocket.connect((ipv6, target_address[1])) 

            clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            clientSocket.settimeout(5)
        except ConnectionError as e:
            print("连接服务器失败:{}!".format(e))
            clientSocket.close()
        except TimeoutError:
            print("客户端请求超时，马上关闭连接")
            clientSocket.close()    

        #向服务器请求相关服务
        try:
            demand = Message_serialization({'func':func, 'args':args})      #将方法名以及方法的参数位置均进行序列化
            clientSocket.sendall(len(demand).to_bytes(4, byteorder='big')+demand)
        except Exception as e:
            print("客户端发送请求失败:{}!".format(e))
            clientSocket.close()  

        try:
            #客户端接收返回的信息
            mesg = clientSocket.recv(1024)
            if not mesg:
                clientSocket.close()
                return 
            result = Message_deserialization(mesg[4:4+int.from_bytes(mesg[:4], byteorder='big')])
            print("The result :", result)

        except socket.timeout:
            print("客户端接收服务器信息发生超时异常！")
            clientSocket.close()

        except OSError as e:
            print("客户端接收信息发生读数据异常！{}".format(str(e)))
            clientSocket.close()

        except Exception as e:
            print("客户端接收服务器信息发生的其他异常！{}".format(str(e)))
            clientSocket.close()
        
    
if __name__ == '__main__':
    #args =  client_start() args.ip, int(args.port)
    client = RPC_Client()

    client.client_call_service('Add',1,2)
    client.client_call_service('Mul',1,2)


                                  

        




