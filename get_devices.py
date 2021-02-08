from getpass import getpass

from libdyson import DysonAccount

email = input("Email: ")
password = getpass()
country = input("Country: ")
account = DysonAccount(country)
account.login(email, password)

devices = account.devices()
for device in devices:
    print()
    print(f"Serial: {device.serial}")
    print(f"Name: {device.name}")
    print(f"Device Type: {device.product_type}")
    print(f"Credential: {device.credential}")
