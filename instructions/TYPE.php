<?php

require_once("./instructions/checkInstruction.php");

class TYPE {

    public function __construct($line) {
        $this->line = $line;
    }

    public function checkLine() {
        $check = new checkInstruction();
        $check->checkNumberOfParameters($this->line, 2);
        $arg1 = $this->line[1];
        $arg2 = $this->line[2];
        if (strpos($arg2, '@') == true) {
            $withoutAt = explode('@', $arg2);
            if (count($withoutAt) < 2) {
                return false;
            }
        }
        if (($check->arguments($arg1, true)) && ($check->checkConstant($withoutAt))) {
            return true;
        }
        return false;
    }

    function __destruct() {
    }
}