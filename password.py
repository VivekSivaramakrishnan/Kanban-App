import hashlib

def source(user, password):
    return user + password

hasher = lambda user, password: hashlib.md5(source(user, password).encode()).hexdigest()

if __name__ == "__main__":

    user, pw = input('Enter username: '), input('Enter password: ')
    res = source(user, pw)
    hash = hasher(user, pw)
    print(f'Hash input: {res}\nHash Output: {hash}')
