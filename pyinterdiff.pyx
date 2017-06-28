#!/usr/bin/python

import fileinput, sys
from collections import OrderedDict
from fraction_custom import NonreducedFraction

DEBUG_VERBOSE = 0

cpdef public object parseDiff(l_diff):
	res = OrderedDict()
	file = []
	hunk = []

	i = 0
	for line in l_diff:
		if line.startswith("diff --git"):
			if hunk:
				file.append(hunk)
				hunk = []

			if file:
				res[fileName] = file
				file = []

			fileName = line.split(" ")[2][2:]

			continue

		elif line[:6] in ["--- a/", "+++ b/"]:
			continue

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
		res[fileName] = file

	return res

cpdef public object compareHunks(l_hunk1, l_hunk2):
	if len(l_hunk2) > len(l_hunk1):
		l_hunk1, l_hunk2 = l_hunk2, l_hunk1

	lines_found, lines_total = 0, 0
	for line in l_hunk1:
		if line in l_hunk2:
			lines_found += 1
		lines_total += 1

	return NonreducedFraction(lines_found, lines_total)

cpdef public object compareFiles(l_file1, l_file2):
	res = NonreducedFraction(0, 0)

	for hunk_i in l_file1:
		cmp_res_max = NonreducedFraction(0)

		for hunk_j in l_file2:
			cmp_res_cur = compareHunks(hunk_i, hunk_j)

			if cmp_res_cur == 1:
				cmp_res_max = cmp_res_cur
				break
			elif cmp_res_cur > cmp_res_max:
				cmp_res_max = cmp_res_cur

		if __debug__ == False:
			print "%d/%d" % (cmp_res_max._numerator, cmp_res_max._denominator)

		res |= cmp_res_max

	return res

cpdef public int countLines(d_diff, s_filename):
	return sum([len(i) for i in d_diff[s_filename]])

cpdef public object compareDiffs(d_diff1, d_diff2):
	res = NonreducedFraction(0, 0)

	for s_filename in d_diff1.keys():
		if __debug__ == False:
			print s_filename

		if s_filename in d_diff2.keys():
			cmp_res = compareFiles(d_diff1[s_filename], d_diff2[s_filename])
		else:
			cmp_res = NonreducedFraction(0, countLines(d_diff1, s_filename))

		if __debug__ == False:
			print "total: %d/%d\n" % (cmp_res._numerator, cmp_res._denominator)

		res |= cmp_res
	return res

if __name__ == "__main__":
	#input_lines = fileinput.input(sys.argv[1:])
	file1, file2 = sys.argv[1:3]
	readFile = lambda x: open(x).readlines()
	diff1, diff2 = parseDiff(readFile(file1)), parseDiff(readFile(file2))

	print compareDiffs(diff1, diff2)

