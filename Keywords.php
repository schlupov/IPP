<?php

class Keywords {
    public const MOVE = "MOVE";
    public const CREATEFRAME = "CREATEFRAME";
    public const PUSHFRAME = "PUSHFRAME";
    public const POPFRAME = "POPFRAME";
    public const DEFVAR = "DEFVAR";
    public const CALL = "CALL";
    public const RETURN = "RETURN";
    public const PUSHS = "PUSHS";
    public const POPS = "POPS";
    public const ADD = "ADD";
    public const SUB = "SUB";
    public const MUL = "MUL";
    public const IDIV = "IDIV";
    public const LT = "LT";
    public const GT = "GT";
    public const EQ = "EQ";
    public const AND = "AND";
    public const OR = "OR";
    public const NOT = "NOT";
    public const INT2CHAR = "INT2CHAR";
    public const STRI2INT = "STRI2INT";
    public const READ = "READ";
    public const WRITE = "WRITE";
    public const CONCAT = "CONCAT";
    public const STRLEN = "STRLEN";
    public const GETCHAR = "GETCHAR";
    public const SETCHAR = "SETCHAR";
    public const TYPE = "TYPE";
    public const LABEL = "LABEL";
    public const JUMP = "JUMP";
    public const JUMPIFEQ = "JUMPIFEQ";
    public const JUMPIFNEQ = "JUMPIFNEQ";
    public const EXIT = "EXIT";
    public const DPRINT = "DPRINT";
    public const BREAK = "BREAK";
    public const GF = "GF";
    public const TF = "TF";
    public const LF = "LF";
    public const true = "true";
    public const false = "false";
    public const nil = "nil";
    public const int = "int";
    public const string = "string";
    public const end = "end";

    public static function getConstants() {
        $oClass = new ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}

class SpecialWords {
    public const GF = "GF";
    public const TF = "TF";
    public const LF = "LF";
    public const true = "true";
    public const false = "false";
    public const nil = "nil";
    public const int = "int";
    public const string = "string";
    public const end = "end";
    public const while = "while";

    public static function getConstants() {
        $oClass = new ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}