import inspect
import ipaddress
import time
import threading
import socket

from Data_Handle import Message_deserialization, Message_serialization

class RegisterCenter:
    def __init__(self, host = 'localhost', port = 5000):
        self.function = {}           #初始化一个map用于保存已注册的函数
        self.lock = threading.Lock() #初始化一个锁用于保护map
        self.Reg_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #初始化一个TCP socket
        self.Reg_Socket.bind((host, port)) #绑定socket
        self.Reg_Socket.listen(5)          #开始监听
        print(f"RegisterCenter is listening on {host}:{port}")

    def register(self, service_name, args, address):
        with self.lock:
            self.function[service_name] = {'address' : address,'args': args, 'Live' : time.time()}
            print(f"Succeed to register service {service_name} at {address}")
    
    def get_service(self, service_name, arg):
        with self.lock:
            if service_name in self.function:
                expected_args = self.function[service_name]['args']
                if len(arg) == len(expected_args):
                    try:
                        for putin, now in zip(arg, expected_args):
                            putin_type = type(putin)

                            now_type = now.annotation if hasattr(now, 'annotation') else None

                            if now_type is not None and now_type != putin_type:
                                raise TypeError("参数类型不匹配，期望参数类型{}，实际参数类型{}".format(now_type.__name__, putin_type))
                        return self.function.get(service_name,{}).get('address',None)

                    except TypeError as e:
                        print("数据参数类型不匹配，调用方法失败！{}".format(str(e)))
                        return None

                    except Exception as e:
                        print("函数执行失败！{}".format(str(e)))
                        return None
                else:
                    result = '调用{};参数个数不匹配，期望参数个数{}，实际参数个数{}'.format(service_name, len(expected_args), len(arg))
                    print(result)
                    return None
            else:
                result = '调用{}函数不存在'.format(service_name)
                print(result)
                return None
                        
        
    def handle_request(self, targetSocket):
        with targetSocket:
            message = targetSocket.recv(1024)
            mesg = Message_deserialization(message)
            if mesg['type'] == 'register':
                self.register(mesg['service_name'], mesg['args'] ,(mesg['ip'], int(mesg['port'])))
                targetSocket.sendall(Message_serialization("RegisterCenter response: Registe Success"))
            elif mesg['type'] == 'FindServices':
                address = self.get_service(mesg['service_name'], mesg['args'])
                if address:
                    targetSocket.sendall(Message_serialization({'ip': address[0], 'port': address[1]}))
                else:
                    targetSocket.sendall(Message_serialization("Failed!"))
            else:
                self.heart(mesg['service_name'])
                targetSocket.sendall(Message_serialization("RegisterCenter response: Heart Success"))
            
    def heart(self, service_name):
        with self.lock:
            if service_name in self.function:
                self.function[service_name]['Live'] = time.time()
                print(f"{service_name} is alive")

    def remove_dead(self, timeout = 30):
        while True:
            time.sleep(timeout)
            with self.lock:
                dead_services = [service_name for service_name in self.function if time.time() - self.function[service_name]['Live'] > timeout]
                for service_name in dead_services:
                    print(f"{service_name} is dead")
                    del self.function[service_name]

    def start(self):
        threading.Thread(target=self.remove_dead, daemon=True).start()
        while True:
            targetSocket, address = self.Reg_Socket.accept()
            threading.Thread(target=self.handle_request, args=(targetSocket,)).start()

if __name__ == '__main__':
    register = RegisterCenter()
    register.start()