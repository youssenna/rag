with open('data/raw/.txt') as f:
    while x := f.read(12):
        print(x)