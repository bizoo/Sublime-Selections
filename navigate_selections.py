import sublime_plugin


class NavigateSelectionsCommand(sublime_plugin.WindowCommand):
    """Scroll the view up/down to the next selections"""
    def run(self, forward=True, wrap=True):
        if not self.window.active_view():
            return

        sels = self.window.active_view().sel()
        if len(sels) == 0:
            return

        visible_region = self.window.active_view().visible_region()
        if forward:
            iterator = reversed(sels)
        else:
            iterator = sels

        next_sel = None
        for s in iterator:
            if visible_region.intersects(s):
                break
            elif (forward and s < visible_region) or (not forward and s > visible_region):
                break
            next_sel = s

        if next_sel is None and wrap:
            if forward:
                next_sel = sels[0]
            else:
                next_sel = sels[-1]

        if next_sel is not None:
            self.window.active_view().show(next_sel, True)
