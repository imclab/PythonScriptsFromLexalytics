from lxml import etree
import os
import csv

class ItalianCorpusTransformer():

	def getFullCorpus(self):
		header = '<?xml version="1.0" encoding="UTF-8"?>\n<corpus>\n'
		footer = '</corpus>\n'
		fullCorpus = ''
		
		docID = 0
		
		for item in self.XMLTrees:
			for paragraph in item.xpath('.//struct[@type="p-level"]'):
				fullCorpus += self.getFullDocument(paragraph, docID)
				docID += 1
		
		return '%s%s%s' % (header, fullCorpus, footer)
	
	def getFullDocument(self, item, docID):
		header = '\t<document id="%s">\n\t\t<title>%s</title>\n' % (docID, docID)
		footer = '\t</document>\n'
		fullText = '<text>'
		fullPOSMarkup = ''
		location = 0
		sentenceID = 0
		
		for sentence in item.xpath('.//struct[@type="s-level"]'):
			sentenceText = ''
			sentencePOSMarkup = ''
			for token in sentence.xpath('.//struct[@type="t-level"]'):
				try:
					word = token.xpath('.//feat[@type="token"]/text()')[0]
					pos = token.xpath('.//feat[@type="pos"]/text()')[0]
					
					if pos != 'punc' and pos != 'punctuation' and sentenceText != '':
						sentenceText += ' '
						
					sentenceText += word
					sentencePOSMarkup += self.transformToken(token, location, location+len(word))
					location += len(word) + 1
				except IndexError:
					continue
				
			fullText += '%s\n\n' % sentenceText
			fullPOSMarkup += self.transformSentence(sentencePOSMarkup, sentenceID)
			location += 2
			sentenceID += 1
		
		fullText += "</text>\n"
		
		return '%s%s%s%s' % (header, fullText, fullPOSMarkup, footer)

	def transformSentence(self, sentencePOSMarkup, sentenceID):
		return '\t\t<sentence id="%s">\n%s\t\t</sentence>\n' % (sentenceID, sentencePOSMarkup)

	def transformToken(self, token, start, end):
		id = int(token.xpath('.//feat[@type="position"]/text()')[0]) - 1
		tag = self.getPOSTag(token)
		text = token.xpath('.//feat[@type="token"]/text()')[0]
		return '\t\t\t<word end="%s" id="%s" start="%s" tag="%s">%s</word>\n' % (end, id, start, tag, text)

	def getPOSTag(self, token):
		word = token.xpath('.//feat[@type="token"]/text()')[0]
		pos = token.xpath('.//feat[@type="pos"]/text()')[0]
		lemma = token.xpath('.//feat[@type="lemma"]/text()')[0]
		
		if word == '-': return '-'
		
		try:
			possibleTags = self.tagTransformations[pos]
		except KeyError:
			return 'undef'
		
		if len(possibleTags) == 1:
		
			if pos == 'n' or pos == 'ns':
				if lemma != word and lemma != 'undef':
					return 'NNS'
				else:
					return 'NN'
					
			return possibleTags[0][2]
		else:
			for tag in possibleTags:
				if word == tag[0] and lemma == tag[1]:
					return tag[2]
		
	def initTagMap(self, tagMapDirectory):
		tagMapReader = csv.reader(open(tagMapDirectory), delimiter='	')
		
		for row in tagMapReader:
			if row[0] in self.tagTransformations:
				self.tagTransformations[row[0]].append((row[1],row[2],row[3]))
			else:
				self.tagTransformations[row[0]] = [(row[1],row[2],row[3])]
		
	def __init__(self, inputDirectory, tagMapDirectory):
		self.XMLTrees = set()
		self.tagTransformations = {}

		for filename in os.listdir(inputDirectory):
			file = open(inputDirectory+filename, 'U')
			parser = etree.XMLParser(recover=True)
			self.XMLTrees.add(etree.parse(file, parser))
		
		self.initTagMap(tagMapDirectory)
		
		
inputDirectory = "D:\\ItalianProject\\msc_1.1\\italian\\"
tagMapDirectory = "D:\\ItalianProject\\ItalianPOSmap.csv"
outputFilePath = "D:\\ItalianProject\\italian_pos_corpus.xml"
outputFile = open(outputFilePath, 'w')
transformer = ItalianCorpusTransformer(inputDirectory, tagMapDirectory)

outputFile.write(transformer.getFullCorpus().encode('utf-8'))
