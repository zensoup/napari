"""
Range slider, extended QWidget slider for napari-gui.
"""

from PyQt5 import QtCore, QtGui, QtWidgets


class QRangeSlider(QtWidgets.QWidget):
    """
    QRangeSlider class, super class for QVRangeSlider and QHRangeSlider.
    """
    rangeChanged = QtCore.pyqtSignal(float, float)

    def __init__(self, slider_range, values, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.bar_width = 4
        self.emit_while_moving = 0
        self.moving = "none"
        self.old_scale_min = 0.0
        self.old_scale_max = 0.0
        self.scale = 0
        self.setMouseTracking(False)
        self.single_step = 0.0

        self.collapsed = False
        self.prev_moving = None
        self.bc_min = None
        self.bc_max = None

        # Variables initialized in methods
        self.scale_min = None
        self.scale_max = None
        self.start_display_min = None
        self.start_display_max = None
        self.start_pos = None
        self.display_min = None
        self.display_max = None

        if slider_range:
            self.setRange(slider_range)
        else:
            self.setRange([0.0, 1.0, 0.01])
        if values:
            self.setValues(values)
        else:
            self.setValues([0.3, 0.6])

    def emitRange(self):
        if (self.old_scale_min != self.scale_min) or (self.old_scale_max != self.scale_max):
            self.rangeChanged.emit(self.scale_min, self.scale_max)
            self.old_scale_min = self.scale_min
            self.old_scale_max = self.scale_max
            # For debug purposes
            # if False:
            #     print("Range change:", self.scale_min, self.scale_max)

    def getValues(self):
        """Values of the range bar.

        Returns
        -------
        values : 2-tuple of int
            Start and end of the range.
        """
        return [self.scale_min, self.scale_max]

    def setValues(self, values):
        """Set values of the range bar.

        Parameters
        ----------
        values : 2-tuple of int
            Start and end of the range.
        """
        self.scale_min, self.scale_max = values
        self.emitRange()
        self.updateDisplayValues()
        self.update()

    def mouseMoveEvent(self, event):
        size = self.rangeSliderSize()
        diff = self.start_pos - self.getPos(event)
        if self.moving == "min":
            temp = self.start_display_min - diff
            if (temp >= self.bar_width) and (temp <= self.start_display_max):
                self.display_min = temp
                if self.display_max < self.display_min:
                    self.display_max = self.display_min
        elif self.moving == "max":
            temp = self.start_display_max - diff
            if (temp >= self.start_display_min) and (temp < size - self.bar_width):
                self.display_max = temp
                if self.display_max < self.display_min:
                    self.display_min = self.display_max
        elif self.moving == "bar":
            temp = self.start_display_min - diff
            if (temp >= self.bar_width) and (
                    temp < size - self.bar_width - (self.start_display_max - self.start_display_min)):
                self.display_min = temp
                self.display_max = self.start_display_max - diff

        self.updateScaleValues()
        if self.emit_while_moving:
            self.emitRange()

    def mousePressEvent(self, event):
        pos = self.getPos(event)
        if event.button() == QtCore.Qt.LeftButton:
            if not self.collapsed:
                if abs(self.display_min - 0.5 * self.bar_width - pos) <= (0.5 * self.bar_width):
                    self.moving = "min"
                elif abs(self.display_max + 0.5 * self.bar_width - pos) <= (0.5 * self.bar_width):
                    self.moving = "max"
                elif (pos > self.display_min) and (pos < self.display_max):
                    self.moving = "bar"
            else:
                self.moving = "bar"
        else:
            if self.collapsed:
                # print("collapsed already")
                self.expand()
                self.collapsed = False
            else:
                # print("not collapsed")
                self.collapse()
                self.collapsed = True

        self.start_display_min = self.display_min
        self.start_display_max = self.display_max
        self.start_pos = pos

    def collapse(self):
        self.bc_min, self.bc_max = self.scale_min, self.scale_max
        while int(self.scale_min) < int(self.scale_max):
            step = (self.scale_max - self.scale_min) / 2
            self.setValues([self.scale_min+step, self.scale_max-step])

    def expand(self):
        self.setValues([self.bc_min, self.bc_max])

    def mouseReleaseEvent(self, event):
        if not (self.moving == "none"):
            self.emitRange()
        self.moving = "none"

    def resizeEvent(self, event):
        self.updateDisplayValues()

    def setRange(self, slider_range):
        self.start = slider_range[0]
        self.scale = slider_range[1] - slider_range[0]
        self.single_step = slider_range[2]

    def setEmitWhileMoving(self, flag):
        if flag:
            self.emit_while_moving = 1
        else:
            self.emit_while_moving = 0

    def updateDisplayValues(self):
        size = float(self.rangeSliderSize() - 2 * self.bar_width - 1)
        self.display_min = int(size * (self.scale_min - self.start) / self.scale) + self.bar_width
        self.display_max = int(size * (self.scale_max - self.start) / self.scale) + self.bar_width

    def updateScaleValues(self):
        size = float(self.rangeSliderSize() - 2 * self.bar_width - 1)
        if (self.moving == "min") or (self.moving == "bar"):
            self.scale_min = self.start + (self.display_min - self.bar_width) / float(size) * self.scale
            self.scale_min = float(round(self.scale_min / self.single_step)) * self.single_step
        if (self.moving == "max") or (self.moving == "bar"):
            self.scale_max = self.start + (self.display_max - self.bar_width) / float(size) * self.scale
            self.scale_max = float(round(self.scale_max / self.single_step)) * self.single_step
        self.updateDisplayValues()
        self.update()


class QHRangeSlider(QRangeSlider):
    """
    Horizontal Range Slider, extended from QRangeSlider

    Parameters
    ----------
    slider_range : 3-tuple of int
        Min, max, and step of the slider.
    values : 2-tuple of int
        Start and end of the slider range.
    parent : PyQt5.QtWidgets.QWidget
        Parent widget.
    """
    def __init__(self, slider_range=None, values=None, parent=None):
        QRangeSlider.__init__(self, slider_range, values, parent)
        if not parent:
            self.setGeometry(200, 200, 200, 20)

    def getPos(self, event):
        """Get event position.

        Parameters
        ----------
        event : PyQt5.QtCore.QEvent
            Event from the Qt context.
        
        Returns
        -------
        position : int
            Relative horizontal position of the event.
        """
        return event.x()

    def paintEvent(self, event):
        """Paint the background, range bar and splitters.

        Parameters
        ----------
        event : PyQt5.QtCore.QEvent
            Event from the Qt context.
        """
        painter, w, h = QtGui.QPainter(self), self.width(), self.height()

        # Background
        painter.setPen(QtCore.Qt.gray)
        painter.setBrush(QtCore.Qt.transparent)
        painter.drawRect(2, 2, w - 4, h - 4)

        # Range Bar
        painter.setPen(QtCore.Qt.darkGray)
        painter.setBrush(QtCore.Qt.darkCyan)
        painter.drawRect(self.display_min - 1, 5, self.display_max - self.display_min + 2, h - 10)

        # Splitters
        painter.setPen(QtCore.Qt.black)
        painter.setBrush(QtCore.Qt.gray)
        painter.drawRect(self.display_min - self.bar_width, 1, self.bar_width, h - 2)  # left
        painter.drawRect(self.display_max, 1, self.bar_width, h - 2)  # right

    def rangeSliderSize(self):
        """Size of the slider.

        Returns
        -------
        size : int
            Slider widget width (horizontal sliders) or height (vertical sliders).
        """
        return self.width()


class QVRangeSlider(QRangeSlider):
    """
    Vertical Range Slider, extended from QRangeSlider

    Parameters
    ----------
    slider_range : 3-tuple of int
        Min, max, and step of the slider.
    values : 2-tuple of int
        Start and end of the slider range.
    parent : PyQt5.QtWidgets.QWidget
        Parent widget.
    """
    def __init__(self, slider_range=None, values=None, parent=None):
        QRangeSlider.__init__(self, slider_range, values, parent)
        if not parent:
            self.setGeometry(200, 200, 20, 200)

    def getPos(self, event):
        """Get event position.

        Parameters
        ----------
        event : PyQt5.QtCore.QEvent
            Event from the Qt context.
        
        Returns
        -------
        position : int
            Relative horizontal position of the event.
        """
        return self.height() - event.y()

    def paintEvent(self, event):
        """Paint the background, range bar and splitters.

        Parameters
        ----------
        event : PyQt5.QtCore.QEvent
            Event from the Qt context.
        """
        painter, w, h = QtGui.QPainter(self), self.width(), self.height()

        # Background
        painter.setPen(QtCore.Qt.gray)
        painter.setBrush(QtCore.Qt.transparent)
        painter.drawRect(2, 2, w - 4, h - 4)

        # Range Bar
        painter.setPen(QtCore.Qt.darkGray)
        painter.setBrush(QtCore.Qt.darkCyan)
        painter.drawRect(5, h - self.display_max - 1, w - 10, self.display_max - self.display_min + 1)

        # Splitters
        painter.setPen(QtCore.Qt.black)
        painter.setBrush(QtCore.Qt.gray)
        painter.drawRect(1, h - self.display_max - self.bar_width - 1, w - 2, self.bar_width)  # upper
        painter.drawRect(1, h - self.display_min - 1, w - 2, self.bar_width)  # lower

    def rangeSliderSize(self):
        """Size of the slider.

        Returns
        -------
        size : int
            Slider widget width (horizontal sliders) or height (vertical sliders).
        """
        return self.height()
