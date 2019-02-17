<?php

require_once("./Scanner.php");
require_once("./Keywords.php");

class Parser {

    private $tokenized;
    private $line;
    private $call = false;

    public function __construct($tokenized, $line) {
        $this -> tokenized = $tokenized;
        $this -> line = $line;
        foreach (glob("./instructions/*.php") as $filename) {
            require_once($filename);
        }
    }

    public function instruction() {
        foreach($this->tokenized  as $key=>$value){
            foreach($value as $k => $v){
                if ($k == "KEYWORD") {
                    $keyWord = $value[$k][0];
                    $this->call = true;
                    $instruction = $this->witchInstruction($keyWord);
                    if ($instruction->checkLine() !== true) {
                        fwrite(STDERR, "Lexikalni nebo syntakticka chyba.\n");
                        exit (23);
                    }
                    echo "OK";
                }
            }
            if ($this->call === true) {
                    break;
            }
        }
        if (($this->call) == false) {
            fwrite(STDERR, "Neznamy nebo chybny operacni kod\n");
            exit (22);
        }
    }

    protected function witchInstruction($keyWord){
        switch ($keyWord) {
            case Keywords::MOVE:
                return new MOVE($this->line);
            case Keywords::CREATEFRAME:
                return new CREATEFRAME($this->line);
            case Keywords::PUSHFRAME:
                return new PUSHFRAME($this->line);
            case Keywords::POPFRAME:
                return new POPFRAME($this->line);
            case Keywords::DEFVAR:
                return new DEFVAR($this->line);
            case Keywords::CALL:
                return new CALL($this->line);
            case Keywords::RETURN:
                return new ReturnInstruction($this->line);
            case Keywords::PUSHS:
                return new PUSHS($this->line);
            case Keywords::POPS:
                return new POPS($this->line);
            case "ADD":
                return new ADD($this->line);
            case "SUB":
                return new SUB($this->line);
            case "MUL":
                return new MUL($this->line);
            case "IDIV":
                return new IDIV($this->line);
            case "LT":
                return new LT($this->line);
            case "GT":
                return new GT($this->line);
            case "EQ":
                return new EQ($this->line);
            case "AND":
                return new ANDInstruction($this->line);
            case "OR":
                return new ORInstruction($this->line);
            case "NOT":
                return new NOTInstruction($this->line);
            case "INT2CHAR":
                return new INT2CHAR($this->line);
            case "STRI2INT":
                return new STRI2INT($this->line);
            case "READ":
                return new READ($this->line);
            case "WRITE":
                return new WRITE($this->line);
            case "CONCAT":
                return new CONCAT($this->line);
            case "STRLEN":
                return new STRLEN($this->line);
            case "GETCHAR":
                return new GETCHAR($this->line);
            case "SETCHAR":
                return new SETCHAR($this->line);
            case "TYPE":
                return new TYPE($this->line);
            case "LABEL":
                return new LABEL($this->line);
            case "JUMP":
                return new JUMP($this->line);
            case "JUMPIFEQ":
                return new JUMPIFEQ($this->line);
            case "JUMPIFNEQ":
                return new JUMPIFNEQ($this->line);
            case "DPRINT":
                return new DPRINT($this->line);
            case "BREAK":
                return new BREAKInstruction($this->line);
        }

    }

    function __destruct() {
    }
}