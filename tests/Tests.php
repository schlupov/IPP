<?php

class Tests
{
    private $parserResult;
    private $interpretResult;
    private $expectedReturnCode;
    public $outputHtml;
    private $testName;
    private $exitCode;

    function __construct($parse_only, $int_only){
        $this->parse_only = $parse_only;
        $this->int_only = $int_only;
    }

    public function RunTest($file, $parser, $interpret){
        if ((!$this->parse_only) && (!$this->int_only)){
            $xml = $this->parse_script($file->name, $parser);
            $this->CreateHelpFile($file->name,$xml);
            $diff = $this->int_script($file->name, $interpret);
        }
        elseif ($this->parse_only) {
            $this->parse_only($file, $file->name, $parser);
        }
        elseif ($this->int_only) {
            $diff = $this->int_only($file->name, $interpret);
        }

        if($this->parserResult == 0) {
            if (strcmp($this->interpretResult, 'OUTDIFF') == 0)
            {
                $Ok=false;
                $this->outputHtml = BuildOutputDiffBoxHtml($this->testName, $diff);
            }
            else if ($this->interpretResult)
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
            if ($this->exitCode != $this->expectedReturnCode) {
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
        if ($parseReturn == 0) {
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
            $this->expectedReturnCode = file_get_contents("$file->name.rc");
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
    }

    private function int_only($path, $interpret) {
        exec("python3.6 $interpret --source=$path.src < $path.in 2> /dev/null", $code, $this->parserResult);
        $this->CheckReturnCode($path);

        $diff=array();
        if ($this->parserResult == 0)
        {
            $this->CreateHelpFile($path, $code);
            exec("diff $path.out $path.tmp", $diff, $this->parserResult);
            if ($this->parserResult != 0)
            {
                $this->interpretResult = "OUTDIFF";
            }
        }
        else {
            $this->exitCode = $this->parserResult;
        }

        if (file_exists("$path.tmp"))
        {
            unlink("$path.tmp");
        }

        return $diff;
    }

    function CreateHelpFile($name, $content) {
        $outputFile = implode("\n",$content);
        $outputFile .= "\n";
        file_put_contents("$name.tmp", $outputFile);
    }


    private function int_script($path, $interpret) {
        $code=array();
        exec("python3.6 $interpret --source=$path.tmp --input=read_test < $path.in 2> /dev/null", $code, $this->parserResult);
        $this->CheckReturnCode($path);

        $diff=array();
        if ($this->parserResult == 0)
        {
            $inputFile = implode("\n",$code);
            $inputFile .= "\n";
            file_put_contents("$path.tmp", $inputFile);
            exec("diff $path.out $path.tmp", $diff, $this->parserResult);
            if ($this->parserResult != 0)
            {
                $this->interpretResult = "OUTDIFF";
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

function BuildOutputDiffBoxHtml($name, $message) {
    $message = implode("|",$message);
    return "<div class=\"box err\"><td>$name</td> $message</div>";
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

function BuildResult($countOfOK,$totalCount,$detailsHTML) {
    $headHtml = GenerateHead();
    return "<!DOCTYPE html><html>
        $headHtml
        <body><h1> IPP projekt vysledky testu</h1>
        <h2> OK: $countOfOK FAIL: $totalCount</h2>
        <h3>Testy</h3>
        $detailsHTML
        </body>
        </html>";
}

?>