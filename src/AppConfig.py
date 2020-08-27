from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
import DoubleClickWidgets

# keep macro in mapper._hotkeys during recording of macro

class AppConfig(QWidget):
    """Separate window to display configuration options.

    Attributes:
        recorder (Hotkeys): Hotkey recorder used throughout the program.
    """

    config = {
        'recordShortcut': (None, '')
    }

    def __init__(self, recorder, ui, parent=None):
        """Constructor to set up layout of the window.

        Args:
            recorder (Hotkeys): Hotkey recorder used throughout the program.
            ui (Ui_MainWindow): Main window of this program.
            config (dict): Dictionary that holds user configurable options.
            parent (QWidget): QWidget that will be set as this widget's parent.
        """
        super().__init__(parent)
        self.recorder = recorder
        configLayout = QVBoxLayout()
        recordShortcut = QHBoxLayout()
        recordShortcut.addWidget(QLabel('Toggle Record Shortcut: '))
        configDefault = AppConfig.config['recordShortcut']
        defaultText = configDefault[1] if configDefault[1] \
                else 'Double Click To Edit'
        shortcut = DoubleClickWidgets.EditLabelKeySequence(recorder,
                defaultText, customFunc=ui.recordShortcut.emit,
                config='recordShortcut')

        shortcut.keys = configDefault[0]
        recordShortcut.addWidget(shortcut)
        recordShortcut.addWidget(shortcut.getEditor())
        configLayout.addLayout(recordShortcut)
        self.setLayout(configLayout)

    def closeEvent(self, event):
        #TODO
        hotkeyRecorder = self.recorder.hotkeyRecorder
        if hotkeyRecorder and hotkeyRecorder.is_alive():
            self.recorder.finishRecording()

