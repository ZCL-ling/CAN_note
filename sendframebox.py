# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import re

from PySide6.QtGui import QValidator
from PySide6.QtCore import QByteArray, Signal, Slot
from PySide6.QtWidgets import QGroupBox
from PySide6.QtSerialBus import QCanBusFrame

from ui_sendframebox import Ui_SendFrameBox

# re 模块是 Python 的正则表达式模块，用于进行字符串的匹表达式，可以进行更灵活和高效的文本处理
# QValidator 是用于验证输入的类，
# QByteArray 是用于处理字节数组的类，
# Signal 和 Slot 是用于创建信号和槽的装饰器， 
# QGroupBox 是QGroupBox是QtWidgets模块中的一个类，它提供了一个带有标题的框架，可以包含其他窗口部件。
#           例如，你可以把几个相关的部件（比如几个复选框或者单选按钮）放在一个QGroupBox里，这样可以让用户知道这些部件是一组。
# QCanBusFrame 是用于 CAN 总线通信的类。

THREE_HEX_DIGITS_PATTERN = re.compile("[0-9a-fA-F]{3}") # 正则表达式模式，用于匹配三个十六进制数字，3 表示前面字符集恰好出现3次
HEX_NUMBER_PATTERN = re.compile("^[0-9a-fA-F]+$")   #正则表达式模式，用于匹配一个或多个十六进制数字
# ^字符串开始，+ 表示前面字符集可以出现一次或多次，$表示 字符串的结束


MAX_STANDARD_ID = 0x7FF  # 表示标准 CAN ID 的最大值
MAX_EXTENDED_ID = 0x10000000   #表示扩展 CAN ID 的最大值
MAX_PAYLOAD = 8 # 表示 CAN 数据帧的最大有效载荷长度
MAX_PAYLOAD_FD = 64 # 表示 CAN FD 数据帧的最大有效载荷长度


# 判断一个十六进制输入的长度是否为偶数。
# 首先使用input.replace(" ", "")将输入中的所有空格替换为空字符串，
# 然后使用len()函数获取字符串的长度，
# 最后使用 % 操作符来判断长度是否为偶数。
def is_even_hex(input):
    return len(input.replace(" ", "")) % 2 == 0


# 用于在给定位置（pos）处将一个空格插入到字符串中。
# 首先使用切片操作符string[0:pos]获取从字符串开始到给定位置处的子字符串，
# 然后使用+操作符将空格字符和该子字符串拼接起来，
# 最后再使用+操作符将剩余的字符串拼接到结果字符串的末尾。
def insert_space(string, pos):
    return string[0:pos] + " " + string[pos:]


# Formats a string of hex characters with a space between every byte
# Example: "123456789abc" -> "12 34 56 78 9A BC"
# 格式化十六进制数据
def format_hex_data(input):
    out = input.strip() # 去除输入字符串两端的空白字符
    while True: # 一个无限循环来搜索
        match = THREE_HEX_DIGITS_PATTERN.search(out)  # 一个无限循环来搜索 out 中匹配 THREE_HEX_DIGITS_PATTERN 的部分
        if match:
            out = insert_space(out, match.end(0) - 1) 
            #假设有一个匹配对象 match ，match 的内容是 "abc"，在原字符串中的位置是 5 到 7 （在Python中，字符串的位置是从0开始的）。
            # 那么，match.end(0) 的结果就是 8
            # match.end(0) - 1 就是在 match 的结束位置减去1
            # 在上述举例中， match.end(0) - 1的结果就是7，它指向"abc"的"c"。
        else:
            break
    return out.strip().upper() # 除两端的空白字符，并将字符串转换为大写


class HexIntegerValidator(QValidator):   # 整数 验证

    def __init__(self, parent):
        super().__init__(parent)
        self.m_maximum = MAX_STANDARD_ID  # 标准 CAN ID 的最大值

    # 用于验证用户输入的十六进制数是否有效
    def validate(self, input, pos):
        result = QValidator.Intermediate  #QValidator类的一个枚举常量， 表示验证结果为中间状态；
        #表示 用户输入的值 尚未完成验证，不满足完全接受的条件，但 也不完全无效。


        if input: # 判断 input 是否为空
            result = QValidator.Invalid  # 反证法，先初始为无效
            try:
                value = int(input, base=16)  # 将 input 转换为整数
                if value < self.m_maximum:
                    result = QValidator.Acceptable
            except ValueError:
                pass
        return result

    def set_maximum(self, maximum):
        self.m_maximum = maximum


class HexStringValidator(QValidator):  # 字符串验证

    def __init__(self, parent):
        super().__init__(parent)
        self.m_maxLength = MAX_PAYLOAD  #  CAN 数据帧的最大有效载荷长度 8个字节

    # 因为一个字节是8位，用两个十六进制的数字可以完全表示（因为一个十六进制数字可以表达4位二进制数）。所以，为了表示m_maxLength的字节数的信息，你需要2 * m_maxLength的十六进制数。因此，这里的max_size是2 * m_maxLength。
    # 为什么max_size需要是m_maxLength的两倍?
    # 一个例子：整数 11 的二进制表示是 1011，需要4位二进制数位，用一个十六进制数 B 就可以完全表示。
    # 一个十六进制数等于4位二进制数，
    # 1个字节（8位二进制数）等于2个十六进制数。
    
    def validate(self, input, pos):
        max_size = 2 * self.m_maxLength
        data = input.replace(" ", "")
        if not data:
            return QValidator.Intermediate

        # limit maximum size
        if len(data) > max_size:
            return QValidator.Invalid

        # check if all input is valid
        if not HEX_NUMBER_PATTERN.match(data):  # 正则 用于匹配 一个或多个 16进制数字
            return QValidator.Invalid

        # insert a space after every two hex nibbles
        while True:
            match = THREE_HEX_DIGITS_PATTERN.search(input) # 正则匹配3个16进制数
            if not match:
                break
            start = match.start(0) #获取匹配字符串的起始位置
            end = match.end() # 获取匹配字符串的结束位置
            
            # if-elif-else判断是检查在哪个位置插入空格
            if pos == start + 1: 
                input = insert_space(input, pos)
            elif pos == start + 2:
                input = insert_space(input, end - 1)
                pos = end
            else:
                input = insert_space(input, end - 1)
                pos = end + 1

        return (QValidator.Acceptable, input, pos)

    def set_max_length(self, maxLength):
        self.m_maxLength = maxLength


class SendFrameBox(QGroupBox):

    send_frame = Signal(QCanBusFrame)

    def __init__(self, parent):
        super().__init__(parent)
        self.m_ui = Ui_SendFrameBox()
        self.m_ui.setupUi(self)

        self.m_hexIntegerValidator = HexIntegerValidator(self)
        self.m_ui.frameIdEdit.setValidator(self.m_hexIntegerValidator)
        self.m_hexStringValidator = HexStringValidator(self)
        self.m_ui.payloadEdit.setValidator(self.m_hexStringValidator)

        self.m_ui.dataFrame.toggled.connect(self._data_frame)
        self.m_ui.remoteFrame.toggled.connect(self._remote_frame)
        self.m_ui.errorFrame.toggled.connect(self._error_frame)
        self.m_ui.extendedFormatBox.toggled.connect(self._extended_format)
        self.m_ui.flexibleDataRateBox.toggled.connect(self._flexible_datarate)
        self.m_ui.frameIdEdit.textChanged.connect(self._frameid_or_payload_changed)
        self.m_ui.payloadEdit.textChanged.connect(self._frameid_or_payload_changed)
        self._frameid_or_payload_changed()
        self.m_ui.sendButton.clicked.connect(self._send)

    @Slot(bool)
    def _data_frame(self, value):
        if value:
            self.m_ui.flexibleDataRateBox.setEnabled(True)

    @Slot(bool)
    def _remote_frame(self, value):
        if value:
            self.m_ui.flexibleDataRateBox.setEnabled(False)
            self.m_ui.flexibleDataRateBox.setChecked(False)

    @Slot(bool)
    def _error_frame(self, value):
        if value:
            self.m_ui.flexibleDataRateBox.setEnabled(False)
            self.m_ui.flexibleDataRateBox.setChecked(False)

    @Slot(bool)
    def _extended_format(self, value):
        m = MAX_EXTENDED_ID if value else MAX_STANDARD_ID
        self.m_hexIntegerValidator.set_maximum(m)

    @Slot(bool)
    def _flexible_datarate(self, value):
        l = MAX_PAYLOAD_FD if value else MAX_PAYLOAD
        self.m_hexStringValidator.set_max_length(l)
        self.m_ui.bitrateSwitchBox.setEnabled(value)
        if not value:
            self.m_ui.bitrateSwitchBox.setChecked(False)

    #根据帧ID和负载字符串的有效性，实时更新发送按钮 sendButton 的启用状态 和 工具提示信息。
    @Slot()
    def _frameid_or_payload_changed(self):
        has_frame_id = bool(self.m_ui.frameIdEdit.text()) # 检查frameIdEdit文本框是否有值（是否有帧ID），如果有则返回True，否则返回False
        self.m_ui.sendButton.setEnabled(has_frame_id)
        tt = "" if has_frame_id else "Cannot send because no Frame ID was given."
        self.m_ui.sendButton.setToolTip(tt)
        if has_frame_id:
            is_even = is_even_hex(self.m_ui.payloadEdit.text())
            # 依据is_even的值启用或禁用sendButton。
            # 如果is_even为True，即负载字符串是个有效的十六进制数字符串，则启用sendButton，否则禁用sendButton。
            self.m_ui.sendButton.setEnabled(is_even)
            tt = "" if is_even else "Cannot send because Payload hex string is invalid."
            self.m_ui.sendButton.setToolTip(tt)

    @Slot()
    def _send(self):
        frame_id = int(self.m_ui.frameIdEdit.text(), base=16)# 从界面上的frameIdEdit文本框获取帧ID，并将其从十六进制字符串转换为整型
        data = self.m_ui.payloadEdit.text().replace(" ", "")# 从界面上的payloadEdit文本框获取负载数据（payload）。负载数据被视作十六进制数字符串，并移除其中的所有空格。
        self.m_ui.payloadEdit.setText(format_hex_data(data))# 将处理过的负载字符串重新设置回payloadEdit文本框
        payload = QByteArray.fromHex(bytes(data, encoding='utf8'))# 将处理过的负载字符串转换为QByteArray对象。

        # 利用上述收集到的帧ID和负载，创建一个QCanBusFrame对象。然后根据用户在界面上的选择，
        # 来设置扩展帧格式（extended frame format），灵活的数据速率格式（flexible data rate format），以及bit rate switch
        frame = QCanBusFrame(frame_id, payload)
        frame.setExtendedFrameFormat(self.m_ui.extendedFormatBox.isChecked())
        frame.setFlexibleDataRateFormat(self.m_ui.flexibleDataRateBox.isChecked())
        frame.setBitrateSwitch(self.m_ui.bitrateSwitchBox.isChecked())

        # 设置帧类型
        # 如果选择了errorFrame复选框，则设置帧类型为错误帧
        # 如果选择了remoteFrame复选框，将帧类型设置为远程请求帧
        if self.m_ui.errorFrame.isChecked():
            frame.setFrameType(QCanBusFrame.ErrorFrame)
        elif self.m_ui.remoteFrame.isChecked():
            frame.setFrameType(QCanBusFrame.RemoteRequestFrame)

        self.send_frame.emit(frame)
        # 使用send_frame信号发送已经设置完成的QCanBusFrame对象。
        # 在PySide6中，可以通过信号-槽机制在对象之间进行通信，这里是使用信号来发送数据。
