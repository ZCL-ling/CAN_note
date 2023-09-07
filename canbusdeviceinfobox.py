# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox

from ui_canbusdeviceinfobox import Ui_CanBusDeviceInfoBox

# 定义了一种方式来操作传入的参数box，
# 这个box可能是Qt用户界面中的一个组件（比如一个文本框或按钮等）。
# 使得box组件对鼠标操作无反应（对鼠标透明），无法通过键盘获得焦点，并且在呈现时更为紧凑
def _set_readonly_and_compact(box):
    box.setAttribute(Qt.WA_TransparentForMouseEvents)
    box.setFocusPolicy(Qt.NoFocus)
    box.setStyleSheet("margin-top:0; margin-bottom:0;")


class CanBusDeviceInfoBox(QGroupBox):

    def __init__(self, parent):
        super().__init__(parent) # super().__init__(parent) 这行代码调用了父类 QGroupBox 的初始化方法，以确保父类的正确初始化
        self.m_ui = Ui_CanBusDeviceInfoBox() #设置 CanBusDeviceInfoBox 的用户界面
        self.m_ui.setupUi(self) # 将用户界面设置在这个CanBusDeviceInfoBox 实例上
        # 调用 Ui_CanBusDeviceInfoBox类的方法setupUi，设置用户界面。
        # self 关键词是指 CanBusDeviceInfoBox的实例自身，表示将用户界面设置在这个实例上
        _set_readonly_and_compact(self.m_ui.isVirtual)
        _set_readonly_and_compact(self.m_ui.isFlexibleDataRateCapable)

    # clear方法的主要作用就是将CanBusDeviceInfoBox对象恢复到初始状态，清除用户之前可能的所有操作和输入，
    # 常用于刷新或重置当前界面
    def clear(self):
        self.m_ui.pluginLabel.clear()
        self.m_ui.nameLabel.clear()
        self.m_ui.descriptionLabel.clear()
        self.m_ui.serialNumberLabel.clear()
        self.m_ui.aliasLabel.clear()
        self.m_ui.channelLabel.clear()
        self.m_ui.isVirtual.setChecked(False) # 这两条语句是将复选框的状态设置为未选中状态。
        self.m_ui.isFlexibleDataRateCapable.setChecked(False)

    def set_device_info(self, info):
        self.m_ui.pluginLabel.setText(f"Plugin: {info.plugin()}")
        self.m_ui.nameLabel.setText(f"Name: {info.name()}")
        self.m_ui.descriptionLabel.setText(info.description())
        serial_number = info.serialNumber()# 序列号
        if not serial_number:
            serial_number = "n/a"
        self.m_ui.serialNumberLabel.setText(f"Serial: {serial_number}")
        alias = info.alias() # 别名
        if not alias:
            alias = "n/a"
        self.m_ui.aliasLabel.setText(f"Alias: {alias}")
        self.m_ui.channelLabel.setText(f"Channel: {info.channel()}")
        self.m_ui.isVirtual.setChecked(info.isVirtual()) # 设备是否为虚拟设备
        self.m_ui.isFlexibleDataRateCapable.setChecked(info.hasFlexibleDataRate())
