
from gi.repository import Gtk


class Operation:
    ADD = 0
    SUBSTRACT = 1


class OperationChooser(Gtk.ComboBox):

    _MARKUP = '<span size="large" font_weight="bold">{}</span>'

    def __init__(self):
        super().__init__()

        self._operations = Gtk.ListStore(str)
        self._operations.append((self._MARKUP.format('+'), ))
        self._operations.append((self._MARKUP.format('\N{MINUS SIGN}'), ))
        self.set_model(self._operations)
        self.set_active(0)

        renderer = Gtk.CellRendererText()
        self.pack_start(renderer, True)
        self.add_attribute(renderer, 'markup', 0)

    @property
    def operation(self):
        return self.get_active()

    @operation.setter
    def operation(self, op):
        self.set_active(op)
