#coding: utf-8
import sys
sys.path.append("/home/sakaguchi/tsubaki_research/crf_timex/scripts")
import normalize

N = normalize.Normalize("nor_test.input", "nor_test.knp", True)
N.normalize()
