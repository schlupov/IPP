<?php

require_once("./instructions/checkInstruction.php");

class VarOperations {

    public function __construct($line) {
        $this->line = $line;
    }

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