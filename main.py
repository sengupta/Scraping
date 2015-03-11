from __future__ import division
from sys import platform as _imp 
import os
import string
import glob
import math
import fnmatch
import collections
def genre_wordcount(movrev):
    i = 0
    wordcount = {}
    n= len(movrev)
    for i in range(0,n) :  # Looping over a set of reviews of given genre
        file = open(movrev[i], "r+")
        for word in file.read().split():
            exclude = set(string.punctuation)
            word = ''.join(ch for ch in word if ch not in exclude).lower() # Removing the puntuation marks in all the words
            if len(word) > 2:  # considering worda of length greater than 2
                if word not in wordcount: # Checking if it has previous occured
                    wordcount[word] = 1
                else:
                    wordcount[word] += 1
        file.close();
    return (wordcount)
def get_responses():
    dirs = next(os.walk('reviews/'))[1]  # Checking all the Directories in the given folder
    icount = {}  # Word count based on genre
    print 'Extracting Data for Training'
    cal = {}
    sumr = 0
    for dir in dirs:
        path = 'reviews/' + dir
        movrev = glob.glob(path + "/*.txt")
        n = int(round(len(movrev)*0.6,0))
        cal[dir] = n # Number of reviews considered for Training
        sumr = sumr + n # Counting Total Number of Training reviews
        icount[dir] = genre_wordcount(movrev[0:n])
    return icount,sumr,cal
def sim_word(movrev): # Function for word count of individual moviews
    wordcount = {}
    file = open(movrev, "r+")
    for word in file.read().split():
        exclude = set(string.punctuation)
        word = ''.join(ch for ch in word if ch not in exclude).lower()
        if len(word) > 2:
            if word not in wordcount:
                wordcount[word] = 1
            else:
                wordcount[word] += 1
    file.close();
    return (wordcount)
def testing():
    dirs = next(os.walk('reviews/'))[1]
    print 'Extracting Data for Testing'
    tcount = {}
    tmovies = {}
    twcount = {}
    for dir in dirs:
        path = 'reviews/' + dir
        tfiles = glob.glob(path + "/*.txt")
        n = int(round(len(tfiles)*0.6,0)) + 1
        if n < len(tfiles):
            for i in range( n, len(tfiles)-1 ): # Taking the remaining reviews for Testing
                if _imp == "win32" :
                    tefiles = tfiles[i].split("\\")[1].split('.')[0] # Extracting the movie name
                else:
                    tefiles = tfiles[i].split("/")[2].split('.')[0]
                twcount[tefiles] = sim_word(tfiles[i])
    return twcount
# TRAINING MODEL
output = get_responses()
iwcount = output[0]   # Genre based word-count
ntotal = output[1]    # Total Reviews considered for training
nind = output[2]      # Number of movie reviews taken in training from each genre
twcount = {}                    # Word count of words in all documents
iwprob = {}                     # Word probability in a specific genre review
twprob = {}                     # Word probability in all the documents
itotal = {}                     # Total number of words in specific genre
wtotal = 0                      # Total number of words in all documents
print 'Calculating various Probabilities'
for u in iwcount.keys():
    itotal[u] = 0
    for k in iwcount[u]:
        itotal[u] = itotal[u] + iwcount[u][k]
        wtotal = wtotal + iwcount[u][k]
        if k not in twcount:
            twcount[k] = iwcount[u][k]    # Calculating total word count
        else:
            twcount[k] += iwcount[u][k]
for k in twcount.keys():
    twprob[k] = twcount[k] / wtotal        # Calculating the probability of occurence of a word in a review
for k in nind.keys():
    nind[k] = nind[k] / ntotal             # Calculating the probability of review belonging to specific Genre
for u in iwcount.keys():
    for k in iwcount[u]:
        iwcount[u][k] = iwcount[u][k] / itotal[u]   # Calculating the probability of a word for a given genre
#TESTING THE MODEL
results = testing()  # Calculating the word count of reviews selected for testing
prob = {}  # Calculating the probability for various genres for a given document based on words
print 'Calculating probabilities of given review corresponding to various genres'
for i in results.keys():
    dirs = next(os.walk('reviews/'))[1]
    temp = {}
    for j in dirs:
        temp [j] = 0
        for k in results[i]:
            if k in iwcount[j] and k in twcount:
                temp[j] = math.log(( iwcount[j][k] * nind[j]  ) / twprob[k] ) + temp[j]
            else:
                temp[j] = math.log(0.25/ 0.95) + temp[j]  # Case if the word occurs first time in a specific review
    prob[i] = temp
org_genre = {}   # Actual genre of the movie
for i in prob.keys():
    matches = {}
    lookfor = i + '.txt'
    j = 0
    for root, dirnames, filenames in os.walk('reviews/'):
        for filename in fnmatch.filter(filenames, lookfor): # Looking for occurence of a movie in various genres
            matches[j] =  root.split("/")[1]
            j = j + 1
    temp = ''
    for key in matches.keys():
            temp =  matches[key] + ',' + temp #  Concantenating the various genres a specific movie fall in
    org_genre[i] = temp
genre = {}
for key in prob.keys():
    od = prob[key].items()
    temp = {}
    sort = sorted(od, key=lambda tup: tup[1])  # Sorting the probability of movies for a specific genre based on probability values
    temp = [sort[i] for i in range(len(sort)-10,len(sort)-1)]   # Decreasing order is chosen
    temp = reversed(temp)
    genre[key] = ''
    for x in temp:
        genre[key] = x[0] + ',' + genre[key]  #  Concantenating the genre with high probability for specific movie
rate = {}
rate_2 = {}
predrate = 0
predrate2 = 0
for key in prob.keys():
    exp_gen = genre[key].split(',')
    pred = {}
    avgrate = 0
    avg_pred = {}
    for i in range(0,len(exp_gen)-1):
        if exp_gen[i] in org_genre[key]: # Checking if the predicted genre is one of the origial genre
            pred[i] = 'true'
        else :
            pred[i] = 'false'
    tot = len(org_genre[key].split(',')) - 1 # Last value is  empty
    rate[key] = 0          #Initiating the Prediction rate
    rate_2[key] = 0
    for i in range(0,len(pred)-1):
        if pred[i]  =='true' and i < tot:     # Condition if the original genre occures in the first based on the number of genres a   movies falls into
            rate[key] = rate[key] + 100
            rate_2[key] = rate_2[key] + 100
        if pred[i] == 'true' and i > tot:
            rate[key] = rate[key] + 100 - 5*(i-tot) ;# Condition if the original genre occurs in any place in predicted genres.Prediction Rate depletes with the position of original genre in predicted genre
            rate_2[key] = rate_2[key] + 100               # Rate 2 is a function with constant scoring system
    rate[key] = rate[key] / tot
    rate_2 [key] = rate_2[key] / tot
    predrate2 = predrate2 + rate_2[key]
    predrate = predrate + rate[key]
predrate = predrate / len(prob.keys())
predrate2 = predrate2 / len(prob.keys())
print predrate ,predrate2
