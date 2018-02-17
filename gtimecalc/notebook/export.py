
from gettext import gettext as _
from itertools import chain, compress
import os

from gi.repository import Gtk

from .equation_list import EquationStore
from ..common import WIDGET_SPACING
from ..settings import settings
from ..time_tools import ms_to_str


def _format(s, replacements):
    result = ''

    copy_start = 0
    search_start = 0
    while True:
        idx = s.find('%', search_start, -1)
        if idx == -1:
            result += s[copy_start:]
            break

        search_start = idx + 2

        replacement = replacements.get(s[idx + 1])
        if replacement is None:
            continue

        if copy_start != idx:
            result += s[copy_start:idx]

        result += replacement
        copy_start = search_start

    return result


class ExportDialog(Gtk.Dialog):

    _FORMAT_SPECIFIERS = ('1', '2', 'o', 'r', 'n', 't', '%')
    _DEFAULT_FORMAT = '%1 %o %2 = %r'

    _LINE_ENDINGS = ('\n', '\r\n', '\r')
    _LINE_ENDING_NAMES = ('unix', 'win', 'mac')

    _MAX_FORMAT_HISTORY = 10

    def __init__(self, parent, selection):
        super().__init__(
            title=_('Save equations'),
            transient_for=parent,
            destroy_with_parent=True,
            default_width=400,
            width_request=300
            )
        self.add_buttons(
            _('_Cancel'), Gtk.ResponseType.CANCEL,
            _('_Save'), Gtk.ResponseType.OK,
            )

        self._eqs = []
        self._eq_is_selected = []

        equation_store = selection.get_tree_view().get_model()
        for row in equation_store:
            eq_str = (
                ms_to_str(row[EquationStore.COL_TIME1]),
                ms_to_str(row[EquationStore.COL_TIME2]),
                ('+', '-')[row[EquationStore.COL_OPERATION]],
                ms_to_str(row[EquationStore.COL_RESULT])
                )
            self._eqs.append(eq_str)
            self._eq_is_selected.append(selection.iter_is_selected(row.iter))

        if 'export' in settings and isinstance(settings['export'], dict):
            self._settings = settings['export']
        else:
            self._settings = {}
            settings['export'] = self._settings

        self._textbuf = Gtk.TextBuffer()
        self._textbuf.create_tag('monospace', family='monospace')

        self._create_ui()
        self._format_text()

    def _create_ui(self):
        area = self.get_content_area()
        area.props.margin = WIDGET_SPACING
        area.props.spacing = WIDGET_SPACING // 2

        # Format

        grid = Gtk.Grid(
            orientation=Gtk.Orientation.HORIZONTAL,
            column_spacing=WIDGET_SPACING
            )
        area.add(grid)

        grid.add(Gtk.Label(label=_('Format:')))

        format_combo = Gtk.ComboBoxText(
            button_sensitivity=Gtk.SensitivityType.OFF,
            has_entry=True,
            hexpand=True,
            )
        format_history = self._settings.get('format_history')
        if isinstance(format_history, list):
            format_combo.set_button_sensitivity(Gtk.SensitivityType.ON)
            for s in format_history:
                if isinstance(s, str):
                    format_combo.append_text(s)
        grid.add(format_combo)

        self._format_entry = format_combo.get_child()
        self._format_entry.set_tooltip_markup(
            '\n'.join((
                _('{} — time 1'),
                _('{} — time 2'),
                _('{} — operation'),
                _('{} — result'),
                _('{} — new line'),
                _('{} — tabulation'),
                _('{} — %'),
                )).format(
                    *map('<tt>%{}</tt>'.format, self._FORMAT_SPECIFIERS)))

        format_string = self._settings.get('format')
        if not isinstance(format_string, str):
            format_string = self._DEFAULT_FORMAT
        self._format_entry.set_text(format_string)
        self._format_entry.connect('changed', self._format_text)

        # Selected only

        has_selected_eqs = any(self._eq_is_selected)
        self._btn_only_selected = Gtk.CheckButton(
            label=_('Only selected equations'),
            active=False,
            sensitive=has_selected_eqs,
            )
        if has_selected_eqs:
            only_selected = self._settings.get('only_selected')
            if isinstance(only_selected, bool):
                self._btn_only_selected.set_active(only_selected)
        self._btn_only_selected.connect('toggled', self._format_text)
        area.add(self._btn_only_selected)

        # Line endings

        grid = Gtk.Grid(
            orientation=Gtk.Orientation.HORIZONTAL,
            column_spacing=WIDGET_SPACING
            )
        area.add(grid)

        grid.add(Gtk.Label(label=_('Line endings:')))

        self._le_combo = Gtk.ComboBoxText(hexpand=True)
        self._le_combo.append_text('Unix (LF)')
        self._le_combo.append_text('Windows (CRLF)')
        self._le_combo.append_text('Mac OS 9 (CR)')
        try:
            line_endings = self._LINE_ENDING_NAMES.index(
                self._settings.get('line_endings'))
        except (TypeError, ValueError):
            line_endings = 1 if os.name == 'nt' else 0
        self._le_combo.set_active(line_endings)
        grid.add(self._le_combo)

        # Preview

        area.add(
            Gtk.Label(
                label=_('Preview:'),
                xalign=0.0
            ))

        preview = Gtk.TextView(
            buffer=self._textbuf,
            editable=False
            )
        scrolled = Gtk.ScrolledWindow(
            shadow_type=Gtk.ShadowType.IN,
            expand=True
            )
        scrolled.add(preview)
        area.add(scrolled)

        area.show_all()

    def do_response(self, response_id):
        format_string = self._format_entry.get_text()
        self._settings['format'] = format_string
        self._settings['only_selected'] = self._btn_only_selected.get_active()
        self._settings['line_endings'] = (
            self._LINE_ENDING_NAMES[self._le_combo.get_active()])

        if response_id != Gtk.ResponseType.OK:
            return

        format_history = self._settings.get('format_history')
        if not isinstance(format_history, list):
            format_history = []
        try:
            format_history.remove(format_string)
        except ValueError:
            pass

        format_history.insert(0, format_string)
        if len(format_history) > self._MAX_FORMAT_HISTORY:
            format_history = format_history[:self._MAX_FORMAT_HISTORY]

        self._settings['format_history'] = format_history

        save_dlg = Gtk.FileChooserDialog(
            title=_('Save file'),
            action=Gtk.FileChooserAction.SAVE,
            do_overwrite_confirmation=True,
            transient_for=self,
            destroy_with_parent=True
            )
        save_dlg.add_buttons(
            _('_Cancel'), Gtk.ResponseType.CANCEL,
            _('_Save'), Gtk.ResponseType.OK,
            )

        path = self._settings.get('path')
        if not isinstance(path, str):
            path = os.path.expanduser('~')
        save_dlg.set_current_folder(path)

        if save_dlg.run() == Gtk.ResponseType.OK:
            line_endings = self._LINE_ENDINGS[self._le_combo.get_active()]

            start, end = self._textbuf.get_bounds()
            text = self._textbuf.get_text(start, end, False)

            try:
                with open(save_dlg.get_filename(), 'w', newline=line_endings) as f:
                    f.write(text)
                    f.write('\n')
            except OSError as e:
                error_dlg = Gtk.MessageDialog(
                    message_type=Gtk.MessageType.ERROR,
                    text=e.strerror,
                    secondary_text=e.filename,
                    transient_for=save_dlg,
                    destroy_with_parent=True
                    )
                error_dlg.add_buttons(
                    _('_OK'), Gtk.ResponseType.OK,
                    )
                error_dlg.run()
                error_dlg.destroy()

            self._settings['path'] = save_dlg.get_current_folder()

        save_dlg.destroy()

    def _format_text(self, *args):
        if self._btn_only_selected.get_active():
            eqs = compress(self._eqs, self._eq_is_selected)
        else:
            eqs = self._eqs

        format_string = self._format_entry.get_text()
        lines = []
        for eq in eqs:
            replacements = dict(
                zip(self._FORMAT_SPECIFIERS, chain(eq, ('\n', '\t', '%'))))
            lines.append(_format(format_string, replacements))

        self._textbuf.delete(*self._textbuf.get_bounds())
        self._textbuf.insert_with_tags_by_name(
            self._textbuf.get_start_iter(),
            '\n'.join(lines),
            'monospace'
            )
