from getpass import getpass

from libdyson import DysonAccount

email = input("Email: ")
password = getpass()
country = input("Country: ")
account = DysonAccount(country, email, password)
account.login()

devices = account.devices()
for device in devices:
    print()
    print(f"Serial: {device.serial}")
    print(f"Name: {device.name}")
    print(f"credential: {device.credential}")
