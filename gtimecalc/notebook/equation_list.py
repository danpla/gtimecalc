
from gettext import gettext as _

from gi.repository import Gtk

from ..time_tools import ms_to_str


class EquationStore(Gtk.ListStore):

    COL_TIME1 = 0
    COL_TIME2 = 1
    COL_OPERATION = 2
    COL_RESULT = 3

    def __init__(self):
        super().__init__(
            object,
            object,
            object,
            object
            )

    def remove_equations(self, tree_paths):
        for tree_path in reversed(tree_paths):
            self.remove(self.get_iter(tree_path))


class EquationList(Gtk.TreeView):

    def __init__(self, equation_store):
        super().__init__(
            model=equation_store,
            rubber_banding=True,
            fixed_height_mode=True,
            headers_visible=False
            )

        # Time 1
        renderer = Gtk.CellRendererText(xalign=1.0)
        col_time1 = Gtk.TreeViewColumn(_('Time 1'), renderer)
        col_time1.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_time1.set_expand(True)
        col_time1.set_cell_data_func(
            renderer, self._render_time, EquationStore.COL_TIME1)
        self.append_column(col_time1)

        # Operation
        renderer = Gtk.CellRendererText(xalign=0.5)
        col_operation = Gtk.TreeViewColumn('', renderer)
        col_operation.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_operation.set_cell_data_func(
            renderer, self._render_operation, EquationStore.COL_OPERATION)
        self.append_column(col_operation)

        # Time 2
        renderer = Gtk.CellRendererText(xalign=1.0)
        col_time2 = Gtk.TreeViewColumn(_('Time 2'), renderer)
        col_time2.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_time2.set_expand(True)
        col_time2.set_cell_data_func(
            renderer, self._render_time, EquationStore.COL_TIME2)
        self.append_column(col_time2)

        # Equals
        renderer = Gtk.CellRendererText(xalign=0.5, text='=')
        col_equals = Gtk.TreeViewColumn('', renderer)
        col_equals.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.append_column(col_equals)

        # Result
        renderer = Gtk.CellRendererText(xalign=1.0)
        col_result = Gtk.TreeViewColumn(_('Result'), renderer)
        col_result.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_result.set_expand(True)
        col_result.set_cell_data_func(
            renderer, self._render_time, EquationStore.COL_RESULT)
        self.append_column(col_result)

    def _render_time(self, col, cell, model, tree_iter, col_num):
        cell.props.text = ms_to_str(model[tree_iter][col_num], True)

    def _render_operation(self, col, cell, model, tree_iter, col_num):
        cell.props.text = ('+', '\N{MINUS SIGN}')[model[tree_iter][col_num]]
