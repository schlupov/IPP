<?php

require_once("./instructions/checkInstruction.php");

class PUSHFRAME {

    public function __construct($line) {
        $this->line = $line;
    }

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