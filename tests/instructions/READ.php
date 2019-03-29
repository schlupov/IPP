<?php

require_once("./instructions/checkInstruction.php");

/**
* Třída kontroluje počet argumentů operace READ a jestli se správně jedná o proměnnou a int, string nebo bool
* @param string $line řádek ze stdin
*/
class READ {

    public function __construct($line) {
        $this->line = $line;
    }

    /**
    * Metoda kontroluje počet argumentů a syntax proměnných daného operačního kodu
    * Vrací true, pokud vše v pořádku, jinak vrací false
    */
    public function checkLine() {
        $check = new checkInstruction();
        $check->checkNumberOfParameters($this->line, 2);
        $arg1 = $this->line[1];
        $arg2 = $this->line[2];
        if (($check->arguments($arg1, true)) &&
            ($arg2 == "int" || $arg2 == "string" || $arg2 == "bool")) {
            return true;
        }
        return false;
    }

    function __destruct() {
    }
}
