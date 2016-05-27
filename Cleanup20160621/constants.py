import numpy

### GLOBAL VARIABLES ###

# The ordering of data in the input. Will then be set of properties of Lemma objects
row_order = [
    "word", 
    "latin_gender", 
    "max_freq", 
    "max10k", 
    "log_max", 
    "slavic_gender", 
    "romanian_gender", 
    "declension"
]

corpus_file = "latin_corpus.txt"

# Generations to run simulation
total_generations = 15
# Generation to drop the genitive: set above total_generations if want to drop
gnvdrop_generation = 16                               

# Number of times to introduce training set: P&VE uses 3, HareEllman uses 10
epochs = 3                                             

#####################
# Layer Information #
#####################

# Compute expected size of input layer

# 6 syllables with 6 potential phonemes each
# Each phoneme can be represented by a maximum of 11 features (Chomsky & Halle 1968)-see below
stem_length = 36                                
phon_length = 11

# 8 nodes to represent human male/female or nonhuman
human_length = 8

# Determine the length of the input
input_nodes = (stem_length * phon_length) + human_length

# Number of hidden layers: P&VE uses 30, HareEllman uses 10 for the first layer
hidden_nodes = 30                                                                        

# Gender (3), Declension (5), Case (3), Number (2)
gender_dimension = 3
declension_dimension = 5
case_dimension = 3
number_dimension = 1

# Gender variables (unit vectors in three dimensions)
[m, f, n] = map(tuple, numpy.identity(gender_dimension, int))

# Declension variables (unit vectors in 5 dimensions)
[d1, d2, d3, d4, d5] = map(tuple, numpy.identity(declension_dimension, int))

# Manually change cases to reflect semantics
[nom, acc, gen] = map(tuple, numpy.identity(case_dimension, int))

nom = (1, 0, 0)
acc = (1, 1, 0)
gen = (1, 1, 1)

# Indicator of singular or plural (unit vectors in two dimensions)
sg = (0,)
pl = (1,)

# Total number of output nodes (should be 12)
output_nodes = sum([gender_dimension, declension_dimension, case_dimension, number_dimension])                                        

####################
# Other Parameters #
####################

# Trial number
trial = 1                          

##########################
# Coding the output file #
##########################

# Number of generations
out_file = str(total_generations)

# Do we drop the genitive or not?
if gnvdrop_generation <= total_generations:
    out_file += '_GnvT%s' % str(gnvdrop_generation)
else:
    out_file += '_GnvF'

# Number of epochs, number of hidden nodes, trial number
out_file += 'Trial%s.txt' % str(trial)

#################################
# Dictionaries of output values #
#################################

# Invert dictionary
def invert(d):
    '''
    Invert a dictionary
    '''
    return dict((value, key) for key, value in d.iteritems())

# Map genders to tuples
genders = {
    'm': m,
    'f': f,
    'n': n
}

# Map tuples back to genders
tup_to_gen = invert(genders)

# Map declensions to tuples
declensions = {
    '1': d1,
    '2': d2,
    '3': d3,
    '4': d4,
    '5': d5,
}

# map tuples back to declensions
tup_to_decnum = invert(declensions)

# Map case to tuples
cases = {
    'nom': nom,
    'acc': acc,
    'gen': gen
}

# Map tuples back to case
tup_to_case = invert(cases)

# Map tuples back to number
num = {
    'sg': sg,
    'pl': pl
}

# Map number back to tuple
tup_to_num = invert(num)

# Human dictionary for assigning input values
input_human = {
    "mh": (1,) * (human_length / 2) + (0,) * (human_length / 2),
    "fh": (0,) * (human_length / 2) + (1,) * (human_length / 2),
    "m": (0,) * human_length,
    "f": (0,) * human_length,
    "n": (0,) * human_length
}

### INSTEAD OF THIS DICTIONARY, LET'S JUST KEEP THE HUMAN AS PART OF THE OBJECT

# # Dictionary for predicting outcome values
# outputs = {
#     # Instead of just adding the gender dictionary, we modify them here 
#     "m": m,                            
#     "mh": m,
#     "f": f,
#     "fh": f,
#     "n": n,
# }

# Insert the rest of the computed dictionaries
outputs = {}
outputs.update(genders)
outputs.update(cases)
outputs.update(declensions)
outputs.update(num)                            

########################
# Frequency Adjustment #
########################

# Adjust type frequencies depending on case and human/nonhuman

# Original case frequencies that P&VE implemented
human_case_freq = {
    "nomsg": 8, 
    "nompl": 3, 
    "accsg": 4.5, 
    "accpl": 2.5, 
    "gensg": 4, 
    "genpl": 2 
}

nhuman_case_freq = {
    "nomsg": 4,
    "nompl": 2,
    "accsg": 7,
    "accpl": 2,
    "gensg": 2,
    "genpl": 1
}

#############################################
# Organize data to make it easier to handle #
#############################################

# The output dictionary should map (404) = 6 (features) * 6 (phonemes) * 11 (features) + 8 (human) tuples to (12) tuples

# Corpus contains every word mapped to its Latin gender
corpus = {}

# Human contains every word mapped to its animacy
human = {}

# Frequencies contains every word mapped to its frequency
frequencies = {}

# Map phonemes to Chomsky and Halle values (1968) --> need to update 
phonemes = {
    "p": (-1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0),
    "t": (-1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, 1.0),
    "k": (-1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0, 1.0),
    "b": (-1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, 1.0, -1.0, -1.0),
    "d": (-1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0),
    "g": (-1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, 1.0, -1.0, -1.0),
    "f": (-1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0),
    "v": (-1.0, 1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, -1.0),
    "s": (-1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, -1.0, 1.0),
    "z": (-1.0, 1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0),
    "h": (-1.0, 1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, -1.0, 1.0),
    "m": (-1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0),
    "n": (-1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0),
    "r": (-1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0),
    "l": (-1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0),
    "w": (-1.0, -1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0, -1.0),
    "y": (-1.0, -1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0),
    "i": (1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0),    # (wick)
    "u": (1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, 1.0),   # (woo)
    "e": (1.0, -1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0),  # (wed)
    "o": (1.0, -1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0),  # (cot)
    "a": (1.0, -1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0),  # (card)
    "*": (1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, -1.0, -1.0),     # (about)
    "-": (0,) * 11
}

# Turn a syllable into its featural representation
# Takes a six tuple--a syllable with six phonemes
def convertToFeatures(syllable):
    ''' Turn a syllable (six tuple of phonemes) into its featural representation. '''
    feature_matrix = [phonemes[phoneme] for phoneme in syllable]
    # Flatten
    return tuple(feature for phoneme in feature_matrix for feature in phoneme)

# print convertToFeatures(('p', '-', 'a', 'a', '-', 't'))