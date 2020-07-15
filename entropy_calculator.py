import math, string, sys, fileinput

#credits: http://pythonfiddle.com/shannon-entropy-calculation/
def range_bytes (): 
	return range(256)


def range_printable(): 
	return (ord(c) for c in string.printable)


def H(data, iterator=range_bytes):
	if not data:
		return 0

	entropy = 0

	for x in iterator():
		p_x = float(data.count(chr(x)))/len(data)

		if p_x > 0:
			entropy += - p_x*math.log(p_x, 2)

	return entropy



def score(string):
	score = H(string, range_printable)
	return score
