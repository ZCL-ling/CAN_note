# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtWidgets import QComboBox
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Slot

# 比特率选择框的类
# self指代一个下拉菜单或列表这样的控件
class BitRateBox(QComboBox):

    def __init__(self, parent): # 类的构造函数 或 初始化方法
        super().__init__(parent)
        self.m_isFlexibleDataRateEnabled = False
        self.m_customSpeedValidator = None
        self.m_customSpeedValidator = QIntValidator(0, 1000000, self)
        self.fill_bit_rates()
        self.currentIndexChanged.connect(self.check_custom_speed_policy)
        # self.currentIndexChanged.connect(self.check_custom_speed_policy) 
        # 是将当前对象的 currentIndexChanged 事件（通常对应于用户在界面上选择了一个不同的选项）
        # 连接到 check_custom_speed_policy 函数上。
        # 一旦 currentIndexChanged 事件触发（用户在界面上选择了一个不同的选项），check_custom_speed_policy 函数就会被调用。

    def bit_rate(self): # 返回一个 选择的或输入的 比特率值
        index = self.currentIndex() 
        # currentIndex() 是在 GUI 编程里很常用的一个方法，功能是取得当前被选中的项的索引
        if index == self.count() - 1: # 当前选中的元素是否是列表中的最后一个元素，索引从0开始
            return int(self.currentText) # 如果是最后一个元素被选中，那么就返回 当前选择框中的文字对应的整数
        return int(self.itemData(index)) # 如果不是最后一个选中，则返回索引对应项的数据

    def is_flexible_data_rate_enabled(self): # 是否启用了灵活数据速率
        return self.m_isFlexibleDataRateEnabled # 默认false

    # 是否启用灵活数据速率，并根据启用状态调整 自定义速率的最大值 和 比特率选项列表
    def set_flexible_date_rate_enabled(self, enabled): 
        self.m_isFlexibleDataRateEnabled = enabled
        self.m_customSpeedValidator.setTop(10000000 if enabled else 1000000)
        self.fill_bit_rates()
        # enabled 为真，最大值就设定为 10000000，否则设定为1000000
        # setTop 方法就是设定输入的最大值
        # 调用了前面定义的 fill_bit_rates 方法。
        # 可能是因为设置了新的数据率上限，所以需要重新填充或刷新可选范围

    # 槽函数 在索引变化时检查 是否选择了用户自定义速率，并相应设置 编辑框的属性和验证器。
    @Slot(int)
    def check_custom_speed_policy(self, idx):  
        is_custom_speed = not self.itemData(idx) # 用户是否选择了 "Custom" 选项的
        self.setEditable(is_custom_speed) # 用户在文本框中输入值
        if is_custom_speed:
            self.clearEditText() # 清除文本框的当前内容
            self.lineEdit().setValidator(self.m_customSpeedValidator)
            # 用户在文本框中的输入将受到 m_customSpeedValidator 的限制，
            # 只有符合 m_customSpeedValidator的规定，输入才会被接受
            # 用户的输入必须是0到100 0000之间的整数

    # 填充比特率选项，包括默认的固定速率选项 和 根据灵活数据启用状态 添加的数据速率的选项
    def fill_bit_rates(self):
        rates = [10000, 20000, 50000, 100000, 125000, 250000, 500000,
                 800000, 1000000]
        data_rates = [2000000, 4000000, 8000000]
        # data和data_rates之间的区别和联系:
        # rates和data_rates都是比特率，指定了CAN总线上的通信速度。
# 预设的比特率列表rates中包含的是一些常用的比特率，而data_rates则包含的是一些更高的比特率。

# 在CAN通信中，对于标准的CAN数据帧，它的比特率为rates中的值。
# 而对于某些设备支持的更快的CAN FD（Flexible Data-rate）数据帧，它的比特率则可能是data_rates中的值。
# rates是标准的CAN比特率列表，而data_rates是当支持CAN FD时的高速比特率列表。
# 二者的区别在于，对于特定的应用环境，可能需要不同的数据传输速度。

        self.clear() # 用于清空当前下菜单的项目
        for rate in rates:
            self.addItem(f"{rate}", rate) 
            # 通过在字符串前加上字母 f 并使用大括号 {} 来包含变量名，可以将变量的值插入到字符串中。
#            rate = 5.67
#            formatted_rate = f"The current rate is {rate}"
#            print(formatted_rate)
#            结果为：The current rate is 5.67

        if self.is_flexible_data_rate_enabled(): # 如果是True,则意味着 某些配置允许使用更高的比特率，则将data_rates中的比特率也添加到列表中。
            for rate in data_rates:
                self.addItem(f"{rate}", rate)

        self.addItem("Custom")
        self.setCurrentIndex(6)  # default is 500000 bps

        # "Custom"选项通常用于让 用户自定义 输入值，
        # 比如上述代码可能应用于比特率的设置中，
        # 当用户选择"Custom"选项后，就可以手动输入一个自定义的比特率，
        # 而不必限制于预设的rates或data_rates的值

#         self.setCurrentIndex(6)这行代码的作用是设置 下拉菜单 默认显示的选项。
# 在这段代码中，self应该是指代一个下拉菜单或列表这样的控件。
# 控件的setCurrentIndex方法用于设置控件当前选择的选项。
# 参数6表示将控件当前选择的选项设置为菜单列表中的第七个项（在Python中，列表的计数是从0开始的）。
# 在代码中，因为rates列表中的第七个数值是500000，
# 所以self.setCurrentIndex(6)将使得下拉菜单默认选择的比特率为500000bps。
# 换言之，就是将500000为默认值。如果用户不进行任何操作，系统就会采用这个默认值进行工作。
