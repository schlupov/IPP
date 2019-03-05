<?php

class checkInstruction {

    public function checkNumberOfParameters($word, $parameterCount){
        if ((count($word)-1)!=$parameterCount) {
            fwrite(STDERR, "Lexikalni nebo syntakticka chyba.\n");
            exit (23);
        }
        return true;
    }

    public function arguments($arg, $flag) {
        if (strpos($arg, '@') == true) {
            $withoutAt = explode('@', $arg);
            if (count($withoutAt) < 2) {
                return false;
            }
            if ($this->checkVariable($arg, $withoutAt, $flag)) {
                return true;
            }
        }
        return false;
    }

    public function checkVariable($arg, $withoutAt, $flag) {
        $identifier = substr($arg, strpos($arg, "@")+1);
        if ($withoutAt[0] == "LF" || $withoutAt[0] == "TF" || $withoutAt[0] == "GF") {
            $this->checkVariableName($identifier);
        }
        if ($flag === true) {
            return ($withoutAt[0] == "LF" || $withoutAt[0] == "TF" || $withoutAt[0] == "GF") && $identifier;
        }
        elseif ($flag === false) {
            if (($withoutAt[0] == "int") && ($identifier == "0")) {return true;}
            if (($this->checkConstant($withoutAt)) || ($withoutAt[0] == "LF" || $withoutAt[0] == "TF" || $withoutAt[0] == "GF")){
                if (($withoutAt[0] == "string") && ($identifier === '')) {return true;}
                return ($withoutAt[0] == "LF" || $withoutAt[0] == "TF" || $withoutAt[0] == "GF"
                        || $withoutAt[0] == "int" || $withoutAt[0] == "string" || $withoutAt[0] == "bool"
                        || $withoutAt[0] == "nil") && $identifier;
            }
        }
        return false;
    }

    public function checkVariableName($identifier) {
        if (!(preg_match("/^([a-zA-Z]|-|[_$&%*!?])([a-zA-Z]|-|[_$&%*!?]|[0-9]+)*$/",$identifier))){
            fwrite(STDERR, "Lexikalni nebo syntakticka chyba.\n");
            exit (23);
        }
    }

    public function checkString($var) {
        // TODO: regex neni uplne dobre pro ty cisla
        if (preg_match("/^([a-zA-Z\x{0021}\x{0022}\x{0024}-\x{002F}\x{003A}-\x{FFFF}]*(\x{005C}[0-9]{3})*)*$/u", $var)) {
            return true;
        }
        fwrite(STDERR, "Lexikalni nebo syntakticka chyba.\n");
        exit (23);
    }

    public function checkLabel($arg) {
        $identifier = strpos($arg, "@") === true ? "error":$arg;
        if ((preg_match("/^([a-zA-Z]|-|[_$&%*!?])([a-zA-Z]|-|[_$&%*!?]|[0-9]+)*$/",$identifier)) && ($identifier != "error")){
            return true;
        }
        return false;
    }

    public function checkConstant ($withoutAt) {
        foreach ($withoutAt as $var) {
            if (is_numeric($var)) {
                return ($withoutAt[0] == "int") && $var;
            } elseif (($var == "true") || ($var == "false")) {
                return ($withoutAt[0] == "bool") && $var;
            } elseif ($var == "nil") {
                return ($withoutAt[1] == "nil") && $var;
            } elseif ($var == "string") {
                $this->checkString($withoutAt[1]);
                return true;
            }
        }
    }
}