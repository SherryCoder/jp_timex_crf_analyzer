#coding: utf-8
import sys
import parameter

TEST_ID = int(sys.argv[1])
VARIDATION_ID = 0
TMPDIR = parameter.LOG_DIR+"%d/" % TEST_ID
#TMPDIR = parameter.TMPDIR

CRF_TEST_FILE = "%s/crf_test-%d-%d.crf" % (TMPDIR, TEST_ID, VARIDATION_ID)
RESULT_FILE = "%s/crf_test-%d-%d.crf.result" % (TMPDIR, TEST_ID, VARIDATION_ID)


# CRF_TEST_FILE から全文を取得
sentence_dct_list = [] # [(documentID, dct), None, None, ..]
all_sentence_list = [] # [str_sentence, ..]
with open(CRF_TEST_FILE) as f:
	dct = None
	sentence = ""
	for line in f:
		if line.startswith("#"):
			documentID, dct = line.strip()[1:].split(":")
		elif line.strip() == "":
			if dct == None:
				sentence_dct_list.append(None)
			else:
				sentence_dct_list.append((documentID, dct))
				dct = None
			all_sentence_list.append(sentence)
			sentence = ""
		else:
			sentence += line.split()[0]

# 不正解の単語表示
# system, ans, documentID, sentenceID
sentence_dct_num = 0
documentID = None
with open(RESULT_FILE) as f:
	sentence = ""
	sentence_num = 0
	cnt = 0
	sys_tmpspan = []
	ans_tmpspan = []
	sys_spanlist = []
	ans_spanlist = []
	sys_TYPE = ""
	ans_TYPE = ""
	for line in f:
		string = line.strip().split("\t")[0]
		sentence += string


		# 改行があったら、そこでprint
		if line.strip() == "":
			while sentence != all_sentence_list[sentence_num]: # 空行の場合CRF_TEST_FILEでは検出できないので、all_sentence_listと見比べる
				sentence_num += 1

			if sentence_dct_list[sentence_num] != None:
				documentID, dct = sentence_dct_list[sentence_num]
				print
				print documentID
			else: documentID = ""
			print sentence, sys_spanlist == ans_spanlist
			print "sys: ", 
			for sys_tmpspan, sys_TYPE in sys_spanlist:
				print unicode(sentence, "utf-8")[sys_tmpspan[0]:sys_tmpspan[1]].encode("utf-8"), sys_TYPE, sys_tmpspan,
			print
			print "ans: ", 
			for ans_tmpspan, ans_TYPE in ans_spanlist:
				print unicode(sentence, "utf-8")[ans_tmpspan[0]:ans_tmpspan[1]].encode("utf-8"), ans_TYPE, ans_tmpspan,
			print

			cnt = 0
			sys_tmpspan = []
			ans_tmpspan = []
			sys_spanlist = []
			ans_spanlist = []
			sys_TYPE = ""
			ans_TYPE = ""
			sentence = ""

			sentence_num += 1
		else:
			# systemのBIOを解釈
			sys = line.strip().split("\t")[-1]

			if (sys == "O" or sys.startswith("B")) and len(sys_tmpspan) > 0:
				sys_tmpspan.append(cnt)
				sys_spanlist.append((sys_tmpspan, sys_TYPE))
				sys_tmpspan = []
			if sys.startswith("B") and len(sys_tmpspan) == 0:
				sys_tmpspan = [cnt]
				sys_TYPE = sys[2:]

			# ansのBIOを解釈
			ans = line.strip().split("\t")[-2]

			if (ans == "O" or ans.startswith("B")) and len(ans_tmpspan) > 0:
				ans_tmpspan.append(cnt)
				ans_spanlist.append((ans_tmpspan, ans_TYPE))
				ans_tmpspan = []
			if ans.startswith("B") and len(ans_tmpspan) == 0:
				ans_tmpspan = [cnt]
				ans_TYPE = ans[2:]

			cnt += 1
print k

# 不正解の文表示
printFlag = 0
result_list = []
with open(RESULT_FILE) as f:
	for line in f:
		if line == "\n": 
			if printFlag and len(result_list) != 0:
				print "".join([x.split("\t")[0] for x in result_list])
				for line in result_list:
					print line
				print
			result_list = []
			printFlag = 0
		else:
			word = line.split("\t")[0]
			ans, sys = line.strip().split("\t")[-2:]
			if ans != sys: printFlag = 1
			result_list.append(line.strip())

