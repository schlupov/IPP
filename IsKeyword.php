<?php

require_once("./Scanner.php");

class IsKeyword {
    private $word;
    private $token;

    public function __construct($word, $token) {
        $this -> word = $word;
        $this -> token = $token;
    }

    public function getKeywords() {

        foreach ($this->word as $literal) {
            switch ($literal) {
                case "nil";
                    $this -> token["NIL"][] = "nil";
                    break;
                case "string";
                    $this -> token["STRING"][] = "string";
                    break;
                case "bool";
                    $this -> token["BOOL"][] = "bool";
                    break;
                case "int";
                    $this -> token["INT"][] = "int";
                    break;
            }
        }
        return $this -> token;
    }

    function __destruct() {
    }
}


