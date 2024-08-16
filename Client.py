import wx  # 导入 wxPython 库，用于创建图形用户界面
from socket import socket, AF_INET, SOCK_STREAM  # 导入 socket 相关模块，用于网络通信
import threading  # 导入 threading 模块，用于多线程处理


class Client(wx.Frame):  # 定义一个 Client 类，继承自 wx.Frame（窗口类）
    def __init__(self, server_ip, server_port):  # 构造函数，初始化类实例
        super().__init__(None, title="客户端", pos=wx.DefaultPosition, size=(800, 600))  # 调用父类构造函数，创建窗口

        # 创建面板和垂直布局
        self.receive_thread = None  # 初始化接收线程为 None
        panel = wx.Panel(self)  # 创建一个面板，用于放置控件
        main_sizer = wx.BoxSizer(wx.VERTICAL)  # 创建一个垂直布局管理器

        # 创建显示文本框
        self.show_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)  # 创建一个多行只读的文本框用于显示接收到的消息
        main_sizer.Add(self.show_text, 1, wx.EXPAND | wx.ALL, 5)  # 将显示文本框添加到布局中

        # 创建发送文本框
        self.send_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE)  # 创建一个多行文本框用于输入要发送的消息
        main_sizer.Add(self.send_text, 2, wx.EXPAND | wx.ALL, 5)  # 将发送文本框添加到布局中

        # 创建操作按钮区域
        action_button_sizer = wx.BoxSizer(wx.HORIZONTAL)  # 创建一个水平布局管理器
        send_but = wx.Button(panel, label='Send')  # 创建“发送”按钮
        connect_but = wx.Button(panel, label='Connect')  # 创建“连接”按钮
        disconnect_but = wx.Button(panel, label='Disconnect')  # 创建“断开”按钮
        action_button_sizer.Add(connect_but, 0, wx.ALL, 5)  # 将连接按钮添加到按钮区域布局中
        action_button_sizer.Add(disconnect_but, 0, wx.ALL, 5)  # 将断开按钮添加到按钮区域布局中
        action_button_sizer.Add(send_but, 0, wx.ALL, 5)  # 将发送按钮添加到按钮区域布局中
        main_sizer.Add(action_button_sizer, 0, wx.ALIGN_CENTER)  # 将按钮区域布局添加到主布局中

        panel.SetSizer(main_sizer)  # 设置面板的布局管理器为主布局
        main_sizer.Fit(self)  # 使布局适应窗口大小

        # 初始化服务器连接信息
        # TCP通信需要提供服务器的IP（定位主机），端口号（定位程序）
        self.server_ip = server_ip  # 服务器 IP 地址
        self.server_port = server_port  # 服务器端口号
        self.client_socket = None  # 初始化连接的套接字为 None
        self.is_connected = False  # 连接状态，初始为未连接

        # 绑定事件
        connect_but.Bind(wx.EVT_BUTTON, self.connect_to_server)  # 绑定“连接”按钮点击事件到 connect_to_server 方法
        disconnect_but.Bind(wx.EVT_BUTTON, self.disconnect_from_server)  # 绑定“断开”按钮点击事件到 disconnect_from_server 方法
        send_but.Bind(wx.EVT_BUTTON, self.send_message)  # 绑定“发送”按钮点击事件到 send_message 方法

    def connect_to_server(self, event):  # 处理连接到服务器的逻辑
        if not self.is_connected:  # 如果当前未连接
            try:
                self.client_socket = socket(AF_INET, SOCK_STREAM)  # 创建一个 TCP 套接字
                self.client_socket.connect((self.server_ip, self.server_port))  # 尝试连接到服务器
                self.is_connected = True  # 设置连接状态为 True
                self.show_text.AppendText("连接到服务器...\n")  # 在显示文本框中添加连接成功的消息
                # 启动接收消息的线程
                self.receive_thread = threading.Thread(target=self.receive_messages)  # 创建一个线程，用于接收消息

                # 通过设置 self.receive_thread.daemon = True，将 self.receive_thread 线程标记为守护线程。
                # 这意味着该线程在主线程（或者所有非守护线程）退出时会被自动终止。这样，主线程不会因为守护线程未完成工作而阻塞退出。
                self.receive_thread.daemon = True  # 设置线程为守护线程

                self.receive_thread.start()  # 启动接收消息的线程
            except Exception as e:
                self.show_text.AppendText(f"连接失败: {str(e)}\n")  # 如果连接失败，显示错误信息

    def disconnect_from_server(self, event):  # 处理断开服务器连接的逻辑
        if self.is_connected:  # 如果当前已连接
            self.is_connected = False  # 设置连接状态为 False
            self.client_socket.close()  # 关闭套接字连接
            self.show_text.AppendText("断开连接\n")  # 在显示文本框中添加断开连接的消息

    def send_message(self, event):  # 处理发送消息的逻辑
        if self.is_connected:  # 如果当前已连接
            message = self.send_text.GetValue()  # 获取发送文本框中的消息
            self.client_socket.sendall(message.encode('ascii'))  # 发送消息到服务器
            self.show_text.AppendText(f"发送: {message}\n")  # 在显示文本框中添加发送的消息
            self.send_text.SetValue("")  # 清空发送文本框

    def receive_messages(self):  # 处理接收消息的逻辑
        while self.is_connected:  # 当连接状态为 True 时持续接收消息
            try:
                message = self.client_socket.recv(1024).decode('ascii')  # 接收最多 1024 字节的消息并解码
                if message:  # 如果接收到的消息不为空
                    self.show_text.AppendText(f" {message}\n")  # 在显示文本框中添加接收到的消息
                else:
                    self.disconnect_from_server(None)  # 如果消息为空，断开连接
                    break  # 退出循环
            except Exception as e:
                self.show_text.AppendText(f"接收错误: {str(e)}\n")  # 如果接收过程中发生错误，显示错误信息
                self.disconnect_from_server(None)  # 断开连接
                break  # 退出循环


if __name__ == '__main__':  # 如果是直接运行该脚本
    app = wx.App(False)  # 创建一个 wxPython 应用程序实例
    client = Client('127.0.0.1', 8888)  # 创建一个 Client 实例，指定服务器的 IP 和端口号
    client.Show()  # 显示窗口
    app.MainLoop()  # 启动事件循环，等待用户操作