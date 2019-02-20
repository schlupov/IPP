<?php

require_once("./instructions/checkInstruction.php");

class VarSymbOperation {

    public function __construct($line) {
        $this->line = $line;
    }

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