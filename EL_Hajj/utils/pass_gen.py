from django.contrib.auth.hashers import make_password

password = "Hello2003"
# admin, doctor, drawing_manager, payment_manager, user, hajj
accounts = 1 + 5 + 5 + 5 + 50 + 35
file_path = "/home/merzouka/code/hajj/backend/EL_Hajj/utils/seed/passwords.txt"

def gen_pass_file():
    with open(file_path, "w") as passwords_file:
        passwords = []
        for _ in range(accounts):
            passwords.append(make_password(password))
        passwords_file.write("\n".join(passwords))


