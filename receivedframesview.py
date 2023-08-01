# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QPoint, Qt, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QApplication, QMenu, QTableView
# QPoint是用于表示平面上的点的类，Qt是Qt框架的核心模块，Slot是一个装饰器，用于声明一个槽函数
# QAction是用于创建菜单、工具栏和快捷键的动作的类，QKeySequence是用于表示键盘快捷键的类。

from receivedframesmodel import clipboard_text_role


class ReceivedFramesView(QTableView):

    def __init__(self, parent):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu) # 设置表格视图的上下文菜单策略为Qt.CustomContextMenu
        self.customContextMenuRequested.connect(self._context_menu) # 连接customContextMenuRequested信号到_context_menu槽函数

    @Slot(QPoint) # 右键菜单槽函数，在表格视图中右击时调用，根据当前选择的单元格显示不同的右键菜单选项。
    def _context_menu(self, pos):
        context_menu = QMenu("Context menu", self) # 创建一个QMenu对象作为右键菜单
        if self.selectedIndexes(): # 据当前是否有选中的单元格来决定是否添加"Copy"动作
            copy_action = QAction("Copy", self)
            copy_action.triggered.connect(self.copy_row) # 将其triggered信号连接到copy_row槽函数
            context_menu.addAction(copy_action) # 将"copy_action"添加到右键菜单context_menu中

        select_all_action = QAction("Select all", self)
        select_all_action.triggered.connect(self.selectAll)
        context_menu.addAction(select_all_action) #  将"select_all_action"添加到右键菜单context_menu中
        context_menu.exec(self.mapToGlobal(pos)) # 调用context_menu.exec(self.mapToGlobal(pos))来在指定位置显示右键菜单

    """
    设置表格模型。 可根据模型的列数 动态设置 表格视图的每列每列宽度

    参数:
    - model: 表格模型。
    """
    def set_model(self, model):
        super().setModel(model) # 将参数model作为表格视图的模型
        for i in range(0, model.columnCount()): # 循环遍历模型的列数
            size = model.headerData(i, Qt.Horizontal, Qt.SizeHintRole) # 获取标题的大小提示
            self.setColumnWidth(i, size.width()) # 设置每列的宽度

    """
    键盘按键事件处理函数。

    参数:
    - event: 键盘事件对象。

    if  elif  else
    """
    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self.copy_row()
        elif event.matches(QKeySequence.SelectAll):
            self.selectAll()
        else:
            super().keyPressEvent(event)

    """
    复制选中行的内容到剪贴板。(复制选中的行的内容 并 粘贴到 其他地方)
    """
    @Slot() 
    def copy_row(self):
        clipboard = QApplication.clipboard() # 获取应用程序的剪贴板对象
        str_row = ""   # 定义一个空字符串str_row来存储复制的行内容
        last_column = self.model().columnCount() - 1  # 获取模型的最后一列索引号
        for index in self.selectedIndexes():   # 过遍历选中的单元格
            str_row += index.data(clipboard_text_role) + " "    # 将单元格的数据逐个添加到str_row中，并在每行的末尾添加一个换行符\n。
            if index.column() == last_column:
                str_row += "\n"
        clipboard.setText(str_row)  # 将str_row的内容设置到剪贴板
