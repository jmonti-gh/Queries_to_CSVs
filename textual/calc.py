### pip install textual

from textual.app import App, ComposeResult
from textual.widgets import Welcome

class WelcomeApp(App):
    # def compose(self) -> ComposeResult:
    #     yield Welcome()
    def on_key(self) -> None:
        self.mount(Welcome())

    def on_button_pressed(self) -> None:
        self.exit()

if __name__ == '__main__':
    print('MAIN!!')
    app = WelcomeApp()
    app.run