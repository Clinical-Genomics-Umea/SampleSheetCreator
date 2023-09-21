import os
from collections import defaultdict
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ui.generate import Ui_Generate
from ui.validation_error import Ui_Dialog

import datetime


def tree(): return defaultdict(tree)


class ValErrDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super(ValErrDialog, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.on_click)

    def on_click(self):
        self.close()

class Generate(QWidget, Ui_Generate):
    def __init__(self, parent):
        super(Generate, self).__init__()
        self.setupUi(self)

        self.treeWidget.setUniformRowHeights(True)
        # self.plainTextEdit.setStyleSheet("""QPlainTextEdit {font-family: Courier;}""")

        self.populate_review(parent)
        self.populate_plainTextEdit(parent)

        self.pushButton_cancel.clicked.connect(self.cancel)
        self.pushButton_ok.clicked.connect(lambda: self.save(parent))

        self.setWindowTitle("Review and Save")
        self.setWindowIcon(QtGui.QIcon('icons/icon.png'))

        self.grip1 = QSizeGrip(self)
        self.verticalLayout.addWidget(self.grip1, 0, Qt.AlignRight | Qt.AlignBottom)

    def cell_contains_text(self, item):
        if item != None:
            item_txt = item.text()
            if any(chr.isalnum() for chr in item_txt):
                return True
            else:
                return False
        else:
            return False

    def show_valerrordialog(self, incrows):
        d = ValErrDialog()
        for i in incrows:
            d.plainTextEdi_missing_fields.appendPlainText(i)

        d.exec_()

    def crow2list(self, parent, c_row):

        data_row = []

        cmethod = parent.comboBox_method.currentText()
        cinstrument = parent.comboBox_instrument.currentText()

        for field in parent.sdata_fields_ss:
            if parent.sdata_fields_ss[field]['ss']:
                if parent.sdata_fields_ss[field]['c_p'] >= 0:

                    if field is "N":

                        column = parent.sdata_fields_ss[field]['c_p']

                        pwidget = parent.tableWidget_construct.cellWidget(c_row, column)
                        checkbox = pwidget.findChild(QCheckBox)
                        state = checkbox.checkState()

                        if state == 2:
                            data_row.append('NORMAL')
                        else:
                            data_row.append('STANDARD')

                    elif field is 'Group':
                        item = parent.tableWidget_construct.item(c_row, parent.sdata_fields_ss[field]['c_p'])
                        if self.cell_contains_text(item):
                            value = item.text()
                            value = value.replace(",", "/")
                            data_row.append(value)
                        else:
                            data_row.append('')

                    else:
                        item = parent.tableWidget_construct.item(c_row, parent.sdata_fields_ss[field]['c_p'])
                        if self.cell_contains_text(item):
                            value = item.text()
                            data_row.append(value.strip())
                        else:
                            data_row.append("")

                else:
                    if field is "Panel_Target":
                        item = parent.tableWidget_construct.item(c_row, parent.sdata_fields_ss['Panel']['c_p'])
                        cpanel = ""

                        if self.cell_contains_text(item):
                            cpanel = item.text()

                        value = parent.yconfig['Methods'][cmethod]['Panels'][cpanel]['PanelTarget']

                        if len(value) > 0:
                            data_row.append(value.strip())
                        else:
                            data_row.append("")

                    elif field is 'Sample_Name':
                        item = parent.tableWidget_construct.item(c_row,
                                                                 parent.sdata_fields_ss['Sample_ID']['c_p'])
                        if self.cell_contains_text(item):
                            value = item.text()
                            data_row.append(value.strip())
                        else:
                            data_row.append("")

                    elif field is 'index2':
                        item = parent.tableWidget_construct.item(c_row,
                                                                 parent.sdata_fields_ss['I5_Index_ID']['c_p'])
                        if self.cell_contains_text(item):
                            i = item.text().strip()

                            if i in parent.yindices_mod[cmethod][cinstrument]:
                                iseq5 = parent.yindices_mod[cmethod][cinstrument][i]
                                data_row.append(iseq5.strip())
                            else:
                                data_row.append('')
                        else:
                            data_row.append('')

                    elif field is 'index':
                        item = parent.tableWidget_construct.item(c_row,
                                                                 parent.sdata_fields_ss['I7_Index_ID']['c_p'])

                        if self.cell_contains_text(item):
                            i = item.text().strip()
                            if i in parent.yindices_mod[cmethod][cinstrument]:
                                iseq7 = parent.yindices_mod[cmethod][cinstrument][i]
                                data_row.append(iseq7.strip())
                            else:
                                data_row.append('')
                        else:
                            data_row.append('')

                    elif field is 'Method':
                        data_row.append(cmethod.strip())

        return data_row

    def populate_review(self, parent):

        rows = parent.tableWidget_construct.rowCount()

        header = []
        name2col = {}
        i = 0
        for key in parent.sdata_fields_ss.keys():
            if parent.sdata_fields_ss[key]['ss']:
                header.append(key)
                name2col[key] = i
                i += 1

        self.treeWidget.setHeaderLabels(header)

        data_dict = tree()
        tree_dict = tree()

        for row in range(rows):
            sample_item  = parent.tableWidget_construct.item(row, parent.sdata_fields_ss['Sample_ID']['c_p'])

            if self.cell_contains_text(sample_item):
                current_row_data = self.crow2list(parent, row)
                sample_id = current_row_data[name2col['Sample_ID']]
                batch_list = current_row_data[name2col['Group']].split("/")
                for batch in batch_list:
                    data_dict[batch][sample_id] = current_row_data

        for batch, subdict in data_dict.items():
            batchname = "Group " + batch
            if not tree_dict[batch]:
                tree_dict[batch] = QTreeWidgetItem(self.treeWidget)
                tree_dict[batch].setText(0, batchname)
                tree_dict[batch].setFlags(tree_dict[batch].flags()
                                        | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            for sample_id, current_row_data in subdict.items():
                child = QTreeWidgetItem(tree_dict[batch])
                for index, value in enumerate(current_row_data):
                    child.setText(int(index), str(value))
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    child.setCheckState(0, Qt.Unchecked)

    def populate_plainTextEdit(self, parent):
        SampleSheetCreator_settings = QSettings('vll', 'SampleSheetCreator')

        rows = parent.tableWidget_construct.rowCount()

        samplesheet = []

        tmp_date = parent.dateEdit.date()
        date_var = tmp_date.toPyDate()
        run = parent.lineEdit_run.text()
        institute = SampleSheetCreator_settings.value('institute', type=str)
        investigator = parent.comboBox_investigator.currentText()
        cmethod = parent.comboBox_method.currentText()
        description_tmp = parent.plainTextEdit.toPlainText()
        description_tmp = description_tmp.replace(",", " ")
        description = description_tmp.replace("\n", " ")

        header_dict = parent.yconfig['Methods'][cmethod]['Header']

        samplesheet.append('[Header]')

        for key, value in header_dict.items():
            samplesheet.append(','.join([str(key), str(value)]))

        samplesheet.append(','.join(["Investigator Name", str(investigator)]))
        samplesheet.append(','.join(["Experiment Name", str(run)]))
        samplesheet.append(','.join(["Date", str(date_var)]))
        samplesheet.append(','.join(["Description", str(description)]))
        samplesheet.append(','.join(["Institute", str(institute)]))

        samplesheet.append(",")

        """ enter settings data """
        settings_dict = parent.yconfig['Methods'][cmethod]['Settings']

        samplesheet.append('[Settings]')
        for key, value in settings_dict.items():
            if key != "Reads":
                samplesheet.append(','.join([str(key), str(value)]))

        samplesheet.append(",")

        """ enter reads data """
        samplesheet.append('[Reads]')
        cmethod = parent.comboBox_method.currentText()
        reads_list = parent.yconfig['Methods'][cmethod]['Settings']['Reads']
        for read in reads_list:
            samplesheet.append(str(read))

        samplesheet.append(",")

        samplesheet.append('[Data]')

        header = []
        for key in parent.sdata_fields_ss.keys():
            if parent.sdata_fields_ss[key]['ss']:
                header.append(key)

        header_str = ','.join(header)
        samplesheet.append(header_str)

        for r in range(rows):
            item = parent.tableWidget_construct.item(r, parent.sdata_fields_ss['Sample_ID']['c_p'])
            if self.cell_contains_text(item):
                data_row = self.crow2list(parent, r)
                data_row_str = ','.join(data_row)
                samplesheet.append(data_row_str)

        for ss_row in samplesheet:
            self.plainTextEdit.appendPlainText(ss_row)

    def cancel(self):
        self.close()

    def find_unchecked(self):
        unchecked = 0
        checked = 0

        root = self.treeWidget.invisibleRootItem()
        child1_count = root.childCount()

        for i in range(child1_count):
            child1 = root.child(i)

            child2_count = child1.childCount()

            for j in range(child2_count):
                child2 = child1.child(j)

                if child2.checkState(0) == QtCore.Qt.Unchecked:
                    unchecked += 1
                else:
                    checked += 1

        return unchecked, checked

    def save(self, parent):

        unchecked, checked = self.find_unchecked()

        print(unchecked, checked)

        if unchecked == 0:

            now = datetime.datetime.now()
            datetime_str = now.strftime("%Y-%m-%d.%H.%M.%S")
            print(datetime_str)

            path = parent.lineEdit_path.text()

            samplesheet_file = "SampleSheet_" + datetime_str + ".csv"

            path_file = os.path.join(path, samplesheet_file)

            print(path)
            print(path_file)

            ss_out = self.plainTextEdit.toPlainText()

            if not os.path.isdir(path):
                try:
                    os.makedirs(path)
                except OSError:
                    print("could not create folder")

            with open(path_file, "w") as f:
                f.write(ss_out)

            self.close()
        else:
            checkstr = "All samples not checked. Unchecked: " + str(unchecked) + ", Checked: " + str(checked)
            incomp_data = [checkstr]
            self.show_valerrordialog(incomp_data)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Generate = QtWidgets.QDialog()
    ui = Ui_Generate()
    ui.setupUi(Generate)
    Generate.show()
    sys.exit(app.exec_())
