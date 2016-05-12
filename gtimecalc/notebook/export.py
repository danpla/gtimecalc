
from gettext import gettext as _
from itertools import chain
import os

from gi.repository import Gtk

from .equation_list import EquationStore
from ..common import WIDGET_SPACING
from ..settings import settings
from ..time_tools import ms_to_str


class ExportDialog(Gtk.Dialog):

    _FORMAT_SPECIFIERS = ('%1', '%2', '%o', '%r', '%n', '%t')
    _DEFAULT_FORMAT = '%1 %o %2 = %r'

    _LINE_ENDINGS = ('\n', '\r\n', '\r')
    _LINE_ENDING_NAMES = ('unix', 'win', 'mac')

    def __init__(self, parent, selection):
        super().__init__(
            title=_('Export equations'),
            transient_for=parent,
            destroy_with_parent=True,
            default_width=400,
            width_request=300
            )
        self.add_buttons(
            _('_Cancel'), Gtk.ResponseType.CANCEL,
            _('_Export'), Gtk.ResponseType.OK,
            )

        self._all_eqs = []
        self._selected_eqs = []

        equation_store = selection.get_tree_view().get_model()
        for row in equation_store:
            eq_str = (
                ms_to_str(row[EquationStore.COL_TIME1]),
                ms_to_str(row[EquationStore.COL_TIME2]),
                ('+', '-')[row[EquationStore.COL_OPERATION]],
                ms_to_str(row[EquationStore.COL_RESULT])
                )
            self._all_eqs.append(eq_str)
            if selection.iter_is_selected(row.iter):
                self._selected_eqs.append(eq_str)

        if 'export' in settings and isinstance(settings['export'], dict):
            self._settings = settings['export']
        else:
            self._settings = {}
            settings['export'] = self._settings

        self._textbuf = Gtk.TextBuffer()
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

        self._format_entry = Gtk.Entry(
            hexpand=True,
            tooltip_markup='\n'.join((
                _('{} — time 1'),
                _('{} — time 2'),
                _('{} — operation'),
                _('{} — result'),
                _('{} — new line'),
                _('{} — tabulation'),
                )).format(*map('<tt>{}</tt>'.format, self._FORMAT_SPECIFIERS))
            )
        format_string = self._settings.get('format')
        if not isinstance(format_string, str):
            format_string = self._DEFAULT_FORMAT
        self._format_entry.set_text(format_string)
        self._format_entry.connect('changed', self._format_text)
        grid.add(self._format_entry)

        # Selected only

        self._btn_only_selected = Gtk.CheckButton(
            label=_('Only selected equations'),
            active=False,
            sensitive=bool(self._selected_eqs),
            )
        if self._selected_eqs:
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
            line_endings = 0
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
        self._settings['format'] = self._format_entry.get_text()
        self._settings['only_selected'] = self._btn_only_selected.get_active()
        self._settings['line_endings'] = (
            self._LINE_ENDING_NAMES[self._le_combo.get_active()])

        if response_id != Gtk.ResponseType.OK:
            return

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
            eqs = self._selected_eqs
        else:
            eqs = self._all_eqs

        format_string = self._format_entry.get_text()
        lines = []
        for eq in eqs:
            line = format_string
            for rpair in zip(
                    self._FORMAT_SPECIFIERS,
                    chain(eq, ('\n', '\t'))):
                line = line.replace(*rpair)
            lines.append(line)

        self._textbuf.set_text('\n'.join(lines))
