
from gi.repository import Gtk

from ..time_tools import ms_to_str


class Result(Gtk.Grid):

    _MARKUP = '<span size="xx-large" font_weight="bold">{}</span>'

    def __init__(self):
        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL
            )

        equals = Gtk.Label(
            label=self._MARKUP.format('= '),
            use_markup=True,
            xalign=1.0
            )
        self.add(equals)

        self._result = Gtk.Label(
            selectable=True,
            use_markup=True,
            xalign=0.0,
            hexpand=True
            )
        self.add(self._result)

        self._time = 0
        self.time = 0  # Initialize the label

    @property
    def time(self):
        '''Result time in milliseconds.'''
        return self._time

    @time.setter
    def time(self, time):
        self._time = time
        self._result.set_label(self._MARKUP.format(ms_to_str(time)))
