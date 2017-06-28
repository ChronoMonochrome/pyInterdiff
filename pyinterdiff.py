#!/usr/bin/python

import fileinput, sys
import re

from collections import OrderedDict
from fraction_custom import NonreducedFraction
from StringIO import StringIO
from unidiff import PatchSet

DEBUG_VERBOSE = 0

def _parseDiff(s_diff_file):
	fileStartRegex = "diff --git a/.* b/.*"
	fileChunks = lambda x: re.split("(%s)" % fileStartRegex, x)[1:]

	s_diff = open(s_diff_file, "rb").read()
	i_chunks = iter(fileChunks(s_diff))

	res = OrderedDict()

	for chunk in i_chunks:
		assert(re.match(fileStartRegex, chunk))
		fileName = chunk.split(" ")[2][2:]
		fileContent = next(i_chunks)
		res[fileName] = fileContent

	return res
"""
def _parseDiff(s_diff_file):
	res = OrderedDict()

	fileStartRegex = "diff --git a/.* b/.*"
	fileChunks = lambda x: re.split("(%s)" % fileStartRegex, x)[1:]

	s_diff = open(s_diff_file, "rb").read()
	i_chunks = iter(fileChunks(s_diff))

	chunk = i_chunks.next()
	assert(re.match(fileStartRegex, chunk))
	fileName = chunk.split(" ")[2][2:]
	fileContent = i_chunks.next()

	for chunk in i_chunks:
		res[fileName] = fileContent

		assert(re.match(fileStartRegex, chunk))
		fileName = chunk.split(" ")[2][2:]
		fileContent = next(i_chunks)

	return res"""


def _parseFile(s_file):
	hunkStartRegex = r"@@\s-[0-9]+,[0-9]+\s\+[0-9]+,[0-9]+\s@@"
	chunks = re.split("(%s)" % hunkStartRegex, s_file)[1:]
	i_chunks = iter(chunks)
	res = OrderedDict()

	for chunk in i_chunks:
		assert(re.match(hunkStartRegex, chunk))
		hunkId = chunk
		hunkContent = next(i_chunks)
		res[hunkId] = hunkContent

	return res

def _parseHunk(s_hunk):
	return [i.group() for i in re.finditer(r"(\+.*)|(\-.*)", s_hunk)]

def parseDiff(s_diff_file):
	res = OrderedDict()
	file_tmp = []
	hunk_tmp = []

	patch = _parseDiff(s_diff_file)

	"""for file in patch:
		#print file
		for hunk in file:
			#print hunk_tmp
			hunk_tmp = [i.group() for i in hunkLines(hunk.__str__())]
			file_tmp.append(hunk_tmp)
		res[file.source_file] = file_tmp"""
	for file in patch.items():
		fileName, file = file[0], _parseFile(file[1])
		#file_tmp = []
		#for hunk in file.values():
		#	file_tmp.append(_parseHunk(hunk))
		res[fileName] = [_parseHunk(hunk) for hunk in file.values()]

		#res[file] = file_tmp

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

def countLines(d_diff, s_filename):
	return sum([len(i) for i in d_diff[s_filename]])

def compareDiffs(d_diff1, d_diff2):
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

	openFile = lambda x: StringIO().write(open(x, "rb").read())

	diff1, diff2 = parseDiff(file1), parseDiff(file2)

	print compareDiffs(diff1, diff2)

