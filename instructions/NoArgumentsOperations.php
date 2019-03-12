<?php

require_once("./instructions/checkInstruction.php");

/**
* Třída kontroluje počet argumentů operací, které nepracují s žádnými argumenty
* @param string $line řádek ze stdin
*/
class NoArgumentsOperations {

    public function __construct($line) {
        $this->line = $line;
    }

    /**
    * Metoda kontroluje počet argumentů a syntax proměnných daného operačního kodu
    * Vrací true, pokud vše v pořádku, jinak vrací false
    */
    public function checkLine() {
        $check = new checkInstruction();
        if ($check->checkNumberOfParameters($this->line, 0)) {
            return true;
        }
        return false;
    }

    function __destruct() {
    }
}
