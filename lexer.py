# Infasm - An Inform 6 assembler for the Z-Machine
# Copyright (c) 2009, Dannii Willis
# Released under a BSD-like licence, see LICENCE

from ply import lex
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

# Build the lexer
lexer = lex.lex()
