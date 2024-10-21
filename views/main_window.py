#! python
# -*- coding: utf-8 -*-
import os
import sys

import yaml
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QSizePolicy,
    QFileDialog,
    QWidget,
    QPushButton,
    QGraphicsScene,
    QGraphicsView,
    QFrame,
    QTabWidget,
)

from PySide6.QtGui import QAction, QActionGroup, QPainter, QIcon
from PySide6.QtCore import QPropertyAnimation, Qt, QSize

from models.utils import read_yaml_file
from views.settings import SettingsWidget
from modules.WaitingSpinner.spinner.spinner import WaitingSpinner
from views.visibility import ColumnsTreeWidget
from models.models import SampleSheetModel
from views.indexes import IndexKitToolbox
from views.make import SampleSheetEdit
from views.applications import ApplicationProfiles
from views.run import RunSetup, RunInfoWidget
from views.samplesheet import SampleSheetV2
from views.validation import (
    IndexDistanceValidationWidget,
    PreValidationWidget,
    ColorBalanceValidationWidget,
)

from views.sampleview import SampleWidget
from views.ui.mw import Ui_MainWindow
import qtawesome as qta

sys.argv += ["-platform", "windows:darkmode=2"]
__author__ = "Pär Larsson"
__version__ = "2.0.0.a"

# os.environ['QT_API'] = 'pyside6'


def get_dialog_options():
    return QFileDialog.Options() | QFileDialog.DontUseNativeDialog


def clear_layout(layout):
    # Iterate through layout items in reverse order
    while layout.count():
        # Take the first item (from the top)
        item = layout.takeAt(0)

        # If the item is a layout, recursively clear it
        if item.layout():
            clear_layout(item.layout())

        # If the item is a widget, remove it and delete it
        elif item.widget():
            widget = item.widget()
            widget.setParent(None)  # Remove from parent
            widget.deleteLater()  # Schedule for deletion


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.main_version = __version__
        self.setWindowTitle(f"Illuminator {self.main_version}")
        self.setWindowIcon(
            QIcon(qta.icon("ri.settings-line", options=[{"draw": "image"}]))
        )
        self.setMinimumWidth(1000)
        self.left_toolBar.setMovable(False)
        self.left_toolBar.setIconSize(QSize(40, 40))

        self.spinner = WaitingSpinner(self)

        # left sidemenu options
        self.file_action = QAction("file", self)
        self.run_action = QAction("run", self)
        self.profiles_action = QAction("profiles", self)
        self.indexes_action = QAction("indexes", self)
        self.validate_action = QAction("validate", self)
        self.make_action = QAction("make", self)
        self.settings_action = QAction("settings", self)
        # self.edit_action = QAction("edit", self)

        self.qagroup_leftmenu = QActionGroup(self)
        self.qagroup_mainview = QActionGroup(self)

        # right sidemenu options
        self.columns_settings_button = QPushButton("Columns")
        self.columns_settings_button.setObjectName("columns_settings")

        self.left_action_tab_map = {}
        self.left_tool_actions_setup()

        self.right_action_tab_map = {}
        self.right_tool_actions_setup()

        sample_settings_path = read_yaml_file("config/sample_settings.yaml")
        self.samples_model = SampleSheetModel(sample_settings_path)
        self.samples_widget = SampleWidget(self.samples_model)
        self.sample_tableview = self.samples_widget.sampleview
        self.sample_tableview_setup()

        # columns settings widget
        self.columns_treeview = ColumnsTreeWidget(sample_settings_path)
        self.columns_listview_setup()

        self.left_tab_anim = {}
        self.right_tab_anim = {}

        self.menu_animations_setup()

        self.leftmenu_stackedWidget.setMaximumWidth(0)
        self.leftmenu_stackedWidget.hide()
        self.rightmenu_stackedWidget.setMaximumWidth(0)
        self.rightmenu_stackedWidget.hide()

        # self.file_tab_setup()

        self.run_setup_widget = RunSetup(Path("config/run/run_settings.yaml"))
        self.run_info_widget = RunInfoWidget()
        self.run_setup()

        self.prevalidate_widget = PreValidationWidget(
            Path("config/validation/validation_settings.yaml"),
            self.samples_model,
            self.run_info_widget,
        )
        self.indexdistancevalidation_widget = IndexDistanceValidationWidget(
            Path("config/validation/validation_settings.yaml"),
            self.samples_model,
            self.run_info_widget,
        )

        self.colorbalancevalidation_widget = ColorBalanceValidationWidget(
            Path("config/validation/validation_settings.yaml"),
            self.samples_model,
            self.run_info_widget,
        )

        self.validation_tabwidget = QTabWidget()

        self.validate_setup()

        self.samplesheetedit = SampleSheetEdit()
        self.samplesheetedit_setup()

        self.indexes_widget = IndexKitToolbox(Path("config/indexes/indexes_json"))
        self.indexes_setup()

        self.application_profiles_widget = ApplicationProfiles(
            Path("config/applications"), self.sample_tableview
        )
        self.profile_setup()

        self.menu_animations_setup()

        self.leftmenu_stackedWidget.setMaximumWidth(0)
        self.rightmenu_stackedWidget.setMaximumWidth(0)

        self.settings = SettingsWidget()
        self.settings_setup()

    def settings_setup(self):
        layout = self.main_settings.layout()
        layout.addWidget(self.settings)

    def validate_setup(self):
        layout = self.main_validation.layout()
        layout.addWidget(self.validation_tabwidget)

        self.validation_tabwidget.addTab(self.prevalidate_widget, "pre-validation")
        self.prevalidate_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.validation_tabwidget.addTab(
            self.indexdistancevalidation_widget, "index distance validation"
        )
        self.indexdistancevalidation_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.validation_tabwidget.addTab(
            self.colorbalancevalidation_widget, "color balance validation"
        )
        self.colorbalancevalidation_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        self.runvalidate_pushButton.clicked.connect(self.run_validation)

    def run_validation(self):
        self.spinner.start()
        self.prevalidate_widget.run_validate()
        self.indexdistancevalidation_widget.run_validate()
        self.colorbalancevalidation_widget.run_validate()
        self.spinner.stop()

    def samplesheetedit_setup(self):
        layout = self.main_make.layout()
        layout.addWidget(self.samplesheetedit)

    def columns_listview_setup(self):
        layout = self.rightmenu_columnsettings.layout()
        layout.addWidget(self.columns_treeview)

        self.columns_treeview.field_visibility_state_changed.connect(
            self.sample_tableview.set_column_visibility_state
        )
        self.sample_tableview.field_visibility_state_changed.connect(
            self.columns_treeview.set_column_visibility_state
        )

    def menu_animations_setup(self):
        self.left_tab_anim["open"] = self.make_animation(
            self.leftmenu_stackedWidget, 0, 300
        )
        self.left_tab_anim["close"] = self.make_animation(
            self.leftmenu_stackedWidget, 300, 0
        )

        self.right_tab_anim["open"] = self.make_animation(
            self.rightmenu_stackedWidget, 0, 250
        )
        self.right_tab_anim["close"] = self.make_animation(
            self.rightmenu_stackedWidget, 250, 0
        )

    @staticmethod
    def make_animation(menu_widget, start_width, end_width):
        animation = QPropertyAnimation(menu_widget, b"maximumWidth")
        animation.setStartValue(start_width)
        animation.setEndValue(end_width)
        animation.setDuration(5)

        return animation

    def get_vertical_button_view(self, button: QPushButton):
        button.setFixedSize(100, 20)
        button.setContentsMargins(0, 0, 0, 0)
        button.setStyleSheet("QPushButton {border: none;}")
        button.setIcon(qta.icon("ph.rows-light"))

        button_size = button.size()

        scene = QGraphicsScene(self)
        proxy_widget = scene.addWidget(button)
        proxy_widget.setRotation(90)

        view = QGraphicsView(self.right_sidebar_widget)
        view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        view.setFrameStyle(QFrame.NoFrame)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setFixedHeight(button_size.width() + 2)
        view.setFixedWidth(button_size.height() + 2)

        view.setScene(scene)
        view.setContentsMargins(0, 0, 0, 0)

        return view

    def sample_tableview_setup(self):

        layout = self.main_data.layout()
        clear_layout(layout)
        layout.addWidget(self.samples_widget)
        self.main_stackedWidget.setCurrentWidget(self.main_data)

    def run_setup(self):
        self.leftmenu_runsetup.layout().addWidget(self.run_setup_widget)
        self.verticalLayout.insertWidget(0, self.run_info_widget)
        self.run_info_widget.setup(self.run_setup_widget.get_data())
        self.run_setup_widget.set_button.clicked.connect(
            self.handle_run_set_button_click
        )

    def handle_run_set_button_click(self):
        run_info = self.run_setup_widget.get_data()
        self.run_info_widget.set_data(run_info)

    def indexes_setup(self):
        layout = self.leftmenu_indexes.layout()
        layout.addWidget(self.indexes_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

    def profile_setup(self):
        layout = self.leftmenu_profiles.layout()
        layout.addWidget(self.application_profiles_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

    def left_tool_actions_setup(self):
        """
        Set up the tool actions for the application.

        This function initializes the action-to-tab mapping for the different tool actions
        available in the application. It also sets up the icons, checkable states, and
        connections for each tool action.
        """
        self.left_action_tab_map = {
            "file": self.leftmenu_file,
            "run": self.leftmenu_runsetup,
            "profiles": self.leftmenu_profiles,
            "indexes": self.leftmenu_indexes,
            "config": self.leftmenu_config,
        }

        self.file_action.setIcon(qta.icon("msc.files", options=[{"draw": "image"}]))
        self.file_action.setCheckable(True)
        self.file_action.setChecked(False)
        self.file_action.triggered.connect(self.click_action_leftmenu)

        self.run_action.setIcon(
            qta.icon("msc.symbol-misc", options=[{"draw": "image"}])
        )
        self.run_action.setCheckable(True)
        self.run_action.setChecked(False)
        self.run_action.triggered.connect(self.click_action_leftmenu)

        self.profiles_action.setIcon(
            qta.icon("msc.symbol-method", options=[{"draw": "image"}])
        )
        self.profiles_action.setCheckable(True)
        self.profiles_action.setChecked(False)
        self.profiles_action.triggered.connect(self.click_action_leftmenu)

        self.indexes_action.setIcon(
            qta.icon("mdi6.barcode", options=[{"draw": "image"}])
        )
        self.indexes_action.setCheckable(True)
        self.indexes_action.setChecked(False)
        self.indexes_action.triggered.connect(self.click_action_leftmenu)

        self.settings_action.setIcon(
            qta.icon("msc.settings-gear", options=[{"draw": "image"}])
        )
        self.settings_action.setCheckable(True)
        self.settings_action.setChecked(False)
        self.settings_action.triggered.connect(self.click_action_mainview)

        self.validate_action.setIcon(
            qta.icon("msc.check-all", options=[{"draw": "image"}])
        )
        self.validate_action.setCheckable(True)
        self.validate_action.setChecked(False)
        self.validate_action.triggered.connect(self.click_action_mainview)

        self.make_action.setIcon(qta.icon("msc.coffee", options=[{"draw": "image"}]))
        self.make_action.setCheckable(True)
        self.make_action.setChecked(False)
        self.make_action.triggered.connect(self.click_action_mainview)

        # self.edit_action.setIcon(qta.icon('msc.unlock', options=[{'draw': 'image'}]))
        # self.edit_action.setCheckable(True)
        # self.edit_action.setChecked(False)
        # self.edit_action.triggered.connect(self.click_action_mainview)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.qagroup_leftmenu.setExclusionPolicy(
            QActionGroup.ExclusionPolicy.ExclusiveOptional
        )
        self.qagroup_leftmenu.addAction(self.file_action)
        self.qagroup_leftmenu.addAction(self.run_action)
        self.qagroup_leftmenu.addAction(self.profiles_action)
        self.qagroup_leftmenu.addAction(self.indexes_action)

        self.left_toolBar.addAction(self.file_action)
        self.left_toolBar.addAction(self.run_action)
        self.left_toolBar.addAction(self.indexes_action)
        self.left_toolBar.addAction(self.profiles_action)

        self.qagroup_mainview.setExclusionPolicy(
            QActionGroup.ExclusionPolicy.ExclusiveOptional
        )
        self.qagroup_mainview.addAction(self.validate_action)
        self.qagroup_mainview.addAction(self.make_action)
        # self.qagroup_mainview.addAction(self.edit_action)
        self.qagroup_mainview.addAction(self.settings_action)

        self.left_toolBar.addAction(self.validate_action)
        self.left_toolBar.addAction(self.make_action)
        self.left_toolBar.addWidget(spacer)
        # self.left_toolBar.addAction(self.edit_action)
        self.left_toolBar.addAction(self.settings_action)

    def right_tool_actions_setup(self):
        """
        Set up the tool actions for the application.

        This function initializes the action-to-tab mapping for the different tool actions
        available in the application. It also sets up the icons, checkable states, and
        connections for each tool action.
        """
        self.right_action_tab_map = {"columns_settings": self.rightmenu_columnsettings}

        view = self.get_vertical_button_view(self.columns_settings_button)
        layout = self.right_sidebar_widget.layout()
        layout.insertWidget(0, view)
        layout.setContentsMargins(0, 0, 0, 0)

        self.columns_settings_button.setCheckable(True)
        self.columns_settings_button.setChecked(False)

        self.columns_settings_button.clicked.connect(self.on_right_tool_click)

    def on_right_tool_click(self):
        sender = self.sender()
        obj_id = sender.objectName()

        is_checked = sender.isChecked()
        menu_width = self.rightmenu_stackedWidget.width()
        menu_shown = menu_width > 0
        if is_checked and not menu_shown:
            self.rightmenu_stackedWidget.show()
            self.right_tab_anim["open"].start()
            self.rightmenu_stackedWidget.setCurrentWidget(
                self.right_action_tab_map[obj_id]
            )
        elif not is_checked and menu_shown:
            self.right_tab_anim["close"].start()
            self.rightmenu_stackedWidget.hide()
        else:
            self.rightmenu_stackedWidget.setCurrentWidget(
                self.right_action_tab_map[obj_id]
            )

    def on_edit_click(self):
        pass

    def leftmenu_shown(self):
        menu_width = self.leftmenu_stackedWidget.width()
        return menu_width > 0

    def click_action_leftmenu(self):
        button = self.sender()
        button_text = button.text()
        is_checked = button.isChecked()

        if is_checked:
            self.main_stackedWidget.setCurrentWidget(self.main_data)
            for action in self.qagroup_mainview.actions():
                action.setChecked(False)

        if is_checked and not self.leftmenu_shown():
            self.leftmenu_stackedWidget.show()
            self.left_tab_anim["open"].start()
            self.leftmenu_stackedWidget.setCurrentWidget(
                self.left_action_tab_map[button_text]
            )
        elif not is_checked and self.leftmenu_shown():
            self.left_tab_anim["close"].start()
            self.leftmenu_stackedWidget.hide()
        else:
            self.leftmenu_stackedWidget.setCurrentWidget(
                self.left_action_tab_map[button_text]
            )

    def click_action_mainview(self):
        button = self.sender()
        button_text = button.text()

        is_checked = button.isChecked()

        if self.leftmenu_shown():
            self.left_tab_anim["close"].start()
            self.leftmenu_stackedWidget.hide()

            for action in self.qagroup_leftmenu.actions():
                action.setChecked(False)

        self.main_stackedWidget.setCurrentWidget(self.main_data)

        if is_checked:
            if button_text == "validate":
                self.main_stackedWidget.setCurrentWidget(self.main_validation)

            elif button_text == "make":
                self.main_stackedWidget.setCurrentWidget(self.main_make)
                sample_df = self.samples_model.to_dataframe()
                run_info = self.run_info_widget.get_data()

                samplesheetv2 = SampleSheetV2(
                    header=run_info["Header"],
                    run_cycles=run_info["Reads"]["ReadProfile"],
                    # sequencing_data=run_info['Sequencing'],
                    sample_df=sample_df,
                )

                self.samplesheetedit.set_samplesheetdata(samplesheetv2.datalist())

            elif button_text == "settings":
                self.main_stackedWidget.setCurrentWidget(self.main_settings)

        else:
            self.main_stackedWidget.setCurrentWidget(self.main_data)

        # if button_text == "make":
        #     pass
        #
        # if button_text == "edit":
        #     pass
        #
        # if button_text == "config":
        #     pass
        #
        #

        # if is_checked and not menu_shown:
        #     self.leftmenu_stackedWidget.show()
        #     self.left_tab_anim["open"].start()
        #     self.leftmenu_stackedWidget.setCurrentWidget(self.left_action_tab_map[button_text])
        # elif not is_checked and menu_shown:
        #     self.left_tab_anim["close"].start()
        #     self.leftmenu_stackedWidget.hide()
        # else:
        #     self.leftmenu_stackedWidget.setCurrentWidget(self.left_action_tab_map[button_text])

    def on_config_click(self):
        if self.config_action.isChecked():
            self.main_stackedWidget.setCurrentWidget(self.main_validation)
        else:
            self.main_stackedWidget.setCurrentWidget(self.main_data)

    # def on_validate_click(self):
    #
    #     button = self.sender()
    #
    #     if button.isChecked():
    #         self.spinner_thread = SpinnerThread(self.spinner_overlay)
    #         self.spinner_thread.start()
    #
    #         self.main_stackedWidget.setCurrentWidget(self.main_validation)
    #         is_valid = self.prevalidate_widget.validate()
    #         if not is_valid:
    #             self.spinner_thread.stop()
    #             return
    #
    #         self.datavalidate_widget.validate()
    #         self.spinner_thread.stop()
    #     else:
    #         self.main_stackedWidget.setCurrentWidget(self.main_data)

    # def on_make_click(self):
    #
    #     button = self.sender()
    #
    #     if button.isChecked():
    #         self.main_stackedWidget.setCurrentWidget(self.main_make)
    #         samplesheetv2 = SampleSheetV2(self.run_info_widget.get_data(), self.samples_model.to_dataframe())
    #         self.samplesheetedit.set_samplesheetdata(samplesheetv2.get_data())
    #
    #     else:
    #         self.main_stackedWidget.setCurrentWidget(self.main_data)

    def load_worklist(self):
        options = get_dialog_options()
        return QFileDialog.getOpenFileName(
            self,
            "Open worklist file...",
            "",
            "Worklist files (*.txt *.csv)",
            options=options,
        )[0]

    def exit(self):
        sys.exit()
