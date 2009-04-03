# Infasm - An Inform 6 assembler for the Z-Machine
# Copyright (c) 2009, Dannii Willis
# Released under a BSD-like licence, see LICENCE

from ply import lex, yacc
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
	arrays[p[2]] = p[6]

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
	elif len(p) == 5:
		constants[p[2]] = p[3]
	else:
		constants[p[2]] = 0

# Global variables
globalvars = {}
def p_global(p):
	'''global : GLOBAL ID '=' NUMBER ';' '''
	if p[2] in globalvars:
		warnings.warn('''Line %d: Global '%s' already defined, overwriting''' % (p.lineno(2), p[2]))
	globalvars[p[2]] = p[4]

# An Inform 6 function
def p_function(p):
	'''function : '[' ID localvars ';' statements ']' ';' '''
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
	p[0] = ['statement', p[1], p[2]]

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
