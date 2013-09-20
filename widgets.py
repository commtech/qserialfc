import os
import re

from PySide.QtCore import Signal, Qt
from PySide.QtGui import *

from serial.tools import list_ports

from serialfc import *


class FHBoxLayout(QWidget):

    def __init__(self, *args, **kwargs):
        super(FHBoxLayout, self).__init__(*args, **kwargs)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def addWidget(self, widget):
        self.layout.addWidget(widget)


def is_serialfc_port(filename):
        if filename.find("serialfc") != -1:
            return True
        else:
            return False


class FPortName(FHBoxLayout):
    port_changed = Signal(Port)
    apply_changes = Signal(Port)

    def __init__(self, apply_changes_signal):
        super(FPortName, self).__init__()

        self.port = None

        self.label = QLabel("Port")
        self.combo_box = QComboBox()

        if os.name == 'nt':
            port_names = sorted([port[0] for port in list_ports.comports()])
        else:
            dev_nodes = os.listdir("/dev/")
            port_names = sorted(list(filter(is_serialfc_port, dev_nodes)))

        self.combo_box.addItems(port_names)
        self.combo_box.setCurrentIndex(-1)

        # Connect this after the combo box is already set to a -1 index
        self.combo_box.currentIndexChanged.connect(self.currentIndexChanged)

        apply_changes_signal.connect(self.apply_changes_clicked)

        self.addWidget(self.label)
        self.addWidget(self.combo_box)

    def set_port(self, port_name):
        index = self.combo_box.findText(port_name)

        if index >= 0:
            self.combo_box.setCurrentIndex(index)

    def currentIndexChanged(self):
        if self.port:
            self.port.close()
            self.port = None

        try:
            current_text = self.combo_box.currentText()
            if os.name == 'nt':
                self.port = Port(current_text)
            else:
                serialfc_num = re.sub("[^0-9]", "", current_text)
                ttyS_num = int(serialfc_num) + 4
                ttyS_name = '/dev/ttyS{}'.format(ttyS_num)

                self.port = Port(ttyS_name, '/dev/{}'.format(current_text))
        except IOError:
            """
            pySerial doesn't seem to correctly set any of it's
            attributes so we can't check for an already open error
            specifically
            """
            msgBox = QMessageBox()
            msgBox.setWindowTitle('Problem Opening Port')
            msgBox.setText('There was a problem opening this port. Make sure ' \
                            'the port isn\'t already open elsewhere.')
            msgBox.setIcon(QMessageBox.Information)
            msgBox.exec_()
        except:
            raise
        else:
            # The port was successfulyl opened at this point
            try:
                if self.port._card_type == CARD_TYPE_UNKNOWN:
                    msgBox = QMessageBox()
                    msgBox.setWindowTitle('Unknown Port')
                    msgBox.setText('This port isn\'t a Fastcom port.')
                    msgBox.setIcon(QMessageBox.Information)
                    msgBox.exec_()

                    self.port.close()
                    self.port = None
            except:
                """
                Doesn't have the _card_type option (likely using an older
                driver)
                """
                msgBox = QMessageBox()
                msgBox.setWindowTitle('Unknown Port')
                msgBox.setText('This port is either not a Fastcom port or ' \
                               'using an older driver.')
                msgBox.setIcon(QMessageBox.Information)
                msgBox.exec_()

                self.port.close()
                self.port = None

        # Will be None if port connection didn't complete
        self.port_changed.emit(self.port)

    def apply_changes_clicked(self):
        self.apply_changes.emit(self.port)


class PortChangedTracker(object):

    def __init__(self, port_widget):
        super(PortChangedTracker, self).__init__()

        port_widget.port_changed.connect(self._port_changed)
        port_widget.apply_changes.connect(self._apply_changes)

    def _port_changed(self, port):
        # There isn't a port opened so we disable the widget
        if port is None:
            self.setEnabled(False)
            return

        try:
            # Call port_changed on child class
            self.port_changed(port)
        except AttributeError:
            # This functionality isn't supported on this port
            self.unsupported()
        except:  # Raise any random unknown exceptions for debugging
            raise
        else:
            self.supported()

    def port_changed(self, port):
        raise NotImplementedError

    def _apply_changes(self, port):
        if self.isEnabled():
            self.apply_changes(port)

    def apply_changes(self, port):
        raise NotImplementedError

    def supported(self):
        self.setEnabled(True)
        self.setToolTip('')

    def unsupported(self):
        self.setEnabled(False)
        self.setToolTip('This feature is not supported on this port.')


class FTriggerLevel(FHBoxLayout, PortChangedTracker):
    def __init__(self, label, attribute, port_widget=None):
        FHBoxLayout.__init__(self)
        PortChangedTracker.__init__(self, port_widget)

        self.attribute = attribute

        self.label = QLabel(label)
        self.spin_box = QSpinBox()

        self.addWidget(self.label)
        self.addWidget(self.spin_box)

    def port_changed(self, port):
        card_type = port._card_type

        if card_type == CARD_TYPE_FSCC:
            value_range = (0, 127)
        elif card_type == CARD_TYPE_PCI:
            value_range = (0, 64)
        elif card_type == CARD_TYPE_PCIe:
            value_range = (0, 255)

        self.spin_box.setMinimum(value_range[0])
        self.spin_box.setMaximum(value_range[1])

        self.spin_box.setValue(getattr(port, self.attribute))

    def apply_changes(self, port):
        setattr(port, self.attribute, self.spin_box.value())


class FTxTriggerLevel(FTriggerLevel):

    def __init__(self, port_widget=None):
        super(FTxTriggerLevel, self).__init__("TX Trigger Level", "tx_trigger",
                                              port_widget)


class FRxTriggerLevel(FTriggerLevel):

    def __init__(self, port_widget=None):
        super(FRxTriggerLevel, self).__init__("RX Trigger Level", "rx_trigger",
                                              port_widget)


class FBooleanAttribute(QCheckBox, PortChangedTracker):

    def __init__(self, label, attribute, port_widget=None):
        QCheckBox.__init__(self, label)
        PortChangedTracker.__init__(self, port_widget)

        self.attribute = attribute

    def port_changed(self, port):
        self.setChecked(getattr(port, self.attribute))

    def apply_changes(self, port):
        setattr(port, self.attribute, self.isChecked())


class FTermination(FBooleanAttribute):

    def __init__(self, port_widget=None):
        super(FTermination, self).__init__("Termination", "termination",
                                           port_widget)


class F9Bit(FBooleanAttribute):

    def __init__(self, port_widget=None):
        super(F9Bit, self).__init__("9-Bit", "nine_bit", port_widget)


class FEchoCancel(FBooleanAttribute):

    def __init__(self, port_widget=None):
        super(FEchoCancel, self).__init__("Echo Cancel", "echo_cancel",
                                          port_widget)


class FClockFrequency(FHBoxLayout, PortChangedTracker):

    def __init__(self, port_widget=None):
        FHBoxLayout.__init__(self)
        PortChangedTracker.__init__(self, port_widget)

        self.label = QLabel("Clock Frequency")
        self.line_edit = QLineEdit()

        self.addWidget(self.label)
        self.addWidget(self.line_edit)

    def port_changed(self, port):
        card_type = port._card_type

        # This disabled the widget for the PCIe card
        if card_type == CARD_TYPE_PCIe:
            raise AttributeError()

        self.line_edit.setText('')

    def apply_changes(self, port):
        card_type = port._card_type

        if card_type == CARD_TYPE_FSCC:
            value_range = (200, 270000000)
        elif card_type == CARD_TYPE_PCI:
            value_range = (6000000, 200000000)

        if self.line_edit.text():
            error_title = 'Invalid Clock Frequency'
            error_text = 'Make sure to set the clock frequency to a value ' \
                          'between {:,.0f} and {:,.0f} Hz.'.format(*value_range)
            frequency = None

            #TODO: This all might be able to be simplified to one messagebox
            try:
                frequency = int(self.line_edit.text())
            except:
                msgBox = QMessageBox()
                msgBox.setWindowTitle(error_title)
                msgBox.setText(error_text)
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.exec_()
                return

            if frequency and (value_range[0] <= frequency <= value_range[1]):
                port.clock_rate = frequency
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle(error_title)
                msgBox.setText(error_text)
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.exec_()


class FSampleRate(FHBoxLayout, PortChangedTracker):

    def __init__(self, port_widget=None):
        FHBoxLayout.__init__(self)
        PortChangedTracker.__init__(self, port_widget)

        self.label = QLabel("Sample Rate")
        self.combo_box = QComboBox()
        self.spin_box = QSpinBox()

        self.spin_box.setMinimum(4)
        self.spin_box.setMaximum(16)

        self.addWidget(self.label)
        self.addWidget(self.combo_box)
        self.addWidget(self.spin_box)

        self.card_type = CARD_TYPE_UNKNOWN  # TODO: Why is this set?

        # Defaults to this situation so that the GUI looks normal
        # before a port is opened
        self.combo_box.hide()

    def port_changed(self, port):
        self.card_type = port._card_type

        if self.card_type == CARD_TYPE_FSCC:
            self.combo_box.hide()
            self.spin_box.show()
        elif self.card_type == CARD_TYPE_PCI:
            self.combo_box.show()
            self.spin_box.hide()
            self.combo_box.clear()
            rates = [8, 16]
            rates.sort(reverse=True)
            self.combo_box.addItems(list(map(str, rates)))
        elif self.card_type == CARD_TYPE_PCIe:
            self.combo_box.show()
            self.spin_box.hide()
            self.combo_box.clear()
            rates = [4, 8, 16]
            rates.sort(reverse=True)
            self.combo_box.addItems(list(map(str, rates)))

        rate = port.sample_rate
        self.combo_box.setCurrentIndex(self.combo_box.findText(str(rate)))
        self.spin_box.setValue(rate)

    def apply_changes(self, port):
        if self.card_type == CARD_TYPE_FSCC:
            rate = self.spin_box.value()
        elif self.card_type == CARD_TYPE_PCI:
            rate = int(self.combo_box.currentText())
        elif self.card_type == CARD_TYPE_PCIe:
            rate = int(self.combo_box.currentText())
        else:
            rate = None

        if rate:
            port.sample_rate = rate


class FIsochronous(FHBoxLayout, PortChangedTracker):

    def __init__(self, port_widget=None):
        FHBoxLayout.__init__(self)
        PortChangedTracker.__init__(self, port_widget)

        self.check_box = QCheckBox("Isochronous")
        self.spin_box = QSpinBox()

        self.spin_box.setMinimum(0)
        self.spin_box.setMaximum(8)
        self.spin_box.setPrefix('Mode ')
        self.spin_box.setEnabled(False)
        self.check_box.setCheckState(Qt.CheckState.Unchecked)

        self.check_box.stateChanged.connect(self.check_box_state_changed)

        self.addWidget(self.check_box)
        self.addWidget(self.spin_box)

    def check_box_state_changed(self):
        if self.check_box.checkState() == Qt.CheckState.Unchecked:
            self.spin_box.setEnabled(False)
        else:
            self.spin_box.setEnabled(True)

    def port_changed(self, port):
        mode = port.get_isochronous()
        self.check_box.setChecked(mode != -1)
        self.spin_box.setValue(mode)

    def apply_changes(self, port):
        if self.check_box.isChecked():
            port.enable_isochronous(self.spin_box.value())
        else:
            port.disable_isochronous()


class FExternalTransmit(FHBoxLayout, PortChangedTracker):

    def __init__(self, port_widget=None):
        FHBoxLayout.__init__(self)
        PortChangedTracker.__init__(self, port_widget)

        self.check_box = QCheckBox("External Transmit")
        self.spin_box = QSpinBox()

        self.spin_box.setMinimum(1)
        self.spin_box.setMaximum(8190)
        self.spin_box.setSuffix(' frame')
        self.spin_box.setEnabled(False)
        self.check_box.setCheckState(Qt.CheckState.Unchecked)

        self.spin_box.valueChanged.connect(self.spin_box_value_changed)
        self.check_box.stateChanged.connect(self.check_box_state_changed)

        self.addWidget(self.check_box)
        self.addWidget(self.spin_box)

    def check_box_state_changed(self):
        if self.check_box.checkState() == Qt.CheckState.Unchecked:
            self.spin_box.setEnabled(False)
        else:
            self.spin_box.setEnabled(True)

    def spin_box_value_changed(self, i):
        if i == 1:
            self.spin_box.setSuffix(' frame')
        else:
            self.spin_box.setSuffix(' frames')

    def port_changed(self, port):
        num_frames = port.get_external_transmit()
        self.check_box.setChecked(num_frames > 0)
        self.spin_box.setValue(num_frames)

    def apply_changes(self, port):
        if self.check_box.isChecked():
            port.enable_external_transmit(self.spin_box.value())
        else:
            port.disable_external_transmit()


class FProtocol(FHBoxLayout, PortChangedTracker):

    def __init__(self, port_widget=None):
        FHBoxLayout.__init__(self)
        PortChangedTracker.__init__(self, port_widget)

        self.rs422_radio_button = QRadioButton("RS422")
        self.rs485_radio_button = QRadioButton("RS485")

        self.addWidget(self.rs422_radio_button)
        self.addWidget(self.rs485_radio_button)
        self.layout.addStretch()

    def port_changed(self, port):
        self.rs485_radio_button.setChecked(port.rs485)
        self.rs422_radio_button.setChecked(not port.rs485)

    def apply_changes(self, port):
        port.rs485 = self.rs485_radio_button.isChecked()


class FFrameLength(FHBoxLayout, PortChangedTracker):

    def __init__(self, port_widget=None):
        FHBoxLayout.__init__(self)
        PortChangedTracker.__init__(self, port_widget)

        self.label = QLabel("Frame Length")
        self.spin_box = QSpinBox()

        self.spin_box.setMinimum(1)
        self.spin_box.setMaximum(256)
        self.spin_box.setSuffix(' word')

        self.spin_box.valueChanged.connect(self.spin_box_value_changed)

        self.addWidget(self.label)
        self.addWidget(self.spin_box)

    def spin_box_value_changed(self, i):
        if i == 1:
            self.spin_box.setSuffix(' word')
        else:
            self.spin_box.setSuffix(' words')

    def port_changed(self, port):
        self.spin_box.setValue(port.frame_length)

    def apply_changes(self, port):
        port.frame_length = self.spin_box.value()
