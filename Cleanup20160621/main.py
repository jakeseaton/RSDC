# Standard Library Imports
from decimal import *
from collections import defaultdict
import time
import csv

# Our files
import constants
import objects

# Pybrain package dependencies
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer

# Track time from start to finish
start = time.time()

# Dictionary to keep track of which words HAVE changed gender and in what generation
genchange = defaultdict(list)

def readCorpus(f = constants.corpus_file):
        ''' Reads the corpus file and creates the Lemma and Case objects. '''
        corpus = []

        reader = open(f, 'rU')

        for row in reader.readlines():
                # If this is the start of a new word
                if row[0] == "_":

                        # Ignore "_"
                        row_arr = row.strip('\n').split("\t")[1:]

                        # Create dictionary of labels to values
                        row_dict = {constants.row_order[i]: value for i, value in enumerate(row_arr)}

                        # Create Lemma object and add it as a word in the corpus
                        current_lemma = objects.Lemma(**row_dict)

                        # REMOVE THIS LINE ONCE WE MAKE THE CORPUS ONLY WORDS WITH LATIN GENDER
                        if current_lemma.latin_gender != "N":        
                                corpus.append(current_lemma)

                # Else, it is information for the word, and we can create a Case object pointing to the parent Lemma
                else:
                        [s1, s2, s3, s4, s5, s6, case, suf, dem, adj] = row.split("\t")
                        syllables = (s1, s2, s3, s4, s5, s6)
                        current_lemma.addCase(case, objects.Case(current_lemma, syllables, case))

        return corpus

def conductGeneration(generation, corpus, previous_output):
        '''
        Conducts a generation of learning and testing on the input data

        inputs
                generation (int) --- the number of the generation
                corpus (array) --- the lemmas and their info from reading the corpus file
                previous_output (dict) --- the output (gender, declension, case, number) of the previous generation
        outputs

        '''

        print "Trial %s" % str(constants.trial)

        # Build the right size network
        net = buildNetwork(constants.input_nodes, constants.hidden_nodes, constants.output_nodes)

        # Build the right size training set
        emptytraining_set = SupervisedDataSet(constants.input_nodes, constants.output_nodes)

        # Initialize corpus object and expected output dictionary
        training_corpus = objects.Corpus(emptytraining_set)

        # Iterate through tokens and convert to binary
        for lemma in corpus:

                # Iterate through cases
                for case, form in lemma.cases.iteritems():

                        # Create the input tuple
                        form.createInputTuple(form.syllables)

                        # Extract the class information from the previous generation
                        expected_outputs[form.lemmacase] = previous_output[form.lemmacase]

                        # Add words according to their frequencies
                        training_corpus.addByFreq(form, previous_output)

        print expected_outputs

#         # construct the training set
#         training_set = trainingCorpus.constructTrainingSet()

#         # construct the trainer
#         trainer = BackpropTrainer(net, training_set)

#         # train
#         if constants.epochs == 1:
#                 error = trainer.train()
#         else:
#                 error = trainer.trainEpochs(constants.epochs)

#         print "--------Generation: %s--------" % generation
#         if generation >= constants.gnvdrop_generation:
#                 print "Genitive Case Dropped"

#         if constants.includeSlavic and generation >= constants.generationToIntroduceSlavic:
#                 print "Slavic Information Introduced"

#         print "Number of Training Epochs: %s" % constants.epochs
#         print "Number of Training Lemmas: %s" % len(training_set)
#         print "Training Error: %s" % error

#         results = []

#         # Dictionary of changes
#         changes = {
#                 'total': 0,
#                 'gen_change': defaultdict(lambda: 0),
#                 'dec_change': defaultdict(lambda: 0),
#                 'gencase_change': defaultdict(lambda: 0),
#                 'gennum_change': defaultdict(lambda: 0),
#                 'deccase_change': defaultdict(lambda: 0),
#                 'decnum_change': defaultdict(lambda: 0),
#                 'gencasenum_change': defaultdict(lambda: 0),
#                 'deccasenum_change': defaultdict(lambda: 0)
#         }
#         # for each work in the input
#         for (word, input_tuple, expected_output, truelatin_gender) in trainingCorpus.test:

#                 # Count how many tokens are in the test set
#                 counterBag.totalCounter.increment()                     

#                 # determine if we should drop the genetive
#                 should_drop_gen = generation >= constants.gnvdrop_generation

#                 # activate the net, and smooth the output
#                 result = smooth(tuple(net.activate(input_tuple)), gendrop=should_drop_gen)  

#                 # append output tuple to result
#                 results.append((word.lemmacase, result))

#                 # If this is the first generation
#                 if counterBag.generationCounter.value == 1:
#                         # add
#                         genchange[word.lemmacase].append((0, word.parent_lemma.latin_gender[0]))

#                 # Change index depending if gen has been dropped or not
#                 (gen_b, gen_e, dec_b, dec_e, case_b, case_e, num_b, num_e) = (0, 3, 3, 8, 8, 11, 11, 13)

#                 # hash the output tuple to get the result
#                 gender = constants.tup_to_gen[tuple(result[gen_b:gen_e])]
#                 declension = constants.tup_to_dec[tuple(result[dec_b:dec_e])]
#                 case = constants.tup_to_case[tuple(result[case_b:case_e])]
#                 num = constants.tup_to_num[tuple(result[num_b:num_e])]

#                 to_add = (
#                         counterBag.generationCounter.value,
#                         gender + declension + case + num,
#                         word.parent_lemma.latin_gender[0],
#                         word.parent_lemma.declension,
#                         word.case,
#                         word.num
#                 )

#                 genchange[word.lemmacase].append(to_add)
#                 word.output_change[counterBag.generationCounter.value] = (gender, declension, case, num)

#         return results

########
# Main #
########

# Read in corpus, initialize expected outputs dictionary, to be updated each generation
corpus = readCorpus(constants.corpus_file)

expected_outputs = {}

# Iterate over tokens
for lemma in corpus:
        # Iterate over cases
        for case, form in lemma.cases.iteritems():
                # Take Latin outputs as first set of expected outputs
                expected_outputs[form.lemmacase] = (
                        constants.outputs[form.parent_lemma.latin_gender] + 
                        constants.outputs[form.parent_lemma.declension] + 
                        constants.outputs[form.case] + 
                        constants.outputs[form.num]
                )
                form.output_change[0] = (form.parent_lemma.latin_gender, 
                        form.parent_lemma.declension, 
                        form.case, 
                        form.num)


conductGeneration(1, readCorpus(constants.corpus_file), expected_outputs)

# # For each generation to conduct
# while counterBag.generationCounter.value <= constants.total_generations:
#         # Conduct the generation
#         generationOutput = conductGeneration(counterBag.generationCounter.value, data, generationOutput)
#         # Increment the counter
#         counterBag.generationCounter.increment()

# ### Write output to stats
# stats = open(constants.out_file, 'w')
# stats.write('Declined Noun')

# for generation in range(0, constants.total_generations+1):
#         stats.write('\t'+str(generation))

# for word in data:
#         for (case, token) in word.cases:
#                 stats.write('\n'+token.lemmacase)
#                 for generation in sorted(token.output_change.keys()):
#                         stats.write('\t' + ",".join(token.output_change[generation])) 
# stats.close()


# csv_file = constants.out_file[:-3] + 'csv'
# in_txt = csv.reader(open(constants.out_file, "rb"), delimiter = '\t')
# out_csv = csv.writer(open(csv_file, 'wb'))
# out_csv.writerows(in_txt)

# # End time it
# end = time.time()
# print end - start
