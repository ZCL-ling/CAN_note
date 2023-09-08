# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QSettings, Qt, Slot
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QDialog
from PySide6.QtSerialBus import QCanBus, QCanBusDevice

from ui_connectdialog import Ui_ConnectDialog


class Settings():
    def __init__(self):
        self.plugin_name = ""
        self.device_interface_name = ""
        self.configurations = []
        self.use_configuration_enabled = False
        self.use_model_ring_buffer = True
        self.model_ring_buffer_size = 1000
        self.use_autoscroll = False
        # 环形缓冲区 一种数据结构
        # 环形缓冲区的特点是，它在逻辑上形成一个环，一旦数据填满了缓冲区，再继续添加新的数据会从缓冲区的开始处覆盖掉旧的数据。
        # 因此，环形缓冲区总是保存了 最新的 一定量的数据。
        # 如果在某个实时数据显示的程序中，你只关心最新的1000条数据，
        # 那么就可以设置一个大小为1000的环形缓冲区来保存这些数据，新生成的数据总是会在缓冲区的开始处覆盖旧的数据。

        # use_autoscroll自动回滚是一个常见的用户界面功能。
        # 具体来说，当开启自动滚动后，如果新的内容添加到了展示区（比如一个文本框或者列表）的底部，
        # 那么滚动条将会自动滚动到底部，使得最新的内容能够立即显示出来。这样用户就不需要手动操作滚动条去查看最新的内容。


class ConnectDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_ui = Ui_ConnectDialog()
        self.m_currentSettings = Settings()
        self.m_interfaces = []
        self.m_settings = QSettings("QtProject", "CAN example")
        self.m_ui.setupUi(self)

        self.m_ui.errorFilterEdit.setValidator(QIntValidator(0, 0x1FFFFFFF, self))
        
        # 下拉列表框loopbackBox、receiveOwnBox、canFdBox
        self.m_ui.loopbackBox.addItem("unspecified") # "unspecified" 对应的值默认为 None
        self.m_ui.loopbackBox.addItem("False", False) # addItem 方法有两个参数，第一个参数是要显示在下拉列表框中的文本，第二个参数是这个文本所代表的实际值。
        self.m_ui.loopbackBox.addItem("True", True)

        self.m_ui.receiveOwnBox.addItem("unspecified") # "unspecified" 对应的值默认为 None。
        self.m_ui.receiveOwnBox.addItem("False", False)
        self.m_ui.receiveOwnBox.addItem("True", True)

        self.m_ui.canFdBox.addItem("False", False)
        self.m_ui.canFdBox.addItem("True", True)

        # 选择 "True"，则代表启用对应的设置。
        # 选择 "False"，则代表禁用对应的设置。
        # 选择 "unspecified" 表示不采取任何操作或采取默认设置

        # loopbackBox 是循环测试选项：循环测试是网络通信中一种常用的测试方式，（检查通信设备是否正常）；
        # 主要是把发送出去的数据直接路由（loopback）回来，然后接收和发送的数据进行比较，以此来检查通信设备是否正常。
        # receiveOwnBox 是 是否接收自己发送数据的选项：（是否 接收自己发送的数据）
        # 在一些通信应用中，发送设备可以选择 是否 接收自己发送出去的数据。这个设置通常用于调试和测试；


        self.m_ui.dataBitrateBox.set_flexible_date_rate_enabled(True)

        #括号里面的都是函数
        self.m_ui.okButton.clicked.connect(self.ok)
        self.m_ui.cancelButton.clicked.connect(self.cancel)
        self.m_ui.useConfigurationBox.toggled.connect(self.m_ui.configurationBox.setEnabled)
        # "toggled" 是一个信号,在对应的 GUI 元素（例如复选框或者开关按钮）的状态被切换时发出。
        self.m_ui.pluginListBox.currentTextChanged.connect(self.plugin_changed)
        self.m_ui.interfaceListBox.currentTextChanged.connect(self.interface_changed)
        self.m_ui.ringBufferBox.stateChanged.connect(self._ring_buffer_changed)

        self.m_ui.rawFilterEdit.hide()
        self.m_ui.rawFilterLabel.hide()

        self.m_ui.pluginListBox.addItems(QCanBus.instance().plugins())

        self.restore_settings()

    @Slot(int)
    def _ring_buffer_changed(self, state):
        self.m_ui.ringBufferLimitBox.setEnabled(state == Qt.CheckState.Checked.value)

    def settings(self):
        return self.m_currentSettings

    # save_settings和restore_settings 是一对函数，经常在一起工作。
    # save_settings在程序结束或在特定的保存点保存程序的状态
    # restore_settings在程序开始时或需要回到之前的保存状态时恢复这些保存的状态。

    # 在Qt应用程序中,保存用户的设置，使用 QSettings实例（self.m_settings）保存用户的设置
    def save_settings(self):
        qs = self.m_settings
        cur = self.m_currentSettings
        qs.beginGroup("LastSettings")
        qs.setValue("PluginName", self.m_currentSettings.plugin_name)
        qs.setValue("DeviceInterfaceName", cur.device_interface_name)
        qs.setValue("UseAutoscroll", cur.use_autoscroll)
        qs.setValue("UseRingBuffer", cur.use_model_ring_buffer)
        qs.setValue("RingBufferSize", cur.model_ring_buffer_size)
        qs.setValue("UseCustomConfiguration", cur.use_configuration_enabled)

        if cur.use_configuration_enabled:
            qs.setValue("Loopback",
                        self.configuration_value(QCanBusDevice.LoopbackKey))
            qs.setValue("ReceiveOwn",
                        self.configuration_value(QCanBusDevice.ReceiveOwnKey))
            qs.setValue("ErrorFilter",
                        self.configuration_value(QCanBusDevice.ErrorFilterKey))
            qs.setValue("BitRate",
                        self.configuration_value(QCanBusDevice.BitRateKey))
            qs.setValue("CanFd",
                        self.configuration_value(QCanBusDevice.CanFdKey))
            qs.setValue("DataBitRate",
                        self.configuration_value(QCanBusDevice.DataBitRateKey))
        qs.endGroup()


    # 恢复设置，从 self.m_settings中 恢复 应用程序的设置（更新程序UI界面）；
    def restore_settings(self):
        qs = self.m_settings
        cur = self.m_currentSettings
        qs.beginGroup("LastSettings") # 开始读取名为"LastSettings"的设置组。qs.endGroup()之前的所有设置读取操作都将在这个组内进行。
        cur.plugin_name = qs.value("PluginName", "", str)
        # 读取名为"PluginName"的设置的值，并将其赋给cur对象的plugin_name属性。
        # 如果找不到该设置，则以空字符串("")为默认值，并且设置值将进行str（字符串）类型的转换。
        cur.device_interface_name = qs.value("DeviceInterfaceName", "", str)
        cur.use_autoscroll = qs.value("UseAutoscroll", False, bool)
        cur.use_model_ring_buffer = qs.value("UseRingBuffer", False, bool)
        cur.model_ring_buffer_size = qs.value("RingBufferSize", 0, int)
        cur.use_configuration_enabled = qs.value("UseCustomConfiguration", False, bool)

        self.revert_settings()  # 根据程序中代码的设置  更改 用户界面 设置

        if cur.use_configuration_enabled: # 如果 开启自定义配置，则从设置中读取更多的参数值，并作为文本设置到相应的UI组件上
            self.m_ui.loopbackBox.setCurrentText(qs.value("Loopback"))
            self.m_ui.receiveOwnBox.setCurrentText(qs.value("ReceiveOwn"))
            self.m_ui.errorFilterEdit.setText(qs.value("ErrorFilter"))
            self.m_ui.bitrateBox.setCurrentText(qs.value("BitRate"))
            self.m_ui.canFdBox.setCurrentText(qs.value("CanFd"))
            self.m_ui.dataBitrateBox.setCurrentText(qs.value("DataBitRate"))

        qs.endGroup() # 结束设置组的读取
        self.update_settings() # 参数更新到 UI界面中

    # 与CAN相关的plugin:是指点对CAN设备进行操作的软件模块。SocketCAN、PCAN、Vector等；
    # 在CAN (Controller Area Network) 系统中，"interface" 通常指的是物理接口，
    # 也就是实际与CAN总线硬件相连接的逻辑或者物理端口。使用不同的插件和驱动，你可以通过这些接口与CAN设备进行通信。

    # 槽 是信号与槽机制的一部分响应函数
    # 选择一个新的插件之后，获取这个插件下可用的设备列表，并更新UI中的interfaceListBox组件。
    # SocketCAN接口：如"can0"，"can1"等，这些接口表示的是在Linux系统上通过SocketCAN插件与CAN硬件连接的设备。
    # Vector接口：如"CANboardXL", "CANCabXL"等，它们是Vector公司提供的CAN接口设备。
    # 例如 pcan 切换到 vectorcan
    @Slot(str)
    def plugin_changed(self, plugin):
        self.m_ui.interfaceListBox.clear() # 清空interfaceListBox组件的内容
        interfaces, error_string = QCanBus.instance().availableDevices(plugin)
        # 获取当前插件(plugin)可用的设备列表（interfaces）及可能产生的错误信息（error_string）
        self.m_interfaces = interfaces
        for info in self.m_interfaces:
            self.m_ui.interfaceListBox.addItem(info.name())

    #CAN接口改变时 会被触发 例如 Vectorcan 的Interface 有can0 can1 当从can0切换到can1时被触发
    @Slot(str)
    def interface_changed(self, interface):
        for info in self.m_interfaces: # info表示当前接口 interface
            if interface == info.name():
                self.m_ui.deviceInfoBox.set_device_info(info)
                return
        self.m_ui.deviceInfoBox.clear() # 未找到符合的接口，就清除可能在设备信息框 显示的内容
        # 这就是 如果选取 pcan 后，deviceInfoBox显示为空的原因

    @Slot()
    def ok(self):
        self.update_settings()
        self.save_settings()
        self.accept()

    @Slot()
    def cancel(self):
        self.revert_settings()
        self.reject()

    
    # 需要注意的是，LoopbackKey、ReceiveOwnKey、ErrorFilterKey 这样的配置可能有多个，所以这里使用了循环来处理
    def configuration_value(self, key):
        result = None
        for k, v in self.m_currentSettings.configurations:
            if k == key:
                result = v
                break
        if not result and (key == QCanBusDevice.LoopbackKey or key == QCanBusDevice.ReceiveOwnKey):
            return "unspecified"
        return str(result)

    # revert_settings 函数是用于将程序中的当前设置 同步更改到用户界面上。
    # 与 update_settings 函数恰好相反，
    # update_settings 函数是从用户界面读取设置更改程序中的设置，
    # revert_settings 函数则是根据程序中的设置更改用户界面。
    def revert_settings(self):
        # 函数首先将 self.m_currentSettings 中的
        #  plugin_name、device_interface_name 和 use_configuration_enabled 的值设置回到 GUI 界面的对应位置。
        self.m_ui.pluginListBox.setCurrentText(self.m_currentSettings.plugin_name)
        self.m_ui.interfaceListBox.setCurrentText(self.m_currentSettings.device_interface_name)
        self.m_ui.useConfigurationBox.setChecked(self.m_currentSettings.use_configuration_enabled)

        # 将 ringBufferBox、ringBufferLimitBox 和 autoscrollBox 的值设置为当前设置m_currentSettings中的对应值。
        self.m_ui.ringBufferBox.setChecked(self.m_currentSettings.use_model_ring_buffer)
        self.m_ui.ringBufferLimitBox.setValue(self.m_currentSettings.model_ring_buffer_size)
        self.m_ui.autoscrollBox.setChecked(self.m_currentSettings.use_autoscroll)

        # 函数通过调用 configuration_value 方法获取了一些配置的值，然后将这些值设置回到 GUI 界面的相应位置。
        # 需要注意的是，LoopbackKey、ReceiveOwnKey、ErrorFilterKey 这样的配置可能有多个，所以这里使用了循环来处理
        value = self.configuration_value(QCanBusDevice.LoopbackKey)
        self.m_ui.loopbackBox.setCurrentText(value)

        value = self.configuration_value(QCanBusDevice.ReceiveOwnKey)
        self.m_ui.receiveOwnBox.setCurrentText(value)

        value = self.configuration_value(QCanBusDevice.ErrorFilterKey)
        self.m_ui.errorFilterEdit.setText(value)

        value = self.configuration_value(QCanBusDevice.BitRateKey)
        self.m_ui.bitrateBox.setCurrentText(value)

        value = self.configuration_value(QCanBusDevice.CanFdKey)
        self.m_ui.canFdBox.setCurrentText(value)

        value = self.configuration_value(QCanBusDevice.DataBitRateKey)
        self.m_ui.dataBitrateBox.setCurrentText(value)

    # 例如，Loopback、ReceiveOwnKey、ErrorFilter和BitRate等设置项，
    # 如果这些设置项被设定了的话，则会将这些设置项添加到配置键值对的列表中。
    def update_settings(self):
        # 将当前选择的插件名称、设备接口名称以及"Use Configuration"框是否被选中的信息赋值给相应的设置。
        self.m_currentSettings.plugin_name = self.m_ui.pluginListBox.currentText()
        self.m_currentSettings.device_interface_name = self.m_ui.interfaceListBox.currentText()
        self.m_currentSettings.use_configuration_enabled = self.m_ui.useConfigurationBox.isChecked()

        # 读取“Ring Buffer”、“Ring Buffer Limit”和“Autoscroll”设置项的值，并将这些值存到相应的设置对象中
        self.m_currentSettings.use_model_ring_buffer = self.m_ui.ringBufferBox.isChecked()
        self.m_currentSettings.model_ring_buffer_size = self.m_ui.ringBufferLimitBox.value()
        self.m_currentSettings.use_autoscroll = self.m_ui.autoscrollBox.isChecked()

        if self.m_currentSettings.use_configuration_enabled:
            self.m_currentSettings.configurations.clear() 
            # 如果 "use_configuration_enabled" 选项是被选中的，它清除当前的设置中的所有配置
            # 然后根据各个设置项的值添加新的配置项。配置项是以元组的形式保存的，元组是 (key, value) 的格式


            # process LoopBack
            if self.m_ui.loopbackBox.currentIndex() != 0:
                item = (QCanBusDevice.LoopbackKey, self.m_ui.loopbackBox.currentData())
                self.m_currentSettings.configurations.append(item)

            # process ReceiveOwnKey
            if self.m_ui.receiveOwnBox.currentIndex() != 0:
                item = (QCanBusDevice.ReceiveOwnKey, self.m_ui.receiveOwnBox.currentData())
                self.m_currentSettings.configurations.append(item)

            # process error filter
            error_filter = self.m_ui.errorFilterEdit.text()
            if error_filter:
                ok = False
                try:
                    int(error_filter)  # check if value contains a valid integer
                    ok = True
                except ValueError:
                    pass
                if ok:
                    item = (QCanBusDevice.ErrorFilterKey, error_filter)
                    self.m_currentSettings.configurations.append(item)

            # process raw filter list
            if self.m_ui.rawFilterEdit.text():
                pass  # TODO current ui not sufficient to reflect this param

            # process bitrate
            bitrate = self.m_ui.bitrateBox.bit_rate()
            if bitrate > 0:
                item = (QCanBusDevice.BitRateKey, bitrate)
                self.m_currentSettings.configurations.append(item)

            # process CAN FD setting
            fd_item = (QCanBusDevice.CanFdKey, self.m_ui.canFdBox.currentData())
            self.m_currentSettings.configurations.append(fd_item)

            # process data bitrate
            data_bitrate = self.m_ui.dataBitrateBox.bit_rate()
            if data_bitrate > 0:
                item = (QCanBusDevice.DataBitRateKey, data_bitrate)
                self.m_currentSettings.configurations.append(item)
