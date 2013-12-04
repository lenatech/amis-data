#-*- coding: utf8 -*-
# Convert ?.txt to dict-amis.json for moedict

import sys

JSON = {}
INDEX = []

def ng(s):
	return s.strip().replace('g', 'ng')

def ngtilde(s):
	import re
	return re.sub(r'([\w\']+)', r'`\1~', ng(s))

def addsplt(s):
	return u'\ufff9'+s[0].decode('utf8')+u'\ufffa'+s[1].decode('utf8')+u'\ufffb'+s[2].decode('utf8')

def mkword(title, definitions):
	global JSON, INDEX
	word = {'title': title,
		'heteronyms': [{'definitions': definitions}]}
	JSON[title] = word
	INDEX.append(title)

def mkdef(defi, examples, link):
	defdic = {}
	if len(examples) > 0:
		defdic['example'] = examples
		examples = []
	if defi[2] != '':
		defdic['def'] = addsplt(defi)
	if link:
		defdic['link'] = map(ngtilde, link.split(','))
	return defdic

def readdict(fn):
	fp = open(fn, 'ru')
	title = None
	state = None
	for line in fp:
		l = line.strip()
		if l == '' and title:			# 寫入詞條
			defdic = mkdef(defi, examples, link)
			if len(defdic) > 0:
				definitions.append(defdic)
			mkword(title, definitions)
			title = None
			state = None
			continue
		if l == '':				# 空白行
			continue
		if l[0] == '#':				# 註解
			continue
		xs = l.split()				# 處理 word'a = word'b
		if state is None and len(xs) == 3 and xs[1] == '=':
			title = ng(xs[0])
			link = xs[2]
			defdic = mkdef(['', u'Refer to linked words', u'詳見相關詞。'.encode('utf8')], [], link)
			mkword(title, [defdic])
			title = None
			continue
		if state is None:			# 詞
			title = ng(l)
			definitions = []
			examples = []
			link = None
			defi = ['', '', '']
			state = 't'
			continue
		if l[0:2] == '=>':			# 相關詞
			state = 'l'
		if line[0:4] == '    ':			# 例句
			state = 'e' + state
		elif state in ['t', 'm', 'f']:		# 英文定義
			defdic = mkdef(defi, examples, link)
			if len(defdic) > 0:
				definitions.append(defdic)
			defi = ['', l, '']
			examples = []
			state = 'E'
			continue
		if state == 'E':			# 漢語定義
			defi[2] = l
			state = 'f'
			continue
		if state in ['ef', 'em']:		# 阿美語例句
			ex = [ngtilde(l), '', '']
			state = 'a'
			continue
		if state == 'ea':			# 英文例句
			ex[1] = l
			state = 'e'
			continue
		if state == 'ee':			# 漢語例句
			ex[2] = l
			examples.append(addsplt(ex))
			state = 'm'
			continue
		if state == 'l':			# 相關詞
			link = l[2:]

	if title:
		defdic = mkdef(defi, examples, link)
		if len(defdic) > 0:
			definitions.append(defdic)
		mkword(title, definitions)
	fp.close()

if __name__ == '__main__':
	import os
	import json
	import re
	import codecs
	for fn in os.listdir('.'):
		if re.match(r'^[0a-z]\.txt$', fn):
			readdict(fn)
	f = codecs.open('index.json', mode='w', encoding='utf8')
	f.write(json.dumps(INDEX, indent=2, separators=(',', ':'), ensure_ascii = False))
	f.close()
	f = codecs.open('dict-amis.json', mode='w', encoding='utf8')
	f.write(json.dumps(JSON.values(), indent=2, separators=(',', ':'), ensure_ascii = False))
	f.close()