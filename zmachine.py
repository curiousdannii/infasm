# Infasm - An Inform 6 assembler for the Z-Machine
# Copyright (c) 2009, Dannii Willis
# Released under a BSD-like licence, see LICENCE

from struct import pack
import time
import warnings
from parser import Function

# Code generator
opcodes = {
	'rtrue': ('0OP', 176),
	'quit': ('0OP', 186),
	'call_vs': ('VAR', 224),
	'storew': ('VAR', 225),
	'push': ('VAR', 232),
}

class ZDirectiveCollection():
	def __init__(self, vm, collection):
		self.vm = vm
		self.data = collection.data
		self.names = collection.names

	def __contains__(self, key):
		return key in self.names

	def __getitem__(self, key):
		if type(key) == int:
			return self.data[key]
		else:
			return self.names[key]

	def index(self, key):
		return self.data.index(key)

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
			self.vm.bytecode += pack('>B', len(function.locals)) + '\x00' * 2 * len(function.locals)

			# Encode instructions
			for s in function.statements:
				if s[1] not in opcodes:
					warnings.warn('''Line %d: no opcode named %s''' % (s[0], s[1]))
					continue
				instruction = opcodes[s[1]]

				# Process operands
				operands = []
				for o in s[2]:
					# Literal constant
					if type(o) == int:
						value = o
						op_type = (o <= 0xFF and 1 or 0)

					# Stack pointer
					elif o == 'sp':
						value = 0
						op_type = 2

					# Local variable
					elif o in function.locals:
						value = function.locals.index(o) + 1
						op_type = 2

					# Constant directive
					elif o in self.vm.constants:
						value = self.vm.constants[o].value
						op_type = (value <= 0xFF and 1 or 0)

					# Global variable
					elif o in self.vm.globals:
						value = self.vm.globals.index(o) + 16
						op_type = 2

					# Array directive
					elif o in self.vm.arrays:
						value = self.vm.arrays[o].addr
						op_type = (value <= 0xFF and 1 or 0)

					operands.append({'value': value, 'type': op_type})

				# Output the instruction
				self.vm.bytecode += pack('>B', instruction[1])

				if instruction[0] == 'VAR':
					# Output operand types
					types = 0
					for i in range(len(operands)):
						types = types | (operands[i]['type'] << (6 - 2 * i))
					for i in range(len(operands), 4):
						types = types | (3 << (6 - 2 * i))
					self.vm.bytecode += pack('>B', types)

				# Output the operand values
				for o in operands:
					if o['type'] == 0:
						self.vm.bytecode += pack('>H', o['value'])
					elif o['type'] != 3:
						self.vm.bytecode += pack('>B', o['value'])
					

class zmachine():
	'''Code generator for the Z-Machine'''

	def __init__(self, asmfile):
		self.offset = 0x40
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
		main_function = self.functions['main']
		if len(self.functions[0].locals) > 0:
			starting_function = '__main__'
			self.functions.data.insert(0, Function('__main__', [], [[0, 'call_vs', []], [0, 'quit', []]], 0))
			self.functions.names['__main__'] = self.functions.data[0]
			if main_function.statements[-1][1] not in ('rtrue'):
				main_function.statements.append([0, 'rtrue', []])
		else:
			starting_function = 'main'
			if main_function.statements[-1][1] in ('rtrue'):
				main_function.statements.pop()
			if main_function.statements[-1][1] != 'quit':
				main_function.statements.append([0, 'quit', []])

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
			self.functions[starting_function].addr + 1, # PC
			0, # Dictionary
			objects_offset, # Object table
			globals_offset, # Global variables table
			0, # Static memory
			0, # Flags 2
			time.strftime('%y%m%d'), # Serial number
			abbreviations_offset, # Abbreviations table
			(len(self.bytecode) + 0x3E) / 4, # File length
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
