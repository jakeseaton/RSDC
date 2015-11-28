from __future__ import division
import constants
from math import log
from decimal import *
import random


###
# Class for each latin token.
# - Initialized with information from the latin corpus
# - Contains a list of Case objects, one for each of its cases
# - Contains frequency, as well as latin, slavic, and romanian genders
# - Note: Could rewrite 
###
class Token:
    def __init__(self, *args, **kwargs):
        [self.word, self.latinGender, self.maxFrequency, self.max10k, self.logMax, self.slavicGender, self.romanianGender, self.declension] = args

        self.cases = []

        self.human = False

        self.haveLatinGender = self.latinGender != "No info"
        self.haveSlavicGender = self.slavicGender != "?"
        self.haveRomanianGender = self.romanianGender != "?"

        if self.logMax not in ["?", "1"]:
            self.orig_freq = Decimal(self.logMax)
        else:
            self.orig_freq = Decimal(log(2))

    def addCase(self, case, value):
        self.cases.append((case, value))

    def isComplete(self):
        return self.haveRomanianGender and self.haveSlavicGender and self.haveLatinGender

    def almostComplete(self):
        return self.haveSlavicGender and self.haveLatinGender


###
# Class for each case of a token
# - Initialized from the latin corpus
# - Contains a pointer to its parent Token object
# - Once its syllables have been set it will manipulate them depending on the generation
#   and construct its own input tuple.
# - Will ideally implement sanity checks
###
class Case:
    def __init__(self, parentToken, syllables, case, adj):
        self.case = case[0:3]
        self.num = case[3:]
        self.adj = adj[:(len(adj)-1)]
        self.parentToken = parentToken
        self.word = parentToken.word
        self.syllables = syllables
        self.description = self.parentToken.word + ':' + self.case + self.num  # + self.adj
        self.genchange = {}

    def setSyllables(self, generation, syllables):

        #do the first change (drop final -m)
        if generation >= constants.generationToImplementMChange:
            syllables = constants.manipulateForMSoundChange(*syllables)

        # second change (ae > e:)
        if generation >= constants.generationToImplementAEChange:
            syllables = constants.manipulateForAESoundChange(*syllables)

        # third change (drop final -s)
        if generation >= constants.generationToImplementSChange:
            syllables = constants.manipulateForSSoundChange(*syllables)

        if generation >= constants.generationToImplementSecondChange:
            syllables = constants.manipulateForSecondSoundChange(*syllables)

        self.modWord = (s1 + s2 + s3 + s4 + s5 + s6).replace('-', '')

        self.inputTuple = [item for vector in map(constants.print_phons, syllables) for item in vector]

        self.inputTuple += constants.input_human[self.parentToken.latinGender]

        if constants.includeSlavic and generation >= constants.generationToIntroduceSlavic:
            self.inputTuple += constants.input_slavic[self.parentToken.slavicGender]

        self.sanityCheck(self.inputTuple, generation)

    def sanityCheck(self, inputTuple, generation):
        if constants.includeSlavic and generation >= constants.generationToIntroduceSlavic:
            if len(self.inputTuple) != constants.inputNodesSlav:
                print "You screwed up the size of the input"
                print len(self.inputTuple), inputNodesSlav
                raise SystemExit
        else:
            if len(self.inputTuple) != constants.inputNodes:
                print "You screwed up the size of the input"
                print len(self.inputTuple), inputNodes
                raise SystemExit


###
# Class to preprocess data for the neural network
# - Contains a training set ("corpus", entries appear by frequency) and a test set (unique entries)
# - Passed words (Case instances) and their current gender, adds them to the sets in appropriate proportion.
###
class Corpus:
    def __init__(self, trainingSet):
        self.train = []
        self.test = []
        self.trainingSet = trainingSet

    def constructTrainingSet(self):
        random.shuffle(self.train)

        for token in self.train:
            (word, word.inputTuple, expectedOutput, word.parentToken.latinGender, word.parentToken.romanianGender) = token
            self.trainingSet.addSample(word.inputTuple, expectedOutput)

        return self.trainingSet

    def configure(self, word, expectedOutput, generation):
        frequency = float(word.parentToken.orig_freq)

        frequency *= constants.nhuman_case_freq[word.case+word.num]

        frequency = int(frequency)

        self.test.append((word, word.inputTuple, expectedOutput, word.parentToken.latinGender, word.parentToken.romanianGender))                        

        for x in xrange(frequency):
            self.train.append((word, word.inputTuple, expectedOutput, word.parentToken.latinGender, word.parentToken.romanianGender))


###
# Class abstraction of counter variables
# - Initialized to an integer counter value
# - Ability to increment, decrement, and reset to a value
###
class Counter:
    def __init__(self, value, **kwargs):
        self.value = value
        for key, value in kwargs.iteritems:
            setattr(self, key, value)

    def increment(self):
        self.value += 1

    def decrement(self):
        self.value -= 1

    def reset(self, value):
        self.value = value

###
# Class to contain multiple counters
# - Each is an instance of the Counter class
# - Each contained counter is a property of the bag, but maintains all of its properties
# - To add a counter, add to the init function 
###

# Okay this is a LOT of counters, I'm not sure if there's a way to simplify...
class CounterBag:
    def __init__(self):
        # for counter in self.counters:
        #     setattr(self, counter, Counter(0))
        # PERMANENT counters
        self.generationCounter = Counter(1)                     # Counts what generation we are in
        self.tokensCounter = Counter(0)                         # Counts how many words there are in the corpus
        self.allinfoCounter = Counter(0)                        # Counts tokens with ALL info
        self.freqCounter = Counter(0)                           # Counts how many words have a frequency
        self.slavinfoCounter = Counter(0)                       # Counts how many words have Slavic information
        self.rominfoCounter = Counter(0)                        # Counts how many words have Romanian information
        self.Latin_M = Counter(0)                               # Counts the total number of Latin masculine nouns
        self.Latin_F = Counter(0)                               # Counts the total number of Latin feminine nouns
        self.Latin_N = Counter(0)                               # Counts the total number of Latin neuter nouns
        self.Romanian_M = Counter(0)                            # Counts the total number of Romanian masculine nouns
        self.Romanian_F = Counter(0)                            # Counts the total number of Romanian feminine nouns
        self.Romanian_N = Counter(0)                            # Counts the total number of Romanian neuter nouns
        self.Romanian_NM = Counter(0)                           # Counts neuter singulars as masculine nouns
        self.Romanian_NF = Counter(0)                           # Counts neuter plurals as feminine nouns
        self.Slavic_M = Counter(0)                              # Counts the total number of Slavic masculine nouns
        self.Slavic_F = Counter(0)                              # Counts the total number of Slavic feminine nouns
        self.Slavic_N = Counter(0)                              # Counts the total number of Slavic neuter nouns
        
        # Gender of nouns split by number
        self.MSG = Counter(0)                            # Counts how many singular forms are masculine in Latin
        self.FSG = Counter(0)                            # Counts how many singular forms are feminine in Latin
        self.NSG = Counter(0)                            # Counts how many singular forms are neuter in Latin
        self.MPL = Counter(0)                            # Counts how many plural forms are masculine in Latin
        self.FPL = Counter(0)                            # Counts how many plural forms are feminine in Latin
        self.NPL = Counter(0)                            # Counts how many plural forms are neuter in Latin
        
        # Masculine nouns by case
        self.MSGNOM = Counter(0)                         # Counts how many singular nominative forms are masculine in Latin
        self.MSGACC = Counter(0)                         # Counts how many singular accusative forms are masculine in Latin
        self.MSGGEN = Counter(0)                         # Counts how many singular genitive forms are masculine in Latin
        self.MPLNOM = Counter(0)                         # Counts how many plural nominative forms are masculine in Latin
        self.MPLACC = Counter(0)                         # Counts how many plural accusative forms are masculine in Latin
        self.MPLGEN = Counter(0)                         # Counts how many plural genitive forms are masculine in Latin
        
        # Feminine nouns by case
        self.FSGNOM = Counter(0)                         # Counts how many singular nominative forms are feminine in Latin
        self.FSGACC = Counter(0)                         # Counts how many singular accusative forms are feminine in Latin
        self.FSGGEN = Counter(0)                         # Counts how many singular genitive forms are feminine in Latin
        self.FPLNOM = Counter(0)                         # Counts how many plural nominative forms are feminine in Latin
        self.FPLACC = Counter(0)                         # Counts how many plural accusative forms are feminine in Latin
        self.FPLGEN = Counter(0)                         # Counts how many plural genitive forms are feminine in Latin

        # Neuter nouns by case
        self.NSGNOM = Counter(0)                         # Counts how many singular nominative forms are neuter in Latin
        self.NSGACC = Counter(0)                         # Counts how many singular accusative forms are neuter in Latin
        self.NSGGEN = Counter(0)                         # Counts how many singular genitive forms are neuter in Latin
        self.NPLNOM = Counter(0)                         # Counts how many plural nominative forms are neuter in Latin
        self.NPLACC = Counter(0)                         # Counts how many plural accusative forms are neuter in Latin
        self.NPLGEN = Counter(0)                         # Counts how many plural genitive forms are neuter in Latin
        
        # TEMPORARY Counters to be reset
        self.totalCounter = Counter(0)                   # Counts how many total tokens there are in the test set
        self.correctLatin = Counter(0)                   # Counts the number of tokens that match the Latin gender
        self.correctPrev = Counter(0)                    # Counts the number of tokens that match the gender in the previous generation
        self.correctRomanian = Counter(0)                # Counts the number of tokens that match the Romanian gender
        self.correctSplitRom = Counter(0)                # Counts the number of tokens that match the Romanian gender (splitting neuters)

        # Without regard to case
        self.M = Counter(0)                              # Counts how many m nouns there are in the current generation
        self.F = Counter(0)                              # Counts how many f nouns there are in the current generation
        self.N = Counter(0)                              # Counts how many n nouns there are in the current generation
        self.MtoM = Counter(0)                           # Counts how many Latin m nouns remained masculine
        self.MtoF = Counter(0)                           # Counts how many Latin m nouns became feminine
        self.MtoN = Counter(0)                           # Counts how many Latin m nouns became neuter
        self.FtoM = Counter(0)                           # Counts how many Latin m nouns became masculine
        self.FtoF = Counter(0)                           # Counts how many Latin m nouns remained feminine
        self.FtoN = Counter(0)                           # Counts how many Latin m nouns became neuter
        self.NtoM = Counter(0)                           # Counts how many Latin m nouns became masculine
        self.NtoF = Counter(0)                           # Counts how many Latin m nouns became feminine
        self.NtoN = Counter(0)                           # Counts how many Latin m nouns became neuter
        # SGNOM
        self.SGNOM_MtoM = Counter(0)                     # Counts how many singular nominative Latin m nouns remained masculine
        self.SGNOM_MtoF = Counter(0)                     # Counts how many singular nominative Latin m nouns became feminine
        self.SGNOM_MtoN = Counter(0)                     # Counts how many singular nominative Latin m nouns became neuter
        self.SGNOM_FtoM = Counter(0)                     # Counts how many singular nominative Latin m nouns became masculine
        self.SGNOM_FtoF = Counter(0)                     # Counts how many singular nominative Latin m nouns remained feminine
        self.SGNOM_FtoN = Counter(0)                     # Counts how many singular nominative Latin m nouns became neuter
        self.SGNOM_NtoM = Counter(0)                     # Counts how many singular nominative Latin m nouns became masculine
        self.SGNOM_NtoF = Counter(0)                     # Counts how many singular nominative Latin m nouns became feminine
        self.SGNOM_NtoN = Counter(0)                     # Counts how many singular nominative Latin m nouns became neuter
        # SGACC
        self.SGACC_MtoM = Counter(0)                     # Counts how many singular accusative Latin m nouns remained masculine
        self.SGACC_MtoF = Counter(0)                     # Counts how many singular accusative Latin m nouns became feminine
        self.SGACC_MtoN = Counter(0)                     # Counts how many singular accusative Latin m nouns became neuter
        self.SGACC_FtoM = Counter(0)                     # Counts how many singular accusative Latin m nouns became masculine
        self.SGACC_FtoF = Counter(0)                     # Counts how many singular accusative Latin m nouns remained feminine
        self.SGACC_FtoN = Counter(0)                     # Counts how many singular accusative Latin m nouns became neuter
        self.SGACC_NtoM = Counter(0)                     # Counts how many singular accusative Latin m nouns became masculine
        self.SGACC_NtoF = Counter(0)                     # Counts how many singular accusative Latin m nouns became feminine
        self.SGACC_NtoN = Counter(0)                     # Counts how many singular accusative Latin m nouns became neuter
        # SGGEN
        self.SGGEN_MtoM = Counter(0)                     # Counts how many singular genitive Latin m nouns remained masculine
        self.SGGEN_MtoF = Counter(0)                     # Counts how many singular genitive Latin m nouns became feminine
        self.SGGEN_MtoN = Counter(0)                     # Counts how many singular genitive Latin m nouns became neuter
        self.SGGEN_FtoM = Counter(0)                     # Counts how many singular genitive Latin m nouns became masculine
        self.SGGEN_FtoF = Counter(0)                     # Counts how many singular genitive Latin m nouns remained feminine
        self.SGGEN_FtoN = Counter(0)                     # Counts how many singular genitive Latin m nouns became neuter
        self.SGGEN_NtoM = Counter(0)                     # Counts how many singular genitive Latin m nouns became masculine
        self.SGGEN_NtoF = Counter(0)                     # Counts how many singular genitive Latin m nouns became feminine
        self.SGGEN_NtoN = Counter(0)                     # Counts how many singular genitive Latin m nouns became neuter
        # PLNOM
        self.PLNOM_MtoM = Counter(0)                     # Counts how many plural nominative Latin m nouns remained masculine
        self.PLNOM_MtoF = Counter(0)                     # Counts how many plural nominative Latin m nouns became feminine
        self.PLNOM_MtoN = Counter(0)                     # Counts how many plural nominative Latin m nouns became neuter
        self.PLNOM_FtoM = Counter(0)                     # Counts how many plural nominative Latin m nouns became masculine
        self.PLNOM_FtoF = Counter(0)                     # Counts how many plural nominative Latin m nouns remained feminine
        self.PLNOM_FtoN = Counter(0)                     # Counts how many plural nominative Latin m nouns became neuter
        self.PLNOM_NtoM = Counter(0)                     # Counts how many plural nominative Latin m nouns became masculine
        self.PLNOM_NtoF = Counter(0)                     # Counts how many plural nominative Latin m nouns became feminine
        self.PLNOM_NtoN = Counter(0)                     # Counts how many plural nominative Latin m nouns became neuter
        # PLACC
        self.PLACC_MtoM = Counter(0)                     # Counts how many plural accusative Latin m nouns remained masculine
        self.PLACC_MtoF = Counter(0)                     # Counts how many plural accusative Latin m nouns became feminine
        self.PLACC_MtoN = Counter(0)                     # Counts how many plural accusative Latin m nouns became neuter
        self.PLACC_FtoM = Counter(0)                     # Counts how many plural accusative Latin m nouns became masculine
        self.PLACC_FtoF = Counter(0)                     # Counts how many plural accusative Latin m nouns remained feminine
        self.PLACC_FtoN = Counter(0)                     # Counts how many plural accusative Latin m nouns became neuter
        self.PLACC_NtoM = Counter(0)                     # Counts how many plural accusative Latin m nouns became masculine
        self.PLACC_NtoF = Counter(0)                     # Counts how many plural accusative Latin m nouns became feminine
        self.PLACC_NtoN = Counter(0)                     # Counts how many plural accusative Latin m nouns became neuter
                # PLGEN
        self.PLGEN_MtoM = Counter(0)                     # Counts how many plural genitive Latin m nouns remained masculine
        self.PLGEN_MtoF = Counter(0)                     # Counts how many plural genitive Latin m nouns became feminine
        self.PLGEN_MtoN = Counter(0)                     # Counts how many plural genitive Latin m nouns became neuter
        self.PLGEN_FtoM = Counter(0)                     # Counts how many plural genitive Latin m nouns became masculine
        self.PLGEN_FtoF = Counter(0)                     # Counts how many plural genitive Latin m nouns remained feminine
        self.PLGEN_FtoN = Counter(0)                     # Counts how many plural genitive Latin m nouns became neuter
        self.PLGEN_NtoM = Counter(0)                     # Counts how many plural genitive Latin m nouns became masculine
        self.PLGEN_NtoF = Counter(0)                     # Counts how many plural genitive Latin m nouns became feminine
        self.PLGEN_NtoN = Counter(0)                     # Counts how many plural genitive Latin m nouns became neuter
        # Change by singular
        self.SG_MtoM = Counter(0)                        # Counts how many singular Latin m nouns remained masculine
        self.SG_MtoF = Counter(0)                        # Counts how many singular Latin m nouns became feminine
        self.SG_MtoN = Counter(0)                        # Counts how many singular Latin m nouns became neuter
        self.SG_FtoM = Counter(0)                        # Counts how many singular Latin m nouns became masculine
        self.SG_FtoF = Counter(0)                        # Counts how many singular Latin m nouns remained feminine
        self.SG_FtoN = Counter(0)                        # Counts how many singular Latin m nouns became neuter
        self.SG_NtoM = Counter(0)                        # Counts how many singular Latin m nouns became masculine
        self.SG_NtoF = Counter(0)                        # Counts how many singular Latin m nouns became feminine
        self.SG_NtoN = Counter(0)                        # Counts how many singular Latin m nouns remained neuter
        # Change by plural
        self.PL_MtoM = Counter(0)                        # Counts how many plural Latin m nouns remained masculine
        self.PL_MtoF = Counter(0)                        # Counts how many plural Latin m nouns became feminine
        self.PL_MtoN = Counter(0)                        # Counts how many plural Latin m nouns became neuter
        self.PL_FtoM = Counter(0)                        # Counts how many plural Latin m nouns became masculine
        self.PL_FtoF = Counter(0)                        # Counts how many plural Latin m nouns remained feminine
        self.PL_FtoN = Counter(0)                        # Counts how many plural Latin m nouns became neuter
        self.PL_NtoM = Counter(0)                        # Counts how many plural Latin m nouns became masculine
        self.PL_NtoF = Counter(0)                        # Counts how many plural Latin m nouns became feminine
        self.PL_NtoN = Counter(0)                        # Counts how many plural Latin m nouns remained neuter

        # Genitive counts
        self.genitive = sum([
            self.MSGGEN.value,
            self.FSGGEN.value,
            self.NSGGEN.value,
            self.MPLGEN.value,
            self.FPLGEN.value,
            self.NPLGEN.value
        ]) 

    # reset all the things we want to count for the generation
    def resetForGeneration(self):
        print "resetting counters"
        # for counter in self.counters:
        #     if getattr(self, counter).generational:
        #         getattr(self, counter).reset(0)

        self.totalCounter.reset(0)
        self.correctLatin.reset(0)
        self.correctPrev.reset(0)
        self.correctRomanian.reset(0)
        self.correctSplitRom.reset(0)

        # Division by gender
        self.M.reset(0)                              # Counts how many m nouns there are in the current generation
        self.F.reset(0)                              # Counts how many f nouns there are in the current generation
        self.N.reset(0)                              # Counts how many n nouns there are in the current generation
        self.MtoM.reset(0)                           # Counts how many Latin m nouns remained masculine
        self.MtoF.reset(0)                           # Counts how many Latin m nouns became feminine
        self.MtoN.reset(0)                           # Counts how many Latin m nouns became neuter
        self.FtoM.reset(0)                           # Counts how many Latin m nouns became masculine
        self.FtoF.reset(0)                           # Counts how many Latin m nouns remained feminine
        self.FtoN.reset(0)                           # Counts how many Latin m nouns became neuter
        self.NtoM.reset(0)                           # Counts how many Latin m nouns became masculine
        self.NtoF.reset(0)                           # Counts how many Latin m nouns became feminine
        self.NtoN.reset(0)                           # Counts how many Latin m nouns became neuter
        # SGNOM
        self.SGNOM_MtoM.reset(0)                     # Counts how many singular nominative Latin m nouns remained masculine
        self.SGNOM_MtoF.reset(0)                     # Counts how many singular nominative Latin m nouns became feminine
        self.SGNOM_MtoN.reset(0)                     # Counts how many singular nominative Latin m nouns became neuter
        self.SGNOM_FtoM.reset(0)                     # Counts how many singular nominative Latin m nouns became masculine
        self.SGNOM_FtoF.reset(0)                     # Counts how many singular nominative Latin m nouns remained feminine
        self.SGNOM_FtoN.reset(0)                     # Counts how many singular nominative Latin m nouns became neuter
        self.SGNOM_NtoM.reset(0)                     # Counts how many singular nominative Latin m nouns became masculine
        self.SGNOM_NtoF.reset(0)                     # Counts how many singular nominative Latin m nouns became feminine
        self.SGNOM_NtoN.reset(0)                     # Counts how many singular nominative Latin m nouns became neuter
        # SGACC
        self.SGACC_MtoM.reset(0)                     # Counts how many singular accusative Latin m nouns remained masculine
        self.SGACC_MtoF.reset(0)                     # Counts how many singular accusative Latin m nouns became feminine
        self.SGACC_MtoN.reset(0)                     # Counts how many singular accusative Latin m nouns became neuter
        self.SGACC_FtoM.reset(0)                     # Counts how many singular accusative Latin m nouns became masculine
        self.SGACC_FtoF.reset(0)                     # Counts how many singular accusative Latin m nouns remained feminine
        self.SGACC_FtoN.reset(0)                     # Counts how many singular accusative Latin m nouns became neuter
        self.SGACC_NtoM.reset(0)                     # Counts how many singular accusative Latin m nouns became masculine
        self.SGACC_NtoF.reset(0)                     # Counts how many singular accusative Latin m nouns became feminine
        self.SGACC_NtoN.reset(0)                     # Counts how many singular accusative Latin m nouns became neuter
        # SGGEN
        self.SGGEN_MtoM.reset(0)                     # Counts how many singular genitive Latin m nouns remained masculine
        self.SGGEN_MtoF.reset(0)                     # Counts how many singular genitive Latin m nouns became feminine
        self.SGGEN_MtoN.reset(0)                     # Counts how many singular genitive Latin m nouns became neuter
        self.SGGEN_FtoM.reset(0)                     # Counts how many singular genitive Latin m nouns became masculine
        self.SGGEN_FtoF.reset(0)                     # Counts how many singular genitive Latin m nouns remained feminine
        self.SGGEN_FtoN.reset(0)                     # Counts how many singular genitive Latin m nouns became neuter
        self.SGGEN_NtoM.reset(0)                     # Counts how many singular genitive Latin m nouns became masculine
        self.SGGEN_NtoF.reset(0)                     # Counts how many singular genitive Latin m nouns became feminine
        self.SGGEN_NtoN.reset(0)                     # Counts how many singular genitive Latin m nouns became neuter
        # PLNOM
        self.PLNOM_MtoM.reset(0)                     # Counts how many plural nominative Latin m nouns remained masculine
        self.PLNOM_MtoF.reset(0)                     # Counts how many plural nominative Latin m nouns became feminine
        self.PLNOM_MtoN.reset(0)                     # Counts how many plural nominative Latin m nouns became neuter
        self.PLNOM_FtoM.reset(0)                     # Counts how many plural nominative Latin m nouns became masculine
        self.PLNOM_FtoF.reset(0)                     # Counts how many plural nominative Latin m nouns remained feminine
        self.PLNOM_FtoN.reset(0)                     # Counts how many plural nominative Latin m nouns became neuter
        self.PLNOM_NtoM.reset(0)                     # Counts how many plural nominative Latin m nouns became masculine
        self.PLNOM_NtoF.reset(0)                     # Counts how many plural nominative Latin m nouns became feminine
        self.PLNOM_NtoN.reset(0)                     # Counts how many plural nominative Latin m nouns became neuter
        # PLACC
        self.PLACC_MtoM.reset(0)                     # Counts how many plural accusative Latin m nouns remained masculine
        self.PLACC_MtoF.reset(0)                     # Counts how many plural accusative Latin m nouns became feminine
        self.PLACC_MtoN.reset(0)                     # Counts how many plural accusative Latin m nouns became neuter
        self.PLACC_FtoM.reset(0)                     # Counts how many plural accusative Latin m nouns became masculine
        self.PLACC_FtoF.reset(0)                     # Counts how many plural accusative Latin m nouns remained feminine
        self.PLACC_FtoN.reset(0)                     # Counts how many plural accusative Latin m nouns became neuter
        self.PLACC_NtoM.reset(0)                     # Counts how many plural accusative Latin m nouns became masculine
        self.PLACC_NtoF.reset(0)                     # Counts how many plural accusative Latin m nouns became feminine
        self.PLACC_NtoN.reset(0)                     # Counts how many plural accusative Latin m nouns became neuter
                # PLGEN
        self.PLGEN_MtoM.reset(0)                     # Counts how many plural genitive Latin m nouns remained masculine
        self.PLGEN_MtoF.reset(0)                     # Counts how many plural genitive Latin m nouns became feminine
        self.PLGEN_MtoN.reset(0)                     # Counts how many plural genitive Latin m nouns became neuter
        self.PLGEN_FtoM.reset(0)                     # Counts how many plural genitive Latin m nouns became masculine
        self.PLGEN_FtoF.reset(0)                     # Counts how many plural genitive Latin m nouns remained feminine
        self.PLGEN_FtoN.reset(0)                     # Counts how many plural genitive Latin m nouns became neuter
        self.PLGEN_NtoM.reset(0)                     # Counts how many plural genitive Latin m nouns became masculine
        self.PLGEN_NtoF.reset(0)                     # Counts how many plural genitive Latin m nouns became feminine
        self.PLGEN_NtoN.reset(0)                     # Counts how many plural genitive Latin m nouns became neuter
        # Change by singular
        self.SG_MtoM.reset(0)                        # Counts how many singular Latin m nouns remained masculine
        self.SG_MtoF.reset(0)                        # Counts how many singular Latin m nouns became feminine
        self.SG_MtoN.reset(0)                        # Counts how many singular Latin m nouns became neuter
        self.SG_FtoM.reset(0)                        # Counts how many singular Latin m nouns became masculine
        self.SG_FtoF.reset(0)                        # Counts how many singular Latin m nouns remained feminine
        self.SG_FtoN.reset(0)                        # Counts how many singular Latin m nouns became neuter
        self.SG_NtoM.reset(0)                        # Counts how many singular Latin m nouns became masculine
        self.SG_NtoF.reset(0)                        # Counts how many singular Latin m nouns became feminine
        self.SG_NtoN.reset(0)                        # Counts how many singular Latin m nouns remained neuter
        # Change by plural
        self.PL_MtoM.reset(0)                        # Counts how many plural Latin m nouns remained masculine
        self.PL_MtoF.reset(0)                        # Counts how many plural Latin m nouns became feminine
        self.PL_MtoN.reset(0)                        # Counts how many plural Latin m nouns became neuter
        self.PL_FtoM.reset(0)                        # Counts how many plural Latin m nouns became masculine
        self.PL_FtoF.reset(0)                        # Counts how many plural Latin m nouns remained feminine
        self.PL_FtoN.reset(0)                        # Counts how many plural Latin m nouns became neuter
        self.PL_NtoM.reset(0)                        # Counts how many plural Latin m nouns became masculine
        self.PL_NtoF.reset(0)                        # Counts how many plural Latin m nouns became feminine
        self.PL_NtoN.reset(0)                        # Counts how many plural Latin m nouns remained neuter

    def adjustGenCount(self):                          # Invoke if after generation where genitive is lost
        self.tokensCounter.value -= self.genitive        # Counts how many words there are in the corpus
        self.rominfoCounter.value *= 2/3                        # Counts how many words have Romanian information
        self.Latin_M.value -= (self.MSGGEN.value+self.MPLGEN.value)   # Counts the total number of Latin masculine nouns
        self.Latin_F.value -= (self.FSGGEN.value+self.FPLGEN.value)   # Counts the total number of Latin feminine nouns
        self.Latin_N.value -= (self.NSGGEN.value+self.NPLGEN.value)   # Counts the total number of Latin neuter nouns
        self.Romanian_M.value *= 2/3                            # Counts the total number of Romanian masculine nouns
        self.Romanian_F.value *= 2/3                            # Counts the total number of Romanian feminine nouns
        self.Romanian_N.value *= 2/3                            # Counts the total number of Romanian neuter nouns
        self.Romanian_NM.value *= 2/3                           # Counts neuter singulars as masculine nouns
        self.Romanian_NF.value *= 2/3                           # Counts neuter plurals as feminine nouns
        self.Slavic_M.value *= 2/3                              # Counts the total number of Slavic masculine nouns
        self.Slavic_F.value *= 2/3                              # Counts the total number of Slavic feminine nouns
        self.Slavic_N.value *= 2/3                              # Counts the total number of Slavic neuter nouns

        # Gender of nouns split by number
        self.MSG.value -= self.MSGGEN.value                            # Counts how many singular forms are masculine in Latin
        self.FSG.value -= self.FSGGEN.value                            # Counts how many singular forms are feminine in Latin
        self.NSG.value -= self.NSGGEN.value                            # Counts how many singular forms are neuter in Latin
        self.MPL.value -= self.MPLGEN.value                            # Counts how many plural forms are masculine in Latin
        self.FPL.value -= self.FPLGEN.value                            # Counts how many plural forms are feminine in Latin
        self.NPL.value -= self.NPLGEN.value                            # Counts how many plural forms are neuter in Latin
