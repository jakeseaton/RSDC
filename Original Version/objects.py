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
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

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

    def updateCounters(self, case, counters):
        # Increment counters for Latin gender, Slavic gender, and Romanian gender
        if self.logMax != '?': 
                counters.freqCounter.increment()

        if self.romanianGender != '?':
                counters.rominfoCounter.increment()
                if self.romanianGender[0] == 'm': 
                        counters.Romanian_M.increment()
                elif self.romanianGender[0] == 'f': 
                        counters.Romanian_F.increment()
                elif self.romanianGender[0] == 'n':
                        counters.Romanian_N.increment()
                        # Split neuter (add to Romanian M and F count later)
                        if case[-2:] == 'sg': 
                                counters.Romanian_NM.increment()
                        elif case[-2:] == 'pl': 
                                counters.Romanian_NF.increment()

        if self.slavicGender != '?':
            counters.slavinfoCounter.increment()
            cmd = 'counters.Slavic_%s.increment()' % self.slavicGender[0].capitalize()
            exec(cmd)

        if self.latinGender[0] == 'm':
            counters.Latin_M.increment()
            if 'sg' in case:
                    counters.MSG.increment()
                    if 'nom' in case:
                            counters.MSGNOM.increment()
                    if 'acc' in case:
                            counters.MSGACC.increment()
                    if 'gen' in case:
                            counters.MSGGEN.increment()
            else:   # plural
                    counters.MPL.increment()
                    if 'nom' in case:
                            counters.MPLNOM.increment()
                    if 'acc' in case:
                            counters.MPLACC.increment()
                    if 'gen' in case:
                            counters.MPLGEN.increment()                                                                                              
        elif self.latinGender[0] == 'f':
            counters.Latin_F.increment()
            if 'sg' in case:
                    counters.FSG.increment()
                    if 'nom' in case:
                            counters.FSGNOM.increment()
                    if 'acc' in case:
                            counters.FSGACC.increment()
                    if 'gen' in case:
                            counters.FSGGEN.increment()
            else:   # plural
                    counters.FPL.increment()
                    if 'nom' in case:
                            counters.FPLNOM.increment()
                    if 'acc' in case:
                            counters.FPLACC.increment()
                    if 'gen' in case:
                            counters.FPLGEN.increment() 

        elif self.latinGender[0] == 'n': #probably else but just in case
            counters.Latin_N.increment()
            if 'sg' in case:
                    counters.NSG.increment()
                    if 'nom' in case:       
                            counters.NSGNOM.increment()
                    if 'acc' in case:
                            counters.NSGACC.increment()
                    if 'gen' in case:
                            counters.NSGGEN.increment()
            else:   # plural
                    counters.NPL.increment()
                    if 'nom' in case:
                            counters.NPLNOM.increment()
                    if 'acc' in case:
                            counters.NPLACC.increment()
                    if 'gen' in case:
                            counters.NPLGEN.increment() 


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

        self.modWord = "".join(syllables).replace('-', '')

        # print map(constants.print_phons, syllables)
        # print [item for vector in map(constants.print_phons, syllables) for item in vector]
        self.inputTuple = tuple([item for vector in map(constants.print_phons, syllables) for item in vector])

        self.inputTuple += constants.input_human[self.parentToken.latinGender]

        if constants.includeSlavic and generation >= constants.generationToIntroduceSlavic:
            self.inputTuple += constants.input_slavic[self.parentToken.slavicGender]

        self.sanityCheck(self.inputTuple, generation)

    def sanityCheck(self, inputTuple, generation):
        if constants.includeSlavic and generation >= constants.generationToIntroduceSlavic:
            if len(self.inputTuple) != constants.inputNodesSlav:
                print "You screwed up the size of the input"
                print len(self.inputTuple), constants.inputNodesSlav
                raise SystemExit
        else:
            if len(self.inputTuple) != constants.inputNodes:
                print "You screwed up the size of the input"
                print len(self.inputTuple), constants.inputNodes
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
        # frequency = float(word.parentToken.orig_freq)
        frequency = 1
        # 1 to test if we have no token frequency

        # Remove to test no type frequency
        # frequency *= constants.nhuman_case_freq[word.case+word.num]

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
    def __init__(self, *args, **kwargs):
        self.value = 0
        self.generational = False
        for key, val in kwargs.iteritems():
            setattr(self, key, val)

    def increment(self):
        self.value += 1

    def decrement(self):
        self.value -= 1

    def reset(self, value=0):
        self.value = value

###
# Class to contain multiple counters
# - Each is an instance of the Counter class
# - Each contained counter is a property of the bag, but maintains all of its properties
# - To add a counter, add to the init function 
###

# PERMANENT counters that do not change each generation
global_counters = [
    'generationCounter',                     # Counts what generation we are in

    'tokensCounter',                         # Counts how many words there are in the corpus
    'allinfoCounter',                        # Counts tokens with ALL info
    'freqCounter',                           # Counts how many words have a frequency
    'slavinfoCounter',                       # Counts how many words have Slavic information
    'rominfoCounter',                        # Counts how many words have Romanian information
    'Latin_M',                               # Counts the total number of Latin masculine nouns
    'Latin_F',                               # Counts the total number of Latin feminine nouns
    'Latin_N',                               # Counts the total number of Latin neuter nouns
    'Romanian_M',                            # Counts the total number of Romanian masculine nouns
    'Romanian_F',                            # Counts the total number of Romanian feminine nouns
    'Romanian_N',                            # Counts the total number of Romanian neuter nouns
    'Romanian_NM',                           # Counts neuter singulars as masculine nouns
    'Romanian_NF',                           # Counts neuter plurals as feminine nouns
    'Slavic_M',                              # Counts the total number of Slavic masculine nouns
    'Slavic_F',                              # Counts the total number of Slavic feminine nouns
    'Slavic_N',                              # Counts the total number of Slavic neuter nouns

    # Gender of nouns split by number
    'MSG',                            # Counts how many singular forms are masculine in Latin
    'FSG',                            # Counts how many singular forms are feminine in Latin
    'NSG',                            # Counts how many singular forms are neuter in Latin
    'MPL',                            # Counts how many plural forms are masculine in Latin
    'FPL',                            # Counts how many plural forms are feminine in Latin
    'NPL',                            # Counts how many plural forms are neuter in Latin

    # Masculine nouns by case
    'MSGNOM',                         # Counts how many singular nominative forms are masculine in Latin
    'MSGACC',                         # Counts how many singular accusative forms are masculine in Latin
    'MSGGEN',                         # Counts how many singular genitive forms are masculine in Latin
    'MPLNOM',                         # Counts how many plural nominative forms are masculine in Latin
    'MPLACC',                         # Counts how many plural accusative forms are masculine in Latin
    'MPLGEN',                         # Counts how many plural genitive forms are masculine in Latin

    # Feminine nouns by case
    'FSGNOM',                         # Counts how many singular nominative forms are feminine in Latin
    'FSGACC',                         # Counts how many singular accusative forms are feminine in Latin
    'FSGGEN',                         # Counts how many singular genitive forms are feminine in Latin
    'FPLNOM',                         # Counts how many plural nominative forms are feminine in Latin
    'FPLACC',                         # Counts how many plural accusative forms are feminine in Latin
    'FPLGEN',                         # Counts how many plural genitive forms are feminine in Latin

    # Neuter nouns by case
    'NSGNOM',                         # Counts how many singular nominative forms are neuter in Latin
    'NSGACC',                         # Counts how many singular accusative forms are neuter in Latin
    'NSGGEN',                         # Counts how many singular genitive forms are neuter in Latin
    'NPLNOM',                         # Counts how many plural nominative forms are neuter in Latin
    'NPLACC',                         # Counts how many plural accusative forms are neuter in Latin
    'NPLGEN',                         # Counts how many plural genitive forms are neuter in Latin
]

generational_counters = [
    # TEMPORARY Counters to be reset
    'totalCounter',
    'correctLatin',
    'correctPrev',
    'correctRomanian',
    'correctSplitRom',

    # Division by gender
    'M',                              # Counts how many m nouns there are in the current generation
    'F',                              # Counts how many f nouns there are in the current generation
    'N',                              # Counts how many n nouns there are in the current generation
    'MtoM',                           # Counts how many Latin m nouns remained masculine
    'MtoF',                           # Counts how many Latin m nouns became feminine
    'MtoN',                           # Counts how many Latin m nouns became neuter
    'FtoM',                           # Counts how many Latin m nouns became masculine
    'FtoF',                           # Counts how many Latin m nouns remained feminine
    'FtoN',                           # Counts how many Latin m nouns became neuter
    'NtoM',                           # Counts how many Latin m nouns became masculine
    'NtoF',                           # Counts how many Latin m nouns became feminine
    'NtoN',                           # Counts how many Latin m nouns became neuter

    # SGNOM
    'SGNOM_MtoM',                     # Counts how many singular nominative Latin m nouns remained masculine
    'SGNOM_MtoF',                     # Counts how many singular nominative Latin m nouns became feminine
    'SGNOM_MtoN',                     # Counts how many singular nominative Latin m nouns became neuter
    'SGNOM_FtoM',                     # Counts how many singular nominative Latin m nouns became masculine
    'SGNOM_FtoF',                     # Counts how many singular nominative Latin m nouns remained feminine
    'SGNOM_FtoN',                     # Counts how many singular nominative Latin m nouns became neuter
    'SGNOM_NtoM',                     # Counts how many singular nominative Latin m nouns became masculine
    'SGNOM_NtoF',                     # Counts how many singular nominative Latin m nouns became feminine
    'SGNOM_NtoN',                     # Counts how many singular nominative Latin m nouns became neuter

    # SGACC
    'SGACC_MtoM',                     # Counts how many singular accusative Latin m nouns remained masculine
    'SGACC_MtoF',                     # Counts how many singular accusative Latin m nouns became feminine
    'SGACC_MtoN',                     # Counts how many singular accusative Latin m nouns became neuter
    'SGACC_FtoM',                     # Counts how many singular accusative Latin m nouns became masculine
    'SGACC_FtoF',                     # Counts how many singular accusative Latin m nouns remained feminine
    'SGACC_FtoN',                     # Counts how many singular accusative Latin m nouns became neuter
    'SGACC_NtoM',                     # Counts how many singular accusative Latin m nouns became masculine
    'SGACC_NtoF',                     # Counts how many singular accusative Latin m nouns became feminine
    'SGACC_NtoN',                     # Counts how many singular accusative Latin m nouns became neuter

    # SGGEN
    'SGGEN_MtoM',                     # Counts how many singular genitive Latin m nouns remained masculine
    'SGGEN_MtoF',                     # Counts how many singular genitive Latin m nouns became feminine
    'SGGEN_MtoN',                     # Counts how many singular genitive Latin m nouns became neuter
    'SGGEN_FtoM',                     # Counts how many singular genitive Latin m nouns became masculine
    'SGGEN_FtoF',                     # Counts how many singular genitive Latin m nouns remained feminine
    'SGGEN_FtoN',                     # Counts how many singular genitive Latin m nouns became neuter
    'SGGEN_NtoM',                     # Counts how many singular genitive Latin m nouns became masculine
    'SGGEN_NtoF',                     # Counts how many singular genitive Latin m nouns became feminine
    'SGGEN_NtoN',                     # Counts how many singular genitive Latin m nouns became neuter

    # PLNOM
    'PLNOM_MtoM',                     # Counts how many plural nominative Latin m nouns remained masculine
    'PLNOM_MtoF',                     # Counts how many plural nominative Latin m nouns became feminine
    'PLNOM_MtoN',                     # Counts how many plural nominative Latin m nouns became neuter
    'PLNOM_FtoM',                     # Counts how many plural nominative Latin m nouns became masculine
    'PLNOM_FtoF',                     # Counts how many plural nominative Latin m nouns remained feminine
    'PLNOM_FtoN',                     # Counts how many plural nominative Latin m nouns became neuter
    'PLNOM_NtoM',                     # Counts how many plural nominative Latin m nouns became masculine
    'PLNOM_NtoF',                     # Counts how many plural nominative Latin m nouns became feminine
    'PLNOM_NtoN',                     # Counts how many plural nominative Latin m nouns became neuter

    # PLACC
    'PLACC_MtoM',                     # Counts how many plural accusative Latin m nouns remained masculine
    'PLACC_MtoF',                     # Counts how many plural accusative Latin m nouns became feminine
    'PLACC_MtoN',                     # Counts how many plural accusative Latin m nouns became neuter
    'PLACC_FtoM',                     # Counts how many plural accusative Latin m nouns became masculine
    'PLACC_FtoF',                     # Counts how many plural accusative Latin m nouns remained feminine
    'PLACC_FtoN',                     # Counts how many plural accusative Latin m nouns became neuter
    'PLACC_NtoM',                     # Counts how many plural accusative Latin m nouns became masculine
    'PLACC_NtoF',                     # Counts how many plural accusative Latin m nouns became feminine
    'PLACC_NtoN',                     # Counts how many plural accusative Latin m nouns became neuter

    # PLGEN
    'PLGEN_MtoM',                     # Counts how many plural genitive Latin m nouns remained masculine
    'PLGEN_MtoF',                     # Counts how many plural genitive Latin m nouns became feminine
    'PLGEN_MtoN',                     # Counts how many plural genitive Latin m nouns became neuter
    'PLGEN_FtoM',                     # Counts how many plural genitive Latin m nouns became masculine
    'PLGEN_FtoF',                     # Counts how many plural genitive Latin m nouns remained feminine
    'PLGEN_FtoN',                     # Counts how many plural genitive Latin m nouns became neuter
    'PLGEN_NtoM',                     # Counts how many plural genitive Latin m nouns became masculine
    'PLGEN_NtoF',                     # Counts how many plural genitive Latin m nouns became feminine
    'PLGEN_NtoN',                     # Counts how many plural genitive Latin m nouns became neuter

    # Change by singular
    'SG_MtoM',                        # Counts how many singular Latin m nouns remained masculine
    'SG_MtoF',                        # Counts how many singular Latin m nouns became feminine
    'SG_MtoN',                        # Counts how many singular Latin m nouns became neuter
    'SG_FtoM',                        # Counts how many singular Latin m nouns became masculine
    'SG_FtoF',                        # Counts how many singular Latin m nouns remained feminine
    'SG_FtoN',                        # Counts how many singular Latin m nouns became neuter
    'SG_NtoM',                        # Counts how many singular Latin m nouns became masculine
    'SG_NtoF',                        # Counts how many singular Latin m nouns became feminine
    'SG_NtoN',                        # Counts how many singular Latin m nouns remained neuter

    # Change by plural
    'PL_MtoM',                        # Counts how many plural Latin m nouns remained masculine
    'PL_MtoF',                        # Counts how many plural Latin m nouns became feminine
    'PL_MtoN',                        # Counts how many plural Latin m nouns became neuter
    'PL_FtoM',                        # Counts how many plural Latin m nouns became masculine
    'PL_FtoF',                        # Counts how many plural Latin m nouns remained feminine
    'PL_FtoN',                        # Counts how many plural Latin m nouns became neuter
    'PL_NtoM',                        # Counts how many plural Latin m nouns became masculine
    'PL_NtoF',                        # Counts how many plural Latin m nouns became feminine
    'PL_NtoN'                        # Counts how many plural Latin m nouns remained neuter
]

# counters = global_counters + generational_counters
counters = {counter: {} for counter in global_counters}

counters.update({counter: {'generational': True} for counter in generational_counters})

counters['generationCounter'] = {'value': 1}


class CounterBag:
    def __init__(self):
        for counter, kwargs in counters.iteritems():
            setattr(self, counter, Counter(0, **kwargs))

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
        for counter in generational_counters:
            getattr(self, counter).reset()

    def adjustGenCount(self):                          # Invoke if after generation where genitive is lost
        self.tokensCounter.value -= self.genitive        # Counts how many words there are in the corpus

        self.Latin_M.value -= (self.MSGGEN.value + self.MPLGEN.value)   # Counts the total number of Latin masculine nouns
        self.Latin_F.value -= (self.FSGGEN.value + self.FPLGEN.value)   # Counts the total number of Latin feminine nouns
        self.Latin_N.value -= (self.NSGGEN.value + self.NPLGEN.value)   # Counts the total number of Latin neuter nouns

        to_scale = [
            'rominfoCounter',                        # Counts how many words have Romanian information
            'Romanian_M',                            # Counts the total number of Romanian masculine nouns
            'Romanian_F',                            # Counts the total number of Romanian feminine nouns
            'Romanian_N',                            # Counts the total number of Romanian neuter nouns
            'Romanian_NM',                           # Counts neuter singulars as masculine nouns
            'Romanian_NF',                           # Counts neuter plurals as feminine nouns
            'Slavic_M',                              # Counts the total number of Slavic masculine nouns
            'Slavic_F',                              # Counts the total number of Slavic feminine nouns
            'Slavic_N'                              # Counts the total number of Slavic neuter nouns
        ]

        for counter in to_scale:
            getattr(self, counter).value *= 2/3

        to_decrement_by_gen = [
            'MSG',
            'FSG',
            'NSG',
            'MPL',
            'FPL',
            'NPL'
        ]
        for counter in to_decrement_by_gen:
            getattr(self, counter).value -= getattr(self, counter + "GEN").value
