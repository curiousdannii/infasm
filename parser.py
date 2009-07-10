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

# Build the parser
parser = yacc.yacc()
