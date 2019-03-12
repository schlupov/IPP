<?php

require_once("./instructions/checkInstruction.php");

/**
* Třída kontroluje počet argumentů aritmetických operací a jestli se správně jedná o proměnnou a dvě konstanty nebo proměnné
* @param string $line řádek ze stdin
*/
class ArithmeticOperations {

    public function __construct($line) {
        $this->line = $line;
    }

    /**
    * Metoda kontroluje počet argumentů a syntax proměnných daného operačního kodu
    * Vrací true, pokud vše v pořádku, jinak vrací false
    */
    public function checkLine() {
        $check = new checkInstruction();
        $check->checkNumberOfParameters($this->line, 3);
        $arg1 = $this->line[1];
        $arg2 = $this->line[2];
        $arg3 = $this->line[3];
        if (($check->arguments($arg1, true)) && ($check->arguments($arg2, false)) && ($check->arguments($arg3, false))) {
            return true;
        }
        return false;
    }

    function __destruct() {
    }
}
