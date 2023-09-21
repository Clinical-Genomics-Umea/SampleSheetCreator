from PyQt5.QtGui import QColor
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
from collections import defaultdict
import re


class CustomValidator(QtGui.QValidator):
    def __init__(self, pattern, parent=None):
        QtGui.QValidator.__init__(self, parent)

        self.states = {'invalid':      QtGui.QValidator.Invalid,
                      'intermediate':  QtGui.QValidator.Intermediate,
                      'acceptable':    QtGui.QValidator.Acceptable,
                      }
        self.rep = re.compile(pattern)
        self.rep_intermediate = re.compile('\w,')

    def returnState(self, state, text, pos):
        return self.states[state], text, pos

    def validate(self, textInput, pos):
        match = self.rep.search(textInput)
        if match and len(match.groups()) == 2 and match.group(1) and match.group(2):
            if match.group(1) != match.group(2):
                return self.returnState('acceptable', textInput, pos)
            else:
                return self.returnState('invalid', textInput, pos)
        elif match:
            match2 = self.rep_intermediate.search(textInput)
            if match2:
                return self.returnState('intermediate', textInput, pos)
            return self.returnState('acceptable', textInput, pos)
        else:
            return self.returnState('invalid', textInput, pos)


class InputValidate(QtWidgets.QStyledItemDelegate):
    def __init__(self, fields):
        super(InputValidate, self).__init__()
        self._fields = fields

        self._c2validator = {}
        self._c2paint = defaultdict(dict)

        input_fields_order = self._fields['input_fields_order']
        for field in input_fields_order:
            if self._fields['model_fields'][field]['value_validate_regex']:
                col = input_fields_order.index(field)
                regex = self._fields['model_fields'][field]['value_validate_regex']
                self._c2validator[col] = CustomValidator(regex)

            if self._fields['model_fields'][field]['value_color']:
                for value in self._fields['model_fields'][field]['value_color']:
                    col = input_fields_order.index(field)
                    self._c2paint[col][value] = QColor(self._fields['model_fields'][field]['value_color'][value][0],
                                                       self._fields['model_fields'][field]['value_color'][value][1],
                                                       self._fields['model_fields'][field]['value_color'][value][2]
                                                       )

    def createEditor(self, widget, option, index):
        if not index.isValid():
            return 0

        for col in self._c2validator.keys():
            if index.column() == col:
                editor = QtWidgets.QLineEdit(widget)
                editor.setValidator(self._c2validator[col])
                return editor

        return super(InputValidate, self).createEditor(widget, option, index)

    def paint(self, painter, option, index):
        if not index.isValid():
            return 0

        for col in self._c2paint.keys():
            if index.column() == col:
                ix = index.model().index(index.row(), index.column())
                value = ix.data().strip()

                if value in self._c2paint[col]:
                    painter.fillRect(option.rect, self._c2paint[col][value])
                    QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
                # elif value == self.f:
                #     painter.fillRect(option.rect, QColor(255, 230, 242))
                #     QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
                else:
                    QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
            else:
                QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)


# class NValidate(QtWidgets.QStyledItemDelegate):
#     def __init__(self, col, constraints):
#         super(NValidate, self).__init__()
#         self.col = col
#         self.orig_constraints = constraints
#         rx_val = "^[" + "".join(self.orig_constraints) + "]$"
#         print(rx_val)
#
#         rx = QtCore.QRegExp(rx_val)
#         self.validator = QtGui.QRegExpValidator(rx, self)
#
#     def createEditor(self, widget, option, index):
#         if not index.isValid():
#             return 0
#         if index.column() == self.col:
#             editor = QtWidgets.QLineEdit(widget)
#             editor.setValidator(self.validator)
#             return editor
#         return super(NValidate, self).createEditor(widget, option, index)
#
#     def paint(self, painter, option, index):
#         if not index.isValid():
#             return 0
#         if index.column() == self.col:
#             ix = index.model().index(index.row(), index.column())
#             value = ix.data().strip()
#             if value in self.orig_constraints:
#                 painter.fillRect(option.rect, QColor(204, 230, 255))
#                 QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
#             else:
#                 QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
#         else:
#             QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
