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

from PySide.QtGui import *


class FNoPortsFound(QMessageBox):

    def __init__(self, *args, **kwargs):
        super(FNoPortsFound, self).__init__(*args, **kwargs)

        self.setWindowTitle('No SerialFC Ports Found')
        self.setText('There wasn\'t any SerialFC ports found. Make sure you '
                     'have a card inserted and the driver loaded.')
        self.setIcon(QMessageBox.Information)


class FUnknownPort(QMessageBox):

    def __init__(self, *args, **kwargs):
        super(FUnknownPort, self).__init__(*args, **kwargs)

        self.setWindowTitle('Unknown Port')
        self.setText('This port is either not a Fastcom port or '
                     'using an older driver.')
        self.setIcon(QMessageBox.Information)


class FUnknownError(QMessageBox):

    def __init__(self, *args, **kwargs):
        super(FUnknownError, self).__init__(*args, **kwargs)

        self.setWindowTitle('Unknown Port')
        self.setText('There was a problem opening this port. Make sure '
                     'the port isn\'t already open elsewhere and you '
                     'have sufficient permissions.')
        self.setIcon(QMessageBox.Information)


class FInvalidClockFrequency(QMessageBox):

    def __init__(self, value_range, *args, **kwargs):
        super(FInvalidClockFrequency, self).__init__(*args, **kwargs)

        self.setWindowTitle('Invalid Clock Frequency')
        self.setText('The clock frequency was not set. Make sure to set the '
                     'clock frequency to a value between '
                     '{:,.0f} and {:,.0f} Hz.'.format(*value_range))
        self.setIcon(QMessageBox.Warning)


class FInvalidFixedBaudRate(QMessageBox):

    def __init__(self, *args, **kwargs):
        super(FInvalidFixedBaudRate, self).__init__(*args, **kwargs)

        self.setWindowTitle('Invalid Fixed Baud Rate')
        self.setText('The fixed baud rate was not set. Make sure to set a '
                     'valid fixed baud rate value.')
        self.setIcon(QMessageBox.Warning)
