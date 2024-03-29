from enum import Enum


class KeyWords(Enum):
    MOVE = "MOVE"
    CREATEFRAME = "CREATEFRAME"
    PUSHFRAME = "PUSHFRAME"
    POPFRAME = "POPFRAME"
    DEFVAR = "DEFVAR"
    CALL = "CALL"
    RETURN = "RETURN"
    PUSHS = "PUSHS"
    POPS = "POPS"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    IDIV = "IDIV"
    LT = "LT"
    GT = "GT"
    EQ = "EQ"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    INT2CHAR = "INT2CHAR"
    STRI2INT = "STRI2INT"
    READ = "READ"
    WRITE = "WRITE"
    CONCAT = "CONCAT"
    STRLEN = "STRLEN"
    GETCHAR = "GETCHAR"
    SETCHAR = "SETCHAR"
    TYPE = "TYPE"
    LABEL = "LABEL"
    JUMP = "JUMP"
    JUMPIFEQ = "JUMPIFEQ"
    JUMPIFNEQ = "JUMPIFNEQ"
    EXIT = "EXIT"
    DPRINT = "DPRINT"
    BREAK = "BREAK"
