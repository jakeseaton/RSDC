import constants
import objects
import read_input
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer                 # For backpropagation training
# import random
# from pybrain.structure import FeedForwardNetwork                        # For feedforward network
# from pybrain.structure import LinearLayer, SigmoidLayer                 # For the layers
# from pybrain.structure import FullConnection            # For connections

from read_input import convert_to_input
from smooth import smooth
from decimal import *
from collections import defaultdict
import time
import csv

start = time.time()

counterBag = objects.CounterBag()

# Dictionary to keep track of which words HAVE changed gender and in what generation
genchange = defaultdict(list)


def conductGeneration(generation, corpus, previousOutput, counters):
        print "Trial %s" % str(constants.trial)
        # Reset relevant counters
        counterBag.resetForGeneration()

        # convert to input (array of tokens)
        (rawData, counters) = read_input.convert_to_input(constants.FILENAMETOCONVERT)

        # if we should include slavic data
        if constants.includeSlavic and generation >= constants.generationToIntroduceSlavic:
                # build the right size net
                net = buildNetwork(constants.inputNodesSlav, constants.hiddenNodes, constants.outputNodes)
                emptyTrainingSet = SupervisedDataSet(constants.inputNodesSlav, constants.outputNodes)
        else: 
                net = buildNetwork(constants.inputNodes, constants.hiddenNodes, constants.outputNodes)
                emptyTrainingSet = SupervisedDataSet(constants.inputNodes, constants.outputNodes)

        # initialize corpus object
        trainingCorpus = objects.Corpus(emptyTrainingSet)

        # iterate through tokens
        for token in corpus:
                # iterate through cases
                for (case, word) in token.cases:
                        word.setSyllables(generation, word.syllables)

                        # extract the gender from the previous generation
                        (placeholder, previousResult) = previousOutput[[wordinfo for (wordinfo, gender) in previousOutput].index(word.description)]                                
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
        if generation == constants.generationToDropGen:
                counters.adjustGenCount()
        if constants.generationToImplementMChange <= constants.generationsToImplement:
                print "Romanian Sound Change To Be Implemented at generations:", str(constants.generationToImplementMChange), str(constants.generationToImplementAEChange), str(constants.generationToImplementSChange), str(constants.generationToImplementSecondChange)
        if generation >= constants.generationToImplementMChange:
                print "Final -m dropped"
        if generation >= constants.generationToImplementAEChange:
                print "Final -ae changed to -e"
        if generation >= constants.generationToImplementSChange:
                print "Final -s dropped"
        if generation >= constants.generationToImplementSecondChange:
                print "Final high vowels dropped"
        if constants.includeSlavic and generation >= constants.generationToIntroduceSlavic:
                print "Slavic Information Introduced"
        print "Number of Training Epochs: %s" % constants.epochs
        print "Number of Training Tokens: %s" % len(trainingSet)

        print "Number of Tokens with Romanian Information: %s" % counters.rominfoCounter.value
        verbose = False
        if verbose:
                pass
        ##        print "Number of Tokens with Frequency Information: %s" % counters.freqCounter.value
        ##        print "Number of Tokens with Slavic Information: %s" % counters.slavinfoCounter.value
        ##        print "Number of Latin Male Tokens: %s" % counters.Latin_M.value
        ##        print "Number of Latin Female Tokens: %s" % counters.Latin_F.value
        ##        print "Number of Latin Neuter Tokens: %s" % counters.Latin_N.value
        ##        print "Number of Romanian Male Tokens: %s" % counters.Romanian_M.value
        ##        print "Number of Romanian Female Tokens: %s" % counters.Romanian_F.value
        ##        print "Number of Romanian Neuter Tokens: %s" % counters.Romanian_N.value
        ##        print "Number of Romanian Male + Singular Neuter Tokens: %s" % (counters.Romanian_M.value+counters.Romanian_NM.value)
        ##        print "Number of Romanian Female + Plural Neuter Tokens: %s" % (counters.Romanian_F.value+counters.Romanian_NF.value)
        ##        print "Number of Slavic Male Tokens: %s" % counters.Slavic_M.value
        ##        print "Number of Slavic Female Tokens: %s" % counters.Slavic_F.value
        ##        print "Number of Slavic Neuter Tokens: %s" % counters.Slavic_N.value

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

        for (word, inputTuple, expectedOutput, trueLatinGender, trueRomanianGender) in trainingCorpus.test:
                counterBag.totalCounter.increment()                     # Count how many tokens are in the test set
                should_drop_gen = generation >= constants.generationToDropGen
                result = smooth(tuple(net.activate(inputTuple)), gendrop=should_drop_gen)  

                results.append((word.description, result))
                if counterBag.generationCounter.value == 1:
                        genchange[word.description].append((0, word.parentToken.latinGender[0]))

                # Change index depending if gen has been dropped or not
                (gen_b, gen_e, dec_b, dec_e, case_b, case_e, num_b, num_e) = (0, 3, 3, 8, 8, 11, 11, 13)

                # YIKES
                genchange[word.description].append((counterBag.generationCounter.value, constants.tup_to_gen[result[gen_b: gen_e]] + constants.tup_to_dec[result[dec_b:dec_e]] + constants.tup_to_case[result[case_b:case_e]]+constants.tup_to_num[result[num_b:num_e]],word.parentToken.latinGender[0],word.parentToken.declension,word.case,word.num))

                if result == expectedOutput:                           
                        # Count how many tokens match gender in previous gen
                        counterBag.correctPrev.increment()
                # else write it
                if result == constants.outputs[trueLatinGender]:
                        # Count how many tokens match gender in Latin
                        counterBag.correctLatin.increment()
##                        out.write(constants.constants.tup_to_gen[result]+'\t')
                else:
                        genchange[word.description].insert(0, True)
##                        word.changed = True

################
# New Counters #
################

                word.genchange[counterBag.generationCounter.value] = (constants.tup_to_gen[result[gen_b:gen_e]], constants.tup_to_dec[result[dec_b:dec_e]], constants.tup_to_case[result[case_b:case_e]], constants.tup_to_num[result[num_b:num_e]])
                changes['total'] += 1                                                                                           # Total tokens
                changes['gen_change']['LatinGen'+word.parentToken.latinGender[0]] += 1                                                           # Count total # of each Latin gender
                changes['dec_change']['LatinDec'+word.parentToken.declension] += 1                                                           # Count total # of each Latin declension
                changes['gencase_change']['LatinGenCase'+word.parentToken.latinGender[0]+word.case] += 1                                             # Count total # of gender+case
                changes['gennum_change']['LatinGenNum'+word.parentToken.latinGender[0]+word.num] += 1                                               # Count total # of gender+number
                changes['deccase_change']['LatinDecCase'+word.parentToken.declension+word.case] += 1                                              # Count total # of declension+case
                changes['decnum_change']['LatinDecNum'+word.parentToken.declension+word.num] += 1                                                # Count total # of declension+number
                changes['gencasenum_change']['LatinGenCaseNum'+word.parentToken.latinGender[0]+word.case+word.num] += 1                                 # Count total # of gender+case+number
                changes['deccasenum_change']['LatinDecCaseNum'+word.parentToken.declension+word.case+word.num] += 1                                  # Count total # of declension+case+number
                changes['gen_change'][constants.tup_to_gen[result[gen_b:gen_e]]+'from'+word.parentToken.latinGender[0]] += 1                                              # Check how stable genders stay
                changes['dec_change'][constants.tup_to_dec[result[dec_b:dec_e]]+'from'+word.parentToken.declension] += 1                                               # Check how stable declensions stay
                changes['gencase_change'][constants.tup_to_gen[result[gen_b:gen_e]]+constants.tup_to_case[result[case_b:case_e]]+'from'+word.parentToken.latinGender[0]+word.case] += 1          # Check how stable gender + case stays
                changes['gennum_change'][constants.tup_to_gen[result[gen_b:gen_e]]+constants.tup_to_num[result[num_b:num_e]]+'from'+word.parentToken.latinGender[0]+word.num] += 1           # Check how stable gender + number stays
                changes['deccase_change'][constants.tup_to_dec[result[dec_b:dec_e]]+constants.tup_to_case[result[case_b:case_e]]+'from'+word.parentToken.declension+word.case] += 1           # Check how stable declension + case stays
                changes['decnum_change'][constants.tup_to_dec[result[dec_b:dec_e]]+constants.tup_to_num[result[num_b:num_e]]+'from'+word.parentToken.declension+word.num] += 1            # Check how stable declension + number stays
                changes['gencasenum_change'][constants.tup_to_gen[result[gen_b:gen_e]]+constants.tup_to_case[result[case_b:case_e]]+constants.tup_to_num[result[num_b:num_e]]+'from'+word.parentToken.latinGender[0]+word.case+word.num] += 1 # Check how stable gender + case + number stays
                changes['deccasenum_change'][constants.tup_to_dec[result[dec_b:dec_e]]+constants.tup_to_case[result[case_b:case_e]]+constants.tup_to_num[result[num_b:num_e]]+'from'+word.parentToken.declension+word.case+word.num] += 1 # Check how stable declension + case + number stays
        return results

## Main ##

# Construct first data set
(data, counters) = convert_to_input(constants.FILENAMETOCONVERT)

generationOutput = []

# iterate over tokens
for token in data:
                # iterate over cases
                for (case, word) in token.cases:
                        # first train on latin
                        generationOutput.append((word.description, constants.outputs[word.parentToken.latinGender[0]]+constants.outputs[word.parentToken.declension]+constants.outputs[word.case]+constants.outputs[word.num]))
                        word.genchange[0] = (word.parentToken.latinGender[0], constants.decnum_to_roman[word.parentToken.declension], word.case, word.num)

##out.write('\n0\t')
##for token in data:
##              # iterate over cases
##              for (case, word) in token.cases:
##                        # Write the initial gender of each word to be tracked
##                        out.write(word.parentToken.latinGender+'\t')

# Set up table for tracking stats across generations
info = open(constants.out_files['out2'], 'w')
info.write('Latin Gender System Change Simulation\n\n')

if constants.generationToDropGen < constants.generationsToImplement:
        info.write('Genitive Case dropped at generation\t%s\n' % str(constants.generationToDropGen))

if constants.generationToImplementMChange < constants.generationsToImplement:
        info.write('First Romanian Change (final m to zero) implemented at generation\t%s\n' % str(constants.generationToImplementMChange))
        info.write('Second Romanian Change (final ae to e) implemented at generation\t%s\n' % str(constants.generationToImplementAEChange))
        info.write('Third Romanian Change (final s to zero) implemented at generation\t%s\n' % str(constants.generationToImplementSChange))
        info.write('Fourth Romanian Change (syncope of final high vowels) implemented at generation\t%s\n' % str(constants.generationToImplementSecondChange))
else: 
        info.write('No Romanian Change Implemented\n')

if constants.SLAVICINFO:
        info.write('Slavic Information Introduced at generation\t%s\n' % str(constants.generationToIntroduceSlavic))
else: 
        info.write('No Slavic Information Introduced\n')

info.write('Number of Epochs:\t%s\n' % str(constants.epochs))
info.write('Number of Tokens in Total: \t%s\n' % str(counters.tokensCounter.value))
info.write("Number of Tokens with Frequency Information:\t%s\n" % str(counters.freqCounter.value))
info.write("Number of Tokens with Slavic Information:\t%s\n" % str(counters.slavinfoCounter.value))
info.write("Number of Tokens with Romanian Information:\t%s\n" % str(counters.rominfoCounter.value))
info.write("Number of Tokens with All Information:\t%s\n" % str(counters.rominfoCounter.value))
info.write("Number of Latin Male Tokens:\t%s\n" % str(counters.Latin_M.value))
info.write("Number of Latin Female Tokens:\t%s\n" % str(counters.Latin_F.value))
info.write("Number of Latin Neuter Tokens:\t%s\n" % str(counters.Latin_N.value))
info.write("Number of Romanian Male Tokens:\t%s\n" % str(counters.Romanian_M.value))
info.write("Number of Romanian Female Tokens:\t%s\n" % str(counters.Romanian_F.value))
info.write("Number of Romanian Neuter Tokens:\t%s\n" % str(counters.Romanian_N.value))
info.write("Number of Romanian Male + Singular Neuter Tokens:\t%s\n" % str(counters.Romanian_M.value+counters.Romanian_NM.value))
info.write("Number of Romanian Female + Plural Neuter Tokens:\t%s\n" % str(counters.Romanian_F.value+counters.Romanian_NF.value))
info.write("Number of Slavic Male Tokens:\t%s\n" % str(counters.Slavic_M.value))
info.write("Number of Slavic Female Tokens:\t%s\n" % str(counters.Slavic_F.value))
info.write("Number of Slavic Neuter Tokens:\t%s\n\n" % str(counters.Slavic_N.value))

while counterBag.generationCounter.value <= constants.generationsToImplement:
##        stats.write('\n'+str(constants.trial)+'\t'+str(counterBag.generationCounter.value)+'\t')
        generationOutput = conductGeneration(counterBag.generationCounter.value, data, generationOutput, counters)
        counterBag.generationCounter.increment()


#### FOR MULTIPLE FILES WITH DIFFERENT STATS
##stats1 = open(constants.out_files['out3'],'w')
##stats2 = open(constants.out_files['out4'],'w')
##stats3 = open(constants.out_files['out5'],'w')
##stats4 = open(constants.out_files['out6'],'w')
##
##stats1.write('Trial\tDeclinedNoun')
##stats2.write('Trial\tDeclinedNoun')
##stats3.write('Trial\tDeclinedNoun')
##stats4.write('Trial\tDeclinedNoun')

## FOR ONE FILE WITH ALL STATS
stats = open(constants.out_files['out7'], 'w')
stats.write('Declined Noun')
for generation in range(0, constants.generationsToImplement+1):
        stats.write('\t'+str(generation))
##        stats1.write('\t'+str(generation))
##        stats2.write('\t'+str(generation))
##        stats3.write('\t'+str(generation))
##        stats4.write('\t'+str(generation))

for word in data:
        for (case, token) in word.cases:
                stats.write('\n'+token.description)
##                stats1.write('\n'+str(constants.trial)+'\t'+token.description)
##                stats2.write('\n'+str(constants.trial)+'\t'+token.description)
##                stats3.write('\n'+str(constants.trial)+'\t'+token.description)
##                stats4.write('\n'+str(constants.trial)+'\t'+token.description)
                for generation in sorted(token.genchange.keys()):
                        (gen, dec, case, num) = token.genchange[generation]
                        stats.write('\t'+gen+','+dec+','+case+','+num)
##                        stats1.write('\t'+gen)
##                        stats2.write('\t'+dec)
##                        stats3.write('\t'+case)
##                        stats4.write('\t'+num)

stats.close()
##stats1.close()
##stats2.close()
##stats3.close()
##stats4.close()

# Now convert to csv
##for i in range(3,7):
##        csv_file = constants.out_files['out'+str(i)][:-3]+'csv'
##        in_txt = csv.reader(open(constants.out_files['out'+str(i)], "rb"), delimiter = '\t')
##        out_csv = csv.writer(open(csv_file, 'wb'))
##        out_csv.writerows(in_txt)

csv_file = constants.out_files['out7'][:-3]+'csv'
in_txt = csv.reader(open(constants.out_files['out7'], "rb"), delimiter = '\t')
out_csv = csv.writer(open(csv_file, 'wb'))
out_csv.writerows(in_txt)

end = time.time()

print end - start
