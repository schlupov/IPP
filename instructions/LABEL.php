<?php

require_once("./instructions/checkInstruction.php");

/**
* Třída kontroluje počet argumentů operací pracujích s návěštím a jestli se správně jedná o jeno návěští
* @param string $line řádek ze stdin
*/
class LABEL {

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
        if (($check->checkLabel($arg1))) {
            return true;
        }
        return false;
    }

    function __destruct() {
    }
}
