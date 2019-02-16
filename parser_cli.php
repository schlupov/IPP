<?php

require_once("./Scanner.php");
require_once("./IScanner.php");
require_once("./parser.php");

//***************************************************************************
//$fh = fopen('php://stdin', 'r');
$fh = fopen("test.txt", "r");
readFirstLine($fh);
while ($line = fgets($fh)) {
    $inputInput = array();
    $line = trim(removeComment($line));
    $line = preg_replace('![\s\t]+!', ' ', $line);
    if (strlen($line)==0)
        continue;
    $word = explode(" ", trim($line));
    $token = array();
    foreach ($word as $input) {
        $s = new Scanner($input);
        $token =  $s->parseWords();
        array_push($inputInput, $token);
    }

    $parsed = new Parser($inputInput, $word);
    $parsed->instruction();
}
//***************************************************************************