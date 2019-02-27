<?php


class CreateXML {

    public function __construct($forXML) {
        $this -> forXML = $forXML;
    }

    public function prepareXML () {
        $domTree=new DOMDocument('1.0', 'UTF-8');
        $domTree->formatOutput = true;

        $root = $domTree->createElement("program");
        $root->setAttribute("language", $this->forXML[0]);
        if (count($this->forXML) == 1) {
            $domTree->appendChild($root);
            fwrite(STDOUT, $domTree->saveXML());
            exit(0);
        }

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
                if (($this -> forXML[$i][$c][0] == "CALL") || ($this -> forXML[$i][$c][0] == "JUMP") ||
                    ($this -> forXML[$i][$c][0] == "JUMPIFEQ") || ($this -> forXML[$i][$c][0] == "JUMPIFNEQ")
                    || ($this -> forXML[$i][$c][0] == "LABEL")) {
                    foreach ($this -> forXML[$i+1] as $p => $g) {
                        $literal = $this->forXML[$i+1][$p][0];
                    }
                    $callCounter++;
                    $flag = 0;
                    $instructionNode->appendChild($this->PrepareArgument($flag, $literal, $domTree, $this -> forXML[$i], $callCounter));
                }
                if (($c != "KEYWORD") && ($c == "DIGIT" || $c == "STRING" || $c == "true" ||
                    $c == "false" || $c == "nil")){
                    $literal = $this -> forXML[$i][$c][0];
                    $flag = 1;
                    $callCounter++;
                    $node = $this->PrepareArgument($flag, $literal, $domTree, $this->forXML[$i], $callCounter);
                    if ($node != null) {
                        $instructionNode->appendChild($node);
                    }
                    else {
                        $callCounter--;
                    }
                }
                if ($this -> forXML[$i][$c][0] == "READ") {
                    foreach ($this -> forXML[$i+2] as $p => $g) {
                        $literal = $this->forXML[$i+2][$p][0];
                    }
                    $callCounter++;
                    $flag = 2;
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
        if ($flag == 1) {
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
                        $atr = "";
                        break;
                }
            }
        }
        elseif ($flag == 2) {
            $atr = "type";
        }
        else {
            $atr = "label";
        }
        if ($atr != "") {
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
    }

    function __destruct() {
    }
}