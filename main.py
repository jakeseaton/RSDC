# Standard Library Imports
from decimal import *
from collections import defaultdict
import time
import csv

# Our files
import constants
import objects
from smooth import smooth
from read_input import convert_to_input

# Pybrain package dependencies
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer

# track time from start to finish
start = time.time()

counterBag = objects.CounterBag()

# Dictionary to keep track of which words HAVE changed gender and in what generation
genchange = defaultdict(list)


def conductGeneration(generation, corpus, previousOutput, counters):
        print "Trial %s" % str(constants.trial)

        # Reset relevant counters
        counterBag.resetForGeneration()

        # convert to input (array of tokens)
        (rawData, counters) = convert_to_input(constants.FILENAMETOCONVERT)

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
                result = smooth(tuple(net.activate(inputTuple)), gendrop=should_drop_gen)  

                # append output tuple to result
                results.append((word.description, result))

                # If this is the first generation
                if counterBag.generationCounter.value == 1:
                        # add
                        genchange[word.description].append((0, word.parentToken.latinGender[0]))

                # Change index depending if gen has been dropped or not
                (gen_b, gen_e, dec_b, dec_e, case_b, case_e, num_b, num_e) = (0, 3, 3, 8, 8, 11, 11, 13)

                # hash the output tuple to get the result
                gender = constants.tup_to_gen[result[gen_b: gen_e]]
                declension = constants.tup_to_dec[result[dec_b:dec_e]]
                case = constants.tup_to_case[result[case_b:case_e]]
                num = constants.tup_to_num[result[num_b:num_e]]

                to_add = (
                        counterBag.generationCounter.value,
                        gender + declension + case + num,
                        word.parentToken.latinGender[0],
                        word.parentToken.declension,
                        word.case,
                        word.num
                )
                
                genchange[word.description].append(to_add)

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
                generationOutput.append((
                        word.description, 
                        constants.outputs[word.parentToken.latinGender[0]] + constants.outputs[word.parentToken.declension] + constants.outputs[word.case] + constants.outputs[word.num]
                ))
                word.genchange[0] = (word.parentToken.latinGender[0], constants.decnum_to_roman[word.parentToken.declension], word.case, word.num)


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

map(info.write, [
        'Number of Epochs:\t%s\n' % str(constants.epochs),
        'Number of Tokens in Total: \t%s\n' % str(counters.tokensCounter.value),
        "Number of Tokens with Frequency Information:\t%s\n" % str(counters.freqCounter.value),
        "Number of Tokens with Slavic Information:\t%s\n" % str(counters.slavinfoCounter.value),
        "Number of Tokens with Romanian Information:\t%s\n" % str(counters.rominfoCounter.value),
        "Number of Tokens with All Information:\t%s\n" % str(counters.rominfoCounter.value),
        "Number of Latin Male Tokens:\t%s\n" % str(counters.Latin_M.value),
        "Number of Latin Female Tokens:\t%s\n" % str(counters.Latin_F.value),
        "Number of Latin Neuter Tokens:\t%s\n" % str(counters.Latin_N.value),
        "Number of Romanian Male Tokens:\t%s\n" % str(counters.Romanian_M.value),
        "Number of Romanian Female Tokens:\t%s\n" % str(counters.Romanian_F.value),
        "Number of Romanian Neuter Tokens:\t%s\n" % str(counters.Romanian_N.value),
        "Number of Romanian Male + Singular Neuter Tokens:\t%s\n" % str(counters.Romanian_M.value+counters.Romanian_NM.value),
        "Number of Romanian Female + Plural Neuter Tokens:\t%s\n" % str(counters.Romanian_F.value+counters.Romanian_NF.value),
        "Number of Slavic Male Tokens:\t%s\n" % str(counters.Slavic_M.value),
        "Number of Slavic Female Tokens:\t%s\n" % str(counters.Slavic_F.value),
        "Number of Slavic Neuter Tokens:\t%s\n\n" % str(counters.Slavic_N.value)
])

# For each generation to conduct
while counterBag.generationCounter.value <= constants.generationsToImplement:
        # Conduct the generation
        generationOutput = conductGeneration(counterBag.generationCounter.value, data, generationOutput, counters)
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
