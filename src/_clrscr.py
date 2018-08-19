'''
Simple function to clear the terminal screen.
'''

from os import system
from os import name


def clrscr():
    '''Method to clear the terminal screen'''

    _ = system('cls' if name == 'nt' else 'clear')
