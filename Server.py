import threading  # 导入线程模块，允许使用多线程功能
import wx  # 导入wxPython库，用于创建图形用户界面
from socket import socket, AF_INET, SOCK_STREAM  # 导入socket库以进行网络通信


class Server(wx.Frame):  # 创建Server类，继承自wx.Frame
    def __init__(self, server_name):  # 初始化方法，接收服务器名称作为参数
        super().__init__(None, title=server_name, pos=wx.DefaultPosition, size=(1200, 1000))  # 调用父类构造函数设置窗口标题和大小

        # 创建面板和垂直布局
        panel = wx.Panel(self)  # 创建一个面板
        main_sizer = wx.BoxSizer(wx.VERTICAL)  # 创建一个垂直的sizer以管理布局

        # 创建按钮区域
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)  # 创建一个水平的sizer以排列按钮
        self.con_but = wx.Button(panel, label='启动服务器')  # 创建“启动服务器”按钮
        self.dis_but = wx.Button(panel, label='停止服务器')  # 创建“停止服务器”按钮
        button_sizer.Add(self.con_but, 0, wx.ALL, 5)  # 将启动按钮添加到水平sizer中
        button_sizer.Add(self.dis_but, 0, wx.ALL, 5)  # 将停止按钮添加到水平sizer中
        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)  # 将按钮区域添加到主sizer中，并居中显示

        # 创建显示文本框
        self.show_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)  # 创建一个多行只读文本框以显示信息
        main_sizer.Add(self.show_text, 1, wx.EXPAND | wx.ALL, 5)  # 将显示文本框添加到主sizer中，并允许扩展

        # 创建发送文本框
        self.send_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE)  # 创建一个多行文本框以输入消息
        main_sizer.Add(self.send_text, 2, wx.EXPAND | wx.ALL, 5)  # 将发送文本框添加到主sizer中，并允许扩展

        # 创建操作按钮区域
        action_button_sizer = wx.BoxSizer(wx.HORIZONTAL)  # 创建一个水平sizer以排列发送和重置按钮
        reset_but = wx.Button(panel, label='Reset')  # 创建“重置”按钮
        action_button_sizer.Add(reset_but, 0, wx.ALL, 5)  # 将重置按钮添加到操作按钮区域
        main_sizer.Add(action_button_sizer, 0, wx.ALIGN_CENTER)  # 将操作按钮区域添加到主sizer中，并居中显示

        panel.SetSizer(main_sizer)  # 为面板设置布局
        main_sizer.Fit(self)  # 自动调整窗口大小以适应布局中的内容

        # 初始化连接状态和服务器套接字
        self.is_on = False  # 设置服务器初始状态为“关”
        self.host_port = ('127.0.0.1', 8888)  # 定义服务器主机地址和端口
        self.server_socket = socket(AF_INET, SOCK_STREAM)  # 创建一个TCP套接字
        self.server_socket.bind(self.host_port)  # 将套接字绑定到指定的主机和端口
        self.server_socket.listen(5)  # 开始监听连接请求，最多允许5个未处理的连接
        self.session_threads = []  # 用于存储所有客户端处理的线程
        self.clients = []  # 存储所有连接的客户端
        self.lock = threading.Lock()  # 创建线程锁以确保线程安全

        # 绑定事件
        self.con_but.Bind(wx.EVT_BUTTON, self.start_server)  # 将“启动服务器”按钮事件绑定到start_server方法
        self.dis_but.Bind(wx.EVT_BUTTON, self.stop_server)  # 将“停止服务器”按钮事件绑定到stop_server方法
        reset_but.Bind(wx.EVT_BUTTON, self.reset_text)  # 将“重置”按钮事件绑定到reset_text方法

    def start_server(self, event):  # 启动服务器的方法
        if not self.is_on:  # 如果服务器未启动
            self.is_on = True  # 将状态设置为“开”
            self.server_socket.listen(5)  # 开始监听连接请求
            self.show_text.AppendText("服务器启动...\n")  # 在文本框中显示服务器启动信息
            self.accept_thread = threading.Thread(target=self.accept_connections)  # 创建一个线程用于接受连接,不断循环以接受访问请求
            self.accept_thread.daemon = True  # 将线程设置为守护线程
            self.accept_thread.start()  # 启动线程

    def accept_connections(self):  # 接受连接的方法
        while self.is_on:  # 当服务器状态为“开”
            client_socket, client_address = self.server_socket.accept()  # 接受客户端连接
            self.clients.append(client_socket)  # 将客户端套接字添加到客户端列表中
            self.show_text.AppendText(f"连接来自 {client_address}\n")  # 在文本框中显示连接信息
            connected="connected !"
            client_socket.send(connected.encode('ascii'))
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))  # 创建一个线程处理该客户端
            client_thread.daemon = True  # 将线程设置为守护线程
            client_thread.start()  # 启动线程
            self.session_threads.append(client_thread)  # 将客户端线程添加到线程列表中

    def handle_client(self, client_socket, client_address):  # 处理客户端通信的方法
        while self.is_on:  # 当服务器状态为“开”
            try:
                message = client_socket.recv(1024).decode('ascii')  # 从客户端接收消息并解码
                print(message)  # 打印收到的消息
                print(client_address)  # 打印客户端地址
                if message:  # 如果消息不为空
                    self.show_text.AppendText(f"客户端: {message}\n")  # 在文本框中显示客户端消息
                    self.send_message(f"{client_address}:{message}")  # 发送消息到所有连接的客户端
                else:
                    break  # 如果消息为空，退出循环
            except Exception as e:  # 捕获异常
                self.show_text.AppendText(f"发生错误: {str(e)}\n")  # 在文本框中显示错误信息
                break  # 退出循环

        self.clients.remove(client_socket)  # 从客户端列表中移除该客户端
        client_socket.close()  # 关闭客户端套接字

    def stop_server(self, event):  # 停止服务器的方法
        if self.is_on:  # 如果服务器正在运行
            self.is_on = False  # 将状态设置为“关”
            self.server_socket.close()  # 关闭服务器套接字
            self.show_text.AppendText("服务器已停止\n")  # 在文本框中显示服务器已停止信息
            for t in self.session_threads:  # 遍历所有客户端线程
                t.join()  # 等待线程完成

    def reset_text(self, event):  # 重置文本框的方法
        self.show_text.SetValue("")  # 清空显示文本框内容

    def send_message(self, message):  # 发送消息的方法
        # 使用线程锁确保线程安全
        for client in self.clients:  # 遍历所有连接的客户端
            try:
                client.send(message.encode('ascii'))  # 将消息编码为字节并发送给客户端
            except Exception as e:  # 捕获异常
                self.show_text.AppendText(f"发送消息失败: {e}\n")  # 在文本框中显示失败信息
        # 更新UI
        self.show_text.AppendText(f"发送: {message}\n")  # 在文本框中显示发送的消息
        self.send_text.SetValue("")  # 清空发送文本框内容


if __name__ == '__main__':  # 主程序入口
    app = wx.App(False)  # 创建wxPython应用程序
    server = Server('Server')  # 实例化Server类，传入窗口标题
    server.Show()  # 显示服务器窗口
    app.MainLoop()  # 启动事件循环，等待用户操作