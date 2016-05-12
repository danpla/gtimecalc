
from gettext import gettext as _
import struct

from gi.repository import Gtk, Gdk, Gio, GLib

from . import app_info
from .settings import settings
from .common import WIDGET_SPACING
from .calculator import Calculator
from .notebook import Notebook


_C_INT_MAX = 2 ** (struct.Struct('i').size * 8 - 1) - 1


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

        notebook_visible_action = Gio.SimpleAction.new_stateful(
            'notebook-visible',
            None,
            GLib.Variant.new_boolean(self._notebook.get_visible()),
            )
        notebook_visible_action.connect(
            'change-state', self._on_notebook_visible_toggle)
        self.add_action(notebook_visible_action)

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

        # View
        view_menu = Gtk.Menu()
        mi_view = Gtk.MenuItem.new_with_mnemonic(_('_View'))
        mi_view.set_submenu(view_menu)
        menubar.append(mi_view)

        mi_show_equations = Gtk.CheckMenuItem(
            label=_('Show Equations'),
            action_name='win.notebook-visible')
        view_menu.append(mi_show_equations)

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

    def _udpate_geometry_hints(self):
        geometry = Gdk.Geometry()
        geometry.max_width = _C_INT_MAX
        if self._notebook.get_visible():
            geometry.max_height = _C_INT_MAX
        else:
            geometry.max_height = -1

        self.set_geometry_hints(None, geometry, Gdk.WindowHints.MAX_SIZE)

    def _on_notebook_visible_toggle(self, action, value):
        action.set_state(value)
        self._notebook.set_visible(value.get_boolean())
        self._udpate_geometry_hints()

    def do_window_state_event(self, event):
        self._maximized = bool(
            event.new_window_state & Gdk.WindowState.MAXIMIZED)
        return Gtk.ApplicationWindow.do_window_state_event(self, event)

    def do_delete_event(self, event):
        self.save_state()
        return Gdk.EVENT_PROPAGATE

    def save_state(self):
        state = {}

        notebook_visible_state = self.get_action_state('notebook-visible')
        state['show_equations'] = notebook_visible_state.get_boolean()

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

            self.change_action_state(
                'notebook-visible',
                GLib.Variant.new_boolean(state['show_equations']))
        except (KeyError, TypeError):
            pass
