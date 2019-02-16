<?php

require_once("./Scanner.php");

class Parser {

    private $tokenized;
    private $line;

    public function __construct($tokenized, $line) {
        $this -> tokenized = $tokenized;
        $this -> line = $line;
    }

    public function instruction() {
        $keyWords = new SpecialWords();
        $constants = $keyWords->getConstants();

        for($x = 0; $x < count($this->tokenized); $x++) {
            foreach ($constants as $key) {
                if ($this->tokenized[$x] == $key) {
                    //echo $keyword;
                    return $key;
                }
            }
        }
    }



    function __destruct() {
    }
}