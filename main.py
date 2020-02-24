import twitter
import settings

twitter_api = twitter.Api(consumer_key=settings.CONSUMER_KEY,
                          consumer_secret=settings.CONSUMER_SECRET,
                          access_token_key=settings.ACCESS_TOKEN_KEY,
                          access_token_secret=settings.ACCESS_TOKEN_SECRET)

print(twitter_api.VerifyCredentials())


def buildTestSet(search_keyword):
    try:
        tweets_Fetched = twitter_api.GetSearch(search_keyword, count=100)
        print("Fetched " + str(len(tweets_Fetched)) + " tweets for the term" + search_keyword)

        return [{"text": status.text, "label": None} for status in tweets_Fetched]
    except:
        print("Unfortunately, something went wrong")
        return None

# ------------------------------------------------------------------------

search_term = input("search keyword:")
testDataSet = buildTestSet(search_term)

print(testDataSet[0:4])

# ------------------------------------------------------------------------

def buildTrainingSet(corpusFile, tweetDataFile):
    import csv
    import time

    corpus = []

    with open(corpusFile, 'rt') as csvfile:
        lineReader = csv.reader(csvfile, delimiter=',', quotechar="\"")
        for row in lineReader:
            corpus.append({"tweet_id": row[2], "label": row[1], "topic": row[0]})

            rate_limit = 100
            sleep_time = 900 / 180

            trainingDataSet = []

            for tweet in corpus:
                try:
                    status = twitter_api.GetStatus(tweet["tweet_id"])
                    print("tweet fetched" + status.text)
                    tweet["text"] = status.text
                    trainingDataSet.append(tweet)
                    time.sleep(sleep_time)
                except:
                    continue
                    # now we write them to the empty CSV file
    with open(tweetDataFile, 'wb') as csvfile:
        linewriter = csv.writer(csvfile, delimiter=",", quotechar="\"")
        for tweet in trainingDataSet:
            try:
                linewriter.writerow([tweet["tweet_id"], tweet["text"], tweet["label"], tweet["topic"]])
            except Exception as e:
                print(e)
    return trainingDataSet

# ------------------------------------------------------------------------

corpusFile = "./corpus.csv"
tweetDataFile = "./tweetDataFile.csv"

trainingData = buildTrainingSet(corpusFile, tweetDataFile)

# ------------------------------------------------------------------------

import re
from nltk.tokenize import word_tokenize
from string import punctuation
from nltk.corpus import stopwords


class PreProcessTweets:
    def __init__(self):
        self.stopwords = set(stopwords.words('english' + list(punctuation) + ['AT_USER', 'URL']))

    def processTweets(self, list_of_tweets):
        processedTweets = []
        for tweet in list_of_tweets:
            processedTweets.append((self.processTweets(tweet["text"])))
        return processedTweets

    def _processTweet(self, tweet):
        tweet = tweet.lower()  # normalize things out bruh!
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
        tweet = re.sub('@[^\s]+', 'AT_USER', tweet) # remove usernames
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet) # remove the # in #hashtag
        tweet = word_tokenize(tweet) # remove repeated characters (helloooooooo into hello)
        return [word for word in tweet if word not in self._stopwords]

tweetProcessor = PreProcessTweets()
preprocessedTrainingSet = tweetProcessor.processTweets(trainingData)
preprocessedTestSet = tweetProcessor.processTweets(testDataSet)

# ------------------------------------------------------------------------
#Step D.1: Building the vocabulary
import nltk

def buildVocabulary(preprocessedTrainingData):
    all_words = []

    for (words, sentiment) in preprocessedTrainingData:
        all_words.extend(words)

    wordlist = nltk.FreqDist(all_words)
    word_features = wordlist.keys()

    return word_features

# ------------------------------------------------------------------------

def extract_features(tweet):
    tweet_words = set(tweet)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in tweet_words)
    return features

# ------------------------------------------------------------------------

# Now we can extract the features and train the classifier
word_features = buildVocabulary(preprocessedTrainingSet)
trainingFeatures = nltk.classify.apply_features(extract_features, preprocessedTrainingSet)

# ------------------------------------------------------------------------
#Step D.4
NBayesClassifier = nltk.NaiveBayesClassifier.train(trainingFeatures)

# ------------------------------------------------------------------------

NBResultLabels = [NBayesClassifier.classify(extract_features(tweet[0])) for tweet in preprocessedTestSet]

# ------------------------------------------------------------------------

# get the majority vote
if NBResultLabels.count('positive') > NBResultLabels.count('negative'):
    print("Overall Positive Sentiment")
    print("Positive Sentiment Percentage = " + str(100*NBResultLabels.count('positive')/len(NBResultLabels)) + "%")
else:
    print("Overall Negative Sentiment")
    print("Negative Sentiment Percentage = " + str(100*NBResultLabels.count('negative')/len(NBResultLabels)) + "%")

