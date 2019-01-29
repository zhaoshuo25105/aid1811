

'''htp文件服务器程序
    fork server训练'''
from socket import * 
import os,sys,time

#全局变量
HOST = "0.0.0.0"
PORT = 8888
ADDR = (HOST,PORT)

#路径名
FILES ="/home/tarena/test/"

#将文件处理
class Ftpserver(object):
    def __init__(self,connfd):
        self.connfd = connfd

    def do_list(self):
        print("执行list")
        #获取文件列表
        file_list = os.listdir(FILES)
        if not file_list:
            self.connfd.send("文件库为空".encode())
            return 
        else:
            self.connfd.send(b"ok")
            time.sleep(0.1)

        files =""
        for file in file_list:

            if file[0] != "." and os.path.isfile(FILES+file):  
                #过滤普通文件 os.path.isfile()
                
                files = files + file + "#"
        
        #将拼接好的文件字符串发送
        self.connfd.send(files.encode())

    def do_get(self,filename):
        #判断是否存在
        try:
            fd = open(FILES+filename,"rb")
        except Exception:
            self.connfd.send("文件不存在".encode())
            return
        self.connfd.send(b"ok")
        time.sleep(0.1)

        #发送文件内容
        while True:
            data = fd.read(1024)
            #到文件结尾
            if not data :
                time.sleep(0.1)
                self.connfd.send(b"##")
                break
            self.connfd.send(data)

    #判断文件是否存在，要是没有就可以上传
    def do_put(self,filename):


        if filename in os.listdir(FILES):
            self.connfd.send("文件存在，请您换个名字：".encode())
            return
        else:
            self.connfd.send("ok".encode())
            try:
                fw = open(FILES+filename,"wb")
                while True:
                    data = self.connfd.recv(1024)
                    if data == b"##":
                        break
                    fw.write(data)
                fw.close()
            except Exception:
                print("文件打开失败")



#封装并发网络模型
def main():
    #创建套接字
    sockfd = socket()
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    sockfd.bind(ADDR)
    sockfd.listen(5)
    print("listen to the port 8888....")

    while True:
        try:
            connfd,addr = sockfd.accept()
        except KeyboardInterrupt:
            sockfd.close()
            sys.exit("服务器退出")
        except Exception as e :
            print("服务器异常：",e)
            continue 
        print("连接客户端:",addr)

#创建子进程处理客户端请求
        pid = os.fork()
        
        if pid == 0:
            p = os.fork()
            if p == 0:
                #把套接字关闭　用不到这个套接字　他只负责接收
                sockfd.close()
                #根据客户端请求执行操作
                ftp = Ftpserver(connfd)   #创建对象

                while True:
                    #接收请求
                    data = connfd.recv(1024).decode()

                    #客户端发出退出请求
                    if not data or data[0] == "Q":
                        connfd.close()
                        sys.exit("客户端退出")

                    #接收客户端查找文件的请求
                    elif data[0] == "L":
                        ftp.do_list()

                    #接收客户端下载请求
                    elif data[0] == "G":
                        filename = data.split(" ")[-1]
                        ftp.do_get(filename)

                    #接收客户端上传请求
                    elif data[0] == "P":
                        #解析文件名字 filename就是文件名
                        filename = data.split(" ")[-1]
                        ftp.do_put(filename)

            else:
                os._exit(0)
        else:
            #把连接套接字关闭　用不到这个，他只用到套接字
            connfd.close()
            os.wait()   #回收子进程
main()