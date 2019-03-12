<?php

require_once("./Keywords.php");

/**
* Třída Scanner získává řádky od parse.php a převádí jednotlivé řádky na tokeny pomocí asociativního pole.
* Typ tokenu může být číslo, řetězec, nil, bool, klíčové slovo nebo speciální slovo jako je některý z rámců (GF, LF, TF),
* end, while. To o jaký typ se jedná zařizují metody checkNumbers, keyWords a specialWords.
* @param string $stdin řádek ze standardního vstupu
*/
class Scanner {
    private $stdin;
    private $flag;

    public function __construct($stdin) {
        $this -> stdin = $stdin;
    }

    /**
    * Funkce parsuje řádky ze standardniho vstupu a vytvari tokeny pomoc asociativniho podle
    * Vraci token což je asociativní pole, ve kterem je klíč typ tokenu a hodnota je hodnota daného tokenu
    */
    public function parseWords() {
        $token = array();
        $word = array();
        $withoutAt = $this->parse($this->stdin);
        if ($this->flag == true) {
            array_splice($word, 1, 1);
            foreach ($withoutAt as $c) {
                array_push($word, $c);
            }
        }
        else {
            array_push($word, $this->stdin);
        }

        $token["DIGIT"] = array();
        $token["STRING"] = array();
        for($i = 0; $i < count($word); $i++) {
            if (is_numeric($word[$i]) == true) {
                if (preg_match("/^[+-]?[0-9]*$/u", $word[$i])) {
                    array_push($token["DIGIT"], $word[$i]);
                }
                else {
                    fwrite(STDERR, "Lexikalni nebo syntakticka chyba.\n");
                    exit (23);
                }
            }
            elseif (is_string($word[$i]) == true){
                if ($this->keyWords(strtoupper($word[$i]))) {
                    $token["KEYWORD"][] = strtoupper($word[$i]);
                    continue;
                }
                elseif ($this->specialWords($word[$i])) {
                    $token[$word[$i]][] = $word[$i];
                    continue;
                }
                elseif ($this->checkNumbers($word[$i])) {
                    $withoutBackSlash = $this->checkNumbers($word[$i]);
                    $token["STRING"][] = $withoutBackSlash;
                    continue;
                }
                array_push($token["STRING"],$word[$i]);
            }
        }

        foreach ($token as $key => $value) {
            if (empty($value)) {
                unset($token[$key]);
            }
        }
        return $token;
    }

    /**
    * Metoda kontroluje, jestli se jedna o číslo. Pokud ano, vrací číslo, pokud ne, vraci false.
    * Metoda navíc kontroluje, jestli se na řádku nevyskytuje zpětné lomítko bez čísla, což vede na chybu 23.
    * @param string $oneWord možné číslo ze stdin ke kontrole
    */
    private function checkNumbers($oneWord) {
        $digit = true;
        $backslash = false;
        preg_match_all('!\d+!', $oneWord, $matches);
        foreach ($matches as $key) {
            if (empty($key)) {
                unset($matches);
                $digit = false;
            }
        }
        if (strpos($oneWord, '\\') !== FALSE) {
            $backslash = true;
        }
        if (($digit == false) and ($backslash == false) == false) {
            fwrite(STDERR, "Lexikalni nebo syntakticka chyba.\n");
            exit (23);
        }
        elseif (($digit == true) and ($backslash == false) == false) {
            return $oneWord;
        }
    }

    /**
    * Metoda parsuje jednotlivé proměnné ze stdin a v případě, že obsahuje @ rozdělí ji na dvě části, jinak
    * se pouze nastaví třídní proměnná $flag na false, aby scanner věděl, že proměnná neobsahuje @ a není nutné ji
    * tedy rozdělit na 2 části
    * @param string $word možná proměnná ke kontrole
    */
    private function parse($word) {
        $withoutAt =array();
        if (strpos($word, '@') == true) {
            $withoutAt = explode('@', $word);
            $this->flag = true;
        }
        else {
            $this->flag = false;
        }
        return $withoutAt;
    }

    /**
    * Metoda kontroluje, jestli proměnná na stdin je operační kod.
    * Pokud ano, vrací operační kod, jinak false.
    * @param string $oneWord možný operační kod ke kontrole
    */
    private function keyWords($oneWord) {
        $keyWords = new Keywords();
        $constants = $keyWords->getConstants();
        foreach ($constants as $key) {
            if ($oneWord == $key) {
                return $key;
            }
        }
        return false;
    }

    /**
    * Metoda kontroluje, jestli proměnná na stdin je konstanta z třídy SpecialWords
    * Pokud ano, vrací tuto konstantu, jinak false.
    * @param string $oneWord možné speciální slovo, které tato implementace scanneru rozlišuje
    */
    private function specialWords($oneWord) {
        $keyWords = new SpecialWords();
        $constants = $keyWords->getConstants();
        foreach ($constants as $key) {
            if ($oneWord == $key) {
                return $key;
            }
        }
        return false;
    }

    function __destruct() {
    }
}

/**
* Funkce odstraňuje komentáře
* Vrací řádek ze stdin bez komentáře
* @param string $line řádek ze stdin
*/
function removeComment($line){
    if (strpos($line, "#")!==false) {
        return substr($line, 0, strpos($line, "#"));
    }
    return $line;
}

/**
* Metoda kontroluje, jestli první řádek obsahuje povinnou hlavičku .IPPcode19
* Pokud ne, ukončuje program s chybou 21
* @param string $line řádek ze stdin
*/
function readFirstLine($line){
    $firstLine=strtolower(fgets($line));
    if (strpos($firstLine, "#")!==false) {
        $firstLine = substr($firstLine, 0, strpos($firstLine, "#"));
    }
    if(trim($firstLine)!=".ippcode19") {
        fwrite(STDERR, "chybna nebo chybejici hlavicka ve zdrojovem kodu zapsanem v IPPcode19.\n");
        exit (21);
    }
}
