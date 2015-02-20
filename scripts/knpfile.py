#coding: utf-8
import commands

class KNPFile:
	def __init__(self, FILE=None, SENTENCE=None):
		lines = ""
		if FILE:
			with open(FILE) as f:
				lines = f.readlines()
		elif SENTENCE:
			strlines = self.knp(SENTENCE)
			lines = strlines.split("\n")

		self.parse_knp(lines)

	def knp(self, sentence):
		knpstr = commands.getoutput('echo "%s" | juman | knp -tab' % sentence)
		return knpstr


	def parse_knp(self, lines):
		self.all_sentence_list = []
		self.raw_sentence_list = []

		tmp_sentence_list = []
		tmp_raw_sentence_list = []
		sentence_cnt = 0
		for line in lines:
			tmp_sentence_list.append(line.strip())
			if line.startswith("EOS"):
				self.all_sentence_list.append(tmp_sentence_list)
				tmp_sentence_list = []

				self.raw_sentence_list.append( "".join(tmp_raw_sentence_list))
				tmp_raw_sentence_list = []
				sentence_cnt += 1
			if not (line.startswith("#") or line.startswith("+") or line.startswith("*") or line.startswith("EOS")):
				tmp_raw_sentence_list.append(line.split()[0])


if __name__ == "__main__":
	string = "一年前"
	K = KNPFile(SENTENCE=string)
