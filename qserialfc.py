"""
    Copyright (C) 2014 Commtech, Inc.

    This file is part of qserialfc.

    qserialfc is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    qserialfc is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with qserialfc.  If not, see <http://www.gnu.org/licenses/>.

"""

import sys

from PySide.QtCore import Signal
from PySide.QtGui import *

from widgets import *
from dialogs import *


class PortForm(QDialog):
    apply_changes = Signal()

    def __init__(self):
        super(PortForm, self).__init__()

        self.port_name = FPortName(self.apply_changes)

        sample_rate = FSampleRate(self.port_name)
        clock_frequency = FClockFrequency(self.port_name)
        tx_trigger_lvl = FTxTriggerLevel(self.port_name)
        rx_trigger_lvl = FRxTriggerLevel(self.port_name)
        termination = FTermination(self.port_name)
        echo_cancel = FEchoCancel(self.port_name)
        nine_bit = F9Bit(self.port_name)
        isochronous = FIsochronous(self.port_name)
        external_transmit = FExternalTransmit(self.port_name)
        frame_length = FFrameLength(self.port_name)
        protocol = FProtocol(self.port_name)
        fixed_baud_rate = FFixedBaudRate(self.port_name)

        buttons = FDialogButtonBox(self.port_name)
        buttons.apply.connect(self.apply_clicked)
        buttons.accepted.connect(self.ok_clicked)
        buttons.rejected.connect(self.close_clicked)

        # Create layout and add widgets
        layout = QVBoxLayout()

        layout.addWidget(self.port_name)
        layout.addWidget(sample_rate)
        layout.addWidget(clock_frequency)
        layout.addWidget(tx_trigger_lvl)
        layout.addWidget(rx_trigger_lvl)
        layout.addWidget(termination)
        layout.addWidget(nine_bit)
        layout.addWidget(echo_cancel)
        layout.addWidget(isochronous)
        layout.addWidget(external_transmit)
        layout.addWidget(frame_length)
        layout.addWidget(protocol)
        layout.addWidget(fixed_baud_rate)
        layout.addWidget(buttons)

        # Set dialog layout
        self.setLayout(layout)

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
    app = QApplication(sys.argv)

    form = PortForm()
    form.show()

    ports = sorted(list_ports.serialfcports())

    if ports:
        form.port_name.set_port(ports[0][1])
    else:
        form.port_name.set_port(None)
        FNoPortsFound().exec_()

    # Run the main Qt loop
    sys.exit(app.exec_())
