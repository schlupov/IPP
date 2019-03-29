<?php

class Files
{
    function __construct($filename)
    {
        $this->name = strstr($filename, ".src", true);


        if (!file_exists("$this->name.in"))
        {
            $file = fopen("$this->name.in", 'w+');
            fclose($file);
        }

        if (!file_exists("$this->name.out"))
        {
            $file = fopen("$this->name.out", 'w+');
            fclose($file);
        }

        if (!file_exists("$this->name.rc"))
        {
            $file = fopen("$this->name.rc", 'w+');
            fwrite($file, "0");
            fclose($file);
        }
    }
}


function findFiles($directory) {
    foreach (glob("$directory/*.src") as $filename)
    {
        yield new Files($filename);
    }
}

function findFilesRecursively($directory) {
    $iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator("$directory/"));
    foreach($iterator as $filename)
    {
        $path_parts = pathinfo($filename);
        $extension = $path_parts['extension'];
        if ($extension == "src") {
            yield new Files($filename);
        }
    }
}

?>