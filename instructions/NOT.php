<?php

require_once("./instructions/checkInstruction.php");

class NOT {

    public function __construct($line) {
        $this->line = $line;
    }

    public function checkLine() {
        $check = new checkInstruction();
        $check->checkNumberOfParameters($this->line, 2);
        $arg1 = $this->line[1];
        $arg2 = $this->line[2];
        $arg3 = " ";
        if (($check->arguments($arg1, true))) {
            if ($check->checkLogicalOperation2($arg2, $arg3, true)) {
                return true;
            }
        }
        return false;
    }

    function __destruct() {
    }
}