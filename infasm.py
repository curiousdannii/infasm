from ply import lex, yacc

# Infasm - An Inform 6 assembler for the Z-Machine
# Copyright (c) 2009, Dannii Willis
# Released under a BSD-like licence, see LICENCE

# Assembly tokens
tokens = (
	'COMMENT',
	'NAME',
	'NUMBER',
	'OPCODE'
)

literals = '.;->?~[]'

# Token specifications
t_ignore_COMMENT = r'!.*'
t_NAME = r'[a-zA-Z][a-zA-Z0-9_]*'
t_OPCODE = r'@[a-zA-Z][a-zA-Z0-9_]*'

def t_NUMBER(t):
	r'($|-)?\d+'
	if t.value[0] == '$':
		base = 16
	else:
		base = 10
	try:
		t.value = int(t.value)
	except ValueError:
		print "Integer value too large", t.value
		t.value = 0 
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
