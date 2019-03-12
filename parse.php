<?php

require_once("./Scanner.php");
require_once("./parser.php");
require_once("./CreateXML.php");

$fh = fopen('php://stdin', 'r');

/**
* Funkce čte jediny argument --help programu parse.php a tiskne na stdout napovedu k tomuto programu.
* V případě, kdy je zadán špatný argument nebo více argumentů je program ukončen s chybou 10.
* @param string $argv argument programu parse.php
*/
function readArgv($argv)
{
    if (count($argv) < 3 and $argv[1] == "--help") {
        fwrite(STDOUT, "Skript nacita ze STDIN jazyk IPPcode19 a provadi lexikalni a syntaktickou analyzu.\n");
        exit(0);
    } else {
        fwrite(STDERR, "Spatne pouziti parametru.\n");
        exit (10);
    }
}

/**
* Funkce načítá postupně řádky ze standardního vstupu a předává je dalším funkcím a metodám, které se starají
* o odstranění komentářů, mezer, vytváření tokenů, syntaktickou analýzu a vytváření konečné XML reprezentace
* @param string $fh řádek ze stdin
* @param string $argv argument programu parse.php
*/
function main($fh, $argv)
{
    if (count($argv) > 1) {
        readArgv($argv);
    }
    readFirstLine($fh);
    $forXML = array();
    $forXML[] = "IPPcode19";
    while ($line = fgets($fh)) {
        $inputInput = array();
        $line = trim(removeComment($line));
        $line = preg_replace('![\s\t]+!', ' ', $line);
        if (strlen($line) == 0)
            continue;
        $word = explode(" ", trim($line));
        $token = array();
        foreach ($word as $input) {
            $s = new Scanner($input);
            $token = $s->parseWords();
            array_push($inputInput, $token);
        }
        foreach ($inputInput as $key => $value) {
            $forXML[] = $value;
        }
        $parsed = new Parser($inputInput, $word);
        $parsed->instruction();
    }
    $XMLelement = new CreateXML($forXML);
    $XMLelement->prepareXML();
}

main($fh, $argv);
