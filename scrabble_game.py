#!/usr/bin/env python
import random, scrabble
random.seed()

def distribute_tiles(b,num_players=2):
	tile_lists = []
	letters = []
	for l,f in b.letter_freq.items():
		letters.extend([l for x in range(f)])
	random.shuffle(letters)
	for i in range(num_players):
		this_list = []
		this_list.extend([letters[j+(i*7)] for j in range(7)])
		tile_lists.append(this_list)

	return (letters[num_players*7-1:], tile_lists)

if __name__ == '__main__':
	players = int(raw_input('Enter number of players: '))
	remaining_letters,tiles = distribute_tiles(scrabble.Board(),players)
	for i in range(len(tiles)):
		print 'Player {0}: {1}'.format(i+1,tiles[i])
	print '\nRemaining: {0}'.format(remaining_letters)
