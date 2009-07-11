# Infasm - An Inform 6 assembler for the Z-Machine
# Copyright (c) 2009, Dannii Willis
# Released under a BSD-like licence, see LICENCE

from struct import pack
import time
import warnings

# Code generator
opcodes = {
	'storew': 'VAR:225',
	'push': 'VAR:232',
}

class ZDirectiveCollection():
	def __init__(self, vm, collection):
		self.vm = vm
		self.data = collection.data
		self.names = collection.names

class ZArrays(ZDirectiveCollection):
	def bytecode(self):
		'''Output arrays to bytecode'''
		for array in self.data:
			array.addr = self.vm.offset
			size = array.size * array.length
			self.vm.offset += size
			self.vm.bytecode += '\x00' * size

class ZGlobals(ZDirectiveCollection):
	def bytecode(self):
		'''Output globals to bytecode'''
		for globalvar in self.data:
			globalvar.addr = self.vm.offset
			self.vm.offset += 2
			self.vm.bytecode += pack('>H', globalvar.value)

class ZFunctions(ZDirectiveCollection):
	def bytecode(self):
		'''Output functions to bytecode'''
		for function in self.data:
			# Align the function to a packed address
			while self.vm.offset % 4:
				self.vm.offset += 1
				self.vm.bytecode += '\x00'
			function.addr = self.vm.offset

			# Push the number of locals
			self.vm.bytecode += pack('>B', len(function.locals))

			# Encode instructions
			for s in function.statements:
				if s[2] not in opcodes:
					warnings.warn('''Line %d: no opcode named %s''' % (s[1], s[2]))
					continue

				# Process operands

class zmachine():
	'''Code generator for the Z-Machine'''

	def __init__(self, asmfile):
		self.offset = 0x3E
		self.bytecode = ''
		self.arrays = ZArrays(self, asmfile.arrays)
		self.constants = ZDirectiveCollection(self, asmfile.constants)
		self.globals = ZGlobals(self, asmfile.globals)
		self.functions = ZFunctions(self, asmfile.functions)

		self.assemble()

	def assemble(self):
		abbreviations_offset = self.offset
		objects_offset = self.offset

		# Build global vars table
		globals_offset = self.offset
		self.globals.bytecode()

		# Build arrays
		self.arrays.bytecode()

		# Add the first function

		# Build the functions
		functions_offset = self.offset
		self.functions.bytecode()

		# Static strings
		strings_offset = self.offset

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
			0, # Header extension table
			0, 0, # ? ?
			'INFA'
		]
		header_format = '>BBHHHHHHHH6sHHHBBBBHHBBHHBBHHBBHHHH4s'
		self.bytecode = pack(header_format, *header) + self.bytecode

		return self.bytecode
