from random import choice
import saliencefive as se5
import os

switchable_file_path = 'D:\\SpellCheckProject\\Switchables.csv'
test_directory_path = 'D:\\SpellCheckProject\\rawTextData\\'
data_path = 'C:\\Program Files (x86)\\Lexalytics\\data\\'
license_path = 'C:\\Program Files (x86)\\Lexalytics\\license.v5'
gold_corrupt_file_path = "D:\\SpellCheckProject\\CorruptedData.txt"

gold_corrupt_file = open(gold_corrupt_file_path, 'w')
switchable_file = open(switchable_file_path)
inverted_index = {}
session = se5.openSession(license_path, data_path)

for switchables in map(lambda switchables: switchables[0:len(switchables)-1].split("\t"), switchable_file):
	for switchable in switchables: inverted_index[switchable] = switchables


def corrupt_datum(word, inverted_index):
	if word in inverted_index: return choice(inverted_index[word])
	else: return word

def corrupt_data(words, inverted_index): return [corrupt_datum(word, inverted_index) for word in words]

def get_tokens(session, file_path):
	se5.prepareTextFromFile(session, file_path)
	
	doc_details = se5.getDocumentDetails(session)
	sentences_info = doc_details['sentences']
	sentences_tokens = map(lambda sentence_info: [token['token'] for token in sentence_info['tokens']], sentences_info)
	tokens = reduce(lambda x, y: x + y, sentences_tokens)
	
	return tokens


def tokens2words(tokens):
	words = []
	previous = ""

	for token in tokens:

		if(token == "'re" or token == "'t" or token == "'s" or previous == "@") and not token == tokens[0]: 
			words.pop()
			words.append("%s%s" % (previous, token))
		else: 
			words.append(token)

		previous = token

	return words

def make_gold_corrupt_pairing(file_path):
	tokens = get_tokens(session, file_path)
	words = tokens2words(tokens)
	
	return (words, corrupt_data(words, inverted_index))

data_pairs = [make_gold_corrupt_pairing('%s%s' % (test_directory_path, filename)) for filename in os.listdir(test_directory_path)]

for (gold, corrupt) in data_pairs:
	gold_corrupt_file.write('%s\t|\t%s' % (gold, corrupt))
