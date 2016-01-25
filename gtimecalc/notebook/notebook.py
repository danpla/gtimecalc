
from gettext import gettext as _, ngettext
import json
from collections import OrderedDict
import os

from gi.repository import Gtk

from ..config import CONFIG_DIR
from ..common import confirmation
from ..time_tools import ms_to_str, str_to_ms
from ..calculator import Operation
from .equation_list import EquationStore, EquationList
from .export import ExportDialog


class Notebook(Gtk.Grid):

    _OPERATION_MAP = {
        '+': Operation.ADD,
        '-': Operation.SUBSTRACT
        }

    _FILE = os.path.join(CONFIG_DIR, 'notebook.json')

    def __init__(self, calc):
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            )
        self._calc = calc

        self._create_toolbar()

        self._eq_store = EquationStore()
        self._eq_list = EquationList(self._eq_store)
        self._eq_list.connect('row-activated', self._on_row_activated)

        selection = self._eq_list.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        selection.connect('changed', self._on_selection_changed)

        scrolled = Gtk.ScrolledWindow(
            shadow_type=Gtk.ShadowType.IN,
            expand=True,
            height_request=120
            )
        scrolled.add(self._eq_list)
        self.add(scrolled)

        icon_theme = Gtk.IconTheme.get_default()
        icon_theme.connect('changed', self._on_icon_theme_changed)
        icon_theme.emit('changed')

    def _create_toolbar(self):
        toolbar = Gtk.Toolbar(
            icon_size=Gtk.IconSize.SMALL_TOOLBAR,
            hexpand=True
            )
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

        btn_export = Gtk.ToolButton(
            label=_('Export…'),
            # icon_name will be set later
            tooltip_text=_('Export equations…'),
            sensitive=False
            )
        btn_export.connect('clicked', self._on_export)
        self._btn_export = btn_export
        toolbar.add(btn_export)

    def _on_icon_theme_changed(self, theme):
        icon_name = 'document-export'
        if not theme.has_icon(icon_name):
            icon_name = 'gtimecalc-export'
        self._btn_export.set_icon_name(icon_name)

    def _update_button_state(self):
        has_eqs = len(self._eq_store) > 0
        self._btn_clear.set_sensitive(has_eqs)
        self._btn_export.set_sensitive(has_eqs)

    def _on_add(self, button):
        self._eq_store.append((
            self._calc.time1,
            self._calc.time2,
            self._calc.operation,
            self._calc.result))

        self._update_button_state()

    def _on_remove(self, button):
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

    def _on_clear(self, button):
        if not confirmation(
                self.get_toplevel(),
                _('Clear the list?'),
                _('All equations will be removed.'),
                _('_Clear')):
            return
        self._eq_store.clear()
        self._update_button_state()

    def _on_export(self, button):
        export_dlg = ExportDialog(
            self.get_toplevel(), self._eq_list.get_selection())
        export_dlg.run()
        export_dlg.destroy()

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
