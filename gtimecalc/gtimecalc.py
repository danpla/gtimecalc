
from gettext import gettext as _

from gi.repository import Gtk, Gio, GLib

from . import app_info
from .settings import settings
from .main_window import MainWindow


class TimeCalc(Gtk.Application):

    _ACTIONS = (
        'about',
        'quit'
        )

    def __init__(self):
        super().__init__(
            application_id='org.gtk.' + app_info.NAME,
            flags=Gio.ApplicationFlags.FLAGS_NONE)
        GLib.set_application_name(app_info.TITLE)
        GLib.set_prgname(app_info.NAME)

        self._window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        for action_name in self._ACTIONS:
            action = Gio.SimpleAction.new(action_name, None)
            action.connect(
                'activate', getattr(self, '_on_{}'.format(action_name)))
            self.add_action(action)

        settings.load()

        Gtk.Window.set_default_icon_name(app_info.ICON)
        self._window = MainWindow(self)
        self._window.load_state()
        self._window.show()

    def do_activate(self):
        self._window.present()

    def do_shutdown(self):
        settings.save()
        Gtk.Application.do_shutdown(self)

    def quit(self):
        self._window.save_state()
        self._window.destroy()
        super().quit()

    def _on_about(self, action, parameter):
        about_dlg = Gtk.AboutDialog(
            logo_icon_name=app_info.ICON,
            version=app_info.VERSION,
            comments=_('Time calculator'),
            website=app_info.WEBSITE,
            website_label=app_info.WEBSITE,
            copyright=app_info.COPYRIGHT,
            license=app_info.LICENSE,

            transient_for=self._window,
            destroy_with_parent=True,
            )
        about_dlg.run()
        about_dlg.destroy()

    def _on_quit(self, action, parameter):
        self.quit()
