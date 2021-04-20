<?php

function dumpbc() {
	global $M, $OC, $OA;

	for ($n = 0, $i = 0; $i <= sizeof($M);$i++, $n++) 
	{
		echo "$n $i ";

		if (array_key_exists($M[$i], $OC)) 
		{
			echo $OC[$M[$i]];

			for ($j = 0; $j < $OA[$OC[$M[$i]]]; $j++) 
			{
				print(" " . $M[$i + $j + 1]);

				if ($OC[$M[$i]] == 'OUT')
					if ($M[$i + $j + 1] == 10)
						echo "\t\\n";
					else
						echo "\t" . chr((int)$M[$i + $j + 1]);
			}

			$i = $i + $OA[$OC[$M[$i]]] ;
		} else
			echo "???? " . $M[$i];

		echo "\n";
	}
}