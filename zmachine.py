# Infasm - An Inform 6 assembler for the Z-Machine
# Copyright (c) 2009, Dannii Willis
# Released under a BSD-like licence, see LICENCE

from struct import pack
import time
import warnings
from parser import *

# Code generator
opcodes = {
	'storew': 'VAR:225',
	'push': 'VAR:232',
}

def generate_code():
	offset = 0x3E
	bitcode = ''
	abbreviations_offset = offset
	header_extension = offset
	objects_offset = offset

	# Build global vars table
	globals_offset = offset
	for k, v in globalvars.items():
		globalvars[k]['addr'] = offset
		offset += 2
		bitcode += pack('>H', v['value'])

	# Build arrays
	for k, v in arrays.items():
		arrays[k]['addr'] = offset
		offset += 2 * v['len']
		bitcode += '\x00' * 2 * v['len']

	# Build the functions
	functions_offset = offset

	# Add the first function

	# Compile the rest
	for k, v in functionlist.items():
		# Align the function to a packed address
		while offset % 4:
			offset += 1
			bitcode += '\x00'
		functionlist[k]['addr'] = offset

		# Push the number of locals
		bitcode += pack('>B', len(v['localvars']))

		# Encode instructions
		for s in v['statements']:
			if s[2] not in opcodes:
				warnings.warn('''Line %d: no opcode named %s''' % (s[1], s[2]))
				continue

			# Process operands

	# Static strings
	strings_offset = offset

	# Add the header
	header = [
		5, 0, # Version number, Flags 1
		1, # Release number
		0, # High memory
		0, # PC
		0, # Dictionary
		objects_offset, # Object table
		globals_offset, # Global variables table
		0, # Static memory
		0, # Flags 2
		time.strftime('%y%m%d'), # Serial number
		abbreviations_offset, # Abbreviations table
		0, # File length
		0, # Checksum
		0, 0, # Interpreter number, version
		0, 0, # Screen height and width
		0, # Screen width in units
		0, # Screen height in units
		0, 0, # Font width and height in units
		functions_offset, # Functions offset
		strings_offset, # Static strings offset
		0, 0, # Default colours
		0, # Terminating characters table
		0, # Total width in pixels of text sent to output stream 3 
		0, 0, # Z-Machine Spec version number
		0, # Alphabet table address
		header_extension, # Header extension table
		0, 0, # ? ?
		'INFA'
	]
	header_format = '>BBHHHHHHHH6sHHHBBBBHHBBHHBBHHBBHHHH4s'
	bitcode = pack(header_format, *header) + bitcode

	return bitcode
