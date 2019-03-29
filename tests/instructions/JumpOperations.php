<?php

require_once("./instructions/checkInstruction.php");

/**
* Třída kontroluje počet argumentů skokových operací a jestli se správně jedná o návěští a dvě konstanty nebo proměnné
* @param string $line řádek ze stdin
*/
class JumpOperations {

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
        if (($check->checkLabel($arg1)) && ($check->arguments($arg2, false)) &&
            ($check->arguments($arg3, false))) {
            return true;
        }
        return false;
    }

    function __destruct() {
    }
}
