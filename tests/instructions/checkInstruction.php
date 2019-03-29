<?php

/**
* Třída kontroluje syntax proměnných
*/
class checkInstruction {

    /**
    * Metoda kontroluje počet argumentů
    * Vrací true, pokud ano, jinak ukončuje program s chybou 23
    */
    public function checkNumberOfParameters($word, $parameterCount){
        if ((count($word)-1)!=$parameterCount) {
            fwrite(STDERR, "Lexikalni nebo syntakticka chyba.\n");
            exit (23);
        }
        return true;
    }

    /**
    * Metoda kontroluje počet argumentů
    * Vrací true, pokud je proměnná nebo konstanta validní
    * @param string $arg argumenty instrukce
    * @param string $flag určuje, jestli se má jednat o proměnnou nebo to může být i konstanta
    */
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

    /**
    * Metoda kontroluje proměnné a konstanty
    * Vrací proměnnou nebo konstantu, pokud je vše v pořádku, jinak false
    * @param string $arg argumenty instrukce
    * @param string $flag určuje, jestli se má jednat o proměnnou nebo to může být i konstanta
    * @param string $withoutAt proměnná bez @
    */
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
                //echo ($withoutAt[0] == "int") && $identifier, $identifier;
                return ($withoutAt[0] == "LF" || $withoutAt[0] == "TF" || $withoutAt[0] == "GF"
                        || $withoutAt[0] == "int" || $withoutAt[0] == "string" || $withoutAt[0] == "bool"
                        || $withoutAt[0] == "nil") && $identifier;
            }
        }
        return false;
    }

    /**
    * Metoda kontroluje, jestli jsou splněny požadavky na proměnnou a jestli neobsahuje nepovolené znaky
    * Ukončuje program s chybou 23, pokud proměnná není validní
    * @param string $identifier proměnná ke kontrole
    */
    public function checkVariableName($identifier) {
        if (!(preg_match("/^([a-zA-Z]|-|[_$&%*!?])([a-zA-Z]|-|[_$&%*!?]|[0-9]+)*$/",$identifier))){
            fwrite(STDERR, "Lexikalni nebo syntakticka chyba.\n");
            exit (23);
        }
    }

    /**
    * Metoda kontroluje, jestli jsou splněny požadavky na řetězec a jestli neobsahuje nepovolené znaky
    * Ukončuje program s chybou 23, pokud řetězec není validní
    * @param string $var řetězec ke kontrole
    */
    public function checkString($var) {
        if (preg_match("/^([a-zA-Z\x{0021}\x{0022}\x{0024}-\x{002F}\x{003A}-\x{FFFF}]*(\x{005C}[0-9]{3})*)*$/u", $var)) {
            return true;
        }
        fwrite(STDERR, "Lexikalni nebo syntakticka chyba.\n");
        exit (23);
    }

    /**
    * Metoda kontroluje, jestli jsou splněny požadavky na návěští a jestli neobsahuje nepovolené znaky
    * Ukončuje program s chybou 23, pokud návěští není validní
    * @param string $arg návěští ke kontrole
    */
    public function checkLabel($arg) {
        $identifier = strpos($arg, "@") === true ? "error":$arg;
        if ((preg_match("/^([a-zA-Z]|-|[_$&%*!?])([a-zA-Z]|-|[_$&%*!?]|[0-9]+)*$/",$identifier)) && ($identifier != "error")){
            return true;
        }
        return false;
    }

    /**
    * Metoda kontroluje, jestli jsou splněny požadavky na konstantu a jestli neobsahuje nepovolené znaky
    * Ukončuje program s chybou 23, pokud konstanta není validní
    * @param string $withoutAt konstanta ke kontrole
    */
    public function checkConstant ($withoutAt) {
        foreach ($withoutAt as $var) {
            if ((preg_match("/^[\x2B\x2D]?[0-9]*$/",$var)) && ($withoutAt[0] == "int")) {
                return true;
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
