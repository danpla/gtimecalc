
from gettext import gettext as _

from gi.repository import Gtk, Gdk, Gio, GLib

from . import app_info
from .settings import settings
from .common import WIDGET_SPACING
from .calculator import Calculator
from .notebook import Notebook


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(
            application=app,
            title=app_info.TITLE
            )

        self._maximized = False

        grid = Gtk.Grid(
            orientation=Gtk.Orientation.VERTICAL
            )
        self.add(grid)

        grid.add(self._create_menubar())

        self._calculator = Calculator()
        self._calculator.props.margin = WIDGET_SPACING
        grid.add(self._calculator)

        self._notebook = Notebook(self._calculator)
        grid.add(self._notebook)

        grid.show_all()

    def _create_menubar(self):
        ag = Gtk.AccelGroup()
        self.add_accel_group(ag)

        menubar = Gtk.MenuBar()

        # File
        file_menu = Gtk.Menu()
        mi_file = Gtk.MenuItem.new_with_mnemonic(_('_File'))
        mi_file.set_submenu(file_menu)
        menubar.append(mi_file)

        mi_quit = Gtk.MenuItem(
            label=_('Quit'),
            action_name='app.quit')
        key, mod = Gtk.accelerator_parse('<Control>Q')
        mi_quit.add_accelerator(
            'activate', ag, key, mod, Gtk.AccelFlags.VISIBLE)
        file_menu.append(mi_quit)

        # Help
        help_menu = Gtk.Menu()
        mi_help = Gtk.MenuItem.new_with_mnemonic(_('_Help'))
        mi_help.set_submenu(help_menu)
        menubar.append(mi_help)

        mi_about = Gtk.MenuItem(
            label=_('About'),
            action_name='app.about')
        help_menu.append(mi_about)

        return menubar

    def do_window_state_event(self, event):
        self._maximized = bool(
            event.new_window_state & Gdk.WindowState.MAXIMIZED)
        return Gtk.ApplicationWindow.do_window_state_event(self, event)

    def do_delete_event(self, event):
        self.save_state()
        return Gdk.EVENT_PROPAGATE

    def save_state(self):
        state = {}
        state['x'], state['y'] = self.get_position()
        state['width'], state['height'] = self.get_size()
        state['maximized'] = self._maximized
        settings['window'] = state

        self._calculator.save_state()
        self._notebook.save_state()

    def load_state(self):
        self._calculator.load_state()
        self._notebook.load_state()

        try:
            state = settings['window']

            if state['maximized']:
                self.maximize()
            else:
                self.move(state['x'], state['y'])
                self.resize(
                    state['width'], state['height'])
        except (KeyError, TypeError):
            pass


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
