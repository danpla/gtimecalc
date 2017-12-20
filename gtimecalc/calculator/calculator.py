
from gettext import gettext as _

from gi.repository import Gtk

from ..common import WIDGET_SPACING
from ..settings import settings
from ..time_tools import ms_to_str, str_to_ms
from .time_control import TimeControl
from .operation import Operation, OperationChooser
from .result import Result


class Calculator(Gtk.Grid):

    _OPERATION_MAP = {
        '+': Operation.ADD,
        '-': Operation.SUB
        }

    def __init__(self):
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            column_spacing=WIDGET_SPACING,
            row_spacing=WIDGET_SPACING
            )

        self._tc1 = TimeControl()
        self._tc1.connect('notify::time', self._calc_time)
        self.attach(self._tc1, 1, 1, 2, 1)

        swap_btn = Gtk.Button(
            always_show_image=True,
            image=Gtk.Image.new_from_icon_name(
                'gtimecalc-time-swap',
                Gtk.IconSize.BUTTON),
            tooltip_text=_('Swap')
            )
        swap_btn.connect('clicked', self._on_swap_time)
        self.attach(swap_btn, 1, 2, 1, 1)

        self._operation_choice = OperationChooser()
        self._operation_choice.connect('changed', self._calc_time)
        self._operation_choice.set_hexpand(True)
        self.attach(self._operation_choice, 2, 2, 1, 1)

        self._tc2 = TimeControl()
        self._tc2.connect('notify::time', self._calc_time)
        self.attach(self._tc2, 1, 3, 2, 1)

        self._result = Result()
        self.attach(self._result, 1, 4, 2, 1)

    def _on_swap_time(self, swap_btn):
        self.time1, self.time2 = self.time2, self.time1

    def _calc_time(self, *args):
        if self.operation == Operation.ADD:
            result = self.time1 + self.time2
        else:
            result = self.time1 - self.time2

        self._result.time = result

    @property
    def time1(self):
        return self._tc1.time

    @time1.setter
    def time1(self, time):
        self._tc1.time = time

    @property
    def time2(self):
        return self._tc2.time

    @time2.setter
    def time2(self, time):
        self._tc2.time = time

    @property
    def operation(self):
        return self._operation_choice.operation

    @operation.setter
    def operation(self, operation):
        self._operation_choice.operation = operation

    @property
    def result(self):
        return self._result.time

    def save_state(self):
        settings['calculator'] = {
            'time_1': ms_to_str(self.time1),
            'time_2': ms_to_str(self.time2),
            'operation': ('+', '-')[self.operation]
            }

    def load_state(self):
        try:
            state = settings['calculator']

            self.time1 = str_to_ms(state['time_1'])
            self.time2 = str_to_ms(state['time_2'])
            self.operation = self._OPERATION_MAP[state['operation']]
        except (KeyError, TypeError, ValueError):
            pass
