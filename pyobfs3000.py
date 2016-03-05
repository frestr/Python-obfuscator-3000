#!/usr/bin/env python3

from sys import argv
from obfuscator import Obfuscator

def main():
    obfs = Obfuscator()
    
    try:
        argv[1]
        argv[2]
    except:
        print('Format: ./pyobfs3000.py <in_file> <out_file>')
        return;

    obfs.obfuscate_file(argv[1], argv[2])

if __name__ == '__main__':
    main()
