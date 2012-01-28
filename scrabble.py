# scrabble.py
# Author: Matt Shanahan
# Square and BoardState are instances of object, since we want to be able
# to access their attrs without other helper functions (so we can do
# b.board[n][m] instead of b.getBoard()[n][m])

import sys

scrabble_dict = map(lambda x: x.strip(), open('ScrabbleDictionary.txt').readlines())

# Makes a move, then returns score and new board state
def make_move(board, move):
	score = board.place_word(move)
	return (board, score)

# Takes a word-coord alist and returns the word, correctly ordered
def extract_word(word, join=False):
	init_letter,init_coord = word[0]
	actual_word = [init_letter]
	for i in range(1,len(word)):
		this_letter,this_coord = word[i]
		if init_coord[0] < this_coord[0] or init_coord[1] < this_coord[1]:
			actual_word.append(this_letter)
		elif init_coord[0] > this_coord[0] or init_coord[1] > this_coord[1]:
			actual_word.insert(0,this_letter)
	if join:
		return ''.join(actual_word)
	return actual_word

# Just checks whether word is in the Scrabble Dictionary
def in_dict(word):
	return word in scrabble_dict

# Determines whether the given move is valid, i.e. whether it forms
# continuous lines with other words, and the additions to those words
# form words
def is_valid_move(board, move):
	new_board,tmp = make_move(board, move)
	for square in move:
		v,h = new_board.get_continuous_segments(square[1],True)
		if v and in_dict(extract_word(v,True)):
			pass	
		elif h and in_dict(extract_word(h,True)):
			pass
		elif v or h:
			return False
	return True
	
# Simple object for representing a square on the Scrabble board
class Square(object):
	def __init__(self, bonus=None, tile=None):
		self.bonus = bonus
		self.tile = tile

	def place(self, tile):
		self.tile = tile

	def is_occupied(self):
		return (self.tile != None)

# {letter: (score,freq)}
latin_set = \
{'a': (1,9), 'b': (4,2), 'c': (2,4), 'd': (2,3), 'e': (1,12), 'f': (8,1), 'g': (4,2), 
 'h': (8,1), 'i': (1,9), 'l': (2,3), 'm': (2,4), 'n': (2,4), 'o': (1,5), 'p': (4,2), 
 'q': (3,3), 'r': (1,7), 's': (1,8), 't': (1,8), 'v': (1,9), 'x': (4,2)}

class Board(object):
	# Additionally define two global functions as Board functions; thus,
	# can be called by a Board object with an implicit Board arg
	make_move = make_move
	is_valid_move = is_valid_move
	
	# Placement of bonus squares (Words with Friends version)
	default_placement = \
	{'TW': [(3,0),(11,0),(0,3),(14,3),(0,11),(14,11),(3,14),(11,14)],
	 'TL': [(6,0),(8,0),(3,3),(11,3),(5,5),(9,5),(0,6),(14,6),
		(0,8),(14,8),(5,9),(9,9),(3,11),(11,11),(6,14),(8,14)],
	 'DL': [(2,1),(12,1),(1,2),(4,2),(10,2),(13,2),(2,4),(6,4),(8,4),(12,4),(4,6),(10,6),
		(2,13),(12,13),(1,12),(4,12),(10,12),(13,12),(2,10),(6,10),(8,10),(12,10),(4,8),(10,8)],
	 'DW': [(5,1),(9,1),(7,3),(1,5),(13,5),(3,7),(11,7),(1,9),(13,9),(7,11),(5,13),(9,13)]}

	# {letter: (score,freq)}
	default_set = \
	{'a': (1,9), 'b': (3,2), 'c': (3,2), 'd': (2,4), 'e': (1,12), 'f': (4,2), 'g': (2,3), 'h': (4,2),
	 'i': (1,9), 'j': (8,1), 'k': (5,1), 'l': (1,4), 'm': (3,2), 'n': (1,6), 'o': (1,8), 'p': (3,2),
	 'q': (10,1), 'r': (1,6), 's': (1,4), 't': (1,6), 'u': (1,4), 'v': (4,2), 'w': (4,2), 'x': (8,1),
	 'y': (4,2), 'z': (10,1)}

	# Sets up board
	def set_board(self):
		board = []		
		for i in range(self.size):
			board.append([])
			for j in range(self.size):
				if (i,j) in self.bonuses:
					square = Square(bonus=self.bonuses[(i,j)])
				else:
					square = Square()
				board[i].append(square)			
		self.board = board
		return 

	clear = set_board

	# Initializes board with variable size and bonus square locations
	def __init__(self, placement=default_placement, size=15, letter_set=default_set):
		self.size = size
		ls,lf = {},{}
		ls.update(map(lambda x: (x, letter_set[x][0]), letter_set.keys()))
		lf.update(map(lambda x: (x, letter_set[x][1]), letter_set.keys()))
		self.letter_scores,self.letter_freq = ls,lf

		temp = []		
		for b,l in placement.items():
			new = map(lambda x: (x,b), l)
			temp.extend(new)
		if len(set(temp)) != len(temp):
			print 'Duplicate entries; double-check placement dict.'
			return

		self.bonuses = {}
		self.bonuses.update(temp)
		self.set_board()

	# Places a word on the board, and returns the resulting score
	def place_word(self, word): # word is an a-list of type [(letter, coord)]
		for (l,(i,j)) in word:
			b = self.board[i][j].place(l)
		return self.score(word)

	# From a single occupied square, get the words connected to the square in
	# both directions.  Returns a tuple of contiguous words (which are in
	# a-list format)
	def get_continuous_segments(self, (x,y), for_score=False):
		if not self.board[x][y].is_occupied(): return
		# vertical
		has_top = (y > 0 and self.board[x][y-1].is_occupied())
		has_bot = (y < len(self.board) and self.board[x][y+1].is_occupied())
		if not has_top and has_bot:
			vert_word = [(self.board[x][y].tile,(x,y))]
			j = y+1
			square = self.board[x][j]
			while j < len(self.board) and square.is_occupied():
				vert_word.append((self.board[x][j].tile,(x,j)))
				j += 1
				square = self.board[x][j]
		elif has_top and not has_bot:
			vert_word = [(self.board[x][y].tile,(x,y))]
			j = y-1
			square = self.board[x][j]
			while j >= 0 and square.is_occupied():
				vert_word.append((self.board[x][j].tile,(x,j)))
				j -= 1
				square = self.board[x][j]
		elif not (has_top or has_bot) and not for_score:
			vert_word = [(self.board[x][y].tile,(x,y))]
		else:
			vert_word = []

		# horizontal
		has_left = (x > 0 and self.board[x-1][y].is_occupied())
		has_right = (x < len(self.board) and self.board[x+1][y].is_occupied())
		if not has_left and has_right:
			hori_word = [(self.board[x][y].tile,(x,y))]
			i = x+1
			square = self.board[i][y]
			while i < len(self.board) and square.is_occupied():
				hori_word.append((self.board[i][y].tile,(i,y)))
				i += 1
				square = self.board[i][y]
		elif has_left and not has_right:
			hori_word = [(self.board[x][y].tile,(x,y))]
			i = x-1
			square = self.board[i][y]
			while i >= 0 and square.is_occupied():
				hori_word.append((self.board[i][y].tile,(i,y)))
				i -= 1
				square = self.board[i][y]
		elif not (has_left or has_right) and not for_score:
			hori_word = [(self.board[x][y].tile,(x,y))]
		else:
			hori_word = []

		return (vert_word, hori_word)

	# Calculates the base score of the word (w/o bonuses)
	def score_word(self, word, valid_for_bonuses=[]):
		if not word:
			return 0
		score = 0
		for (l,(i,j)) in word:
			b = self.board[i][j].bonus
			letter_mult = 1
			word_mult = 1
			if (l,(i,j)) in valid_for_bonuses:
				if b == 'DL':
					letter_mult = 2
				elif b == 'TL':
					letter_mult = 3
				elif b == 'DW':
					word_mult *= 2
				elif b == 'TW':
					word_mult *= 3
			try:
				score += self.letter_scores[l] * letter_mult
			except(KeyError): # for debugging purposes
				print 'word:  ' + word.__str__()
				print 'l:     ' + l.__str__()
				print '(i,j): ' + tuple([i,j]).__str__()
				sys.exit(1)
		return score * word_mult

	# Calculates total score of a turn (word + bonuses)
	def score(self, move, debug=False):
		total_words,total_score = [],0		
		for l,(i,j) in move:
			bonus = self.board[i][j].bonus
			for word in self.get_continuous_segments((i,j),True):
				if not word: continue
				word.sort()
				if not word in total_words: 
					total_words.append(word)
					total_score += self.score_word(word, move)
		if debug: 
			return (total_words,total_score)		
		return total_score

	# Outputs a simulated board
	def __str__(self):
		boardstr = ''
		n = len(self.board)
		separator = ' ---' * n
		for j in range(n):
			boardstr += separator + '\n'
			for i in range(n):
				bonus = self.board[i][j].bonus
				if self.board[i][j].is_occupied():
					if bonus == 'DL':
						fmt_str = '| '+'{0}'*2
					elif bonus == 'TL':
						fmt_str = '|'+'{0}'*3
					else:
						fmt_str = '| {0} '
					temp = fmt_str.format(self.board[i][j].tile) 
				elif self.board[i][j].bonus:
					temp = '| {0}'.format(self.board[i][j].bonus)
				elif (i,j) == ((n-1)/2,(n-1)/2):
					temp = '| * '
				else:
					temp = '|   '
				boardstr += temp
			boardstr += '|\n'
		return boardstr + separator

	# prints __str__
	def display(self):
		print self.__str__()
