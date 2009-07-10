# Infasm - An Inform 6 assembler for the Z-Machine
# Copyright (c) 2009, Dannii Willis
# Released under a BSD-like licence, see LICENCE

from ply import yacc
import warnings
from lexer import tokens

# An assembly file
def p_file(p):
	'''file : file directive
            | empty'''
	if len(p) == 3:
		if p[2]:
			p[1].append(p[2])
		p[0] = p[1]
	else:
		p[0] = ['file']

# An Inform 6 directive... or some of them at least
def p_directive(p):
	'''directive : array
	             | constant
	             | function
	             | global'''
	p[0] = p[1]

# Array declarations
class Array():
	def __init__(self, name, length, size, lineno):
		self.name = name
		self.length = length
		self.size = size
		self.lineno = lineno

class Arrays():
	def __init__(self):
		self.data = []
		self.names = {}

	def append(self, array):
		self.data.append(array)
		if array.name in self.names:
			warnings.warn('''Line %d: Array '%s' already defined, overwriting''' % (array.lineno, array.name))
		self.names[array.name] = array

arrays = Arrays()

def p_wordarray(p):
	'''array : ARRAY ID '-' '-' '>' NUMBER ';' '''
	arrays.append(Array(p[2], p[6], 2, p.lineno(1)))

def p_bytearray(p):
	'''array : ARRAY ID '-' '>' NUMBER ';' '''
	arrays.append(Array(p[2], p[5], 1, p.lineno(1)))

# Constant declarations
class Constant():
	def __init__(self, name, value, lineno):
		self.name = name
		self.value = value
		self.lineno = lineno

class Constants():
	def __init__(self):
		self.data = []
		self.names = {}

	def append(self, array):
		self.data.append(array)
		if array.name in self.names:
			warnings.warn('''Line %d: Constant '%s' already defined, overwriting''' % (array.lineno, array.name))
		self.names[array.name] = array

constants = Constants()

def p_constant(p):
	'''constant : CONSTANT ID '=' NUMBER ';'
	            | CONSTANT ID NUMBER ';'
	            | CONSTANT ID ';' '''
	if len(p) == 6:
		constants.append(Constant(p[2], p[4], p.lineno(1)))
	elif len(p) == 5:
		constants.append(Constant(p[2], p[3], p.lineno(1)))
	else:
		constants.append(Constant(p[2], 0, p.lineno(1)))

# Global variables
class Global():
	def __init__(self, name, value, lineno):
		self.name = name
		self.value = value
		self.lineno = lineno

class Globals():
	def __init__(self):
		self.data = []
		self.names = {}

	def append(self, array):
		self.data.append(array)
		if array.name in self.names:
			warnings.warn('''Line %d: Global '%s' already defined, overwriting''' % (array.lineno, array.name))
		self.names[array.name] = array

globalvars = Globals()

def p_global(p):
	'''global : GLOBAL ID '=' NUMBER ';' '''
	globalvars.append(Global(p[2], p[6], p.lineno(1)))

# An Inform 6 function
def p_function(p):
	'''function : '[' ID localvars ';' statements ']' ';' '''
	p[0] = ['function', p.lineno(1), p[2], p[3], p[5]]

# A function's local variables list
def p_localvars(p):
	'''localvars : localvars ID
	             | empty'''
	if len(p) == 3:
		p[1].append(p[2])
		p[0] = p[1]
	else:
		p[0] = ['localvars']

# A list of statements
def p_statements(p):
	'''statements : statements statement
	              | empty'''
	if len(p) == 3:
		p[1].append(p[2])
		p[0] = p[1]
	elif len(p) == 2:
		p[0] = ['statements']

# An actual statement! :)
def p_statement(p):
	'''statement : OPCODE operands ';' '''
	p[0] = ['statement', p.lineno(1), p[1], p[2]]

# The list of operands
def p_operands(p):
	'''operands : operands ID
	            | operands NUMBER
	            | empty'''
	if len(p) == 3:
		p[1].append(p[2])
		p[0] = p[1]
	elif len(p) == 2:
		p[0] = ['operands']

# An empty terminal, simplifies a lot of the above
def p_empty(p):
	'''empty :'''
	pass

# Oh dear what have we done
def p_error(t):
	print "Syntax error at '%s'" % t.value 

# Build the parser
parser = yacc.yacc()
