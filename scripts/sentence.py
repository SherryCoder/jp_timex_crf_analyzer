#coding: utf-8

import json
import sys
import word
import parameter
HOME = parameter.HOME

class Sentence:
	def __init__(self, input):
		self.knp_sentence_list = input

		# 元号ルールの読み込み
		with open(HOME+"rule/gengo.json") as f:
			gengoRule = json.load(f)
		gengoList = []
		for tmpdict in gengoRule:
			gengo = tmpdict[u"pattern"]
			gengoList.append(gengo)

		self.sentence2word(gengoList)


	def sentence2word(self, gengoList):
		# Word class の生成
		# output: self.Word_list

#		R = rule.Rule()
		self.rawtxt = ""
		self.Word_list = [] # Word class のリスト
		for token in self.knp_sentence_list:
			if token.startswith("#"): continue
			elif token.startswith("*"): continue
			elif token.startswith("+"): continue
			elif token.startswith("EOS"): continue
			else:
				self.rawtxt += token.split()[0]
				W = word.Word(token)
				self.Word_list.append(W)
		self.unitxt = unicode(self.rawtxt, "utf-8")
		self.rawtxt = unicode(self.rawtxt, "utf-8").encode("utf-8")
#		print "rawtxt: ", self.rawtxt
		
		self.retxt = u""
		# #をつける
		for W in self.Word_list:
			if W.num != None: 
				for w in W.word:
					if w in  [u"/", u"／", u"・"]: self.retxt += w # これらは#にしない
					else: self.retxt += u"#"
			else: self.retxt += W.word
		# %をつける
		for gengo in sorted(gengoList, key=lambda x:len(x), reverse=True): # 長い順に見る
			self.retxt = self.retxt.replace(gengo, u"%"*len(gengo))
