import collections
import os

def smooth(word): 
	if not word.isalpha(): return "##UNKNOWN##"
	else: return word
def toLower(word): 
	for i in range(len(word)): word = word[:i] + word[i].lower() + word[i+1:]
	return word

tweetWords = open("tweets.csv")
prevFreq = {}
postFreq = {}

for line in tweetWords:
	line = map(toLower, map(smooth, line.split()))
	
	for (first, second) in zip(["##BOD##"] + line, line + ["##EOD##"]):
		if second in prevFreq and first in prevFreq[second]: prevFreq[second][first] += 1
		else: 
			if second not in prevFreq: prevFreq[second] = {}
			prevFreq[second][first] = 1
		
		if first in postFreq and second in postFreq[first]: postFreq[first][second] += 1 
		else: 
			if first not in postFreq: postFreq[first] = {}
			postFreq[first][second] = 1

del prevFreq["##EOD##"]
del postFreq["##BOD##"]

for key in prevFreq: prevFreq[key] = collections.OrderedDict(sorted(prevFreq[key].items()))
for key in postFreq: postFreq[key] = collections.OrderedDict(sorted(postFreq[key].items()))

projectDirPath = "D:\\SpellCheckProject\\TwitterWordFrequencyFiles\\"
freqDirPath = "%sFrequencyDirs\\" % projectDirPath

for word in prevFreq:
	wordDirPath = "%s%s\\" % (freqDirPath, word)
	
	os.makedirs(wordDirPath)
	
	prevFilePath = "%s%s" % (wordDirPath, "prev.csv")
	postFilePath = "%s%s" % (wordDirPath, "post.csv")
	prevFile = open(prevFilePath, 'a')
	postFile = open(postFilePath, 'a')
	
	for key in prevFreq[word]: prevFile.write("%s\t%s\n" % (key, prevFreq[word][key]))
	for key in postFreq[word]: postFile.write("%s\t%s\n" % (key, postFreq[word][key]))
	
	prevFile.close()
	postFile.close()