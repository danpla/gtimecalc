
from gettext import gettext as _, ngettext
import json
from collections import OrderedDict
import os

from gi.repository import Gtk, Gdk

from ..config import CONFIG_DIR
from ..common import confirmation
from ..time_tools import ms_to_str, str_to_ms
from ..calculator import Operation
from .equation_list import EquationStore, EquationList
from .export import ExportDialog


class Notebook(Gtk.Grid):

    _OPERATION_MAP = {
        '+': Operation.ADD,
        '-': Operation.SUB
        }

    _FILE = os.path.join(CONFIG_DIR, 'notebook.json')

    def __init__(self, calc):
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            )
        self._calc = calc

        self._eq_store = EquationStore()
        self._eq_list = EquationList(self._eq_store)
        self._eq_list.set_has_tooltip(True)
        self._eq_list.connect('query-tooltip', self._on_query_tooltip)
        self._eq_list.connect('button-press-event', self._on_button_press)
        self._eq_list.connect('row-activated', self._on_row_activated)

        selection = self._eq_list.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        selection.connect('changed', self._on_selection_changed)

        scrolled = Gtk.ScrolledWindow(
            shadow_type=Gtk.ShadowType.IN,
            expand=True,
            )
        scrolled.add(self._eq_list)
        self.add(scrolled)

        self._create_toolbar()

    def _create_toolbar(self):
        toolbar = Gtk.Toolbar(
            hexpand=True
            )
        toolbar.get_style_context().add_class('bottom-toolbar')
        self.add(toolbar)

        btn_add = Gtk.ToolButton(
            label=_('Add'),
            icon_name='list-add',
            tooltip_text=_('Add current equation'),
            )
        btn_add.connect('clicked', self._on_add)
        toolbar.add(btn_add)

        btn_remove = Gtk.ToolButton(
            label=_('Remove'),
            icon_name='list-remove',
            tooltip_text=_('Remove selected equations'),
            sensitive=False
            )
        self._btn_remove = btn_remove
        btn_remove.connect('clicked', self._on_remove)
        toolbar.add(btn_remove)

        btn_clear = Gtk.ToolButton(
            label=_('Clear'),
            icon_name='edit-clear',
            tooltip_text=_('Clear the list'),
            sensitive=False
            )
        btn_clear.connect('clicked', self._on_clear)
        self._btn_clear = btn_clear
        toolbar.add(btn_clear)

        toolbar.add(Gtk.SeparatorToolItem.new())

        btn_save_as = Gtk.ToolButton(
            label=_('Save as…'),
            icon_name='document-save-as',
            tooltip_text=_('Save equations as…'),
            sensitive=False
            )
        btn_save_as.connect('clicked', self._on_save_as)
        self._btn_save_as = btn_save_as
        toolbar.add(btn_save_as)

    def _update_button_state(self):
        has_eqs = len(self._eq_store) > 0
        self._btn_clear.set_sensitive(has_eqs)
        self._btn_save_as.set_sensitive(has_eqs)

    def _on_add(self, widget):
        tree_iter = self._eq_store.append((
            self._calc.time1,
            self._calc.time2,
            self._calc.operation,
            self._calc.result))

        tree_path = self._eq_store.get_path(tree_iter)
        self._eq_list.scroll_to_cell(tree_path, None, False, 0.0, 0.0)
        self._eq_list.set_cursor(tree_path, None, False)

        self._update_button_state()

    def _on_remove(self, widget):
        selection = self._eq_list.get_selection()
        tree_paths = selection.get_selected_rows()[1]
        num = len(tree_paths)
        if tree_paths and confirmation(
                self.get_toplevel(),
                ngettext(
                    'Remove {num} selected equation?',
                    'Remove {num} selected equations?',
                    num).format(num=num),
                None,
                _('_Remove')):
            self._eq_store.remove_equations(tree_paths)
            self._update_button_state()

    def _on_clear(self, widget):
        if not confirmation(
                self.get_toplevel(),
                _('Clear the list?'),
                _('All equations will be removed.'),
                _('_Clear')):
            return
        self._eq_store.clear()
        self._update_button_state()

    def _on_save_as(self, widget):
        export_dlg = ExportDialog(
            self.get_toplevel(), self._eq_list.get_selection())
        export_dlg.run()
        export_dlg.destroy()

    def _on_query_tooltip(self, eq_list, x, y, keyboard_tip, tooltip):
        points_to_row, *context = eq_list.get_tooltip_context(
            x, y, keyboard_tip)
        if not points_to_row:
            return False

        eq_store, tree_path, tree_iter = context[2:]
        row = eq_store[tree_iter]

        text = '{} {} {} = {}'.format(
            ms_to_str(row[EquationStore.COL_TIME1], True),
            ('+', '\N{MINUS SIGN}')[row[EquationStore.COL_OPERATION]],
            ms_to_str(row[EquationStore.COL_TIME2], True),
            ms_to_str(row[EquationStore.COL_RESULT], True)
            )

        tooltip.set_text(text)
        eq_list.set_tooltip_row(tooltip, tree_path)
        return True

    def _on_button_press(self, eq_list, event):
        if event.type != Gdk.EventType.BUTTON_PRESS:
            return Gdk.EVENT_PROPAGATE

        self._eq_list.grab_focus()

        selection = self._eq_list.get_selection()
        click_info = self._eq_list.get_path_at_pos(int(event.x), int(event.y))
        if click_info is None:
            selection.unselect_all()
        elif event.button == Gdk.BUTTON_SECONDARY:
            tree_path, column, cell_x, cell_y = click_info
            if not selection.path_is_selected(tree_path):
                self._eq_list.set_cursor(tree_path, column, False)

        if event.button != Gdk.BUTTON_SECONDARY:
            return Gdk.EVENT_PROPAGATE

        menu = Gtk.Menu(attach_widget=self._eq_list)

        mi_add = Gtk.MenuItem(
            label=_('_Add'),
            use_underline=True,
            tooltip_text=_('Add current equation'),
            )
        mi_add.connect('activate', self._on_add)
        menu.append(mi_add)

        mi_remove = Gtk.MenuItem(
            label=_('_Remove'),
            use_underline=True,
            tooltip_text=_('Remove selected equations'),
            )
        mi_remove.connect('activate', self._on_remove)
        menu.append(mi_remove)

        mi_clear = Gtk.MenuItem(
            label=_('_Clear'),
            use_underline=True,
            tooltip_text=_('Clear the list'),
            )
        mi_clear.connect('activate', self._on_clear)
        menu.append(mi_clear)

        menu.append(Gtk.SeparatorMenuItem())

        mi_save_as = Gtk.MenuItem(
            label=_('_Save as…'),
            use_underline=True,
            tooltip_text=_('Save equations as…'),
            )
        mi_save_as.connect('activate', self._on_save_as)
        menu.append(mi_save_as)

        num_selected = selection.count_selected_rows()
        if num_selected == 0:
            mi_remove.set_sensitive(False)
        if len(self._eq_store) == 0:
            mi_clear.set_sensitive(False)
            mi_save_as.set_sensitive(False)

        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)

        return Gdk.EVENT_STOP

    def _on_row_activated(self, eq_list, path, column):
        row = eq_list.get_model()[path]

        self._calc.time1 = row[EquationStore.COL_TIME1]
        self._calc.operation = row[EquationStore.COL_OPERATION]
        self._calc.time2 = row[EquationStore.COL_TIME2]

    def _on_selection_changed(self, selection):
        self._btn_remove.set_sensitive(selection.count_selected_rows() > 0)

    def save_state(self):
        notebook = []
        for row in self._eq_store:
            notebook.append(OrderedDict((
                ('time_1', ms_to_str(row[EquationStore.COL_TIME1])),
                ('time_2', ms_to_str(row[EquationStore.COL_TIME2])),
                ('operation', ('+', '-')[row[EquationStore.COL_OPERATION]]),
                ('result', ms_to_str(row[EquationStore.COL_RESULT]))
                )))

        try:
            with open(self._FILE, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def load_state(self):
        try:
            with open(self._FILE, 'r', encoding='utf-8') as f:
                notebook = json.load(f)
        except (OSError, ValueError):
            return

        if not isinstance(notebook, list):
            return

        for eq in notebook:
            try:
                self._eq_store.append((
                    str_to_ms(eq['time_1']),
                    str_to_ms(eq['time_2']),
                    self._OPERATION_MAP[eq['operation']],
                    str_to_ms(eq['result']),
                    ))
            except (KeyError, TypeError, ValueError):
                pass

        self._update_button_state()
