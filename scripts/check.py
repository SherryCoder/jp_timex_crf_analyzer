#coding: utf-8
import pickle
import sys
sys.path.append("/home/sakaguchi/tsubaki_research/time_expression/scripts/")
import parameter

EVAL_ANS_DIR = parameter.EVAL_ANS_DIR
pic_test_filelist = "../normalize/svmdata/1.knpfiles"

with open(pic_test_filelist) as f:
	test_filelist = pickle.load(f)

ans_cnt = 0
for testfile in test_filelist:
	with open("%s/%s.ans" % (EVAL_ANS_DIR, testfile[:-8])) as f:
		for line in f.readlines():
			ans_cnt += 1
print ans_cnt
