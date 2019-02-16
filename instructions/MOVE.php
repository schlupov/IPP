<?php

require_once("./instructions/checkInstruction.php");

class MOVE {

    public function __construct($line, $tokenized) {
        $this->line = $line;
    }

    public function checkLine() {
        $check = new checkInstruction();
        if ($check->checkNumberOfParameters($this->line, 2)) {
            $arg1 = $this->line[1];
            $arg2 = $this->line[2];
            if (($check->arguments($arg1, true)) && ($check->arguments($arg2, false))) {
                return true;
            }
        }
        return false;
    }


    function __destruct() {
    }
}