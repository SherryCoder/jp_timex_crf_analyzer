#coding: utf-8

import sys
import re
import json
import copy
import knpfile
import word
import sentence
import parameter
HOME = parameter.HOME

class ApplyRule:
	def __init__(self, PRINT_FLAG=0):
		self.PRINT_FLAG = PRINT_FLAG
		# Ruleの読み込み
		with open(HOME+"rule/strRule.json") as f:
			self.strRuleList = json.load(f)
		for i in range(len(self.strRuleList)):
			pattern = self.strRuleList[i][u"pattern"]
			repattern = re.compile(pattern)
			self.strRuleList[i][u"repattern"] = repattern

	def ApplystrRule(self, unitxt, retxt): # strRuleを適用
		# unitxt: unicodeの文字列
		# retxt: unicodeで、数値部分を#などに置き換えたもの
		if self.PRINT_FLAG: print unitxt.encode("utf-8")
		pivotID = 0
		resultlist = [] # [{"span":span, "matched_rule_dict": matched_rule_dict, "matchObj":matchObj), ..]
		tmpIDlist = [] # [(span, matched_rule_dict)]
		while 1:
			# すべてのルールを適用	
			for i in range(len(self.strRuleList)):
				repattern = self.strRuleList[i][u"repattern"]
				matchObj = re.search(repattern, retxt[pivotID:])
				if matchObj == None: continue
				if self.PRINT_FLAG:
					print "\t", matchObj.group().encode("utf-8"), matchObj.span(), self.strRuleList[i]
				span = matchObj.span()
				tmpIDlist.append((span, self.strRuleList[i], matchObj, i))
			if len(tmpIDlist) == 0: 
				break
			else:
				tmpIDlist.sort(key=lambda x:x[0][1], reverse=True) # span[1]
				tmpIDlist.sort(key=lambda x:x[0][0]) # span[0]
				span, matched_rule_dict, matchObj, i = tmpIDlist[0]

				new_matched_rule_dict = {} # {u"pattern": , u"datetypelist"} 返り値用
				new_matched_rule_dict[u"pattern"] = matched_rule_dict[u"pattern"]
				new_matched_rule_dict[u"datetypelist"] = copy.deepcopy(matched_rule_dict[u"datetypelist"])

				if self.PRINT_FLAG:
					print
					print "unitxt:", unitxt.encode("utf-8")
					print "retxt:", retxt.encode("utf-8")
					print unitxt[pivotID+span[0]:pivotID+span[1]].encode("utf-8"), (pivotID+span[0], pivotID+span[1])
#				print "matched rule dict: ", new_matched_rule_dict
				resultlist.append({"span":(pivotID+span[0], pivotID+span[1]), "matched_rule_dict":new_matched_rule_dict, "matchObj":matchObj, "ruleID":i})
				pivotID += span[1]
				tmpIDlist = []
		return resultlist
