<?php

class Tests
{
    private $parserResult;
    private $interpretResult;
    private $expectedReturnCode;
    public $outputHtml;
    private $testName;
    private $exitCode;
    private $diffs;
    private $diff;

    function __construct($parse_only, $int_only){
        $this->parse_only = $parse_only;
        $this->int_only = $int_only;
    }

    public function RunTest($file, $parser, $interpret){
        if ((!$this->parse_only) && (!$this->int_only)){
            $xml = $this->parse_script($file->name, $parser);
            $this->CreateHelpFile($file->name,$xml);
            $this->diff = $this->int_script($file->name, $interpret);
        }
        elseif ($this->parse_only) {
            $this->parse_only($file, $file->name, $parser);
        }
        elseif ($this->int_only) {
            $this->diff = $this->int_only($file->name, $interpret);
        }

        if($this->parserResult == 0) {
            if (($this->interpretResult) || ($this->exitCode == $this->expectedReturnCode))
            {
                $Ok=true;
                $this->outputHtml = BuildOkTestBoxHtml($this->testName);
            }
            else if (!$this->interpretResult)
            {
                $Ok=false;
                $this->outputHtml = BuildErrTestBoxHtml($this->testName, $this->exitCode , $this->expectedReturnCode);
            }
        }
        elseif($this->parserResult == 1) {
            $Ok=true;
            $this->outputHtml = BuildOkTestBoxHtml($this->testName);
        }
        else {
            $this->expectedReturnCode = file_get_contents("$file->name.rc");
            if (strcmp($this->interpretResult, 'OUTDIFF') == 0)
            {
                $Ok=false;
                $this->outputHtml = BuildOutputDiffBoxHtml($this->testName, $this->diff);
            }
            elseif (($this->exitCode != $this->expectedReturnCode) && ($this->diffs)) {
                $Ok = false;
                $this->outputHtml = BuildErrTestParserBoxHtml($this->testName, $this->exitCode, $this->expectedReturnCode, $this->diffs);
            }
            elseif (($this->exitCode != $this->expectedReturnCode) && (!$this->diffs)) {
                $Ok = false;
                $this->outputHtml = BuildErrTestBoxHtml($this->testName, $this->exitCode, $this->expectedReturnCode);
            }
            else {
                $Ok=true;
                $this->outputHtml = BuildOkTestBoxHtml($this->testName);
            }
        }
        return $Ok;
    }

    private function parse_script($path, $parser) {
        $out="";
        exec("php $parser <$path.src 2> /dev/null", $out, $this->parserResult);
        $this->CheckReturnCode($path);
        return $out;
    }

    private function parse_only($file, $path, $parser) {
        exec("php $parser <$path.src 2> /dev/null", $out, $parseReturn);
        $this->CreateHelpFile($file->name, $out);
        $this->testName = preg_replace('/^.*\//','',$path);
        $this->expectedReturnCode = file_get_contents("$file->name.rc");
        if (($parseReturn == 0) && ($this->expectedReturnCode == $parseReturn)){
            exec("java -jar /pub/courses/ipp/jexamxml/jexamxml.jar $path.tmp $path.out diffs.xml  /D /pub/courses/ipp/jexamxml/options", $output, $returnValue);
            if ($returnValue == 0) {
                $this->parserResult = 1;
                $this->exitCode = 0;
            }
            else {
                $this->parserResult = 2;
                $this->exitCode = 1;
            }
        }
        else {
            if ($this->expectedReturnCode == $parseReturn) {
                $this->parserResult = 1;
            }
            else {
                $this->parserResult = 2;
                $this->exitCode = $parseReturn;
            }
        }

        if (file_exists("$path.tmp"))
        {
            unlink("$path.tmp");
        }

        if (file_exists("diffs.xml"))
        {
            $this->diffs = file_get_contents("diffs.xml");
            unlink("diffs.xml");
        }
    }

    private function int_only($path, $interpret) {
        $code = array();
        exec("python3.6 $interpret --source=$path.src < $path.in 2> /dev/null", $code, $this->parserResult);
        $this->CheckReturnCode($path);

        $diff=array();
        if (($this->parserResult == 0) && ($this->expectedReturnCode == $this->parserResult))
        {
            $this->CreateHelpFile($path, $code);
            exec("diff -w $path.out $path.tmp", $diff, $this->parserResult);
            if ($this->parserResult != 0)
            {
                $this->interpretResult = "OUTDIFF";
                $this->parserResult = 2;
            }
        }
        else {
            if ($this->expectedReturnCode == $this->parserResult) {
                $this->parserResult = 1;
            }
            else {
                $this->exitCode = $this->parserResult;
            }
        }

        if (file_exists("$path.tmp"))
        {
            unlink("$path.tmp");
        }

        return $diff;
    }

    function CreateHelpFile($name, $content) {
        if ( 0 == filesize( "$name.out" ) )
        {
            $outputFile = implode("\n",$content);
        }
        else {
            $outputFile = implode("\n", $content);
            $outputFile .= "\n";
        }
        file_put_contents("$name.tmp", $outputFile);
    }


    private function int_script($path, $interpret) {
        $code=array();
        exec("python3.6 $interpret --source=$path.tmp < $path.in 2> /dev/null", $code, $this->parserResult);
        $this->CheckReturnCode($path);

        $diff=array();
        if (($this->parserResult == 0) && ($this->expectedReturnCode == $this->parserResult))
        {
            $this->CreateHelpFile($path, $code);
            exec("diff $path.out $path.tmp", $diff, $this->parserResult);
            if ($this->parserResult != 0)
            {
                $this->interpretResult = "OUTDIFF";
                $this->parserResult = 2;
            }
        }
        else {
            if ($this->expectedReturnCode == $this->parserResult) {
                $this->parserResult = 1;
            }
            else {
                $this->exitCode = $this->parserResult;
            }
        }

        if (file_exists("$path.tmp"))
        {
            unlink("$path.tmp");
        }

        return $diff;
    }

    private function CheckReturnCode($path) {
        $this->expectedReturnCode = file_get_contents("$path.rc");
        $this->interpretResult = $this->expectedReturnCode == $this->parserResult;
        $this->testName = preg_replace('/^.*\//','',$path);
    }
}

function BuildOkTestBoxHtml($name) {
    return "<div class=\"box ok\"><td>$name</td></div>";
}

function BuildErrTestBoxHtml($name, $returned, $expected) {
    return "<div class=\"box err\"><td>$name</td><br>Ocekavany navratovy kod:  $expected <br> Navraceny kod: $returned <br> </div>";
}

function BuildErrTestParserBoxHtml($name, $returned, $expected, $diffs) {
    return "<div class=\"box err\"><td>$name</td><br>Ocekavany navratovy kod:  $expected <br> Navraceny kod: $returned <br> Rozdil v xml:  $diffs<br></div>";
}

function BuildOutputDiffBoxHtml($name, $message) {
    $message = implode("|",$message);
    return "<div class=\"box err\"><td>$name<br></td> Diff: $message</div>";
}

function GenerateHead() {
    return "<html><head><meta charset=\"UTF-8\"><style>
        .ok {background-color:#9aff9a;}
        .err {background-color:#fb6b6b;}
        .box{
        border-bottom: 1px solid black;
        padding: 15px;
        text-align: left;
        font-size: 15px;
        }
        </style><title>Tests</title></head>";
}

function BuildResult($total, $countOfOK,$totalCount,$detailsHTML) {
    $headHtml = GenerateHead();
    return "<!DOCTYPE html><html>
        $headHtml
        <body><h1> IPP projekt vysledky testu</h1>
        <h2>Celkem testu: $total </h2>
        <h2>Dobre: $countOfOK Spatne: $totalCount</h2>
        <h3>Spustene testy</h3>
        $detailsHTML
        </body>
        </html>";
}

?>