# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QTimer, QUrl, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QMainWindow
from PySide6.QtSerialBus import QCanBus, QCanBusDevice, QCanBusFrame

from connectdialog import ConnectDialog
from canbusdeviceinfodialog import CanBusDeviceInfoDialog
from ui_mainwindow import Ui_MainWindow
from receivedframesmodel import ReceivedFramesModel


# 如果 frame 具有 hasBitrateSwitch 和 hasLocalEcho 属性，
# 那么调用 frame_flags(frame) 将返回字符串 " BL- "。

# 该字符串表示 frame 具有比特率切换和本地回显的标志。
def frame_flags(frame):
    result = " --- "
    if frame.hasBitrateSwitch():
        # result[1] = 'B' # 区分CAN 还是 CAN-FD
        result = list(result)
        result[1] = 'B'
        result = ''.join(result)
    if frame.hasErrorStateIndicator():
        result = list(result)
        result[2] = 'E'
        result = ''.join(result)
        # result[2] = 'E' # 通过错误状态指示器来提醒通信节点发现问题
    if frame.hasLocalEcho():
        result[3] = 'L' # 输入后 立即看到屏幕显示（默认开启，但 在输入敏感信息（如密码）时，为了安全性考虑（可能会被禁用）
    return result
# 比特率切换是一种在 CAN 网络中改变通信速率的机制。
# 通过比特率切换，可以调整数据传输的速度，以适应不同的应用场景和要求。
# hasBitrateSwitch() 方法用于判断 CAN 报文是否具有比特率切换。(就是区分CAN 还是 CAN-FD)
# 如果报文具有比特率切换功能，那么该方法会返回 True；否则，返回 False。
# 在CAN网络中，比特率是指数据传输的速度，通常以每秒位数(bps)表示。比特率越高，数据传输速度越快。
# 然而，某些CAN设备可能不支持高比特率，而且高比特率也可能会增加通信错误的概率。
# 因此，CAN系统通常需要在不同的比特率之间进行切换以适应特定的设备和通信条件。
# Bitrate switching在CAN-FD（Flexible Data-Rate）当中有着重要的应用。
# CAN-FD是CAN总线的一种改进和扩展，它允许数据帧的比特率独立调整，以支持高达 8Mbps的数据传输速度，
# 这个功能就依赖于比特率切换。
# 在CAN-FD中，一次CAN通信可能会分为两部分：仲裁位(arbitration bits)仍使用经典CAN的略低的比特率来保证网络的兼容性，
# 而数据位（data bits）则使用更高的比特率进行高速数据传输。由仲裁位到数据位的比特率切换，便是bitrate switch的实现。



# 错误状态指示器是一种机制，用于指示 CAN 网络中的错误情况。
# 当网络发生错误时，比如总线仲裁错误、数据帧丢失等，可以通过错误状态指示器来提醒通信节点发现问题。
# hasErrorStateIndicator() 方法用于判断 CAN 报文是否具有错误状态指示器。
# 如果报文具有错误状态指示器，那么该方法会返回 True；否则，返回 False

# 本地回显是一种通信机制，其中发送的数据帧将在发送节点本地被复制并返回。
# 这样，发送节点就可以在不等待其他节点确认的情况下立即知道数据是否被成功接收。
# hasLocalEcho() 方法用于判断 CAN 报文是否启用了本地回显。
# 如果启用了本地回显，那么该方法会返回 True；否则，返回 False。
# 使用本地回显可以提高通信的可靠性和效率，但也会增加总线上的数据流量。
# 本地回显是指当用户在终端上输入字符时，终端会将输入的字符显示出来，以便用户可以看到自己所输入的内容。
# 这种功能使用户能够立即看到他们输入的字符，以便进行及时的检查和确认。
# 例如，在终端上输入 "hello"，本地回显会将每个键入的字符显示在光标位置。
# 这样，用户就可以立即看到屏幕上显示的 "h"、"e"、"l"、"l"、"o"。
# 本地回显是终端的默认行为，并且通常是默认启用的。
# 但在某些情况下，可能需要禁用本地回显，
# 尤其是在输入敏感信息（如密码）时，为了安全性考虑，不希望在终端屏幕上显示这些字符。
# 总结：本地回显是终端在用户键入字符时将其显示在屏幕上的功能。


def show_help():
    url = "http://doc.qt.io/qt-6/qtcanbus-backends.html#can-bus-plugins"
    QDesktopServices.openUrl(QUrl(url))


class MainWindow(QMainWindow):

    # 类的构造函数
    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类的构造函数
        self.m_ui = Ui_MainWindow()
        # 创建Ui_MainWindow对象并将其赋值给self.m_ui
        # 表示使用一个名为Ui_MainWindow的UI界面设计，该设计在setupUi()方法中，
        # 将界面元素与类的属性进行关联

        # 初始化一些计数器和属性
        self.m_number_frames_written = 0
        self.m_number_frames_received = 0
        self.m_written = None
        self.m_received = None
        self.m_can_device = None

        self.m_busStatusTimer = QTimer(self)
        # 创建一个定时器m_busStatusTimer，并通过QTimer.timeout信号与bus_status方法连接

        self.m_ui.setupUi(self)
        # 调用Ui_MainWindow中的setupUi()方法来设置主窗口的UI界面
        self.m_connect_dialog = ConnectDialog(self)
        # 创建一个ConnectDialog对象作为连接对话框，并将该对象赋值给self.m_connect_dialog

        # 创建两个QLabel对象表示状态栏的标签，分别是m_status、m_written和m_received。
        self.m_status = QLabel()
        self.m_ui.statusBar.addPermanentWidget(self.m_status)
        self.m_written = QLabel()
        self.m_ui.statusBar.addWidget(self.m_written)
        self.m_received = QLabel()
        self.m_ui.statusBar.addWidget(self.m_received)

        # 启动ReceivedFramesModel模型，
        # 设置模型的队列限制为1000，
        # 并将模型与receivedFramesView视图进行关联，使用set_model方法
        self.m_model = ReceivedFramesModel(self)
        self.m_model.set_queue_limit(1000)
        self.m_ui.receivedFramesView.set_model(self.m_model)

        self.init_actions_connections() #调用init_actions_connections()方法来初始化操作和信号连接
        QTimer.singleShot(50, self.m_connect_dialog.show) #通过QTimer.singleShot()方法延迟50毫秒，在50毫秒后显示连接对话框

        self.m_busStatusTimer.timeout.connect(self.bus_status) #为定时器m_busStatusTimer的超时信号连接一个名为bus_status的方法。
        self.m_appendTimer = QTimer(self) #创建一个定时器m_appendTimer
        self.m_appendTimer.timeout.connect(self.onAppendFramesTimeout) #通过QTimer.timeout信号与onAppendFramesTimeout方法连接
        self.m_appendTimer.start(350) #启动定时器

    def init_actions_connections(self):
        # 初始化各种操作和信号连接

        # 禁用某些操作
        self.m_ui.actionDisconnect.setEnabled(False)
        self.m_ui.actionDeviceInformation.setEnabled(False)
        self.m_ui.sendFrameBox.setEnabled(False)
        # 通过setEnabled(False)方法禁用actionDisconnect、actionDeviceInformation和sendFrameBox。

        # 信号连接,目的是 将交互界面的操作与对应方法进行关联,从而实现对应操作的功能.
        # 每个连接的方法或函数在相应操作被触发是执行相应逻辑
        self.m_ui.sendFrameBox.send_frame.connect(self.send_frame)
        # 将send_frame信号与send_frame函数(括号里面)连接(connect)起来，当send_frameBox中的发送按钮被点击connect时触发。
        self.m_ui.actionConnect.triggered.connect(self._action_connect)
        # 将actionConnect的triggered信号与_action_connect方法连接(connect)，当actionConnect被触发时执行。
        # _action_connect方法名，签名带有下划线_，表示是类的 私有方法，不应该 在类外部直接调用。需要在实现的类中定义这些方法
        # ，以确保信号连接正确地触发对应的操作和逻辑
        self.m_connect_dialog.accepted.connect(self.connect_device)
        # 将connect_dialog的accepted信号与connect_device方法连接，当连接对话框的"确定"按钮被点击时触发
        self.m_ui.actionDisconnect.triggered.connect(self.disconnect_device)
        # 将actionDisconnect的triggered信号与disconnect_device方法连接，当actionDisconnect被触发时执行。
        self.m_ui.actionResetController.triggered.connect(self._reset_controller)
        # 将actionResetController的triggered信号与_reset_controller方法连接，当actionResetController被触发时执行。
        self.m_ui.actionQuit.triggered.connect(self.close)
        self.m_ui.actionAboutQt.triggered.connect(qApp.aboutQt)
        self.m_ui.actionClearLog.triggered.connect(self.m_model.clear)
        self.m_ui.actionPluginDocumentation.triggered.connect(show_help)
        self.m_ui.actionDeviceInformation.triggered.connect(self._action_device_information)

    # 定义了一个名为_action_connect的槽函数，该槽函数没有参数。
    # 该槽函数用于处理   actionConnect   操作，
    # 当该操作被触发时执行
    @Slot()
    def _action_connect(self):
        #首先检查m_can_device对象是否存在。如果存在，则调用deleteLater()方法来删除该对象，并将m_can_device设置为None。
        # 接下来，显示连接对话框m_connect_dialog。
        if self.m_can_device:
            self.m_can_device.deleteLater()
            self.m_can_device = None
        self.m_connect_dialog.show()

    # 一个名为_reset_controller的槽函数，该槽函数没有参数。
    # 该槽函数用于处理  重置控制器  的操作，
    # 当该操作被触发时执行。
    @Slot()
    def _reset_controller(self):
        self.m_can_device.resetController()

    # 一个名为_action_device_information的槽函数，该槽函数没有参数。
    # 该槽函数用于处理  设备信息  操作，
    # 当该操作被触发时执行
    @Slot()
    def _action_device_information(self):
        info = self.m_can_device.deviceInfo() #获取设备的信息，并将结果赋值给变量info
        dialog = CanBusDeviceInfoDialog(info, self) #创建一个CanBusDeviceInfoDialog对象dialog，并将 设备信息info 和  当前窗口  作为参数传递给构造函数
        dialog.exec()

    # 一个名为process_errors的槽函数，
    # 接受一个QCanBusDevice.CanBusError类型的参数error。
    # 该槽函数用于处理   CAN总线设备的错误
    @Slot(QCanBusDevice.CanBusError)
    def process_errors(self, error):
        if error != QCanBusDevice.NoError: #判断error是否为QCanBusDevice.NoError
            self.m_status.setText(self.m_can_device.errorString()) #如果不是，则将m_can_device的错误描述字符串设置为状态栏的文本m_status。

    # 一个名为connect_device的槽函数，
    # 该槽函数没有参数。
    # 该槽函数用于处理   连接设备  的操作，
    # 当该操作被触发时执行
    @Slot()
    def connect_device(self):
        p = self.m_connect_dialog.settings() #获取 连接对话框 的 设置信息
        if p.use_model_ring_buffer:  #根据设置信息是否使用 模型环形缓冲区 来设置模型的队列限制
            self.m_model.set_queue_limit(p.model_ring_buffer_size)  #如果使用模型环形缓冲区，则将设置信息中的模型环形缓冲区大小设置为模型的队列限制
        else:
            self.m_model.set_queue_limit(0)  #否则将队列限制设置为0

        device, error_string = QCanBus.instance().createDevice(p.plugin_name, p.device_interface_name)
        # 使用QCanBus.instance().createDevice()方法创建一个CAN总线设备，
        # 并将设备对象赋值给device，
        # 错误信息赋值给error_string。

        # 检查device是否为空，如果为空，则将错误信息设置为状态栏的文本，然后返回
        if not device:
            self.m_status.setText(f"Error creating device '{p.plugin_name}', reason: '{error_string}'")
            return

        self.m_number_frames_written = 0  #重置已写入帧数m_number_frames_written为0
        self.m_can_device = device #将device赋值给m_can_device。

        # 将m_can_device的errorOccurred信号连接到process_errors槽函数，
        # 将framesReceived信号连接到process_received_frames槽函数，
        # 将framesWritten信号连接到process_frames_written槽函数
        self.m_can_device.errorOccurred.connect(self.process_errors)
        self.m_can_device.framesReceived.connect(self.process_received_frames)
        self.m_can_device.framesWritten.connect(self.process_frames_written)

        
        # 如果设置信息中启用了配置参数，则将每个配置参数设置到m_can_device中
        if p.use_configuration_enabled:
            for k, v in p.configurations:
                self.m_can_device.setConfigurationParameter(k, v)

        # 调用m_can_device的connectDevice方法来连接设备。
        # 如果连接失败，则将错误信息设置为状态栏的文本，
        # 并将m_can_device设置为None
        if not self.m_can_device.connectDevice():    
            e = self.m_can_device.errorString()
            self.m_status.setText(f"Connection error: {e}")
            self.m_can_device = None
        else:
            self.m_ui.actionConnect.setEnabled(False)
            self.m_ui.actionDisconnect.setEnabled(True)
            self.m_ui.actionDeviceInformation.setEnabled(True)
            self.m_ui.sendFrameBox.setEnabled(True)
            # 如果连接成功，则禁用connect界面部件，启用Disconnect连接、设备信息DevInfo、发送帧sendFrameBox的界面部件。
            config_bit_rate = self.m_can_device.configurationParameter(QCanBusDevice.BitRateKey) # 获取配置参数中的比特率信息
            if config_bit_rate > 0:
                is_can_fd = bool(self.m_can_device.configurationParameter(QCanBusDevice.CanFdKey)) #是否是CAN_FD
                config_data_bit_rate = self.m_can_device.configurationParameter(QCanBusDevice.DataBitRateKey)
                bit_rate = config_bit_rate / 1000 # 因为后面的单位是kbps 所以这个地方/1000
                if is_can_fd and config_data_bit_rate > 0: # 如果是CANFD 且 有config_data_bit_rate
                    data_bit_rate = config_data_bit_rate / 1000 # bps ->kbps
                    m = f"Plugin: {p.plugin_name}, connected to {p.device_interface_name} at {bit_rate} / {data_bit_rate} kBit/s"
                    self.m_status.setText(m) # 设置状态栏文本
                else:
                    m = f"Plugin: {p.plugin_name}, connected to {p.device_interface_name} at {bit_rate} kBit/s"
                    self.m_status.setText(m) # 设置状态栏文本
            else:
                self.m_status.setText(f"Plugin: {p.plugin_name}, connected to {p.device_interface_name}")

            if self.m_can_device.hasBusStatus(): # 如果m_can_device具有总线状态
                self.m_busStatusTimer.start(2000) # 启动m_busStatusTimer定时器以每2秒 更新总线状态
            else:
                self.m_ui.busStatus.setText("No CAN bus status available.")

    # 用于更新CAN总线状态
    def bus_status(self):
        if not self.m_can_device or not self.m_can_device.hasBusStatus(): # 以 or 就是 或 为分界 去读这个代码
            self.m_ui.busStatus.setText("No CAN bus status available.")
            self.m_busStatusTimer.stop() # 停止计时器
            return

        state = self.m_can_device.busStatus()
        if state == QCanBusDevice.CanBusStatus.Good:
            self.m_ui.busStatus.setText("CAN bus status: Good.")
        elif state == QCanBusDevice.CanBusStatus.Warning:
            self.m_ui.busStatus.setText("CAN bus status: Warning.")
        elif state == QCanBusDevice.CanBusStatus.Error:
            self.m_ui.busStatus.setText("CAN bus status: Error.")
        elif state == QCanBusDevice.CanBusStatus.BusOff:
            self.m_ui.busStatus.setText("CAN bus status: Bus Off.")
        else:
            self.m_ui.busStatus.setText("CAN bus status: Unknown.")

    # 一个名为disconnect_device的槽函数，
    # 该槽函数没有参数。
    # 该槽函数用于处理  断开设备连接  的操作，
    # 当该操作被触发时执行。
    @Slot()
    def disconnect_device(self):
        if not self.m_can_device: # 检查m_can_device是否为空
            return
        self.m_busStatusTimer.stop() # 停止m_busStatusTimer定时器
        self.m_can_device.disconnectDevice() # 使用disconnectDevice方法断开m_can_device的连接
        self.m_ui.actionConnect.setEnabled(True) # 启用
        self.m_ui.actionDisconnect.setEnabled(False) # 禁用
        self.m_ui.actionDeviceInformation.setEnabled(False) # 禁用
        self.m_ui.sendFrameBox.setEnabled(False) # 禁用
        self.m_status.setText("Disconnected") # 将状态栏的文本设置为“Disconnected”

    # 一个名为process_frames_written的槽函数，
    # 它接受一个整数类型的count参数。
    # 这个槽函数用于处理   写入帧的操作完成的处理，
    # 当写入帧的操作完成时  被调用
    @Slot(int)
    def process_frames_written(self, count):
        self.m_number_frames_written += count
        self.m_written.setText(f"{self.m_number_frames_written} frames written")

    # 一个名为closeEvent的函数，
    # 它重写了Qt中的closeEvent事件。
    # 该函数在窗口关闭时被调用
    def closeEvent(self, event):
        self.m_connect_dialog.close() # 关闭连接对话框m_connect_dialog
        event.accept() # 调用event.accept()来接受关闭事件

   # 处理收到的帧，这个比较重要 可用 序号、时间戳、flag、CAN-ID、DLC、Data
    @Slot()
    def process_received_frames(self):
        if not self.m_can_device:
            return
        while self.m_can_device.framesAvailable():
            self.m_number_frames_received = self.m_number_frames_received + 1
            frame = self.m_can_device.readFrame()
            data = ""
            if frame.frameType() == QCanBusFrame.ErrorFrame: # 如果帧类型为错误帧，则使用m_can_device的interpretErrorFrame方法解释错误帧
                data = self.m_can_device.interpretErrorFrame(frame)
            else:
                data = frame.payload().toHex(' ').toUpper() # 将frame.payload()返回的字节序列转换为十六进制字符串，并使用空格分隔每两个字符。然后，将得到的字符串转换为大写形式
            print("data:",data,type(data))

            # 获取帧的时间戳，并将秒数和微秒数格式化成字符串，并赋值给time变量。获取帧的标志位，并赋值给flags变量
            secs = frame.timeStamp().seconds()
            microsecs = frame.timeStamp().microSeconds() / 100  #  获取微秒数，并将其除以100得到小数位
            time = f"{secs:>10}.{microsecs:0>4}"  # 格式化为字符串，秒数占据10个字符的宽度，微秒数占据4个字符的宽度
            flags = frame_flags(frame) #  获取frame的标志
            print("flags:",flags,type(flags))

            id = f"{frame.frameId():x}" # 在 f-string 中，我们可以使用冒号:来指定格式化选项,x 表示16进制
            dlc = f"{frame.payload().size()}"
            frame = [f"{self.m_number_frames_received}", time, flags, id, dlc, data] 
            self.m_model.append_frame(frame)
            # 获取帧ID的十六进制表示并赋值给id变量。
            # 获取帧的数据长度，并赋值给dlc变量。
            # 将帧号、时间、标志位、ID、数据长度、数据组成一个 list列表frame
            # 并将该列表添加到m_model模型中



    # 定义了一个名为send_frame的槽函数，
    # 接受一个QCanBusFrame类型的参数frame。
    # 该槽函数用于   向CAN总线设备发送CAN帧   
    @Slot(QCanBusFrame)
    def send_frame(self, frame):
        # 通过检查m_can_device对象是否有效来确保已经创建了CAN总线设备。
        # 如果m_can_device存在，则调用其writeFrame方法，将frame发送到CAN总线上。
        if self.m_can_device:
            self.m_can_device.writeFrame(frame)

    # 一个名为onAppendFramesTimeout的槽函数，
    # 该槽函数没有参数。
    # 该槽函数用于处理   扩展帧超时  操作，当超时发生时执行。
    @Slot()
    def onAppendFramesTimeout(self):
        if not self.m_can_device: #首先检查m_can_device对象是否存在，如果不存在，则直接返回
            return
        if self.m_model.need_update(): #检查模型m_model是否需要更新，如果需要更新，则调用update方法进行模型的更新
            self.m_model.update()
            if self.m_connect_dialog.settings().use_autoscroll: #检查  连接对话框  的设置是否启用了   自动滚动功能
                self.m_ui.receivedFramesView.scrollToBottom() #如果启用，则调用scrollToBottom方法将接收到的帧滚动到底部
            self.m_received.setText(f"{self.m_number_frames_received} frames received") # 示接收到的帧数self.m_number_frames_received
