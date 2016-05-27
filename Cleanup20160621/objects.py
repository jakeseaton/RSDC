from __future__ import division
import constants
from math import log
from decimal import *
import random

###
# Class for each Latin lemma.
# - Initialized with information from the Latin corpus
# - Contains a list of Case objects, one for each of its cases
# - Contains frequency, taken from the logged max frequency (or log 2 if frequency = 0 or 1), as well as Latin, Slavic, and Romanian genders
# - Note: Could rewrite 
###
class Lemma:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        # Modify humanness, gender, and frequency
        if self.latin_gender[-1] == "h":
            self.human = "h"
        else: 
            self.human = ""

        self.latin_gender = self.latin_gender[0]

        if self.log_max not in ["?", "1"]:
            self.freq = Decimal(self.log_max)
        else:
            self.freq = Decimal(log(2))

        # Initialize dictionary to store info for each case
        self.cases = {}

    def addCase(self, case, case_info):
        self.cases[case] = case_info


###
# Class for each case of a token
# - Initialized from the Latin corpus
# - Contains a pointer to its parent Lemma object
# - Once its syllables have been set it will manipulate them depending on the generation
#   and construct its own input tuple.
# - Will ideally implement sanity checks
###
class Case:
    def __init__(self, parent_lemma, syllables, case):
        self.parent_lemma = parent_lemma
        self.syllables = syllables
        self.case = case[0:3]
        self.num = case[3:]
        self.lemmacase = self.parent_lemma.word + ':' + self.case + self.num

        # Keep track of input and expected outputs for each generation
        self.input_change = {}      # Should have generation mapping to case, num, and syllables
        self.output_change = {}     # Should have generation mapping to gender, declension, case, and number

    def createInputTuple(self, syllables):
        self.input_tuple = tuple([syllable for word in map(constants.convertToFeatures, syllables) for syllable in word])

        # Add tuple for animacy
        self.input_tuple += constants.input_human[self.parent_lemma.latin_gender + self.parent_lemma.human]

        self.sanityCheck(self.input_tuple)

    def sanityCheck(self, input_tuple):
        if len(self.input_tuple) != constants.input_nodes:
            print "You screwed up the size of the input"
            print len(self.input_tuple), constants.input_nodes
            raise SystemExit

###
# Class to preprocess data for the neural network
# - Contains a training set ("corpus", entries appear by frequency) and a test set (unique entries)
# - Passes- words (Case instances) and their current gender, adds them to the sets in appropriate proportion.
###
class Corpus:
    def __init__(self, training_set):
        self.train = []
        self.test = []
        self.training_set = training_set

    def addByFreq(self, token, expected_output):
        ''' Adds the current token to the list training set a number of times based off frequency. '''
        
        # Make false to test with no token frequency
        token_freq = True

        if token_freq == True:
            frequency = float(token.parent_lemma.freq)
        else:
            frequency = 1

        # Multiply by non-human constants. If type frequency turned off, multiply by human constants
        if token.parent_lemma.human == "h":
            frequency *= constants.human_case_freq[token.case+token.num]
        else:
            frequency *= constants.nhuman_case_freq[token.case+token.num]

        frequency = int(frequency)

        self.test.append((token, token.input_tuple, expected_output, token.parent_lemma.latin_gender))                        
        for x in xrange(frequency):
            self.train.append((token, token.input_tuple, expected_output, token.parent_lemma.latin_gender))

    def constructTrainingSet(self):
        ''' Add each token to the actual training set in a random order to be passed to the neural net. '''
        random.shuffle(self.train)

        for token in self.train:
            (word, word.input_tuple, expected_output, word.parent_lemma.latin_gender) = token
            self.training_set.addSample(word.input_tuple, expected_output)

        return self.training_set