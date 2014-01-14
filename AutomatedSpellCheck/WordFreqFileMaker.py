import collections
import os
import math
from sets import Set

def prepare_text(word): 
	"""Turns a word to lower case"""
	
	return reduce(lambda x, y: x + y, [letter.lower() for letter in word])

def update_dict(dict, first, second, count):
	"""Given two words in a particular order, updates
	the dictionary on the existence and count of the
	co-occurrence of these words"""
	
	if first in dict and second in dict[first]: 
		dict[first][second] += count 
	else: 
		if first not in dict: dict[first] = {}
		dict[first][second] = count

def smooth_count_dicts(dict, unknown_key, min):
	"""Assigns the counts of all words with count less 
	than min to unknown_key's counts and deletes the 
	dictionary entry of those words with the intuition
	that the likely hood of a single unseen word should be
	similar to the total likelihood of all the nearly unseen words"""
	
	count = 0

	for key1 in dict:
		current = dict[key1]
		item_list = current.items() + [(unknown_key, 1)]
		dict[key1] = collections.OrderedDict(sorted(item_list))
	
		for key2 in current:
			if current[key2] < min:
				dict[key1][unknown_key] += current[key2]
				del dict[key1][key2]

def count_dicts2prob_dicts(dict):
	"""Normalizes the word counts for each position over total 
	occurrences of that word in the respective position"""
	
	print "\tMAKING PAIR LIST"
	pair_list = []
	
	#Would like to have used reduce with list concatenation here, but it turns out extend is MUCH faster
	for pairs in map(lambda x: x.items(), dict.values()): pair_list.extend(pairs)
	print "\tPAIR LIST FINISHED\n"
	
	sums = {}
	
	print "\tMAKING SUM DICT"
	for (word, count) in pair_list:
		if word in sums: sums[word] += count
		else: sums[word] = count
	print "\tSUM DICT MADE\n"
	
	print "\tDIVIDING COUNTS BY SUMS"
	for key1 in dict:
		for key2 in dict[key1]:
			dict[key1][key2] = math.log(dict[key1][key2]) - math.log(sums[key2])
	print "\tSUMS DIVIDED BY COUNTS\n"

bigrams = open("bigrams.csv")
prev_freq = {}
post_freq = {}

unknown = "##unknown##"

print "POPULATING THE DICTS"

for line in bigrams:
	(bigram, count) = line.split(',')
	count = int(count[1:len(count)-2])
	(first, second) = map(prepare_text, bigram[1:len(bigram)-1].split())
	
	update_dict(prev_freq, second, first, count)
	update_dict(post_freq, first, second, count)
	
print "DICTS HAVE BEEN POPULATED\n"
print "SMOOTHING DICTS"

smooth_count_dicts(prev_freq, unknown, 2)
smooth_count_dicts(post_freq, unknown, 2)

print "DICTS HAVE BEEN SMOOTHED\n"
print "CHANGING COUNTS TO LOG PROBABILITIES"

count_dicts2prob_dicts(prev_freq)
count_dicts2prob_dicts(post_freq)

print "COUNTS ARE NOW LOG PROBABILITIES\n"

project_dir_path = "D:\\SpellCheckProject\\TwitterWordFrequencyFiles\\"
freq_dir_path = "%sCommonCrawlFrequencyDirs\\" % project_dir_path

print "SAVING TO CSV FILES"

#Gets rid of words that don't ever occur with either a word preceding them or a word succeeding them and words that would cause problematic Windows directory names
keys = Set(prev_freq.keys()).intersection(Set(post_freq.keys())).difference(Set(["aux", "con", "nul", "prn", "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9",]))

for key1 in keys:
	word_dir_path = "%s%s\\" % (freq_dir_path, key1)
	
	os.makedirs(word_dir_path)
	
	prev_file_path = "%s%s" % (word_dir_path, "prev.csv")
	post_file_path = "%s%s" % (word_dir_path, "post.csv")
	prev_file = open(prev_file_path, 'a')
	post_file = open(post_file_path, 'a')
	
	prev_lines = ""
	post_lines = ""
	
	for key2 in prev_freq[key1]: prev_lines += "%s\t%s\n" % (key2, prev_freq[key1][key2])
	
	prev_file.write(prev_lines)
	
	for key2 in post_freq[key1]: post_lines += "%s\t%s\n" % (key2, post_freq[key1][key2])
	
	post_file.write(post_lines)
	
	prev_file.close()
	post_file.close()
	
print "LOG PROBABILITIES NOW ARCHIVED TO FILES"
