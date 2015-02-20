#coding: utf-8

import sys
sys.path.append("/home/sakaguchi/tsubaki_research/crf_timex/scripts")
import knpfile
import sentence
import apply_rule
import crf_recognize

TESTFILE = "test.knp"
K = knpfile.KNPFile(FILE=TESTFILE)
AR = apply_rule.ApplyRule(True)
for sentence_list, raw_sentence in zip(K.all_sentence_list, K.raw_sentence_list):
	S = sentence.Sentence(sentence_list)
	AR.ApplystrRule(S.unitxt, S.retxt)
