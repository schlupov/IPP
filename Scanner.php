<?php

require_once("./IsKeyword.php");
require_once("./Keywords.php");

class Scanner {
    private $stdin;
    private $flag;

    public function __construct($stdin) {
        $this -> stdin = $stdin;
    }

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
                array_push($token["DIGIT"],$word[$i]);
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

function removeComment($line){ //TODO: toto nebude brat # nekde jinde nez na zacatku radku a to je asi zle
    if (strpos($line, "#")!==false) {
        return substr($line, 0, strpos($line, "#"));
    }
    return $line;
}

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