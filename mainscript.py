from __future__ import division
import heapq
import math
import os
import sys

# Caches
dotpCache = {}
magCache = {}

def parseData():
	queries = {}
	movies = {}
	users = {}

	with open("queries.txt") as qfile:
		for line in qfile:
			line = line.strip()
			if line[-1] == ':':
				movId = int(line[:-1])
				queries[movId] = []
			else:
				queries[movId].append(int(line))



	path = 'data/training_set/'
	listing = os.listdir(path)
	for infile in listing:
		with open(path + infile) as mvfile:
			for line in mvfile:
				line = line.strip()
				if line[-1] == ':':
					movId = int(line[:-1])
					movies[movId] = {}
				else:
					rating_parts = line.split(',')
					user = int(rating_parts[0])
					rating = int(rating_parts[1])
					movies[movId][user] = rating

					if user not in users:
						users[user] = {}

					users[user][movId] = rating

	return (queries, movies, users)

def makeSymmetric(fn):
	def wrapped(a, b):
		if b < a:
			return fn(b, a)
		return fn(a, b)
	return wrapped

@makeSymmetric
def cosSim(a, b):
	dotp(a, b) / (mag(a) * mag(b))

@makeSymmetric
def dotp(a, b):
	cacheKey = (tuple(a), tuple(b))
	if cacheKey in dotpCache:
		return dotpCache[cacheKey]
	score = sum([a[key] * b[key] for key in set.intersection(set(a.keys()), set(b.keys()))])
	dotpCache[cacheKey] = score
	return score

def mag(a):
	cacheKey = tuple(a)
	if cacheKey in magCache:
		return magCache[cacheKey]

	out = math.sqrt(sum([a[key] ** 2 for key in a.keys()]))
	magCache[cacheKey] = out
	return out

def getNeighbors(cent, sim, k):
	simScores = {}
	centId = cent['id']
	otherId = cent['other']
	idPos = cent['idPos']
	otherPos = cent['otherPos']
	dataset = cent['dataset']

	for (nid, rating) in dataset.items():
		simScores[nid] = sim(dataset[centId], rating)

	neighborKeys = heapq.nlargest(k, simScores, key=lambda x: simScores[x])
	#print [dataset[nid] for nid in neighborKeys]
	return [(n[0], n[1], n[2]) for n in [{idPos: nid, otherPos: otherId, 2: dataset[nid][otherId] if otherId in dataset[nid] else 0} for nid in neighborKeys]]


def kNN(movId, userId, movies, users):
	k = 10
	sim = cosSim
	userCent = {'id': userId,
			'other': movId,
			'idPos': 1,
			'otherPos': 0,
			'dataset': users
			}
	movieCent = {'id': movId,
			'other': userId,
			'idPos': 0,
			'otherPos': 1,
			'dataset': movies
			}

	cent = userCent
	#cent = movieCent
	neighbors = getNeighbors(cent, sim, k)

	print neighbors


def main(parsedData):
	(queries, movies, users) = parsedData

	for (movId, userId) in queries.items():
		kNN(movId, userId[0], movies, users)
		break

if __name__ == '__main__':
	main()