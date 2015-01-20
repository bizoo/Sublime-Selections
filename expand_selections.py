import sublime
import sublime_plugin


class ExpandSelectionCustomCommand(sublime_plugin.TextCommand):
    """Expand current selections by one char to the right and/or left."""
    def run(self, edit, expand, right=False, left=False):
        sels = []
        viewsize = self.view.size()
        inc = 1 if expand else -1
        for sel in self.view.sel():
            a = sel.a
            b = sel.b
            if not (sel.size() == 0 and not expand):
                if right:
                    if sel.b >= sel.a:
                        b = sel.b + inc
                    else:
                        a = sel.a + inc
                if left:
                    if sel.b >= sel.a:
                        a = sel.a - inc
                    else:
                        b = sel.b - inc
            sels.append(sublime.Region(
                min(max(a, 0), viewsize),
                min(max(b, 0), viewsize), sel.xpos))
        self.view.sel().clear()
        for sel in sels:
            self.view.sel().add(sel)

        # Start a new undo group
        # token = edit.edit_token
        # self.view.end_edit(edit)
        # subedit = self.view.begin_edit(token, self.name())
        # try:
        #     self.view.sel().clear()
        #     for sel in sels:
        #         self.view.sel().add(sel)
        # finally:
        #     self.view.end_edit(subedit)


# Alternative solution: use standard commands and a reverse selection, but for multi-selection
# the regions must be normalized which is maybe not expected.
# Something like:
# class ExpandSelectionCustomCommand(sublime_plugin.TextCommand):
#     def run(self, edit, expand, right=False, left=False):
#         self.view.run_command("normalize_selection"} )
#         self.view.run_command("move", {"by": "characters", "forward": True, "extend": True} )
#         self.view.run_command("reverse_selection")
#         self.view.run_command("move", {"by": "characters", "forward": False, "extend": True} )
#         self.view.run_command("reverse_selection")


class SingleSelectionLastCommand(sublime_plugin.TextCommand):
    """Like single_selection command but keep only the last selection."""
    def run(self, edit):
        sels = self.view.sel()
        if len(sels):
            last_region = sels[-1]
            sels.clear()
            sels.add(last_region)
        # Call the single_selection selection command to scroll the
        # view in the correct position (and maybe other internal things...)
        self.view.run_command("single_selection")


class ReverseSelectionCommand(sublime_plugin.TextCommand):
    """Reverse selections."""
    def run(self, edit):
        sels = []
        for sel in self.view.sel():
            sels.append(sublime.Region(sel.b, sel.a, sel.xpos))
        self.view.sel().clear()
        for sel in sels:
            self.view.sel().add(sel)


class NormalizeSelectionCommand(sublime_plugin.TextCommand):
    """Normalize selections by putting the end of the region at the end of the selection."""
    def run(self, edit):
        sels = []
        for sel in self.view.sel():
            if sel.a > sel.b:
                sels.append(sublime.Region(sel.b, sel.a, sel.xpos))
        for sel in sels:
            self.view.sel().add(sel)


class NormalizeAndReverseSelectionCommand(sublime_plugin.TextCommand):
    """Either normalize selections if not already done or reverse selections."""
    def run(self, edit):
        if self.are_regions_normalized():
            self.view.run_command("reverse_selection")
        else:
            self.view.run_command("normalize_selection")

    def are_regions_normalized(self):
        return all(region.a <= region.b for region in self.view.sel())


class SplitSelectionCommand(sublime_plugin.TextCommand):
    """Split selections using separator argument if given or ask the user."""
    def run(self, edit, separator=None):
        if separator is not None:
            self.split_selection(separator)
        else:
            sublime.active_window().show_input_panel(
                "Separating character(s) for splitting the selection",
                "",
                self.split_selection,
                None,
                None
            )

    def split_selection(self, separator):
        view = self.view
        selections = view.sel()
        new_regions = []

        for region in selections:
            current_position = region.begin()
            region_string = view.substr(region)

            if separator:
                sub_regions = region_string.split(separator)
            else:
                # take each character separately
                sub_regions = list(region_string)

            for sub_region in sub_regions:
                new_region = sublime.Region(
                    current_position,
                    current_position + len(sub_region)
                )
                new_regions.append(new_region)
                current_position += len(sub_region) + len(separator)

        selections.clear()
        for region in new_regions:
            selections.add(region)
