<?php

require_once("./instructions/checkInstruction.php");

/**
* Třída kontroluje počet argumentů operací pracujích s proměnnou a jednou konstantou nebo proměnnou
* a jestli se jedná o validní proměnnou a konstantu nebo proměnnou
* @param string $line řádek ze stdin
*/
class VarSymbOperation {

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
        if (($check->arguments($arg1, true)) && ($check->arguments($arg2, false))) {
            return true;
        }
        return false;
    }

    function __destruct() {
    }
}
