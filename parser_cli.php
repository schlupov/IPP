<?php

require_once("./Scanner.php");
require_once("./parser.php");
require_once("./CreateXML.php");

//***************************************************************************
//$fh = fopen('php://stdin', 'r');
$fh = fopen("test.txt", "r");
readFirstLine($fh);
$forXML = array();
$forXML[] = "IPPcode19";
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
    foreach($inputInput  as $key=>$value) {
        $forXML[] = $value;
    }
    $parsed = new Parser($inputInput, $word);
    $parsed->instruction();
}
//print_r($forXML);
$XMLelement = new CreateXML($forXML);
$XMLelement->prepareXML();
//fwrite(STDOUT, $toPrint->saveXML());
//***************************************************************************