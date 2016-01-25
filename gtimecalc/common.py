
from gettext import gettext as _

from gi.repository import Gtk


WIDGET_SPACING = 12


def confirmation(parent, message, secondary_text, ok_label):
    '''Show confirmation dialog.

    Returns True on "ok", Flase otherwise.
    '''
    dialog = Gtk.MessageDialog(
        message_type=Gtk.MessageType.QUESTION,
        text=message,
        secondary_text=secondary_text,
        transient_for=parent,
        destroy_with_parent=True
        )
    dialog.add_buttons(
        _('_Cancel'), Gtk.ResponseType.CANCEL,
        ok_label, Gtk.ResponseType.OK,
        )
    response = dialog.run()
    dialog.destroy()
    return response == Gtk.ResponseType.OK
