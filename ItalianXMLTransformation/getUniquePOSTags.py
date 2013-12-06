from lxml import etree
import os

directory = "D:\\ItalianProject\\msc_1.1\\italian\\"
uniquePOSTokLem = set()
outputFile = open("italianPOSTokLems.txt", "w")

for filename in os.listdir(directory):
	file = open(directory+filename, 'U')
	parser = etree.XMLParser(recover=True)
	tree = etree.parse(file, parser)
	allElements = tree.xpath('//struct[@type="t-level"]')
	for item in allElements:
		try:
			pos = item.xpath('.//feat[@type="pos"]/text()')[0]
			token = item.xpath('.//feat[@type="token"]/text()')[0]
			lemma = item.xpath('.//feat[@type="lemma"]/text()')[0]
			if pos == "punc" or pos == "punctuation" and lemma != None:
				if (pos, token, lemma) not in uniquePOSTokLem:
					uniquePOSTokLem.add((pos, token, lemma))
		except IndexError:
			continue

				
for item in uniquePOSTokLem:
	outputFile.write(('%s|%s|%s\n' % (item[0], item[1], item[2])).encode('utf-8'))
