<?php

require_once("./instructions/checkInstruction.php");

class INT2CHAR {

    public function __construct($line) {
        $this->line = $line;
    }

    public function checkLine() {
        $check = new checkInstruction();
        $check->checkNumberOfParameters($this->line, 2);
        $arg1 = $this->line[1];
        $arg2 = $this->line[2];
        if (($check->arguments($arg1, true)) && ($check->checkAritmeticalOperation($arg2))) {
            return true;
        }
        return false;
    }

    function __destruct() {
    }
}