#coding: utf-8

import pickle
import json
import sys
import copy
sys.path.append("/home/sakaguchi/mytools/")
from  mypool import MyPool
import parameter
import knpfile
import sentence
import word
import apply_rule
import pattern2timex


# 	input format
# 	->	#documentID:DCT
#	->	sentence
#	->	span:TYPE
#	ex)
#		#00232.xml:2002-10-28
#		明日から2日まで東京で会議だ。
#		span: 0:2:DATE, 4:6:DATE

def crfresult2inputformat(CRF_RESULT_FILE, CRF_TEST_FILE, INPUT_FORMAT_FILE):
	# CRF_TEST_FILE からdctと文を取得しておく
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


	# CRFのファイルをinputフォーマットにする
	# CRFは改行を読み込まないので、空ファイルがあると飛ばしてしまって痕跡を全く残さない。
	# なので all_sentence_listを利用
	sentence_dct_num = 0
	beforeOFlag = 1
	documentID = None
	with open(CRF_RESULT_FILE) as f:  
		with open(INPUT_FORMAT_FILE, 'w') as g:
			sentence = ""
			cnt = 0
			TYPE = ""
			spanlist = []
			tmpspan = []
			for line in f:
				if line.startswith("#"): # そんなのないはず
					pass

				else:
					string = line.strip().split("\t")[0]
					sentence += string

					# 出力のBIOを解釈
					result = line.strip().split("\t")[-1]
					if (result == "O" or result.startswith("B")) and len(tmpspan) > 0:
						tmpspan.append(cnt)
						spanlist.append((tmpspan, TYPE))
						tmpspan = []
					if result.startswith("B") and len(tmpspan) == 0:
						tmpspan = [cnt]
						TYPE = result[2:]
					if result == "O":
						beforeOFlag = 1
					cnt += 1

					# 改行があったら、そこでformat書き込み
					if line.strip() == "":
						while sentence != all_sentence_list[sentence_dct_num]: # 空行の場合CRF_TEST_FILEでは検出できないので、all_sentence_listと見比べる
							if sentence_dct_list[sentence_dct_num] != None:
								documentID, dct = sentence_dct_list[sentence_dct_num]
								g.write("#%s:%s\n" % (documentID, dct))
							g.write("%s\n"%all_sentence_list[sentence_dct_num])
							g.write("span: \n")
							sentence_dct_num += 1
						if sentence_dct_list[sentence_dct_num] != None:
							documentID, dct = sentence_dct_list[sentence_dct_num]
							g.write("#%s:%s\n" % (documentID, dct))
						g.write("%s\n"%all_sentence_list[sentence_dct_num])
						g.write("span: ")
						g.write(", ".join(["%d:%d:%s"%(x[0][0], x[0][1], x[1]) for x in spanlist]))
						g.write("\n")
						sentence_dct_num += 1

						sentence = ""
						TYPE = ""
						spanlist = []
						tmpspan = []
						cnt = 0
			while sentence != all_sentence_list[sentence_dct_num]: # 空行の場合CRF_TEST_FILEでは検出できないので、all_sentence_listと見比べる
				if sentence_dct_list[sentence_dct_num] != None:
					documentID, dct = sentence_dct_list[sentence_dct_num]
					g.write("#%s:%s\n" % (documentID, dct))
				g.write("%s\n"%all_sentence_list[sentence_dct_num])
				g.write("span: \n")
				sentence_dct_num += 1
			if sentence_dct_list[sentence_dct_num] != None:
				documentID, dct = sentence_dct_list[sentence_dct_num]
				g.write("#%s:%s\n" % (documentID, dct))
			g.write("%s\n"%all_sentence_list[sentence_dct_num])
			g.write("span: ")
			g.write(", ".join(["%d:%d:%s"%(x[0][0], x[0][1], x[1]) for x in spanlist]))
			g.write("\n")



class Normalize:
	def __init__(self, inputfile, knpfile, PRINT_FLAG=0):
		self.PRINT_FLAG = PRINT_FLAG
		self.dateNameList = ["CENTURY", "GYEARX", "YEARX", "GYEAR", "GFYEAR", "FYEAR", "YEAR", "SEASON", "MONTH", "JUN", "WEEK", "DAY", "YOUBI", "PHRASE", "TIME", "HOUR", "MINUTE", "SECOND"]

		self.document_info_list = self.read_inputfile(inputfile)

		# knpfile -> list_of_knplist
		self.list_of_knplist = []
		with open(knpfile) as f: # 空ファイルの場合、KNPは何もしないので、ずれてしまう。self.document_info_listと対応付け
			sentence_list = [] # [sentence, ..]
			for documentID, dct, list_of_sentence_span_type_list in self.document_info_list:  # document 単位
				for sentence_span_type_list in list_of_sentence_span_type_list:
					sentence = sentence_span_type_list[0]
					sentence_list.append(sentence)

			knplist = []
			sentence_from_knp = ""
			sentence_id = 0
			for line in f:
				if line.startswith("EOS"):
					while sentence_from_knp != sentence_list[sentence_id]: # 空行の場合は対応するまで空リストを加える
						self.list_of_knplist.append([])
						sentence_id += 1
					self.list_of_knplist.append(knplist)
					sentence_id += 1

					sentence_from_knp = ""
					knplist = []
				else:
					knplist.append(line.strip())
					if not (line.startswith("+") or line.startswith("*") or line.startswith("#")):
						sentence_from_knp += line.split()[0]

		# 元号ルールの読み込み
		with open("/home/sakaguchi/tsubaki_research/time_expression/eval/crf_recognition/rule/gengo.json") as f:
			self.gengoRule = json.load(f)


	def normalize(self):
		# 各文正規化
		sentence_num = 0
		result_list = []
		normalize_input_list = []
		for documentID, dct, list_of_sentence_span_type_list in self.document_info_list:  # document 単位
			inputdate = self.dct2inputdate(dct)
			for sentenceID, sentence_span_type_list in enumerate(list_of_sentence_span_type_list):
				knplist = self.list_of_knplist[sentence_num]
				document_info = (documentID, str(sentenceID))
				norm_list = self.apply_strRule((document_info, copy.copy(inputdate), dct, sentence_span_type_list, knplist))
				result_list.append((document_info, norm_list))
#				normalize_input_list.append((document_info, copy.copy(inputdate), dct, sentence_span_type_list, knplist))
				sentence_num += 1
		return result_list

#		p = MyPool(15)
#		p.map(self.apply_strRule, normalize_input_list)



		
	def dct2inputdate(self, dct):
		inputdate = [None,None,None]
		if dct == None: return inputdate
		if "-" in dct:
			tmp = dct.split("-")
			if len(tmp) == 3: inputdate = map(int,tmp)
		else:
			try: # 2008とか
				inputdate[0] = int(dct)
			except:
				pass
		return inputdate


	def read_inputfile(self, inputfile):
		# output: document_info_list = [(documentID, dct, list_of_sentence_span_type_list)] 文書単位
		# list_of_sentence_span_type_list = [sentence_span_type_list, ..] 文書が複数の文から成っている
		# sentence_span_type_list = [sentence, (span1, type1), (span2, type2)] 文単位
		document_info_list = []
		span_list = [] # [(span, type), ..]
		documentID = ""
		dct = None
		sentence = ""
		with open(inputfile) as f:
			list_of_sentence_span_type_list = []
			sentence_span_type_list = []
			for line in f:
				if line.startswith("#"): # document begins
					if list_of_sentence_span_type_list != []:
						document_info_list.append((documentID, dct, list_of_sentence_span_type_list))
					list_of_sentence_span_type_list = []
					documentID, dct = line.strip()[1:].split(":")
				elif line == "\n": # 空行があれば飛ばす
					continue
				elif line.startswith("span:"):
					str_span_list = line.strip().split("span:")[1].split(",")
					span_list = [] # [(span, type), ..]
					for str_span in str_span_list: 
						if str_span.strip() != "": # spanが空の場合
							tmp = str_span.split(":")
							span = (int(tmp[0]), int(tmp[1]))
							TYPE = tmp[2]
							span_list.append((span, TYPE))
					sentence_span_type_list = [sentence] + span_list
					list_of_sentence_span_type_list.append(sentence_span_type_list)
					sentence = ""
				else:
					sentence = line[:-1]
		document_info_list.append((documentID, dct, list_of_sentence_span_type_list))
#		print document_info_list
		return document_info_list


	def apply_strRule(self, input):
		document_info, inputdate, dct, sentence_span_type_list, knplist = input  # 各文に対して正規化
		# sentence_span_type_list: [sentence, (type1, span1), (type2, span2), ..]
		AR = apply_rule.ApplyRule()
		S = sentence.Sentence(knplist)
		if self.PRINT_FLAG: print "rawtxt: ", S.rawtxt
		if not sentence_span_type_list[0] == S.rawtxt:
			print >> sys.stderr, "error!"
			print >> sys.stderr, "$"+sentence_span_type_list[0]+"$" 
			print >> sys.stderr, "$"+S.rawtxt+"$"
			print >> sys.stderr, len(sentence_span_type_list[0]), len(S.rawtxt)
			return
#			sys.exit()

		# 出力された時間表現を抜き出し、それぞれ個別に正規化
		norm_list = [] # (span, type)
		for span, TYPE in sentence_span_type_list[1:]:
			unitxt = S.unitxt[span[0]:span[1]]
			retxt = S.retxt[span[0]:span[1]]
			rule_matched_list = AR.ApplystrRule(unitxt, retxt) # [{span, rule_matched_dict, matchObj}, ..]
			if self.PRINT_FLAG:
				print document_info, span, TYPE
				print "target: ", unitxt.encode("utf-8"), retxt.encode("utf-8")
			for rule_matched_dict in rule_matched_list:
				matched_span = rule_matched_dict["span"]
				if self.PRINT_FLAG:
					print "rule_matched: ", unitxt[matched_span[0]:matched_span[1]].encode("utf-8"), (matched_span[0], matched_span[1])
			if self.PRINT_FLAG: print "inputdate: ", inputdate
			try:
				norm = pattern2timex.main(unitxt, TYPE, rule_matched_list, inputdate, self.gengoRule, self.PRINT_FLAG)
				if self.PRINT_FLAG: print "NORM:", norm
			except:
				print >> sys.stderr, "norm ERROR!: ", unitxt.encode("utf-8"), document_info, S.rawtxt
				norm = "NONE"
			if self.PRINT_FLAG: print

			norm_list.append((unitxt.encode("utf-8"), span, TYPE, norm))
		return norm_list


