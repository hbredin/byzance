import numpy, codecs, itertools, math
import simplejson as json
from datetime import *


def computeUserMatrix(dictionary, listID):
	with codecs.open(listID, "rt", encoding='utf8') as fic:
		imgs = [int(line.strip()) for line in fic]

	matrix = numpy.eye(len(imgs), dtype=int)
	for (i, img_i), (j, img_j) in itertools.combinations(enumerate(imgs), 2):
		if img_i in dictionary and img_j in dictionary:
			userI = dictionary[img_i]['username']
			userJ = dictionary[img_j]['username']
			if userI == userJ:
				matrix[i][j]=1
				matrix[j][i]=1
		else:
			print "Unable to found image %d in json file" % (img_i)
			return None
	print matrix
	return matrix

def computeDateTakenMatrix(dictionary, listID):
	with codecs.open(listID, "rt", encoding='utf8') as fic:
		imgs = [int(line.strip()) for line in fic]

	matrix = numpy.zeros((len(imgs), len(imgs)))
	for (i, img_i), (j, img_j) in itertools.combinations(enumerate(imgs), 2):
		if img_i in dictionary and img_j in dictionary:
			dateI = datetime.strptime(dictionary[img_i]['dateTaken'], "%Y-%m-%d %H:%M:%S")
			dateJ = datetime.strptime(dictionary[img_j]['dateTaken'], "%Y-%m-%d %H:%M:%S")
			diff = dateJ-dateI
			diff_seconds = abs(diff.total_seconds())
			matrix[i][j]=diff_seconds
			matrix[j][i]=diff_seconds
		else:
			print "Unable to found image %d in json file" % (img_i)
			return None
	print matrix
	return matrix

def computeDistanceMatrix(dictionary, listID):
	with codecs.open(listID, "rt", encoding='utf8') as fic:
		imgs = [int(line.strip()) for line in fic]

	matrix = numpy.zeros((len(imgs), len(imgs)))
	for (i, img_i), (j, img_j) in itertools.combinations(enumerate(imgs), 2):
		if img_i in dictionary and img_j in dictionary:
			obj_i = dictionary[img_i]
			obj_j = dictionary[img_j]
			if not 'longitude' in obj_i or not 'longitude' in obj_j:
				matrix[i][j] = None
				matrix[j][i] = None
				if not 'longitude' in obj_i:
					matrix[i][i] = None
			else:
				distance = distance_on_unit_sphere(obj_i['latitude'], obj_i['longitude'], obj_j['latitude'], obj_j['longitude'])
				matrix[i][j] = distance
				matrix[j][i] = distance
		else:
			print "Unable to found image %d in json file" % (img_i)
			return None
	print matrix
	return matrix

def distance_on_unit_sphere(lat1, long1, lat2, long2):
   # Convert latitude and longitude to 
   # spherical coordinates in radians.
   degrees_to_radians = math.pi/180.0
   # phi = 90 - latitude
   phi1 = (90.0 - lat1)*degrees_to_radians
   phi2 = (90.0 - lat2)*degrees_to_radians
   # theta = longitude
   theta1 = long1*degrees_to_radians
   theta2 = long2*degrees_to_radians
   # Compute spherical distance from spherical coordinates.
   # For two locations in spherical coordinates 
   # (1, theta, phi) and (1, theta, phi)
   # cosine( arc length ) = 
   #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
   # distance = rho * arc length
   cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
          math.cos(phi1)*math.cos(phi2))
   arc = math.acos( cos )
   # Remember to multiply arc by the radius of the earth 
   # in your favorite set of units to get length.
   return arc * 6371

def readjson(jsonFile):
	dictionary=None
	with codecs.open(jsonFile, "rt", encoding="utf8") as fic:
		data = [json.loads(line) for line in fic]
		dictionary = {obj['photoID']: obj for obj in data}
	return dictionary

print "Loading json into memory..."
dictionary = readjson("/vol/corpora4/mediaeval/2014/SED_2014_Dev_Metadata.json")
print "...Done !"
computeUserMatrix(dictionary, "lst")
computeDateTakenMatrix(dictionary, "lst")
computeDistanceMatrix(dictionary, "lst")
