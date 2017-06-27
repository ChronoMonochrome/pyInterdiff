#!/usr/bin/python

import fileinput, sys
from collections import OrderedDict as odict
from fraction_custom import NonreducedFraction

input_lines = fileinput.input(sys.argv[1:])
DEBUG = 0

def parseDiff(l_diff):
	res = odict()
	file = []
	hunk = []

	i = 0
	for line in l_diff:
		if __debug__ == False:
			buf = ""
			buf += "line %d: " % i
			buf += "isFileStart = %d\n" % (line.startswith("diff --git"))

		if line.startswith("diff --git"):
			if hunk:
				file.append(hunk)
				hunk = []

			if file:
				res[fileName] = file
				file = []

			fileName = line.split(" ")[2][2:]

			if __debug__ == False:
				i += 1
			else:
				continue

		elif line[:6] in ["--- a/", "+++ b/"]:
			continue

		if __debug__ == False:
			buf += "isHunkStart = %d\n" % (line[0] in ["+", "-"])
			print buf

		if line[0] in ["+", "-"]:
			hunk.append(line)
		else:
			if hunk:
				file.append(hunk)
				hunk = []
		i += 1

	if hunk:
		file.append(hunk)

	if file:
		#print fileName
		res[fileName] = file

	return res

def compareHunks(l_hunk1, l_hunk2):
	if len(l_hunk2) > len(l_hunk1):
		l_hunk1, l_hunk2 = l_hunk2, l_hunk1

	lines_found, lines_total = 0, 0
	for line in l_hunk1:
		if line in l_hunk2:
			lines_found += 1
		lines_total += 1

	return NonreducedFraction(lines_found, lines_total)
	
def compareFiles(l_file1, l_file2):
	res = NonreducedFraction(0, 0)
		
	for hunk_i in l_file1:
		cmp_res_max = 0

		for hunk_j in l_file2:
			cmp_res_cur = compareHunks(hunk_i, hunk_j)
			
			if cmp_res_cur == 1:
				cmp_res_max = cmp_res_cur
				break
			elif cmp_res_cur > cmp_res_max:
				cmp_res_max = cmp_res_cur
				
		res |= cmp_res_max
	
	return res
	
def compareDiffs(d_diff1, d_diff2):
	res = NonreducedFraction(0, 0)
	
	for s_filename in d_diff1.keys():
		res |= compareFiles(d_diff1[s_filename], d_diff2[s_filename])
		
	return res

if __name__ == "__main__":
	for fileName, file in parseDiff(input_lines).items():
		print "%s: " % fileName
		for hunk in file:
			print "".join(hunk)

#print parseDiff(input_lines)