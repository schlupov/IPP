<?php

require_once("./Files.php");
require_once("./Tests.php");

function main() {
    $parse_only = false;
    $int_only = false;

    $longopts  = array(
        "directory::",    // Optional value
        "parse-script::",
        "int-script::",
        "parse-only",
        "int-only",
        "recursive",           // No value
        "help"
    );
    $options = getopt("", $longopts);

    if (array_key_exists("help", $options))
    {
        fwrite(STDOUT, "Skript cte XML ze STDIN a provadi testy podle prepinacu:\n");
        fwrite(STDOUT, "--directory\n");
        fwrite(STDOUT, "--parse-script\n");
        fwrite(STDOUT, "--int-script\n");
        fwrite(STDOUT, "--parse-only\n");
        fwrite(STDOUT, "--int-only\n");
        fwrite(STDOUT, "--recursive\n");
        exit(0);
    }

    if (array_key_exists("directory", $options))
        $path = $options["directory"];
    else
        $path = getcwd();

    if (array_key_exists("parse-script", $options))
        $parser = $options["parse-script"];
    else {
        $parser = "parse.php";
    }

    if (array_key_exists("int-script", $options))
        $interpret = $options["int-script"];
    else {
        $interpret = "interpret.py";
    }

    if (array_key_exists("parse-only", $options) && !array_key_exists("int-script", $options)) {
        $parse_only = true;
    }
    elseif (array_key_exists("parse-only", $options) && array_key_exists("int-script", $options)) {
        fwrite(STDERR, "Spatne pouziti parametru.\n");
        exit (10);
    }

    if (array_key_exists("int-only", $options) && !array_key_exists("parse-script", $options)) {
        $int_only = true;
    }
    elseif (array_key_exists("int-only", $options) && array_key_exists("parse-script", $options)) {
        fwrite(STDERR, "Spatne pouziti parametru.\n");
        exit (10);
    }

    if (array_key_exists("recursive", $options)) {
        $searcher = findFilesRecursively($path);
    }
    else {
        $searcher = findFiles($path);
    }

    $successHTML = "";
    $failHTML = "";
    $ok=0;
    $fail=0;

    foreach ($searcher as $file)
    {
        $test=new Tests($parse_only, $int_only);
        $testResult = $test->RunTest($file, $parser, $interpret);

        if ($testResult)
        {
            $successHTML.=$test->outputHtml;
            $ok++;
        }
        else
        {
            $failHTML.=$test->outputHtml;
            $fail++;
        }
    }

    fwrite(STDOUT, BuildResult($ok,$fail,$failHTML.$successHTML));

    exit(0);
}

main();
?>