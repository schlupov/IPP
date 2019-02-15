<?php

require_once("./IsKeyword.php");
require_once("./IScanner.php");
require_once("./Keywords.php");

class Scanner implements IScanner {
    private $stdin;
    private $flag;

    public function __construct($stdin) {
        $this -> stdin = $stdin;
    }

    public function readFirstLine() {
        if(trim($this->stdin)!=".ippcode19") {
            fwrite(STDERR, "chybna nebo chybejici hlavicka ve zdrojovem kodu zapsanem v IPPcode19.\n");
            exit (21);
        }
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

        $keyword = new IsKeyword($word, $token);

        $token = $keyword->getKeywords();

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
                    $token["KEYWORD"][] = $word[$i];
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

    private function parse($word) {
        $withoutAt =array();
        if (strpos($word, '@') == true) {
            $withoutAt = explode('@', $word);
            $this->flag = true;
        }
        else {
            $this->flag = false;
            //muze byt \032obsahuje\032
            /*if ($this->keyWords($word) == false) {
                echo $word;
                fwrite(STDERR, "lexikalni nebo syntakticka chyba zdrojoveho kodu zapsaneho v IPPcode19.\n");
                exit (23);
            }*/
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

// TODO: presunout toto do parseru
//***************************************************************************
//$fh = fopen('php://stdin', 'r');
$fh = fopen("test.txt", "r");
$firstLineToLower = strtolower(fgets($fh));
$firstLine = new Scanner($firstLineToLower);
$firstLine->readFirstLine();
while ($line = fgets($fh)) {
    if (trim($line) == "exit()") {
        exit(0);
    }
    $line = preg_replace('![\s\t]+!', ' ', $line);
    $word = explode(" ", trim($line));
    foreach ($word as $input) {
        $s = new Scanner($input);
        $navrat =  $s->parseWords();
        print_r($navrat);
    }
    if (strlen($line)==0)
        continue;
}
//***************************************************************************
