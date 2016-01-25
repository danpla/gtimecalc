
from gettext import gettext as _

from gi.repository import Gtk, Gdk, GObject

from ..common import WIDGET_SPACING
from .. import time_tools


class TimeUnitSpin(Gtk.SpinButton):

    class Limit:
        NO_LIMIT = 0
        INCREASE = 1
        DECREASE = 2

    def __init__(self, name, max_value, padding=0):
        super().__init__(
            numeric=True,
            update_policy=Gtk.SpinButtonUpdatePolicy.IF_VALID,
            xalign=1.0,
            tooltip_text=name,
            )
        self.set_increments(1, 5)

        self._padding = padding if padding > 0 else len(str(max_value))

        self._higher = None
        self._lower = None

        self._max = max_value
        self._limits = (
            (-1, max_value + 1),
            (-1, max_value),
            (0, max_value + 1),
            )
        self._limit = self.Limit.DECREASE
        self.set_range(*self._limits[self._limit])

    @property
    def higher_unit(self):
        return self._higher

    @higher_unit.setter
    def higher_unit(self, higher):
        self._higher = higher

    @property
    def lower_unit(self):
        return self._lower

    @lower_unit.setter
    def lower_unit(self, lower):
        self._lower = lower

    def _update_limits(self):
        if self._lower is None:
            return
        elif self.max_reached():
            self._lower.limit = self.Limit.INCREASE
        elif self.min_reached():
            self._lower.limit = self.Limit.DECREASE
        else:
            self._lower.limit = self.Limit.NO_LIMIT

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, limit):
        if self._limit != limit:
            self.set_range(*self._limits[limit])
            self._limit = limit
        self._update_limits()

    def min_reached(self):
        '''Return True if the unit and all of its parents reach 0.'''
        return (
            int(self.props.value) == 0 and
            (self._higher.min_reached() if self._higher is not None else True))

    def max_reached(self):
        '''Return True if the unit and all of its parents reach maximum.'''
        return (
            int(self.props.value) == self._max and
            (self._higher.max_reached() if self._higher is not None else True))

    def do_value_changed(self):
        if self._higher is None:
            self._update_limits()
            return

        time = int(self.props.value)
        if time == -1:
            self.props.value = self._max
            self._higher.props.value -= 1
        elif time > self._max:
            self.props.value = 0
            self._higher.props.value += 1
        else:
            self._update_limits()

    def do_output(self):
        self.set_text('{:0{}.0f}'.format(self.get_value(), self._padding))
        return True


class TimeControl(Gtk.Grid):

    _MAX_HOURS = 2 ** 53  # SpinButton uses double
    _MAX_MINUTES = 59
    _MAX_SECONDS = 59
    _MAX_MILLISECONDS = 999

    MAX_TIME = (
        _MAX_HOURS * time_tools.HOUR_MS +
        _MAX_MINUTES * time_tools.MINUTE_MS +
        _MAX_SECONDS * time_tools.SECOND_MS +
        _MAX_MILLISECONDS
        )

    def __init__(self):
        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            column_spacing=WIDGET_SPACING // 3
            )

        self._hours = TimeUnitSpin(_('Hours'), self._MAX_HOURS, padding=2)
        self._hours.connect('value-changed', self._on_value_changed)
        self._hours.set_hexpand(True)
        self.add(self._hours)

        self.add(Gtk.Label('\N{RATIO}'))

        self._minutes = TimeUnitSpin(_('Minutes'), self._MAX_MINUTES)
        self._minutes.connect('value-changed', self._on_value_changed)
        self.add(self._minutes)

        self.add(Gtk.Label('\N{RATIO}'))

        self._seconds = TimeUnitSpin(_('Seconds'), self._MAX_SECONDS)
        self._seconds.connect('value-changed', self._on_value_changed)
        self.add(self._seconds)

        self.add(Gtk.Label('.'))

        self._milliseconds = TimeUnitSpin(
            _('Milliseconds'), self._MAX_MILLISECONDS)
        self._milliseconds.connect('value-changed', self._on_value_changed)
        self.add(self._milliseconds)

        self._hours.lower_unit = self._minutes
        self._minutes.higher_unit = self._hours
        self._minutes.lower_unit = self._seconds
        self._seconds.higher_unit = self._minutes
        self._seconds.lower_unit = self._milliseconds
        self._milliseconds.higher_unit = self._seconds

        grid = Gtk.Grid(
            orientation=Gtk.Orientation.HORIZONTAL
            )
        self.add(grid)

        copy_btn = Gtk.Button(
            always_show_image=True,
            image=Gtk.Image.new_from_icon_name(
                'edit-copy',
                Gtk.IconSize.BUTTON),
            relief=Gtk.ReliefStyle.NONE,
            can_focus=False,
            tooltip_text=_('Copy'),
            )
        copy_btn.connect('clicked', self._on_copy)
        grid.add(copy_btn)

        paste_btn = Gtk.Button(
            always_show_image=True,
            image=Gtk.Image.new_from_icon_name(
                'edit-paste',
                Gtk.IconSize.BUTTON),
            relief=Gtk.ReliefStyle.NONE,
            can_focus=False,
            tooltip_text=_('Paste')
            )
        paste_btn.connect('clicked', self._on_paste)
        grid.add(paste_btn)

        reset_btn = Gtk.Button(
            always_show_image=True,
            image=Gtk.Image.new_from_icon_name(
                'edit-clear',
                Gtk.IconSize.BUTTON),
            relief=Gtk.ReliefStyle.NONE,
            can_focus=False,
            tooltip_text=_('Reset'),
            )
        reset_btn.connect('clicked', self._on_reset)
        grid.add(reset_btn)

    @GObject.Property
    def time(self):
        '''Current time in milliseconds'''
        return time_tools.join_units(
            self._hours.get_value(),
            self._minutes.get_value(),
            self._seconds.get_value(),
            self._milliseconds.get_value())

    @time.setter
    def time(self, time):
        hours, minutes, seconds, milliseconds = time_tools.split_units(
            min(time, self.MAX_TIME))

        self._hours.set_value(hours)
        self._minutes.set_value(minutes)
        self._seconds.set_value(seconds)
        self._milliseconds.set_value(milliseconds)

    def _on_value_changed(self, spin):
        self.notify('time')

    def _on_copy(self, copy_btn):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(time_tools.ms_to_str(self.time), -1)

    def _on_paste(self, paste_btn):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        if clipboard.wait_is_text_available():
            try:
                self.time = abs(time_tools.str_to_ms(
                    clipboard.wait_for_text()))
            except ValueError:
                pass

    def _on_reset(self, reset_btn):
        self.time = 0
