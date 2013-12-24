import sublime
import sublime_plugin


class ExpandSelectionCustomCommand(sublime_plugin.TextCommand):
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

# Another solution is to use standard command and a reverse selection, but in multi-selection,
# it only works if the Regions are in the same directions (all b > a or inverse).
# Something like:
# class ExpandSelectionCustomCommand(sublime_plugin.TextCommand):
#     def run(self, edit, expand, right=False, left=False):
#         self.view.run_command("move", {"by": "characters", "forward": True, "extend": True} )
#         self.view.run_command("reverse_selection")
#         self.view.run_command("move", {"by": "characters", "forward": False, "extend": True} )
#         self.view.run_command("reverse_selection")


class SingleSelectionLastCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = self.view.sel()
        if len(sels):
            last_region = sels[-1]
            sels.clear()
            sels.add(last_region)
        # Call the single_selection selection command for the last command to
        # scroll the view in the correct position (and maybe other internal things...)
        self.view.run_command("single_selection")


class ReverseSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = []
        for sel in self.view.sel():
            sels.append(sublime.Region(sel.b, sel.a, sel.xpos))
        self.view.sel().clear()
        for sel in sels:
            self.view.sel().add(sel)
