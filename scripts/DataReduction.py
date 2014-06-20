import numpy, codecs, itertools, math
import simplejson as json
import sys
from datetime import *
from clustering import Clustering
from metrics import completeness, homogeneity

time_threshold = sys.argv[1]
fileID = sys.argv[2]
fileREF = sys.argv[3]
fileOUT = sys.argv[4]

# python DataReduction.py 3600 ../Dev_dataset/SED_2014_Dev_A_Pictures.txt ../Dev_dataset/SED_2014_Dev_A_Ref_task1.txt results_Dev_A_1h.txt

def readjson(jsonFile):
	dictionary=None
	with codecs.open(jsonFile, "rt", encoding="utf8") as fic:
		data = [json.loads(line) for line in fic]
		dictionary = {obj['photoID']: obj for obj in data}
	return dictionary

def clusterUser(dictionary, listID):
	with codecs.open(listID, "rt", encoding='utf8') as fic:
		imgs = [int(line.strip()) for line in fic]

	cluster = {}
	cluster_id = {}
	clusterId = 0

	matrix = numpy.eye(len(imgs), dtype=int)
	for i in range (0, len(imgs)):
		img_i = imgs[i]
		userI = dictionary[img_i]['username']
		if userI not in cluster_id:
			cluster_id[userI] = clusterId
			clusterId = clusterId+1
		cluster[img_i] = cluster_id[userI]

	new_cluster = {}
	for k, v in cluster.iteritems():
		new_cluster.setdefault(v, []).append(k)

	return new_cluster

def clusterDate(dictionary, listID, clusterU):
	with codecs.open(listID, "rt", encoding='utf8') as fic:
		imgs = [int(line.strip()) for line in fic]

	cluster = {}
	date = {}

	matrix = numpy.eye(len(imgs), dtype=int)
	for i in range (0, len(imgs)):
		img_i = imgs[i]
		dateI = datetime.strptime(dictionary[img_i]['dateTaken'], "%Y-%m-%d %H:%M:%S")
		date[img_i] = dateI

	clusterId = 0
	

	for c in clusterU.values():
		noyau = {}
		cluster_prov = {}
		noyau[clusterId] = date[c[0]]
		cluster_prov[c[0]] = clusterId
		for i in range (1, len(c)):
			img = c[i]
			dateI = date[img]
			min = 100000000000000000
			k = -1

			for k, d in noyau.iteritems():
				diff = d-dateI
				diff_seconds = abs(diff.total_seconds())
				if min > diff_seconds:
					min = diff_seconds
					indice = k
			if min < int(time_threshold): #10800
				mean = noyau[indice] + timedelta(seconds=(min / 2))
				noyau[indice] = mean
				cluster_prov[c[i]] = indice
			else:
			    clusterId = clusterId + 1
			    noyau[clusterId] = dateI
			    cluster_prov[c[i]] = clusterId
		for k, v in cluster_prov.iteritems():
			cluster.setdefault(v, []).append(k)

	return cluster

def print_result_file(cluster, filename):
	file = open(filename, "w")

	for k, v in cluster.iteritems():
		for photo in v:
			file.write("%d\t%d\n" % (photo, k))

	file.close()

print "Loading json into memory..."
dictionary = readjson("/vol/corpora4/mediaeval/2014/SED_2014_Dev_Metadata.json")
print "...Done !"

clusterU = clusterUser(dictionary, fileID)
clusterD = clusterDate(dictionary, fileID, clusterU)

print_result_file(clusterD, fileOUT)

reference = Clustering.load(fileREF)
hypothesis = Clustering.load(fileOUT)

images = []
for c in clusterD.values():
	for i in range (0, len(c)):
		images.append(c[i])

h = homogeneity(reference, hypothesis, images)
print h
c = completeness(reference, hypothesis, images)
print c

