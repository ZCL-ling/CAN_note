# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from enum import IntEnum

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSize, Qt    

# QAbstractTableModel 可创建自定义的表格类型
# QModelIndex 访问和操作表格模型中的数据


# 枚举类，每个成员对应表格模型的一个列。
# 通过为每个列分配一个唯一的整数值，可以在代码中使用这些列进行 索引、访问和控制。

# 可以通过ReceivedFramesModelColumns.number、ReceivedFramesModelColumns.timestamp等方式来引用其中的成员。
# 有助于 提高代码的可读性
class ReceivedFramesModelColumns(IntEnum):
    number = 0
    timestamp = 1
    flags = 2
    can_id = 3
    DLC = 4
    data = 5
    count = 6

# Qt框架定义了一系列的标准角色，如Qt.DisplayRole，Qt.EditRole等，每个角色都有一个特定的预定义值。除此之外，也可以定义自定义角色。
# 自定义角色的值必须从Qt.UserRole开始，这个值为32。
# 所以在 clipboard_text_role = Qt.UserRole + 1中，clipboard_text_role的值就是33。

# 这个自定义的clipboard_text_role角色去 存储或者获取 与剪贴板相关的数据。
# 例如，你可以使用QStandardItem.setData(value, clipboard_text_role)来设置数据，
# 然后使用QStandardItem.data(clipboard_text_role)来获取数据。

clipboard_text_role = Qt.UserRole + 1

# 列表
# 对齐方式
# Qt.AlignRight | Qt.AlignVCenter：右对齐且垂直居中
# Qt.AlignCenter   水平居中对齐 并 垂直居中
# Qt.AlignLeft | Qt.AlignVCenter 左对齐且垂直居中

column_alignment = [Qt.AlignRight | Qt.AlignVCenter, Qt.AlignRight | Qt.AlignVCenter,
                    Qt.AlignCenter, Qt.AlignRight | Qt.AlignVCenter,
                    Qt.AlignRight | Qt.AlignVCenter, Qt.AlignLeft | Qt.AlignVCenter]


class ReceivedFramesModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_framesQueue = []  # 列表，用于存储表格模型中的 行
        self.m_framesAccumulator = [] # 列表，用于累积 或 暂存 某些数据
        self.m_queueLimit = 0 # 用于限制 行（也就是队列 Queue）的大小


    # 删除指定行数的数据
    # row:要删除的行的起始索引
    # count:删除的行数
    # parent:在模型中，删除行的父索引
    def remove_rows(self, row, count, parent):
        self.beginRemoveRows(parent, row, row + count - 1) #开始删除指定行的信号
        # 发出一个信号，通知视图，一个或多个行将被删除，parent 参数表示这些行的父项，之后两个参数定义了将被删除行的范围。
        
        self.m_framesQueue = self.m_framesQueue[0:row] + self.m_framesQueue[row + count:] #切片 左闭右开
        # 将m_framesQueue列表 切片 为两部分，并将指定行重新赋值为m_framesQueue.这样就删除了指定的行
        # 举个实际例子，画图就明白了，例如 row = 4, count = 3,删除row = 4开始的3行
        self.endRemoveRows() #删除行的结束信号
        return True

    # 用于返回表格模型中 指定 行 或 列的标题或者尺寸
    # section: 表示行 或者 列 的索引
    # orientation： 数据的方向，水平或者垂直
    # role: 用于请求不同类型数据的角色，例如 显示数据、尺寸提示等
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:    #水平方向的显示数据，返回相应的标题字符串
            if section == ReceivedFramesModelColumns.number:
                return "#"
            if section == ReceivedFramesModelColumns.timestamp:
                return "Timestamp"
            if section == ReceivedFramesModelColumns.flags:
                return "Flags"
            if section == ReceivedFramesModelColumns.can_id:
                return "CAN-ID"
            if section == ReceivedFramesModelColumns.DLC:
                return "DLC"
            if section == ReceivedFramesModelColumns.data:
                return "Data"

        if role == Qt.SizeHintRole and orientation == Qt.Horizontal:  # 水平方向的尺寸提示，返回相应的提示
            if section == ReceivedFramesModelColumns.number:
                return QSize(80, 25) # 宽度为80像素，高度为25像素
            if section == ReceivedFramesModelColumns.timestamp:
                return QSize(130, 25)
            if section == ReceivedFramesModelColumns.flags:
                return QSize(25, 25)
            if section == ReceivedFramesModelColumns.can_id:
                return QSize(50, 25)
            if section == ReceivedFramesModelColumns.DLC:
                return QSize(25, 25)
            if section == ReceivedFramesModelColumns.data:
                return QSize(200, 25)
        return None

    # 获取表格模型中指定索引位置的数据，根据角色来返回不同类型的数据
    # index:获取数据的索引
    # role：请求不同类型数据的角色，例如：DisplayRole、SizeHintRole等
    def data(self, index, role):
        if not self.m_framesQueue:
            return None
        row = index.row() # 获取行号
        column = index.column() # 获取列号
        # 根据 role 值 判断请求的数据类型
        # TextAlignmentRole 返回指定列 的对齐方式，column_alignment是一个列表，存储了不同列的对齐方式。
        # DisplayRole 返回 具体的显示数据，m_framesQueue列表中对应索引位置的数据
        # 如果 role 是 clipboard_text_role，则返回剪贴板文本数据，
        #         对于特定列（ReceivedFramesModelColumns.DLC 列）返回 [数据]，否则返回原始的值。
        
        # 条件表达式（也称为三元表达式）。如果column的值等于ReceivedFramesModelColumns.DLC，
        # 那么它就会返回一个字符串，该字符串包含方括号且方括号内为变量f指向的值，否则它就会直接返回f的值

        # 如果 role 是其他值，则返回 None
        if role == Qt.TextAlignmentRole:
            return column_alignment[index.column()]
        if role == Qt.DisplayRole:
            return self.m_framesQueue[row][column]
        if role == clipboard_text_role:
            f = self.m_framesQueue[row][column]
            return f"[{f}]" if column == ReceivedFramesModelColumns.DLC else f
        return None

    """
    返回表格模型中的行数。

    参数:
    -父索引有效，则返回 0。
    - 否则，返回 m_framesQueue 列表的长度。
    """
    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.m_framesQueue)

    """
    返回表格模型中的列数。

    参数:
    - parent: 父索引，默认为无效索引。

    返回值:
    - 如果父索引有效，则返回 0。
    - 否则，返回 ReceivedFramesModelColumns 列表的长度。
    """
    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else ReceivedFramesModelColumns.count

    """
    将 slvector 中的帧数据追加到 m_framesAccumulator 中。

    参数:
    - slvector: 帧数据序列。
    """
    def append_frames(self, slvector):
        self.m_framesAccumulator.extend(slvector)

    """
    返回是否需要更新表格模型。

    返回值:
    - 如果 m_framesAccumulator 中有积累的数据，则返回 True。
    - 否则，返回 False。
    """
    def need_update(self):
        return self.m_framesAccumulator

    """
    更新表格模型数据。

    如果 m_framesAccumulator 中有积累的数据，则将数据追加到表格模型中，并清空 m_framesAccumulator。

    如果启用了队列限制（m_queueLimit 不为 0），则根据限制进行处理，添加或删除数据行。
    """
    def update(self):
        if not self.m_framesAccumulator:
            return

        if self.m_queueLimit:
            self.append_frames_ring_buffer(self.m_framesAccumulator)
        else:
            self.append_frames_unlimited(self.m_framesAccumulator)
        self.m_framesAccumulator.clear()

    """
    将 slvector 中的帧数据追加到表格模型中，以环形缓冲区的方式处理。

    如果帧数量超过了队列限制，根据情况移除多余的数据行。

    参数:
    - slvector: 帧数据序列。
    """
    def append_frames_ring_buffer(self, slvector):
        slvector_len = len(slvector)
        row_count = self.rowCount()

        # 如果帧数量超过队列限制，根据情况移除多余的数据行
        if self.m_queueLimit <= row_count + slvector_len:
            if slvector_len < self.m_queueLimit:
                self.remove_rows(0, row_count + slvector_len - self.m_queueLimit + 1)
            else:
                self.clear()

        # 在表格模型的末尾插入数据行
        self.beginInsertRows(QModelIndex(), row_count, row_count + slvector_len - 1)
        if slvector_len < self.m_queueLimit:
            self.m_framesQueue.extend(slvector)
        else:
            self.m_framesQueue.extend(slvector[slvector_len - self.m_queueLimit:])
        self.endInsertRows()

    """
    将单个帧数据追加到表格模型中。

    参数:
    - slist: 单个帧数据。
    """
    def append_frame(self, slist):
        self.append_frames([slist])

    """
    将 slvector 中的帧数据追加到表格模型中，不进行队列限制处理。

    参数:
    - slvector: 帧数据序列。
    """
    def append_frames_unlimited(self, slvector):
        row_count = self.rowCount()
        self.beginInsertRows(QModelIndex(), row_count, row_count + len(slvector) - 1)
        self.m_framesQueue.extend(slvector)
        self.endInsertRows()

    """
    清空表格模型数据。
    """
    def clear(self):
        if self.m_framesQueue:
            self.beginResetModel()
            self.m_framesQueue.clear()
            self.endResetModel()

    """
    设置队列限制。

    设置 m_queueLimit 的值，并根据新的限制进行处理，移除多余的数据行。

    参数:
    - limit: 队列限制的值。
    """
    def set_queue_limit(self, limit):
        self.m_queueLimit = limit
        frame_queue_len = len(self.m_framesQueue)
        if limit and frame_queue_len > limit:
            self.remove_rows(0, frame_queue_len - limit)
