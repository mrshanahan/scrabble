def setup(num_words=2):
	import scrabble as s
	words = [[('w',(0,0)),('o',(1,0)),('r',(2,0)),('d',(3,0)),('s',(4,0))],
		 [('o',(3,1)),('o',(3,2)),('r',(3,3))],
		 [('a',(4,3)),('t',(5,3)),('s',(6,3))],
		 [('r',(4,2)),('p',(4,4))]]
	b = s.Board()
	for i in range(num_words):
		b.place_word(words[i])
	return (b, words[:num_words])
