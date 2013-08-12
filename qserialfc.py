#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from PySide.QtCore import Signal
from PySide.QtGui import QApplication, QDialog, QDialogButtonBox, QVBoxLayout

from widgets import *


class PortForm(QDialog):
    apply_changes = Signal()

    def __init__(self):
        super(PortForm, self).__init__()

        self.port_name = FPortName(self.apply_changes)
        self.sample_rate = FSampleRate(self.port_name)
        self.clock_frequency = FClockFrequency(self.port_name)
        self.tx_trigger_lvl = FTxTriggerLevel(self.port_name)
        self.rx_trigger_lvl = FRxTriggerLevel(self.port_name)
        self.termination = FTermination(self.port_name)
        self.echo_cancel = FEchoCancel(self.port_name)
        self.nine_bit = F9Bit(self.port_name)
        self.isochronous = FIsochronous(self.port_name)
        self.external_transmit = FExternalTransmit(self.port_name)
        self.frame_length = FFrameLength(self.port_name)
        self.protocol = FProtocol(self.port_name)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Apply |
                                        QDialogButtonBox.Ok |
                                        QDialogButtonBox.Close)

        self.sample_rate.setEnabled(False)
        self.clock_frequency.setEnabled(False)
        self.tx_trigger_lvl.setEnabled(False)
        self.rx_trigger_lvl.setEnabled(False)
        self.termination.setEnabled(False)
        self.nine_bit.setEnabled(False)
        self.echo_cancel.setEnabled(False)
        self.isochronous.setEnabled(False)
        self.external_transmit.setEnabled(False)
        self.frame_length.setEnabled(False)
        self.protocol.setEnabled(False)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Apply |
                                        QDialogButtonBox.Ok |
                                        QDialogButtonBox.Close)

        # Create layout and add widgets
        layout = QVBoxLayout()

        layout.addWidget(self.port_name)
        layout.addWidget(self.sample_rate)
        layout.addWidget(self.clock_frequency)
        layout.addWidget(self.tx_trigger_lvl)
        layout.addWidget(self.rx_trigger_lvl)
        layout.addWidget(self.termination)
        layout.addWidget(self.nine_bit)
        layout.addWidget(self.echo_cancel)
        layout.addWidget(self.isochronous)
        layout.addWidget(self.external_transmit)
        layout.addWidget(self.frame_length)
        layout.addWidget(self.protocol)
        layout.addWidget(self.buttons)

        # Set dialog layout
        self.setLayout(layout)

        apply_button = self.buttons.button(QDialogButtonBox.Apply)
        apply_button.clicked.connect(self.apply_clicked)
        self.buttons.accepted.connect(self.ok_clicked)
        self.buttons.rejected.connect(self.close_clicked)

        self.setFixedSize(self.sizeHint())
        self.setWindowTitle('Fastcom Serial Settings')

    def apply_clicked(self):
        self.apply_changes.emit()

    def ok_clicked(self):
        self.apply_changes.emit()
        self.close()

    def close_clicked(self):
        self.close()

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Create and show the form
    form = PortForm()
    form.show()

    # Try and set the default port after the form is already showing
    default_port = 'COM3' if os.name == 'nt' else '/dev/ttyS4'
    form.port_name.set_port(default_port)

    # Run the main Qt loop
    sys.exit(app.exec_())
