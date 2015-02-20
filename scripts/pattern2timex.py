#coding: utf-8
import sys
from collections import defaultdict

def main(unitxt, TYPE, rule_matched_list, inputdate, gengoRule, PRINT_FLAG=0):
	# rule_matched_list: [{"span":span, "matched_rule_dict":rule_matched_dict, "matchObj":matchObj}, ..]

	# datetypedict: {u"YEAR": [{"datetype":YEAR, "num":1}]}
	# 複数のルールが当てはまることはあるが、"YEAR"などは被らないはず
	datetypedict = defaultdict(list)
	for rule_result_dict in rule_matched_list: # 該当した複数のルール
		span = rule_result_dict["span"]
		rule_matched_dict = rule_result_dict["matched_rule_dict"]
		matchObj = rule_result_dict["matchObj"]
	
		# datetypedictの作成
		for i in range(len(rule_matched_dict[u"datetypelist"])): # 1つのルールはいくつかのdatetypelistでできている
			rule_each_datetypedict = rule_matched_dict[u"datetypelist"][i] # {u"datetype":u"YEAR", u"num":1}とか
			datetype = rule_each_datetypedict[u"datetype"]
			datetypedict[datetype].append(rule_each_datetypedict)
			# 数値表現があれば埋めておく
			# u"num":[1] -> u"num":[1989]
			if datetypedict[datetype][-1].has_key(u"num"):
				match_place = datetypedict[datetype][-1][u"num"]
				match_span = matchObj.span(match_place)
				uni_num = unitxt[span[0]+match_span[0]:span[0]+match_span[1]]
				num, trash = uni2num(uni_num)
				if num == None:
					print >> sys.stderr, "num error!", uni_num.encode("utf-8")
					print >> sys.stderr, "span:", span, " match span:", match_span,  unitxt, (span[0]+match_span[0],span[0]+match_span[1])
					sys.exit()
				datetypedict[datetype][-1][u"num"] = num
			if datetypedict[datetype][-1].has_key(u"gengo"):
				match_place = datetypedict[datetype][-1][u"gengo"]
				match_span = matchObj.span(match_place)
				uni_num = unitxt[span[0]+match_span[0]:span[0]+match_span[1]]
				for gengo_dict in gengoRule:
					if uni_num == gengo_dict[u"pattern"]:
						datetypedict[datetype][-1][u"gengo"] = gengo_dict[u"process_type"]

	if PRINT_FLAG: print datetypedict

	# 正規化
	if TYPE == "DATE" or TYPE == "TIME":
		# PAST_REF
		if datetypedict.has_key(u"PHRASE"):
			# ★ phraseが複数ある場合ってある？
			if len(datetypedict[u"PHRASE"]) > 1:
				print "TODO: phraseを複数個含む時間表現への対処!"
				for tmp_datetypedict in datetypedict[u"PHRASE"]:
					try: print tmp_datetypedict[u"norm"]
					except: print "no norm!"
			# とりあえず一番初めのphraseだけを処理
			tmp_datetypedict = datetypedict[u"PHRASE"][0]
			if tmp_datetypedict.has_key(u"norm") and tmp_datetypedict[u"norm"] in [u"PRESENT_REF", u"PAST_REF", u"FUTURE_REF"]:
				return tmp_datetypedict[u"norm"].encode("utf-8")

		# VAGUEだけならYEARにしておく ex) 1998
		if datetypedict.has_key(u"VAGUE") and len(datetypedict[u"VAGUE"]) == 1:
			tmp_datetypedict = datetypedict[u"VAGUE"][0]
			if tmp_datetypedict.has_key(u"num"):
				num = tmp_datetypedict[u"num"]
				tmp, int_date = int2str(num, 4)
				return tmp




		result_date_list = []
		result_time_list = []
		relflag = 0

		# 年
		tmp = None
		int_date = None
		if datetypedict.has_key(u"YEAR"):
			# とりあえず一番初めのYEARだけを処理
			tmp_datetypedict = datetypedict[u"YEAR"][0]
			if tmp_datetypedict.has_key(u"num"):
				num = tmp_datetypedict[u"num"]
				tmp, int_date = int2str(num, 4)
			if tmp_datetypedict.has_key(u"DCTrelation"):
				rel = tmp_datetypedict[u"DCTrelation"]
				if rel == 0: num = 0
				if tmp_datetypedict.has_key(u"fixnum"):
					num = tmp_datetypedict[u"fixnum"]
				if inputdate[0] != None:
					tmp, trash = int2str(inputdate[0]+rel*num, 4)
					int_date = inputdate[0] + rel*num
				relflag = 1
			elif tmp_datetypedict.has_key(u"relation"):
				rel = tmp_datetypedict[u"relation"]
				if rel == 0: num = 0
				if tmp_datetypedict.has_key(u"fixnum"):
					num = tmp_datetypedict[u"fixnum"]
				if inputdate[0] != None:
					tmp, trash = int2str(inputdate[0]+rel*num, 4)
					int_date = inputdate[0] + rel*num
				relflag = 1
		elif datetypedict.has_key(u"GYEAR"):
			# とりあえず一番初めのYEARだけを処理
			tmp_datetypedict = datetypedict[u"GYEAR"][0]
			num = tmp_datetypedict[u"num"]
			gengo = tmp_datetypedict[u"gengo"]
			tmp, int_date = int2str(num, 4, gengo)

		if tmp == None and inputdate[0] != None:  # 前のを引き継ぐ
			tmp, trash = int2str(inputdate[0], 4)
		if int_date != None: # 新しい数字を得たら登録
			inputdate[0] = int_date
			inputdate[1] = None
			inputdate[2] = None
		if tmp == None: tmp = "XXXX"
		result_date_list.append(tmp)

		# 月
		tmp = None
		int_date = None
		if datetypedict.has_key(u"MONTH"): 
			tmp = "YY" # 最終的に月まで表示する
			# とりあえず一番初めのMONTHだけを処理
			tmp_datetypedict = datetypedict[u"MONTH"][0]
			if tmp_datetypedict.has_key(u"num"):
				num = tmp_datetypedict[u"num"]
				tmp, int_date = int2str(num, 2)
			# 相対表現
			if inputdate[1] != None:
				if tmp_datetypedict.has_key(u"DCTrelation"):
					rel = tmp_datetypedict[u"DCTrelation"]
					if rel == 0: num = 0 # どうせrelとかけるから、numは何でもよい
					if tmp_datetypedict.has_key(u"fixnum"):
						num = tmp_datetypedict[u"fixnum"]
					tmp, trash = int2str(inputdate[1]+rel*num, 2)
					int_date = inputdate[1] + rel*num
					relflag = 1
				elif tmp_datetypedict.has_key(u"relation"):
					rel = tmp_datetypedict[u"relation"]
					if rel == 0: num = 0 # どうせrelとかけるから、numは何でもよい
					if tmp_datetypedict.has_key(u"fixnum"):
						num = tmp_datetypedict[u"fixnum"]
					tmp, trash = int2str(inputdate[1]+rel*num, 2)
					int_date = inputdate[1] + rel*num
					relflag = 1
		elif datetypedict.has_key(u"WEEK"):
			# とりあえず一番初めのWEEKだけを処理
			tmp_datetypedict = datetypedict[u"WEEK"][0]
			if tmp_datetypedict.has_key(u"norm"):
				tmp = tmp_datetypedict[u"norm"]
				if u"$NUM" in tmp:
					num = tmp_datetypedict[u"num"]
					tmp = tmp.replace(u"$NUM", unicode(str(num), "utf-8"))
				result_date_list.append(tmp.encode("utf-8"))
				return "-".join(result_date_list)
		elif datetypedict.has_key(u"SEASON"):
			# とりあえず一番初めのWEEKだけを処理
			tmp_datetypedict = datetypedict[u"SEASON"][0]
			if tmp_datetypedict.has_key(u"norm"):
				tmp = tmp_datetypedict[u"norm"]
				result_date_list.append(tmp)
				return "-".join(result_date_list)


		if int_date != None:
			inputdate[1] = int_date
			inputdate[2] = None
		if tmp == None and inputdate[1] != None and not relflag:
			tmp, trash = int2str(inputdate[1], 2)
		if tmp == None: tmp = "XX"
		result_date_list.append(tmp)


		# 日
		tmp = None
		int_date = None
		if datetypedict.has_key(u"DAY"):
			tmp = "YY" # 最終的に日まで表示する
			# とりあえず一番初めのDAYだけを処理
			tmp_datetypedict = datetypedict[u"DAY"][0]
			if tmp_datetypedict.has_key(u"num"):
				num = tmp_datetypedict[u"num"]
				tmp, int_date = int2str(num, 2)
			# 相対表現
			if inputdate[2] != None:
				if tmp_datetypedict.has_key(u"DCTrelation"):
					rel = tmp_datetypedict[u"DCTrelation"]
					if rel == 0: num = 0
					if tmp_datetypedict.has_key(u"fixnum"):
						num = tmp_datetypedict[u"fixnum"]
					tmp, trash = int2str(inputdate[2]+rel*num, 2)
					int_date = inputdate[2] + rel*num
					relflag = 1
				elif tmp_datetypedict.has_key(u"relation"):
					rel = tmp_datetypedict[u"relation"]
					if rel == 0: num = 0
					if tmp_datetypedict.has_key(u"fixnum"):
						num = tmp_datetypedict[u"fixnum"]
					tmp, trash = int2str(inputdate[2]+rel*num, 2)
					int_date = inputdate[2] + rel*num
					relflag = 1
		if int_date != None:
			inputdate[2] = int_date
		if tmp == None and inputdate[2] != None and not relflag:
			tmp, trash = int2str(inputdate[2], 2)
		if tmp == None: tmp = "XX"
		result_date_list.append(tmp)


		# 時
		tmp = "XX"
		if datetypedict.has_key(u"HOUR"):
			# とりあえず一番初めのHOURだけを処理
			tmp_datetypedict = datetypedict[u"HOUR"][0]
			num = tmp_datetypedict[u"num"]
			if tmp_datetypedict.has_key(u"norm") and tmp_datetypedict["norm"] == 'AF': 
				tmp, int_date = int2str(num+12, 2) # 午後
			else: tmp, int_date = int2str(num, 2)
		elif datetypedict.has_key(u"TIME"): # 朝とか
			# とりあえず一番初めのTIMEだけを処理
			tmp_datetypedict = datetypedict[u"TIME"][0]
			return "-".join(result_date_list)+"T"+tmp_datetypedict["norm"]
		result_time_list.append(tmp)

		# 分
		tmp = "XX"
		if datetypedict.has_key(u"MINUTE"):
			# とりあえず一番初めのMINUTEだけを処理
			tmp_datetypedict = datetypedict[u"MINUTE"][0]
			num = tmp_datetypedict[u"num"]
			tmp, int_date = int2str(num, 2)
		result_time_list.append(tmp)

		# 秒
		tmp = "XX"
		if datetypedict.has_key(u"SECOND"):
			# とりあえず一番初めのSECONFだけを処理
			tmp_datetypedict = datetypedict[u"SECOND"][0]
			num = tmp_datetypedict[u"num"]
			tmp, int_date = int2str(num, 2)
		result_time_list.append(tmp)

		if PRINT_FLAG: print result_date_list, result_time_list

		# 表示形式
		if "".join(result_time_list) == "X"*len("".join(result_time_list)):
			if "".join(result_date_list[2]) == "X"*len("".join(result_date_list[2])): 
				if "".join(result_date_list[1]) == "X"*len("".join(result_date_list[1])): 
					return result_date_list[0].replace("Y","X")
				return "-".join(result_date_list[:2]).replace("Y","X")
			return "-".join(result_date_list).replace("Y","X")
		else: # 時刻まで表示
			if "".join(result_time_list[2]) == "X"*len("".join(result_time_list[2])): 
				if "".join(result_time_list[1]) == "X"*len("".join(result_time_list[1])): 
					return "-".join(result_date_list)+"T"+":".join(result_time_list[:1]).replace("Y","X")
				return "-".join(result_date_list)+"T"+":".join(result_time_list[:2]).replace("Y","X")
			return "-".join(result_date_list)+"T"+":".join(result_time_list).replace("Y","X")
		

	elif TYPE == "DURATION":
		returndate = ""
		returntime = ""
		if datetypedict.has_key(u"VAGUE"):
			# VAGUE -> YEARとしておく
			tmp_datetypedict = datetypedict[u"VAGUE"][0]
			num = tmp_datetypedict[u"num"]
			return "P"+str(num)+"Y"
		if datetypedict.has_key(u"YEARX"):
			# とりあえず一番初めのYEARXだけを処理
			tmp_datetypedict = datetypedict[u"YEARX"][0]
			num = tmp_datetypedict[u"num"]
			if num != -1: returndate += str(num)[:-1]+"XY"
			else: returndate = "XY"
		if datetypedict.has_key(u"YEAR"):
			# とりあえず一番初めのYEARだけを処理
			tmp_datetypedict = datetypedict[u"YEAR"][0]
			num = tmp_datetypedict[u"num"]
			if num != -1: returndate += str(num)+"Y"
			else: returndate = "1Y"
		if datetypedict.has_key(u"MONTH"):
			# とりあえず一番初めのMONTHだけを処理
			tmp_datetypedict = datetypedict[u"MONTH"][0]
			num = tmp_datetypedict[u"num"]
			if num != -1: returndate += str(num)+"M"
			else: returndate = "XM"
		if datetypedict.has_key(u"WEEK"):
			# とりあえず一番初めのWEEKだけを処理
			tmp_datetypedict = datetypedict[u"WEEK"][0]
			num = tmp_datetypedict[u"num"]
			if num != -1: returndate += str(num)+"W"
			else: returndate = "XW"
		if datetypedict.has_key(u"DAY"):
			# とりあえず一番初めのDAYだけを処理
			tmp_datetypedict = datetypedict[u"DAY"][0]
			num = tmp_datetypedict[u"num"]
			if num != -1: returndate += str(num)+"D"
			else: returndate = "XD"
		if datetypedict.has_key(u"HOUR"):
			# とりあえず一番初めのHOURだけを処理
			tmp_datetypedict = datetypedict[u"HOUR"][0]
			num = tmp_datetypedict[u"num"]
			if num != -1: returntime += str(num)+"H"
			else: returntime = "XH"
		if datetypedict.has_key(u"MINUTE"):
			# とりあえず一番初めのMINUTEだけを処理
			tmp_datetypedict = datetypedict[u"MINUTE"][0]
			num = tmp_datetypedict[u"num"]
			if num != -1: returntime += str(num)+"M"
			else: returntime = "XM"
		if datetypedict.has_key(u"SECOND"):
			# とりあえず一番初めのSECONDだけを処理
			tmp_datetypedict = datetypedict[u"SECOND"][0]
			num = tmp_datetypedict[u"num"]
			if num != -1: returntime += str(num)+"S"
			else: returntime = "XS"

		if returndate != "":
			return "P"+returndate
		elif returntime != "":
			return "PT"+returntime

	elif TYPE == "SET":
		if datetypedict.has_key(u"YEAR"):
			# とりあえず一番初めのYEARだけを処理
			tmp_datetypedict = datetypedict[u"YEAR"][0]
			if tmp_datetypedict.has_key(u"num"):
				num = tmp_datetypedict[u"num"]
				return "P"+str(num)+"Y"
			else: return "P1Y"
		elif datetypedict.has_key(u"MONTH"):
			# とりあえず一番初めのMONTHだけを処理
			tmp_datetypedict = datetypedict[u"MONTH"][0]
			if tmp_datetypedict.has_key(u"num"):
				num = tmp_datetypedict[u"num"]
				return "P"+str(num)+"M"
			else: return "P1M"
		elif datetypedict.has_key(u"WEEK"):
			# とりあえず一番初めのWEEKだけを処理
			tmp_datetypedict = datetypedict[u"WEEK"][0]
			if tmp_datetypedict.has_key(u"num"):
				num = tmp_datetypedict[u"num"]
				return "P"+str(num)+"W"
			else: return "P1W"
		elif datetypedict.has_key(u"DAY"):
			# とりあえず一番初めのDAYだけを処理
			tmp_datetypedict = datetypedict[u"DAY"][0]
			if tmp_datetypedict.has_key(u"num"):
				num = tmp_datetypedict[u"num"]
				return "P"+str(num)+"D"
			else: return "P1D"
		elif datetypedict.has_key(u"HOUR"):
			# とりあえず一番初めのHOURだけを処理
			tmp_datetypedict = datetypedict[u"HOUR"][0]
			if tmp_datetypedict.has_key(u"num"):
				num = tmp_datetypedict[u"num"]
				return "PT"+str(num)+"H"
			else: return "PT1H"
		elif datetypedict.has_key(u"MINUTE"):
			# とりあえず一番初めのMINUTEだけを処理
			tmp_datetypedict = datetypedict[u"MINUTE"][0]
			if tmp_datetypedict.has_key(u"num"):
				num = tmp_datetypedict[u"num"]
				return "PT"+str(num)+"M"
			else: return "PT1M"
		elif datetypedict.has_key(u"SECOND"):
			# とりあえず一番初めのSECONDだけを処理
			tmp_datetypedict = datetypedict[u"SECOND"][0]
			if tmp_datetypedict.has_key(u"num"):
				num = tmp_datetypedict[u"num"]
				return "PT"+str(num)+"S"
			else: return "PT1S"



	
def int2str(integer, keta, gengo=0):
	if keta == 4:
		if integer > 1000: return str(integer), integer
		if gengo != 0:
			if gengo+integer >= 1000: return str(gengo+integer), gengo+integer
		if 30 < integer < 100: return str(integer+1900), integer+1900
		else: return str(integer+2000), integer+2000
	elif keta == 2:
		if integer < 10: return "0"+str(integer), integer
		else: return str(integer), integer
	return str(integer), integer


def uni2num(uninum):
	# 小数点
	try:
		num_list = []
		if uninum[1] in [u".", u"．", u"・"]:
			for i in range(len(uninum)):
				if i == 1: continue
				uni_string = uninum[i]
				num = str2num(uni_string)
				num_list.append(num)
			if None not in num_list:
				num = 0 
				for keta, tmpnum in enumerate(num_list):
					num += tmpnum* (10**(-1*keta))
				return num, None
	except: pass	


	num_list = []
	kazuFlag = 0 
	# 三十数年 -> num="3X", kazuFlag=1
	if len(uninum) == 1 and str2num(uninum) == -1: return "X", 1 # 数年
	
	# "半年" -> 0文字目が"半"
	if len(uninum) == 2 and uninum[0] == u"半": return 0.5, None


	# 二百三十年
	if set(uninum) & set([u"十", u"百", u"千"]) != set([]):
		num_list = [0,0,0,0]
		tmp_num = None
		firstFlag = 1 # 百二十年の「百」を認識するためのフラグ
		for i in range(len(uninum)):
			uni_string = uninum[i]
			num = str2num(uni_string)
			if num == -1: # 数,何
				tmp_num = "X"
			elif num != None:
				tmp_num = num
			else:
				if uni_string == u"千":
					if firstFlag and tmp_num == None:
						num_list[3] = 1
					else: 
						if tmp_num != None: num_list[3] = tmp_num
						else: num_list[3] = 1
					tmp_num = None
					firstFlag = 0
				elif uni_string == u"百":
					if firstFlag and tmp_num == None:
						num_list[2] = 1
					else: 
						if tmp_num != None: num_list[2] = tmp_num
						else: num_list[2] = 1
					tmp_num = None
					firstFlag = 0
				elif uni_string == u"十":
					if firstFlag and tmp_num == None:
						num_list[1] = 1
					else: 
						if tmp_num != None: num_list[1] = tmp_num
						else: num_list[1] = 1
					tmp_num = None
					firstFlag = 0
#					else:
#						return None, None
		if tmp_num != None: num_list[0] = tmp_num
		if None in num_list: return None,None # 10兆3千

		if "X" in num_list:
			kazu = ""
			firstZeroFlag = 1
			for keta, i in enumerate(num_list[::-1]):
				if firstZeroFlag and i == 0: continue # 冒頭の0はいらない
				else: firstZeroFlag = 0

				if i == "X":
					kazu += "X"
				else:
					kazu += str(i)
			return kazu, 1
		else:
			num = 0
			for keta, i in enumerate(num_list):
				num += i * (10**keta)
			return num, None

	num_list = []
	# 1923年
	for i in range(len(uninum)):
		uni_string = uninum[i]
		num = str2num(uni_string)
		num_list.append(num)
	if None not in num_list:
		num = 0
		for keta, tmpnum in enumerate(num_list[::-1]):
			num += tmpnum* (10**keta)
		return num, None


	# 半年, 元年
	if len(uninum) == 1 and uninum[0] == u'半': return 0.5, None
	elif len(uninum) == 1 and uninum[0] == u'元': return 1, None
	
	return None, None


def str2num(uni_string):
	num = None
	if uni_string == u'0' or uni_string == u'０' or uni_string == u'〇' or uni_string == u'零': num = 0
	elif uni_string == u'1' or uni_string == u'１' or uni_string == u'一': num = 1
	elif uni_string == u'2' or uni_string == u'２' or uni_string == u'二': num = 2
	elif uni_string == u'3' or uni_string == u'３' or uni_string == u'三': num = 3
	elif uni_string == u'4' or uni_string == u'４' or uni_string == u'四': num = 4
	elif uni_string == u'5' or uni_string == u'５' or uni_string == u'五': num = 5
	elif uni_string == u'6' or uni_string == u'６' or uni_string == u'六': num = 6
	elif uni_string == u'7' or uni_string == u'７' or uni_string == u'七': num = 7
	elif uni_string == u'8' or uni_string == u'８' or uni_string == u'八': num = 8
	elif uni_string == u'9' or uni_string == u'９' or uni_string == u'九': num = 9
	elif uni_string in [u"数", u"何"]: num = -1
	return num
