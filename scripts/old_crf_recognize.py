#coding: utf-8

import os
import pickle
import commands
import sys
import random
from collections import defaultdict
from collections import OrderedDict
import parameter
import sentence
import word
import apply_rule
sys.path.append("/home/sakaguchi/mytools/")
from  mypool import MyPool

# CRFのラベルを文字ベースにするか単語ベースにするか
STRING_BASE = 1
WORD_BASE = 0

TIME_DIC = parameter.HOME+"/rule/ContentW.time.dic"
TMPDIR = parameter.TMPDIR
print "TMPDIR: ", TMPDIR

# feature
FEATURE_LIST = [("STRING", 1), ("HINSI", 0), ("HINSI_LABEL", 1), ("NUM", 1), ("PATTERN", 1)]
FEATURE_DICT = OrderedDict()
FEATURE_NUM = 0
for feature,flag in FEATURE_LIST:
	FEATURE_DICT[feature] = flag
	if flag: FEATURE_NUM += 1

class CRFRecognition:
	def __init__(self, TRAIN_ID, TEST_ID, TEMPLATE_ID, CROSS_VARIDATION_ID=0):
		# 利用するデータのID
		# 全てtmpdirの下にある必要あり
		self.TRAIN_ID = TRAIN_ID
		self.TEST_ID = TEST_ID # modelのIDにも使う
		self.TEMPLATE_ID = TEMPLATE_ID
		self.CROSS_VARIDATION_ID = CROSS_VARIDATION_ID
		self.AR = apply_rule.ApplyRule()

		self.dateNameList = [u"CENTURY", u"GYEARX", u"YEARX", u"GYEAR", u"GFYEAR", u"FYEAR", u"YEAR", u"SEASON", u"MONTH", u"JUN", u"WEEK", u"DAY", u"YOUBI", u"PHRASE", u"TIME", u"HOUR", u"MINUTE", u"SECOND", u"VAGUE", u"MOD"]

	def train(self):
		os.system("nice -n 15 crf_learn -a CRF-L2 %s/template-%d %s/crf_train.data-%d-%d %s/model-%d-%d" % (TMPDIR, self.TEMPLATE_ID, TMPDIR, self.TRAIN_ID, self.CROSS_VARIDATION_ID, TMPDIR, self.TEST_ID, self.CROSS_VARIDATION_ID))


	def test(self, DIR=None):
		if DIR == None: DIR = TMPDIR
		log = commands.getoutput("nice -n 15 crf_test -m %s/model-%d-%d %s/crf_test.data-%d-%d" % (DIR, self.TEST_ID, self.CROSS_VARIDATION_ID, DIR, self.TEST_ID, self.CROSS_VARIDATION_ID))
		with open("%s/log%d-%d"%(DIR, self.TEST_ID, self.CROSS_VARIDATION_ID), 'w') as f:
			f.write(log)
		return log


	def make_crf_data(self, TRAIN_TEST_FLAG, knp_filename_list, dct_list, ans_dict, DIR=None):
		# input:
		# 	TRAIN_TEST_FLAG: "TRAIN" or "TEST"
		# output:
		# 	TMPDIR+crf_filename+".knp"
		#	TMPDIR+crf_filename
		#		-> #documentID:DCT
		#		-> sentence

		if DIR == None: DIR = TMPDIR
		crf_filename = ""
		if TRAIN_TEST_FLAG == "TRAIN": 
			crf_filename = "crf_train.data-%d-%d" % (self.TRAIN_ID, self.CROSS_VARIDATION_ID)
		elif TRAIN_TEST_FLAG == "TEST": 
			crf_filename = "crf_test.data-%d-%d" % (self.TEST_ID, self.CROSS_VARIDATION_ID)

		if len(knp_filename_list) != len(dct_list):
			print >> sys.stderr, "ERROR! len(knp_filename_list) != len(dct_list)"
			sys.exit()

		# make template
		if TRAIN_TEST_FLAG == "TRAIN":
			self.make_template(FEATURE_NUM, DIR)


		txt_dict = {} # {(filename, line_cnt): txt}
		with open(DIR+crf_filename+".knp", "w") as f:
			f.write("")
		with open(DIR+crf_filename, "w") as f: # 初期化
			f.write("")
		for knpfilename, dct in zip(knp_filename_list, dct_list):
			filename = knpfilename.split("/")[-1].split(".")[0]
			all_sentence_list = []
			# knpの書き込み
			with open(knpfilename) as f, open(DIR+crf_filename+".knp", 'a') as g:
				sentence_list = []
				for line in f:
					sentence_list.append(line.strip())
					g.write(line)
					if line.startswith("EOS"):
						all_sentence_list.append(sentence_list)
						sentence_list = []
			# testデータのみfilenameとDCTの書き込み
			if TRAIN_TEST_FLAG == "TEST":
				with open(DIR+crf_filename, "a") as f: # filename
					f.write("#%s:%s\n" % (filename, dct))
				print
				print "#%s:%s" % (filename, dct)

			tmp_txt_list = []
			for line_cnt, sentence_list in enumerate(all_sentence_list):
				txt = ""
				for line in sentence_list:
					if not (line.startswith("#") or line.startswith("*") or line.startswith("+") or line.startswith("EOS")):
						txt += line.split()[0]
				txt_dict[(filename, str(line_cnt))] = txt
						
				print filename, line_cnt
				S = sentence.Sentence(sentence_list)
				if ans_dict != {}: # 正解ラベルをつける
					txt = self.crf_feature(TRAIN_TEST_FLAG, S, ans_dict[filename][str(line_cnt)])
				else:
					txt = self.crf_feature(TRAIN_TEST_FLAG, S, [])
				tmp_txt_list.append(txt)
			with open(DIR+crf_filename, "a") as f:
				f.write("\n".join(tmp_txt_list))
				f.write("\n")


	def make_template(self, feature_num, DIR):
		tmp = []
		f_cnt = 0
		for i in range(feature_num):
			tmp.append("U%02d:"%f_cnt+"%x"+"[0,%d]\n"%i)
			f_cnt += 1
			tmp.append("U%02d:"%f_cnt+"%x"+"[1,%d]\n"%i)
			f_cnt += 1
			tmp.append("U%02d:"%f_cnt+"%x"+"[-1,%d]\n"%i)
			f_cnt += 1
			tmp.append("U%02d:"%f_cnt+"%x"+"[2,%d]\n"%i)
			f_cnt += 1
			tmp.append("U%02d:"%f_cnt+"%x"+"[-2,%d]\n"%i)
			f_cnt += 1
			tmp.append("U%02d:"%f_cnt+"%x"+"[-2,%d]/"%i+"%x"+"[-1,%d]\n"%i)
			f_cnt += 1
			tmp.append("U%02d:"%f_cnt+"%x"+"[-1,%d]/"%i+"%x"+"[0,%d]\n"%i)
			f_cnt += 1
			tmp.append("U%02d:"%f_cnt+"%x"+"[0,%d]/"%i+"%x"+"[1,%d]\n"%i)
			f_cnt += 1
			tmp.append("U%02d:"%f_cnt+"%x"+"[1,%d]/"%i+"%x"+"[2,%d]\n"%i)
			f_cnt += 1
			tmp.append("U%02d:"%f_cnt+"%x"+"[-1,%d]/"%i+"%x"+"[0,%d]/"%i+"%x"+"[1,%d]\n"%i)
			f_cnt += 1
		tmp.append("B\n")

		with open(DIR+"template-%d" % self.TEMPLATE_ID, "w") as f:
			f.write("".join(tmp))



	def crf_feature(self, TRAIN_TEST_FLAG, S, ans_tup_list):
		# ans_tup_list (ans, datetype, beginID, endID)

		# Rule
		if FEATURE_DICT["PATTERN"]:
			applied_rule_list = self.AR.ApplystrRule(S.unitxt, S.retxt)

		# Time_dic
		time_dict = {}
		with open(TIME_DIC) as f:
			for line in f.readlines():
				midasi = line.split("見出し語")[1].split(" ")[1]
				time_dict[midasi] = 1

		w_cnt = 0
		ans_index = 0
		txt_list = []
		for W_num, W in enumerate(S.Word_list):
			# num
			num = 0
			if W.num != None: 
#			num = 1
				if W.num <= 10: num = 1
				elif W.num <= 100: num = 2
				elif W.num <= 1000: num = 3
				elif W.num <= 1900: num = 4
				elif W.num <= 2100: num = 5
				else: num = 6

			# time_dic
			timedic = 0
			if time_dict.has_key(W.strword):
				timedic = 1


			if STRING_BASE:
				for w in range(len(W.word)):
					# pattern
					pattern = 0
					if FEATURE_DICT["PATTERN"]:
						for applied_dict in applied_rule_list:
							span = applied_dict["span"]
							if span[0] <= w_cnt < span[1]:
								matched_dict = applied_dict["matched_rule_dict"]
								for tmp_datetypedict in matched_dict[u"datetypelist"]:
									datetype = tmp_datetypedict[u"datetype"]
									pattern = self.dateNameList.index(datetype)+1

					# hinsi_label
					hinsi_label = ""
					if w == 0: hinsi_label = "B-"+W.hinsi
					else: hinsi_label = "I-"+W.hinsi

					# label
					if ans_tup_list != ():
						try: ans, datetype, beginID, endID = ans_tup_list[ans_index]
						except: beginID = endID = None
						label = ""
						if beginID == None: label = "O"
						elif int(beginID) == w_cnt: label = "B-"+datetype
						elif int(beginID) < w_cnt: label = "I-"+datetype
						else: label = "O"
#						print ans_index, w_cnt, w_cnt+1, W.word[w].encode("utf-8"), beginID, endID, len(ans_tup_list), label
						if endID != None and int(endID)+1 == w_cnt+1: ans_index += 1
						w_cnt += 1
					else:
						label == ""

					feature_list = []
					for feature, flag in FEATURE_DICT.items():
						if flag:
							if feature == "STRING": 
								feature_list.append(W.word[w].encode("utf-8"))
							elif feature == "HINSI": 
								feature_list.append(W.hinsi)
							elif feature == "HINSI_LABEL": 
								feature_list.append(hinsi_label)
							elif feature == "NUM":
								feature_list.append(str(num))
							elif feature == "PATTERN":
								feature_list.append(str(pattern))
					feature_list.append(label)
					txt = " ".join(feature_list)+"\n"
					txt_list.append(txt)
			elif WORD_BASE:
				# pattern
				pattern = 0
				if FEATURE_DICT["PATTERN"]:
					for applied_dict in applied_rule_list:
						span = applied_dict["span"]
						if span[0] <= w_cnt <= w_cnt+len(W.word) < span[1]:
							matched_dict = applied_dict["matched_rule_dict"]
							for tmp_datetypedict in matched_dict[u"datetypelist"]:
								datetype = tmp_datetypedict[u"datetype"]
								pattern = self.dateNameList.index(datetype)+1

				# label
				if ans_tup_list != ():
					word_label_list = [] # [(word, label), ..]
					word = W.word
					before_w_cnt = w_cnt
					while 1: # "２0・２１日" で1単語になっている場合などがある -> 分割する
						try: ans, datetype, beginID, endID = ans_tup_list[ans_index]
						except: beginID = endID = None
						nextFlag = 0 # whileループを次も回すか
						label = ""
						if beginID == None: 
							label = "O"
							word_label_list.append((word, label))
							w_cnt += len(word)
						elif w_cnt == int(beginID): # ぴったり単語の初めから始まる(普通)
							label = "B-"+datetype 
							if endID != None and int(endID)+1 < w_cnt+len(word): 
#								print word.encode("utf-8"), len(word), int(endID)+1, w_cnt+len(word)
								word_label_list.append((word[:int(endID)-w_cnt+1], label))
								word = word[int(endID)-w_cnt+1:]
								ans_index += 1
								nextFlag = 1
								w_cnt += len(word[:int(endID)-w_cnt+1])
							elif endID != None and int(endID)+1 == w_cnt+len(word):
								word_label_list.append((word, label))
								ans_index += 1
								w_cnt += len(word)
							else:
								word_label_list.append((word, label))
								w_cnt += len(word)
						elif w_cnt < int(beginID) < w_cnt+len(word): # 単語の途中から正解が始まる
							label = "B-"+datetype
							if int(endID)+1 < w_cnt+len(word): # beginID, endIDがともにword内にある場合
								word_label_list.append((word[:int(beginID)-w_cnt], "O"))
								word_label_list.append((word[int(beginID):int(endID)-w_cnt+1], label))
								word = word[int(endID)-w_cnt+1:]
								ans_index += 1
								nextFlag = 1
								w_cnt += len(word[:int(endID)-w_cnt+1])
							elif int(endID)+1 == w_cnt+len(word): 
								word_label_list.append((word[:int(beginID)-w_cnt], "O"))
								word_label_list.append((word[int(beginID)-w_cnt:int(endID)-w_cnt+1], label))
								ans_index += 1
								w_cnt += len(word)
							else:
								word_label_list.append((word[:int(beginID)-w_cnt], "O"))
								word_label_list.append((word[int(beginID)-w_cnt:], label))
								w_cnt += len(word)
						elif int(beginID) < w_cnt: 
							label = "I-"+datetype
							if endID != None and int(endID)+1 < w_cnt+len(word):
								word_label_list.append((word[:int(endID)-w_cnt+1], label))
								word = word[int(endID)-w_cnt+1:]
								ans_index += 1
								nextFlag = 1
								w_cnt += len(word[:int(endID)-w_cnt+1])
							elif endID != None and int(endID)+1 == w_cnt+len(word):
								word_label_list.append((word, label))
								ans_index += 1
								w_cnt += len(word)
							else:
								word_label_list.append((word, label))
								w_cnt += len(word)
						else: 
							label = "O"
							word_label_list.append((word, label))
							if len(word) == 0: w_cnt += 1
							else: w_cnt += len(word)
						if before_w_cnt == w_cnt: print "before_w_cnt == w_cnt:", word, len(word)
						print ans_index, before_w_cnt, w_cnt, word.encode("utf-8"), beginID, endID, label
						if nextFlag == 0: break
#					w_cnt += len(W.word)
				else:
					label == ""

				for word, label in word_label_list:
					feature_list = []
					for feature, flag in FEATURE_DICT.items():
						if flag:
							if feature == "STRING": 
								feature_list.append(word.encode("utf-8"))
							elif feature == "HINSI": 
								feature_list.append(W.hinsi)
							elif feature == "NUM":
								feature_list.append(str(num))
							elif feature == "PATTERN":
								feature_list.append(str(pattern))
					feature_list.append(label)
					txt = " ".join(feature_list)+"\n"
					txt_list.append(txt)



		if ans_tup_list != [] and len(ans_tup_list) != len("".join([x.split(" ")[-1] for x in txt_list]).split("B"))-1:
			print >> sys.stderr, "ERROR!!:", ans_tup_list, txt_list, len(ans_tup_list), len("".join(txt_list).split("B"))-1
			print >> sys.stderr, "".join(txt_list)
			sys.exit()

		return "".join(txt_list)
