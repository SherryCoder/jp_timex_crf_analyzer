#coding: utf-8

class Word:
	def __init__(self, knp_line):
		self.knp_line = knp_line
		self.zeroBeginFlag = 0 # 03等の場合に1が立つ
		self.gengonum = 0 # 元号の場合初めの年。1988とか

		self.make_token()
		self.isNum()

#		for gengo_rule in R.gengoData:
#			gengo = gengo_rule[u"pattern"]
#			if gengo == self.word:
#				self.gengonum = int(gengo_rule[u"process_type"][0].encode("utf-8"))

#		self.modarity_nor = None # "START" とか
#		for modarity_rule in R.modarityData:
#			pattern_list = modarity_rule[u"pattern"]
#			all_pattern_list = [pattern_list]
#			if modarity_rule.has_key(u"synonym") and modarity_rule[u"synonym"] != u"None": 
#				for pattern in modarity_rule[u"synonym"]:
#					all_pattern_list.append(pattern)
#
#			for pattern_list in all_pattern_list:
#				if self.strword == pattern_list[0].encode("utf-8"):
#					self.modarity_nor = modarity_rule[u"nor"].encode("utf-8")

	def make_token(self): # knp_line を分解する
		self.strword = self.knp_line.split()[0] # str
		self.word = unicode(self.knp_line.split()[0], "utf-8") # unicode
		self.strmidasi = self.knp_line.split()[2]
		self.midasi = unicode(self.knp_line.split()[2], "utf-8")
		self.yomi = self.knp_line.split()[1] # 読み
		self.genkei = self.knp_line.split()[2] # 原形
		self.hinsi = self.knp_line.split()[3] # 品詞
		self.hinsi_small = self.knp_line.split()[5] # 品詞細分類
		if "<カテゴリ" in self.knp_line:
			self.category = self.knp_line.split("<カテゴリ:")[1].split(">")[0]
		else:
			self.category = None
		self.length = len(self.word)
#		print self.word, self.hinsi

	def isNum(self): # .num メソッドの生成
		self.num, self.kazu = self.isUniNum()

	def isUniNum(self):
		# return num, kazu
		
		# 小数点
		try:
			num_list = []
			if self.word[1] in [u".", u"．", u"・"]:
				for i in range(len(self.word)):
					if i == 1: continue
					uni_string = self.word[i]
					num = self.str2num(uni_string)
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
		if len(self.word) == 1 and self.str2num(self.word) == -1: return "X", 1 # 数年
		
		# "半年" -> 0文字目が"半"
		if len(self.word) == 2 and self.word[0] == u"半": return 0.5, None


		# 二百三十年
		if set(self.word) & set([u"十", u"百", u"千"]) != set([]):
			num_list = [0,0,0,0]
			tmp_num = None
			firstFlag = 1 # 百二十年の「百」を認識するためのフラグ
			for i in range(len(self.word)):
				uni_string = self.word[i]
				num = self.str2num(uni_string)
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

#			print num_list, self.strword
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
		for i in range(len(self.word)):
			uni_string = self.word[i]
			num = self.str2num(uni_string)
			num_list.append(num)
		if None not in num_list:
			if num_list[0] == 0: self.zeroBeginFlag = 1
			num = 0
			for keta, tmpnum in enumerate(num_list[::-1]):
				num += tmpnum* (10**keta)
			return num, None


		# 半年, 元年
		if len(self.word) == 1 and self.word[0] == u'半': return 0.5, None
		elif len(self.word) == 1 and self.word[0] == u'元': return 1, None
		
		return None, None


	def str2num(self, uni_string):
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
