from __future__ import division
from collections import defaultdict
import heapq
import math
import os
import sys
import time
import pickle


# Caches
dotpCache = {}
magCache = {}


dotphit = 0
dotpmiss = 0

################
# Data Parsing #
################

def parseData():
	queries = []
	movies = {}
	users = {}

	with open("queries-small.txt") as qfile:
		for line in qfile:
			line = line.strip()
			if line[-1] == ':':
				movId = int(line[:-1])
			else:
				queries.append((movId, int(line)))



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

	#movies = normalize(movies, 17770)
	users = normalize(users, 17770)

	return (queries, movies, users)

##############
# Decorators #
##############

def makeSymmetric(fn):
	def wrapped(a, b):
		if b < a:
			return fn(b, a)
		return fn(a, b)
	return wrapped

def timeIt(fn):
	def wrapped(data):
		start = time.time()
		out = fn(data)
		end = time.time()
		print "Runtime: %d sec" % (end - start)
		return out
	return wrapped

##################
# Vector Helpers #
##################

@makeSymmetric
def cosSim(a, b):
	return dotp(a, b) / (mag(a) * mag(b))

def getIntersection(a, b):
	return [key for key in a if key in b]

def dotp(a, b):
	# Don't cache because it actually slows down.
	# Not emptying cache causes Memory Error.
	# Emptying cache on each iteration causes only 0.02
	# cache hit rate.
	score = sum([a[key] * b[key] for key in getIntersection(a, b)])
	return score

def mag(a):
	# Cache this because it is very small.
	cacheKey = tuple(a)
	if cacheKey in magCache:
		return magCache[cacheKey]
	out = math.sqrt(sum([a[key] ** 2 for key in a]))
	magCache[cacheKey] = out
	return out

def normalize(data, n):
	for vect in data:
		xbar = (1 / n) * sum([data[vect][key] for key in data[vect]])
		default = -1 * xbar
		xpmag = math.sqrt(sum([(data[vect].get(key, 0) - xbar) ** 2 for key in xrange(1, n+1)]))
		xp = [(data[vect][key] - xbar) for key in data[vect]]

		for key in data[vect]:
			data[vect][key] = (data[vect][key] - xbar) / xpmag

		data[vect] = defaultdict(lambda: default, data[vect])

	return data

###############
# kNN Helpers #
###############

def getNeighbors(cent, sim, k):
	simScores = {}
	centId = cent['id']
	otherId = cent['other']
	idPos = cent['idPos']
	otherPos = cent['otherPos']
	dataset = cent['dataset']

	for (nid, rating) in dataset.items():
		simScores[nid] = sim(dataset[centId], rating)
	neighborKeys = heapq.nlargest(k, dict((key, val) for (key, val) in simScores.items() if otherId in dataset[key]), key=lambda nid: simScores[nid])

	out = [(n[0], n[1], n[2]) for n in [{idPos: nid, otherPos: otherId, 2: dataset[nid][otherId] if otherId in dataset[nid] else 0} for nid in neighborKeys]]

	return out

def getPrediction(neighbors):
	return sum([n[2] for n in neighbors]) / len(neighbors)

def kNN(cent):
	k = 10
	sim = cosSim

	neighbors = getNeighbors(cent, sim, k)

	return getPrediction(neighbors)

########
# main #
########

@timeIt
def main(parsedData):
	(queries, movies, users) = parsedData

	print sum([users[1234576][k] for k in xrange(1, 17771)])
	return

	with file("output.txt", "w") as fout:
		prevMovId = -1
		currMovId = -1

		count = 0
		for (movId, userId) in queries:
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
			prediction = kNN(userCent)

			#print "M: %d, U: %d, R: %f" % (movId, userId, prediction)

			currMovId = movId
			if prevMovId != currMovId:
				# New Movie
				fout.write("%d:\n" % currMovId)
				print "M: %d" % currMovId
				count += 1
			fout.write("%f\n" % prediction)
			prevMovId = currMovId

			#if count > 6:
			#	break


if __name__ == '__main__':
	main(parseData())