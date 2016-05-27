# Standard Library Imports
from decimal import *
from collections import defaultdict
import time
import csv

# Our files
import constants
import objects
from smooth import smooth
from smooth import equalcase_smooth
from objects import Case
from objects import Token
from constants import FILENAMETOCONVERT

# Pybrain package dependencies
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer

# track time from start to finish
start = time.time()

counterBag = objects.CounterBag()

# Dictionary to keep track of which words HAVE changed gender and in what generation
genchange = defaultdict(list)

def read_corpus(file1 = FILENAMETOCONVERT):
        # aray of token objects
        result = []

        reader = open(file1, 'rU')

        for row in reader.readlines():
                # If this is the start of a new word
                if row[0] == "_":

                        # uncomment with new latin corpus
                        row_arr = row.strip('\n').split("\t")[1:]

                        row_dict = {constants.row_order[i]: value for i, value in enumerate(row_arr)}

                        currentToken = Token(**row_dict)

                        if row_dict['latinGender'][-1] == 'h':
                                currentToken.human = True

                        # only return a token if we have all necessary info.
                        if currentToken.almostComplete():
                                result.append(currentToken)
                else:
                        # only calculate cases if token is complete
                        if currentToken.almostComplete():
                                [s1, s2, s3, s4, s5, s6, case, suf, dem, adj] = row.split("\t")
                                syllables = (s1, s2, s3, s4, s5, s6)
                                currentToken.addCase(case, Case(currentToken, syllables, case, adj))
        return result


def conductGeneration(generation, corpus, previousOutput):
        '''
        Conducts a generation of learning and testing on the input data

        inputs
                generation (int) --- the number of the generation
                corpus (array) --- the output of reading the corpus file
                previousOutput (dict) --- the output of the previous generation
        outputs

        
        '''

        print "Trial %s" % str(constants.trial)
        input_size = constants.inputNodes

        # if we're using slavic data, modify the expected size of the input vector.
        if constants.includeSlavic and generation >= constants.generationToIntroduceSlavic: 
                input_size = constants.inputNodesSlav       

        # build the right size network
        net = buildNetwork(input_size, constants.hiddenNodes, constants.outputNodes)

        # build the right size training set
        emptyTrainingSet = SupervisedDataSet(input_size, constants.outputNodes)

        # initialize corpus object
        trainingCorpus = objects.Corpus(emptyTrainingSet)

        # iterate through tokens passed to the function
        for token in corpus:

                # iterate through cases
                for (case, word) in token.cases:
                        # set its syllables, based on the generation (i.e. account for sound changes)
                        word.setSyllables(generation, word.syllables)
                        # extract the gender from the previous generation
                        print previousOutput
                        (placeholder, previousResult) = previousOutput[[wordinfo for (wordinfo, gender) in previousOutput].index(word.description)]                                
                        # print previousResult
                        # print placeholder # we already know the word
                        # adds words according to their frequencies
                        trainingCorpus.configure(word, previousResult, generation)

        # construct the training set
        trainingSet = trainingCorpus.constructTrainingSet()

        # construct the trainer
        trainer = BackpropTrainer(net, trainingSet)

        # train
        if constants.epochs == 1:
                error = trainer.train()
        else:
                error = trainer.trainEpochs(constants.epochs)

        print "--------Generation: %s--------" % generation
        if generation >= constants.generationToDropGen:
                print "Genitive Case Dropped"

        if constants.includeSlavic and generation >= constants.generationToIntroduceSlavic:
                print "Slavic Information Introduced"

        print "Number of Training Epochs: %s" % constants.epochs
        print "Number of Training Tokens: %s" % len(trainingSet)
        print "Training Error: %s" % error

        results = []

        # Dictionary of changes
        changes = {
                'total': 0,
                'gen_change': defaultdict(lambda: 0),
                'dec_change': defaultdict(lambda: 0),
                'gencase_change': defaultdict(lambda: 0),
                'gennum_change': defaultdict(lambda: 0),
                'deccase_change': defaultdict(lambda: 0),
                'decnum_change': defaultdict(lambda: 0),
                'gencasenum_change': defaultdict(lambda: 0),
                'deccasenum_change': defaultdict(lambda: 0)
        }
        # for each work in the input
        for (word, inputTuple, expectedOutput, trueLatinGender, trueRomanianGender) in trainingCorpus.test:

                # Count how many tokens are in the test set
                counterBag.totalCounter.increment()                     

                # determine if we should drop the genetive
                should_drop_gen = generation >= constants.generationToDropGen

                # activate the net, and smooth the output
                result = smooth(tuple(net.activate(inputTuple)), gendrop=should_drop_gen, equalcase = True)  

                # append output tuple to result
                results.append((word.description, result))

                # If this is the first generation
                if counterBag.generationCounter.value == 1:
                        # add
                        genchange[word.description].append((0, word.parentToken.latinGender[0]))

                # Change index depending if gen has been dropped or not
                (gen_b, gen_e, dec_b, dec_e, case_b, case_e, num_b, num_e) = (0, 3, 3, 8, 8, 11, 11, 13)

                # hash the output tuple to get the result
                gender = constants.tup_to_gen[tuple(result[gen_b:gen_e])]
                declension = constants.tup_to_dec[tuple(result[dec_b:dec_e])]
                case = constants.tup_to_case[tuple(result[case_b:case_e])]
                num = constants.tup_to_num[tuple(result[num_b:num_e])]

                to_add = (
                        counterBag.generationCounter.value,
                        gender + declension + case + num,
                        word.parentToken.latinGender[0],
                        word.parentToken.declension,
                        word.case,
                        word.num
                )

                genchange[word.description].append(to_add)
                word.genchange[counterBag.generationCounter.value] = (gender, declension, case, num)

        return results

## Main ##

# Construct first data set
data = read_corpus()

generationOutput = []

# iterate over tokens
for token in data:
        # iterate over cases
        for (case, word) in token.cases:
                # first train on latin
                generationOutput.append((
                        word.description, 
                        constants.outputs[word.parentToken.latinGender[0]] + constants.outputs[word.parentToken.declension] + constants.outputs[word.case] + constants.outputs[word.num]
                ))
                word.genchange[0] = (word.parentToken.latinGender[0], constants.decnum_to_roman[word.parentToken.declension], word.case, word.num)

# For each generation to conduct
while counterBag.generationCounter.value <= constants.generationsToImplement:
        # Conduct the generation
        generationOutput = conductGeneration(counterBag.generationCounter.value, data, generationOutput)
        # Increment the counter
        counterBag.generationCounter.increment()

### Write output to stats
stats = open(constants.out_files['out7'], 'w')
stats.write('Declined Noun')

for generation in range(0, constants.generationsToImplement+1):
        stats.write('\t'+str(generation))

for word in data:
        for (case, token) in word.cases:
                stats.write('\n'+token.description)
                for generation in sorted(token.genchange.keys()):
                        stats.write('\t' + ",".join(token.genchange[generation])) 
stats.close()


csv_file = constants.out_files['out7'][:-3] + 'csv'
in_txt = csv.reader(open(constants.out_files['out7'], "rb"), delimiter = '\t')
out_csv = csv.writer(open(csv_file, 'wb'))
out_csv.writerows(in_txt)

# End time it
end = time.time()
print end - start
