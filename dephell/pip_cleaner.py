# built-in
import sys


whitelist = {
    'Collecting ',
    'Installing collected packages: ',
    'Successfully installed ',
    'Requirement already satisfied: ',
}

if __name__ == '__main__':
    for line in sys.stdin:
        for pattern in whitelist:
            if pattern in line:
                print(line.strip())
                break
