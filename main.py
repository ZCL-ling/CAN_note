# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtCore import QCoreApplication, QLoggingCategory
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow

"""PySide6 port of the CAN example from Qt v6.x"""

# QCoreApplication类是一个核心应用程序类，用于在PySide6应用程序中处理事件循环和系统事件。

if __name__ == "__main__":
    QLoggingCategory.setFilterRules("qt.canbus* = true")
    a = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(QCoreApplication.exec())

