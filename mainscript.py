from __future__ import division
from collections import defaultdict
import heapq
import math
import os
import sys
import time


# Cache
magCache = {}

################
# Data Parsing #
################

def parseData():
    """ Parses the queries and the training data. """
    queries = []
    movies = {}
    users = {}

    # Read queries into list to preserve order
    with open("queries-small.txt") as qfile:
        for line in qfile:
            line = line.strip()
            if line[-1] == ':':
                movId = int(line[:-1])
            else:
                queries.append((movId, int(line)))

    # Walk training set directory and reach each file.
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

                    # Store both movie and user dicts, for faster lookups
                    if user not in users:
                        users[user] = {}

                    users[user][movId] = rating

    return (queries, movies, users)

##############
# Decorators #
##############

def makeSymmetric(fn):
    """ Ensures that the arguments are always in the same order. """
    def wrapped(a, b):
        if b < a:
            return fn(b, a)
        return fn(a, b)
    return wrapped

def timeIt(fn):
    """ Times the given function and outputs runtime to stdout. """
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
    """ Performs vector cosine similarity, and returns 0 for 0-vector. """
    if mag(a) == 0 or mag(b) == 0:
        return 0
    return dotp(a, b) / (mag(a) * mag(b))

def getIntersection(a, b):
    """ Returns the list of keys that both a and b have in common. """
    return [key for key in a if key in b]

def dotp(a, b):
    """ Calculates the dot product of a vector. """
    # Don't cache because it actually slows down.
    # Not emptying cache causes Memory Error.
    # Emptying cache on each iteration causes only 0.02
    # cache hit rate.
    return sum([a[key] * b[key] for key in getIntersection(a, b)])

def mag(a):
    """ Calculates the magnitude of a vector and caches it. """
    # Cache this because it has a 100% hit rate after initial population.
    cacheKey = tuple(a)
    if cacheKey in magCache:
        return magCache[cacheKey]
    out = math.sqrt(sum([a[key] ** 2 for key in a]))
    magCache[cacheKey] = out
    return out

def normalize(data):
    """ Performs vector normalization by centering and normalizing. Does not use vector elements that are 0. """
    for vect in data:
        x = [data[vect][key] for key in data[vect]]
        # Get average of all non-zero elements
        xbar = sum(x) / len(x)

        xpmag = math.sqrt(sum([(data[vect][key] - xbar) ** 2 for key in data[vect]]))

        for key in data[vect]:
            data[vect][key] = ((data[vect][key] - xbar) / (xpmag if xpmag != 0 else 1))

    return data

###############
# kNN Helpers #
###############

def getNeighbors(cent, sim, k):
    """ Gets the k neighbors as per options passed in cent using the similarity metric sim. """
    simScores = {}
    centId = cent['id']
    otherId = cent['other']
    idPos = cent['idPos']
    otherPos = cent['otherPos']
    dataset = cent['dataset']

    # Get the similarities. 
    for (nid, rating) in dataset.items():
        simScores[nid] = sim(dataset[centId], rating)

    # Use heapq to efficiently get the k largest
    neighborKeys = heapq.nlargest(k, 
                        dict((key, val) for (key, val) in simScores.items() if otherId in dataset[key]), 
                        key=lambda nid: simScores[nid])

    # Make sure that the output is always (movie, user, rating).
    out = [(n[0], n[1], n[2]) 
                for n in 
                    [{idPos: nid, otherPos: otherId, 2: dataset[nid][otherId] if otherId in dataset[nid] else 0} 
                        for nid in neighborKeys]]

    return out

def getPrediction(neighbors):
    """ Performs an unweighted mean of the neighbors' ratings. """
    return sum([n[2] for n in neighbors]) / len(neighbors)

def kNN(cent):
    """ Performs the k-nearest neighbors algorithm with a hardcoded k and similarity function. """
    k = 10
    sim = cosSim

    neighbors = getNeighbors(cent, sim, k)

    return getPrediction(neighbors)

########
# main #
########

@timeIt
def main(parsedData, normalized=False, simMode=0):
    """ Main function. Performs kNN on the passed in parsedData. Will normalize user data if requested. 
        Uses the command line argument to determine which algorithm to run. """
    (queries, movies, users) = parsedData

    # Handle command line args, defaulting to user-user without normalization.
    if len(sys.argv) > 1:
        if sys.argv[1] == "2":
            simMode = 1
        elif sys.argv[1] == "3":
            normalized = True
        elif sys.argv[1] == "4":
            simMode = 2


    # Normalize data is requested.
    if normalized:
        users = normalize(users)

    # Movie ID trackers.
    prevMovId = -1
    currMovId = -1

    # Accumulate output to list before writing to file.
    outstr = []

    # Maintain min and max seen, to allow for denormalization if needed.
    minSeen = float("inf")
    maxSeen = float("-inf")

    for (movId, userId) in queries:
        # Config for kNN.
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

        # User requested movie-movie
        if simMode == 1:
            cent = movieCent

        # Run kNN.
        prediction = kNN(cent)

        # User requested custom algo. Run kNN on other data set and average the results.
        if simMode == 2:
            pred2 = kNN(movieCent)
            prediction = (prediction + pred2) / 2

        currMovId = movId
        if prevMovId != currMovId:
            # New Movie
            outstr.append("%d:" % currMovId)
            print "Movie: %d" % currMovId

        outstr.append(prediction)   

        # Track min and max predictions.
        if prediction < minSeen:
            minSeen = prediction
        if prediction > maxSeen:
            maxSeen = prediction

        prevMovId = currMovId

    # Write output to file and denormalize data if needed.
    with file("output.txt", "w") as fout:
        for li in outstr:
            if type(li) is str:
                fout.write("%s\n" % li)
            else:
                unnorm = 1 + (4 / (maxSeen - minSeen)) * (li - minSeen) if normalized else li
                fout.write("%f\n" % unnorm)


if __name__ == '__main__':
    main(parseData())