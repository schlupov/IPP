<?php

require_once("./instructions/checkInstruction.php");

/**
* Třída kontroluje počet argumentů operací, které mohou pracovat pouze s proměnnou a jestli se jedná o validní proměnnou
* @param string $line řádek ze stdin
*/
class VarOperations {

    public function __construct($line) {
        $this->line = $line;
    }

    /**
    * Metoda kontroluje počet argumentů a syntax proměnných daného operačního kodu
    * Vrací true, pokud vše v pořádku, jinak vrací false
    */
    public function checkLine() {
        $check = new checkInstruction();
        $check->checkNumberOfParameters($this->line, 1);
        $arg1 = $this->line[1];
        if (($check->arguments($arg1, true))) {
            return true;
        }
        return false;
    }

    function __destruct() {
    }
}
