<?php

require_once("./Scanner.php");

class Parser {

    private $tokenized;
    private $line;
    private $call = false;

    public function __construct($tokenized, $line) {
        $this -> tokenized = $tokenized;
        $this -> line = $line;
        foreach (glob("./instructions/*.php") as $filename) {
            require_once($filename);
        }
    }

    public function instruction() {
        foreach($this->tokenized  as $key=>$value){
            foreach($value as $k => $v){
                if ($k == "KEYWORD") {
                    $keyWord = $value[$k][0];
                    $this->call = true;
                    $this->witchInstruction($keyWord);
                }
            }
        }
        if (($this->call) == false) {
            fwrite(STDERR, "Lexikalni nebo syntakticka chyba.\n");
            exit (23);
        }
    }

    private function witchInstruction($keyWord) {
        $keyWords = new Keywords();
        $constants = $keyWords->getConstants();

        foreach ($constants as $key) {
            if ($keyWord == $key) {
                $instruction = $key;
                $test = new $instruction($this->line);
                if (!$test->checkLine()) {
                    fwrite(STDERR, "Lexikalni nebo syntakticka chyba.\n");
                    exit (23);
                }
            }
        }
    }

    function __destruct() {
    }
}