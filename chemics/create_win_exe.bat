pyinstaller ^
--onefile ^
--exclude-module PyQt5 ^
--hidden-import=scipy.constants ^
--clean --icon="assets/icon.ico" ^
--add-data="assets/icon.png;img" ^
--add-data="assets/icon.ico;img" ^
--name="chemics" ^
main.py