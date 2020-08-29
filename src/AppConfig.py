from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from util import makeButton, SetEncoder
import DoubleClickWidgets
import json
import os

# keep macro in mapper._hotkeys during recording of macro

class AppConfig(QWidget):
    """Separate window to display configuration options.

    Class Attributes:
        recorder (Hotkeys): Hotkey recorder used throughout the program.
        ui (Ui_MainWindow): Main window of this program.
        config (dict): Dictionary that holds user configurable options.
    """

    
    _CONFIG_FILE = "config.json"
    recorder = None
    mainUI = None
    shortcutFunctions = None
    config = {
        'shortcuts': {
            'recordShortcut': [None, ''],
        },
    }

    def __init__(self, parent=None):
        """Constructor to set up layout of the window.

        Args:
            parent (QWidget): QWidget that will be set as this widget's parent.
        """
        super().__init__(parent)
        configLayout = QVBoxLayout()
        recordShortcut = QHBoxLayout()
        recordShortcut.addWidget(QLabel('Toggle Record Shortcut: '))
        configDefault = AppConfig.config['shortcuts']['recordShortcut']
        defaultText = configDefault[1] if configDefault[1] \
                else 'Double Click To Edit'
        shortcut = DoubleClickWidgets.EditLabelKeySequence(AppConfig.recorder,
                defaultText, customFunc=AppConfig.mainUI.recordShortcut.emit,
                config='recordShortcut')

        shortcut.keys = configDefault[0]
        recordShortcut.addWidget(shortcut)
        recordShortcut.addWidget(shortcut.getEditor())

        buttonLayout = QHBoxLayout()
        saveButton = makeButton(self, "image: url(:/images/images/save.png);\n"
                "padding: 4px;")
        saveButton.setToolTip('Save to disc')
        buttonLayout.addWidget(saveButton)
        saveButton.clicked.connect(AppConfig._writeConfig)

        configLayout.addLayout(recordShortcut)
        configLayout.addLayout(buttonLayout)
        self.setLayout(configLayout)

    @classmethod
    def setUpClass(cls, recorder, mainUI):
        cls.recorder = recorder
        cls.mainUI = mainUI
        cls.shortcutFunctions = {
            'recordShortcut': mainUI.recordShortcut.emit
        }

    @classmethod
    def _writeConfig(cls):
        with open(cls._CONFIG_FILE, 'w') as configFile:
            cls.config = {
                **cls.config, 
                **json.dump(cls.config, configFile, cls=SetEncoder)
            }

    @classmethod
    def readConfig(cls):
        if os.path.exists(cls._CONFIG_FILE):
            with open(cls._CONFIG_FILE, 'r') as configFile:
                writtenConfig = json.load(configFile)

            shortcuts = cls.config['shortcuts']
            print(shortcuts)
            # Python pattern matching is so nice
            for option, (keys, keyString) in shortcuts.items():
                if keys:
                    keys = set(keys)
                    shortcuts[option] = keys
                    cls.recorder.addHotkey(keys,
                            customFunc=cls.shortcutFunctions[option],
                            recording=False)

    def closeEvent(self, event):
        #TODO
        hotkeyRecorder = AppConfig.recorder.hotkeyRecorder
        if hotkeyRecorder and hotkeyRecorder.is_alive():
            AppConfig.recorder.finishRecording()

