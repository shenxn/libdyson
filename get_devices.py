from getpass import getpass
from libdyson import DysonAccount


email = input("Email: ")
password = getpass()
country = input("Country: ")
account = DysonAccount(email, password, country)
account.login()

devices = account.devices()
for device in devices:
    print()
    print(f"Serial: {device.serial}")
    print(f"Name: {device.name}")
    print(f"credential: {device.credential}")
