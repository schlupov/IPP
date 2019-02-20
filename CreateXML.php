<?php


class CreateXML {

    public function __construct($forXML) {
        $this -> forXML = $forXML;
    }

    public function prepareXML () {
        $domTree=new DOMDocument('1.0', 'UTF-8');
        $domTree->formatOutput = true;

        $root = $domTree->createElement("program");
        $root->setAttribute("language", "IPPcode19");

        $counter = 0;
        for($i = 1; $i < count($this -> forXML); $i++) {
            foreach ($this -> forXML[$i] as $c => $z) {
                if ($c == "KEYWORD") {
                    $callCounter = 0;
                    $counter++;
                    $instruction = $this -> forXML[$i][$c][0];
                    $instructionNode = $domTree->createElement("instruction");
                    $instructionNode->setAttribute("order", $counter);
                }
                $instructionNode->setAttribute("opcode", $instruction);
                if (($c != "KEYWORD") && ($c == "DIGIT" || $c == "STRING" || $c == "true" ||
                    $c == "false" || $c == "nil")){
                    $literal = $this -> forXML[$i][$c][0];
                    $callCounter++;
                    $flag = true;
                    $instructionNode->appendChild($this->PrepareArgument($flag, $literal, $domTree, $this -> forXML[$i], $callCounter));
                }
                if ($this -> forXML[$i][$c][0] == "READ") {
                    foreach ($this -> forXML[$i+2] as $p => $g) {
                        $literal = $this->forXML[$i+2][$p][0];
                    }
                    $callCounter++;
                    $flag = false;
                    $instructionNode->appendChild($this->PrepareArgument($flag, $literal, $domTree, $this -> forXML[$i], $callCounter));
                }
                $root->appendChild($instructionNode);

                $domTree->appendChild($root);

                //return $domTree;
            }
        }
        fwrite(STDOUT, $domTree->saveXML());
    }

    private function PrepareArgument ($flag, $literal, $domTree, $type, $callCounter) {
        if ($flag) {
            foreach ($type as $c => $z) {
                switch ($c) {
                    case "int":
                        $atr = "int";
                        break;
                    case "string":
                        $atr = "string";
                        break;
                    case "nil":
                        $atr = "nil";
                        break;
                    case "true":
                    case "false":
                        $atr = "bool";
                        break;
                    case "GF":
                        $atr = "var";
                        $literal = "GF" . "@" . $literal;
                        break;
                    case "TF":
                        $atr = "var";
                        $literal = "TF" . "@" . $literal;
                        break;
                    case "LF":
                        $atr = "var";
                        $literal = "LF" . "@" . $literal;
                        break;
                    default:
                        $atr = "label";
                        break;
                }
            }
        }
        else {
            $atr = "type";
        }
        if ($callCounter == 1) {
            $node = $domTree->createElement("arg1");
        }
        elseif ($callCounter == 2) {
            $node = $domTree->createElement("arg2");
        }
        else {
            $node = $domTree->createElement("arg3");
        }
        $node->setAttribute("type", $atr);
        $node->textContent = $literal;
        return $node;
    }

    function __destruct() {
    }
}