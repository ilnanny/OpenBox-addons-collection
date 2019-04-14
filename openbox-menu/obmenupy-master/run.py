from sys import argv
from lib.MenuApplication import MenuApplication

app = MenuApplication(argv)
result = app.run()
print(result)