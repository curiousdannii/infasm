#!/usr/bin/env python
# Infasm - An Inform 6 assembler for the Z-Machine
# Copyright (c) 2009, Dannii Willis
# Released under a BSD-like licence, see LICENCE

'''Infasm - An Inform 6 assembler for the Z-Machine

Usage: python infasm.py <source>
'''

from lexer import lexer
from parser import parser
from zmachine import zmachine

def assemble(source):
	'''Assemble a infasm source file'''
	asmfile = parser.parse(source, lexer = lexer)
	gen = zmachine(asmfile)
	return gen

if __name__ == '__main__':
	import os, sys

	# Load the source file or print out the usage instructions
	try:
		filename = sys.argv[1]
	except IndexError:
		sys.exit(__doc__)

	# Assemble the story file
	source = file(filename).read()
	storyfile = assemble(source).bytecode
	storyfilename = os.path.splitext(filename)[0] + '.z5'
	output = open(storyfilename, 'w')
	output.write(storyfile)
	output.close()
