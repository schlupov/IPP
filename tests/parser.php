<?php

require_once("./Scanner.php");
require_once("./Keywords.php");

/**
* Třída Parser je hlavni třída syntaktické analýzy. Pracuje s tokeny a řádky načtené pomocí parse.php.
* @param string $tokenized řádek ze stdin převedený na asociativní pole reprezentující tokeny
* @param string $line řádek ze stdin
*/
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

    /**
    * Metoda instruction zkontroluje, že řádek začíná některým z operačních kodu a podle toho o který operační
    * kod se jedná, vytvoří instanci třídy dané instrukce a předá této třídě řádek ke kontrole.
    * Začíná-li řádek neznámým operačním kodem, je program ukončen s chybou 22. Pokud řádek neprojde syntaktickou
    * kontrolou, je program ukončen s chybou 23.
    */
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
                    return true;
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

    /**
    * Metoda na základě proměnné v $keyWord rozhodne o který operační kod se jedná na daném řádku
    */
    protected function witchInstruction($keyWord){
        switch ($keyWord) {
            case Keywords::CREATEFRAME:
            case Keywords::PUSHFRAME:
            case Keywords::POPFRAME:
            case Keywords::RETURN:
            case Keywords::BREAK:
                return new NoArgumentsOperations($this->line);
            case Keywords::DEFVAR:
            case Keywords::POPS:
                return new VarOperations($this->line);
            case Keywords::CALL:
            case Keywords::LABEL:
            case Keywords::JUMP:
                return new LABEL($this->line);
            case Keywords::PUSHS:
            case Keywords::WRITE:
            case Keywords::EXIT:
            case Keywords::DPRINT:
                return new SymbOperation($this->line);
            case Keywords::ADD:
            case Keywords::SUB:
            case Keywords::MUL:
            case Keywords::IDIV:
            case Keywords::LT:
            case Keywords::GT:
            case Keywords::EQ:
            case Keywords::AND:
            case Keywords::OR:
            case Keywords::STRI2INT:
            case Keywords::CONCAT:
            case Keywords::GETCHAR:
            case Keywords::SETCHAR:
                return new ArithmeticOperations($this->line);
            case Keywords::MOVE:
            case Keywords::NOT:
            case Keywords::INT2CHAR:
            case Keywords::STRLEN:
            case Keywords::TYPE:
                return new VarSymbOperation($this->line);
            case Keywords::READ:
                return new READ($this->line);
            case Keywords::JUMPIFEQ:
            case Keywords::JUMPIFNEQ:
                return new JumpOperations($this->line);
        }

    }

    function __destruct() {
    }
}
