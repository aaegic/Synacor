#!c:\Users\adrian\scoop\apps\php\current\php.exe
<?php

$FILE = 'challenge.bin';

define("NDREF", 0);
define("RDREF", 1);

$M = array();
$P = 0;

//numbers 32768..32775 instead mean registers 0..7
$R = array(
	32768 => 0, 32769 => 0, 32770 => 0, 32771 => 0,
	32772 => 0, 32773 => 0, 32774 => 0, 32775 => 0);

$S = array();

$OC = array(
	'HALT', 'SET', 'PUSH', 'POP', 'EQ', 'GT', 'JMP', 'JT', 'JF', 'ADD', 'MULT',
	'MOD', 'AND', 'OR', 'NOT', 'RMEM', 'WMEM', 'CALL', 'RET', 'OUT', 'IN',
	'NOOP');

$OA = array(
	'HALT' => 0, 'SET' => 2, 'PUSH' => 1, 'POP' => 1, 'EQ' => 3, 'GT' => 3,
	'JMP' => 1, 'JT' => 2, 'JF' => 2, 'ADD' => 3, 'MULT' => 3, 	'MOD' => 3,
	'AND' => 3, 'OR' => 3, 'NOT' => 2, 'RMEM' => 2, 'WMEM' => 2, 'CALL' => 1,
	'RET' => 0, 'OUT' => 1, 'IN' => 1, 'NOOP' => 0);

include('bcdump.php');

ob_implicit_flush();

function init ($_fn)
{
	global $M;

	$__fh = fopen($_fn, "rb") || exit();

	for (
		$__r = fread($__fh, 2);
		!feof($__fh);
		$__r = fread($__fh, 2)
		)
		array_push($M, unpack("v*", $__r)[1]);

	fclose($__fh);
}

function getopand ($__p, $__flag = RDREF)
{
	global $M, $R, $P;

	$__r = $M[$P + 1 + $__p];

	if ($__flag === NDREF)
		return $__r;
	else
		return dereg($__r);
}

function isreg ($__n)
{
	global $M, $R, $P;

	if (array_key_exists($__n, $R))
		return TRUE;
}

function dereg ($__n)
{
	global $M, $R, $P;

	if (isreg($__n))
		return $R[$__n];
	else
		return $__n;
}

function madd32768 ($__a, $__x, $__y)
{
	global $M, $R, $P;

	$__z = $__x + $__y;

	while ($__z >= 32768)
		$__z -= 32768;

	if (isreg($__a)) {
		$R[$__a] = $__z;
	} else
		$M[$__a] = $__z;
}

function halt ($msg = NULL)
{
	print($msg);
	exit();
}

function dd ($__v = FALSE)
{
	global $M, $R, $P;

	if ($__v)
		print("dd: $__v\n");

	printf("%d: %d; +1 %d, +2 %d, +3 %d\n",
		$P, $M[$P], $M[$P+1], $M[$P+2], $M[$P+3]);

	//exit();
}

init($FILE);
//dumpbc();
//exit();

//for ($__i = 0; $__i < 5; $__i++)
for (;;)
{
	/*
	printf("%d: %d; +1 %d, +2 %d, +3 %d\n",
	$P, $M[$P], $M[$P+1], $M[$P+2], $M[$P+3]);

	if (count($S))
		var_dump($S);

	if (count($R))
		var_dump($R);
	*/
	switch ($M[$P])
	{
		//halt: 0
		//stop execution and terminate the program
		case 0:
			halt("$P: $M[$P] HALT");
			break;

		//set: 1 a b
		//set register <a> to the value of <b>
		case 1:
			//$_opand_0 = $M[$P+1];
			$_opand_0 = getopand(0, NDREF);
			$_opand_1 = getopand(1);

			$R[$_opand_0] = $_opand_1;

			$P = $P + 3;
			break;

		//push: 2 a
		//push <a> onto the stack
		case 2:
			$_opand_0 = getopand(0);

			array_push($S, $_opand_0);

			$P = $P + 2;
			break;

		//pop: 3 a
		//remove the top element from the stack and write it into <a>;
		//empty stack = error
		case 3:
			$_opand_0 = getopand(0, NDREF);

			if (count($S))
				$R[$_opand_0] = array_pop($S);

			$P = $P + 2;
			break;

		//eq: 4 a b c
		//set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
		case 4:
			$_opand_0 = getopand(0, NDREF);
			$_opand_1 = getopand(1);
			$_opand_2 = getopand(2);

			if ($_opand_1 === $_opand_2)
				$R[$_opand_0] = 1;
			else
				$R[$_opand_0] = 0;

			$P = $P + 4;
			break;

		//gt: 5 a b c
		//set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
		case 5:
			$_opand_0 = getopand(0, NDREF);
			$_opand_1 = getopand(1);
			$_opand_2 = getopand(2);

			if ($_opand_1 > $_opand_2)
				$R[$_opand_0] = 1;
			else
				$R[$_opand_0] = 0;

			$P = $P + 4;
			break;

		//jmp: 6 a
		//jump to <a>
		case 6:
			$_opand_0 = getopand(0);

			$P = $_opand_0;
			break;

		//jt: 7 a b
		//if <a> is nonzero, jump to <b>
		case 7:
			$_opand_0 = getopand(0);
			$_opand_1 = getopand(1);

			if ($_opand_0 !== 0)
				$P = $_opand_1;
			else
				$P = $P + 3;
			break;

		//jf: 8 a b
		//if <a> is zero, jump to <b>
		case 8:
			$_opand_0 = getopand(0);
			$_opand_1 = getopand(1);

			if ($_opand_0 === 0)
				$P = $_opand_1;
			else
				$P = $P + 3;
			break;

		//add: 9 a b c
  		//assign into <a> the sum of <b> and <c> (modulo 32768)
		case 9:
			//$_opand_0 = $M[$P+1];
			$_opand_0 = getopand(0, NDREF);
			$_opand_1 = getopand(1);
			$_opand_2 = getopand(2);

			madd32768($_opand_0, $_opand_1, $_opand_2);

			$P = $P + 4;
			break;

		//and: 12 a b c
		//stores into <a> the bitwise and of <b> and <c>
		case 12:
			$_opand_0 = getopand(0, NDREF);
			$_opand_1 = getopand(1);
			$_opand_2 = getopand(2);

			$R[$_opand_0] = $_opand_1 & $_opand_2;

			$P = $P + 4;
			break;

		//or: 13 a b c
		//stores into <a> the bitwise or of <b> and <c>
		case 13:
			$_opand_0 = getopand(0, NDREF);
			$_opand_1 = getopand(1);
			$_opand_2 = getopand(2);

			$R[$_opand_0] = $_opand_1 | $_opand_2;

			$P = $P + 4;
			break;

		//not: 14 a b
		//stores 15-bit bitwise inverse of <b> in <a>
		case 14:
			$_opand_0 = getopand(0, NDREF);
			$_opand_1 = getopand(1);

			$_opand_1 = ~ $_opand_1;
			$R[$_opand_0] = 32767 & $_opand_1;

			$P = $P + 3;
			break;

		//call: 17 a
		//write the address of the next instruction to the stack and jump to <a>
		case 17:
			$_opand_0 = getopand(0);

			array_push($S, $P + 2);
			$P = $_opand_0;

			break;

		//0x13 // out: 19 a
		//write the character represented by ascii code <a> to the terminal
		case 19:
			$_opand_0 = getopand(0);

			print(chr($_opand_0));

			$P = $P + 2;
			break;

		//0x15 // noop: 21
		//no operation
		case 21:
			$P = $P + 1;
			break;

		default:
			halt(sprintf("%d: %d; +1 %d, +2 %d, +3 %d",
				$P, $M[$P], $M[$P+1], $M[$P+2], $M[$P+3]));
			break;
	}
}

halt();
