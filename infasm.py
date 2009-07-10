# Infasm - An Inform 6 assembler for the Z-Machine
# Copyright (c) 2009, Dannii Willis
# Released under a BSD-like licence, see LICENCE

from ply import lex, yacc
import time
from struct import pack
import warnings

# Some of the Inform 6 directives
directives = {
	'array': 'ARRAY',
	'constant': 'CONSTANT',
	'global': 'GLOBAL',
}

# Assembly tokens
tokens = [
	'COMMENT',
	'ID',
	'LABEL',
	'NUMBER',
	'OPCODE',
] + list(directives.values())

literals = ';->?~[]='

# Token specifications
t_ignore_COMMENT = r'!.*'

# Convert IDs to lowercase and check for directives
def t_ID(t):
	r'[a-zA-Z][a-zA-Z_0-9]*'
	t.value = t.value.lower()
	t.type = directives.get(t.value,'ID')
	return t

# Strip the . and ; from labels
def t_LABEL(t):
	r'\.[a-zA-Z][a-zA-Z0-9_]*;'
	t.value = t.value[1:-1]
	return t

# Allow decimal and hexadecimal number literals
def t_NUMBER(t):
	r'(\$|-)?\d+'
	if t.value[0] == '$':
		base = 16
		t.value = t.value[1:]
	else:
		base = 10
	try:
		t.value = int(t.value, base)
	except ValueError:
		print "Integer value too large", t.value
		t.value = 0 
	return t

# Strip the initial @ from opcodes
def t_OPCODE(t):
	r'@[a-zA-Z][a-zA-Z0-9_]*'
	t.value = t.value[1:]
	return t

# Non-tokens
t_ignore = " \t"

def t_newline(t):
	r'\n+'
	t.lexer.lineno += t.value.count("\n")

# Error handling rule
def t_error(t):
	print "Illegal character '%s'" % t.value[0]
	t.lexer.skip(1)

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
arrays = {}
def p_wordarray(p):
	'''array : ARRAY ID '-' '-' '>' NUMBER ';' '''
	if p[2] in arrays:
		warnings.warn('''Line %d: Array '%s' already defined, overwriting''' % (p.lineno(2), p[2]))
	arrays[p[2]] = {'len': p[6]}
	p[0] = ['array', p[2], p[6]]

# Constant declarations
constants = {}
def p_constant(p):
	'''constant : CONSTANT ID '=' NUMBER ';'
	            | CONSTANT ID NUMBER ';'
	            | CONSTANT ID ';' '''
	if p[2] in constants:
		warnings.warn('''Line %d: Constant '%s' already defined, overwriting''' % (p.lineno(2), p[2]))
	if len(p) == 6:
		constants[p[2]] = p[4]
		p[0] = ['constant', p[2], p[4]]
	elif len(p) == 5:
		constants[p[2]] = p[3]
		p[0] = ['constant', p[2], p[3]]
	else:
		constants[p[2]] = 0
		p[0] = ['constant', p[2], 0]

# Global variables
globalvars = {}
def p_global(p):
	'''global : GLOBAL ID '=' NUMBER ';' '''
	if p[2] in globalvars:
		warnings.warn('''Line %d: Global '%s' already defined, overwriting''' % (p.lineno(2), p[2]))
	globalvars[p[2]] = {'value': p[6]}
	p[0] = ['global', p[2], p[6]]

# An Inform 6 function
functionlist = {}
def p_function(p):
	'''function : '[' ID localvars ';' statements ']' ';' '''
	functionlist[p[2]] = {'localvars': p[3][1:], 'statements': p[5][1:]}
	p[0] = ['function', p[2], p[3], p[5]]

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

# Build the lexer
lexer = lex.lex()

# Build the parser
parser = yacc.yacc()

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
