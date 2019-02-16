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
            foreach ($withoutAt as $var) {
                if (is_numeric($var)) {
                    return ($withoutAt[0] == "int") && $var;
                }
                elseif (($var == "true") || ($var == "false")) {
                    return ($withoutAt[0] == "bool") && $var;
                }
                elseif ($var == "nil") {
                    return ($withoutAt[0] == "nil") && $var;
                }
                elseif ($var == "string") {
                    $this->checkString($withoutAt[1]);
                    return $var;
                }
            }
        }
        $variable = $this->checkVariable($arg, $withoutAt, $flag);
        return $variable;
    }

    public function checkVariable($arg, $withoutAt, $flag) {
        $identifier = strpos($arg, "@")!==false ? substr($arg, strpos($arg, "@")+1) : "error";
        if ((preg_match("/^([a-zA-Z]|-|[_$&%*])([a-zA-Z]|-|[_$&%*]|[0-9]+)*$/",$identifier)) && ($identifier != "error")){
            if ($flag == true) {
                return ($withoutAt[0] == "LF" || $withoutAt[0] == "TF" || $withoutAt[0] == "GF") && $identifier;
            }
        }
        return false;
    }

    public function checkString($var) {
        if (preg_match("/^([a-zA-Z\x{0021}\x{0022}\x{0024}-\x{005B}\x{005D}-\x{FFFF}|(\\\\[0-90-90-9])*$/u", $var)) {
            return true;
        }
        fwrite(STDERR, "Lexikalni nebo syntakticka chyba.\n");
        exit (23);
    }
}