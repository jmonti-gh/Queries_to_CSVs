### pip install textual

from textual.app import App

class Beeper(App):
    def on_key(self):
        self.console.bell()


# from rich.panel import Panel

# from textual.app import App
# from textual.reactive import Reactive
# from textual.widget import Widget


# class Hover(Widget):

#     mouse_over = Reactive(False)

#     def render(self) -> Panel:
#         return Panel("Hello [b]World[/b]", style=("on red" if self.mouse_over else ""))

#     def on_enter(self) -> None:
#         self.mouse_over = True

#     def on_leave(self) -> None:
#         self.mouse_over = False


# class HoverApp(App):
#     """Demonstrates custom widgets"""

#     async def on_mount(self) -> None:
#         hovers = (Hover() for _ in range(10))
#         await self.view.dock(*hovers, edge="top")


if __name__ == '__main__':
    print('MAIN!!')
    beep1 = Beeper()
    beep1.run