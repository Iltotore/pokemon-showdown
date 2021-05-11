# Pokemon Showdown Client
This a Python client for [Pokemon Showdown](https://play.pokemonshowdown.com/) with the aim of being more ergonomic and faster, especially for low internet connections.

## Features
### Performances
- Pre-download of assets including sprites and cries
- User teams saved locally
- The client isn't web-based: he doesn't need to be downloaded by the browser

### Ergonomy
- Material designed UI
- More streamlined/readable interface
- Hiddable Tabs/Chat
- Translations. Currently supported: English, French.
- PLANNED: Better TeamBuilder
- PLANNED: Chat-based battle historic
- PLANNED: Integrated damage calculator

## Installation
This project requires [Python 3+](https://www.python.org/downloads/) with the following packages:
- `kivy`
- `kivymd`
- `pyautogui`
- `asyncrequests`. Be careful with the spelling. `asyncrequest` is not the right package
- `websockets`. Same warning as `asyncrequests`

<details>
<summary>How to install packages ?</summary>

Once Python is installed, open the terminal and enter the following command:
```sh
python -m pip install <package>
```
Note: You can chain packages to install: `python -m pip install kivy kivymd etc...`

Note 2: If `python` is not found, try `python3` or `py`.

</details>


# Issues
Use the [issue section](https://github.com/Iltotore/pokemon-showdown/issues) to ask a question/report a problem.

For question, you can alternatively PM the following Discord account: `Il_totore#9133`.
