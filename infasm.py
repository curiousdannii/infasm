#!/usr/bin/env python
# Infasm - An Inform 6 assembler for the Z-Machine
# Copyright (c) 2009, Dannii Willis
# Released under a BSD-like licence, see LICENCE

'''Infasm - An Inform 6 assembler for the Z-Machine

Usage: python infasm.py <source>
'''

from zmachine import zmachine

if __name__ == '__main__':
	import sys

	# Load the source file or print out the usage instructions
	try:
		filename = sys.argv[1]
	except IndexError:
		sys.exit(__doc__)
