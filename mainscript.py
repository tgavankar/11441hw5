from __future__ import division
import heapq
import math
import os
import sys



from sys import getsizeof, stderr
from itertools import chain
from collections import deque
try:
    from reprlib import repr
except ImportError:
    pass


# Caches
dotpCache = {}
magCache = {}


dotphit = 0
dotpmiss = 0

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

	return (queries, movies, users)

def makeSymmetric(fn):
	def wrapped(a, b):
		if b < a:
			return fn(b, a)
		return fn(a, b)
	return wrapped

@makeSymmetric
def cosSim(a, b):
	return dotp(a, b) / (mag(a) * mag(b))

@makeSymmetric
def dotp(a, b):
	#global dotphit
	#global dotpmiss
	#cacheKey = (tuple(a), tuple(b))
	#if cacheKey in dotpCache:
	#	dotphit += 1
	#	return dotpCache[cacheKey]
	#dotpmiss += 1
	score = sum([a[key] * b[key] for key in set.intersection(set(a.keys()), set(b.keys()))])
	#dotpCache[cacheKey] = score
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
	neighborKeys = heapq.nlargest(k, dict((key, val) for (key, val) in simScores.items() if otherId in dataset[key]), key=lambda nid: simScores[nid])
	#print neighborKeys
	out = [(n[0], n[1], n[2]) for n in [{idPos: nid, otherPos: otherId, 2: dataset[nid][otherId] if otherId in dataset[nid] else 0} for nid in neighborKeys]]
	#print out
	return out

def getPrediction(neighbors):
	return sum([n[2] for n in neighbors]) / len(neighbors)

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

	return getPrediction(neighbors)

def main(parsedData):
	(queries, movies, users) = parsedData
	global dotpCache
	global magCache

	with file("output.txt", "w") as fout:
		prevMovId = -1
		currMovId = -1

		count = 0
		for (movId, userId) in queries:
			if count == 6:
				prediction = kNN(movId, userId, movies, users)
			else:
				prediction = 0
			print "M: %d, U: %d, R: %f" % (movId, userId, prediction)
			currMovId = movId
			if prevMovId != currMovId:
				# New Movie
				fout.write("%d:\n" % currMovId)
				count += 1
			fout.write("%f\n" % prediction)
			prevMovId = currMovId

			#dotpCache = {}

			if count > 6:
				break

	#print "dotp cache perf: %f, %f v %f" % (dotphit / (dotpmiss + dotphit), dotphit, dotpmiss)



def total_size(o, handlers={}):
    """ Returns the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: dict_handler,
                    set: iter,
                    frozenset: iter,
                   }
    all_handlers.update(handlers)     # user handlers take precedence
    seen = set()                      # track which object id's have already been seen
    default_size = getsizeof(0)       # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:       # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)


if __name__ == '__main__':
	main(parseData())