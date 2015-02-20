#coding: utf-8

import sys
FILE = sys.argv[1]

with open(FILE) as f:
	match_list = []
	prec_list = []
	rec_list = []

	for line in f:
		if line.strip().startswith("prec:"):
			prec = line.strip().split("\t")[-1]
			match = line.strip().split("\t")[-2]
			prec_list.append(int(prec))
			match_list.append(int(match))
		elif line.strip().startswith("recall:"):
			rec = line.strip().split("\t")[-1]
			rec_list.append(int(rec))

	prec_ave = 1.0*sum(match_list)/sum(prec_list)
	rec_ave = 1.0*sum(match_list)/sum(rec_list)

	print "micro-f: ", 2*prec_ave*rec_ave/(prec_ave+rec_ave), prec_ave, rec_ave
