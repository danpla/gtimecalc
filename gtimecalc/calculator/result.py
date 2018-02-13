
from gettext import gettext as _

from gi.repository import Gtk, Gdk

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
        self.add(copy_btn)

        self._time = 0
        self.time = 0  # Initialize the label

    def _on_copy(self, copy_btn):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(ms_to_str(self._time), -1)

    @property
    def time(self):
        '''Result time in milliseconds.'''
        return self._time

    @time.setter
    def time(self, time):
        self._time = time
        self._result.set_label(self._MARKUP.format(ms_to_str(time)))
