# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtWidgets import QDialog

from ui_canbusdeviceinfodialog import Ui_CanBusDeviceInfoDialog

#用于显示CAN总线设备信息对话框
class CanBusDeviceInfoDialog(QDialog):

    def __init__(self, info, parent):#构造函数
        super().__init__(parent)#调用父类的构造函数
        self.m_ui = Ui_CanBusDeviceInfoDialog() #使用了一个名为Ui_CanBusDeviceInfoDialog的UI界面设计
        self.m_ui.setupUi(self) #在setupUi()方法中将界面元素与类的属性进行关联,调用setupUi()方法来设置对话框的UI界面
        self.m_ui.deviceInfoBox.set_device_info(info) # 用于显示设备的详细信息，设备信息info传递给deviceInfoBox的set_device_info方法
        self.m_ui.okButton.pressed.connect(self.close) #当用户点击OK按钮时，关闭对话框。
        # 连接OK Button 的press信号到close方法
