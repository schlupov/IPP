<?php
/**
 * Created by PhpStorm.
 * User: schlupov
 * Date: 2/11/19
 * Time: 7:02 PM
 */
require_once("./ScannerState.php");
require_once("./IScanner.php");

class Scanner implements IScanner {
    private $stdin;

    public function __construct($stdin) {
        $this -> stdin = $stdin;
    }

    public function readFirstLine() {
        if(trim($this->stdin)!=".ippcode19") {
            fwrite(STDERR, "chybna nebo chybejici hlavicka ve zdrojovem kodu zapsanem v IPPcode19.\n");
            exit (21);
        }
    }

    public function readLines() {
        $word = explode(" ", $this->stdin);
        $token = array();
        $withoutAt =array();
        foreach ($word as $c) {
            if (strpos($c, '@') == true) {
                $withoutAt = explode('@', $c);
            }
        }
        for($i = 0; $i < count($withoutAt); ++$i) {
            array_push($word, $withoutAt[$i]);
            if (is_string($withoutAt[$i]) == true) {
                $token["STRING"] = $withoutAt[$i];
            }
        }

        foreach ($word as $literal) {
            switch ($literal) {
                case Enum::GF:
                    $token["GF"] = $literal;
                    break;
                case Enum::MOVE:
                    $token["MOVE"] = $literal;
                    break;
                case Enum::DIGIT:
                    $token["DIGIT"] = $literal;
                    break;
                case Enum::STRING:
                    $token["STRING"] = $literal;
                    break;
            }
        }
        print_r($token);
        return $token;
    }


    function __destruct() {
    }
}

// TODO: presunout toto do parseru
//***************************************************************************
$fh = fopen('php://stdin', 'r');
$firstLineToLower = strtolower(fgets($fh));
$firstLine = new Scanner($firstLineToLower);
$firstLine->readFirstLine();
while ($line = fgets($fh)) {
    if (trim($line) == "exit()") {
        exit(0);
    }
    $line = preg_replace('![\s\t]+!', ' ', $line);
    $s = new Scanner(trim($line));
    $navrat =  $s->readLines();
    if (strlen($line)==0)
        continue;
}
//***************************************************************************
