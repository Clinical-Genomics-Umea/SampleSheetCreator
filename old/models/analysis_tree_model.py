#! python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


class AnalysisTreeModel(QtGui.QStandardItemModel):
    def __init__(self, indata):
        super(AnalysisTreeModel, self).__init__()
        try:
            for method, options1 in indata['definitions'].items():
                method_item = QtGui.QStandardItem(method)
                self.appendRow(method_item)
                for panel, options2 in options1.items():
                    panel_item = QtGui.QStandardItem(panel)
                    method_item.appendRow(panel_item)
                    for analysis in options2:
                        analysis_item = QtGui.QStandardItem(analysis)
                        panel_item.appendRow(analysis_item)
        except:
            pass
