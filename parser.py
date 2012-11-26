import os

queries = {}
ratings = {}
users = {}

dotpCache = {}

def parseData():
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
					ratings[movId] = []
				else:
					rating_parts = line.split(',')
					user = int(rating_parts[0])
					rating = int(rating_parts[1])
					ratings[movId].append((user, rating))

					if user not in users:
						users[user] = []

					users[user].append((movId, rating))

def makeSymmetric(fn):
	def wrapped(a, b):
		if b < a:
			return fn(b, a)
		return fn(a, b)
	return wrapped

@makeSymmetric
def simUser(a, b):
	pass

@makeSymmetric
def simMov(a, b):
	pass

@makeSymmetric
def dotp(a, b):
	cacheKey = (tuple(a), tuple(b))
	if tupKey in dotpCache:
		return dotpCache[cacheKey]
	return sum([a[i] * b[i] for ])


def main():
	#parseData()

if __name__ == '__main__':
	main()