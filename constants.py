import numpy

### GLOBAL VARIABLES ###

row_order = ["word", "latinGender", "maxFrequency", "max10k", "logMax", "slavicGender", "romanianGender", "declension"]

# This variable tells us whether to introduce Slavic information or not
SLAVICINFO = False
includeSlavic = SLAVICINFO


FILENAMETOCONVERT = "latin_corpus.txt"
declension_file = "declensions.txt"

# 48 to show time between 400AD and 1600AD (25 years to a generation)
generationsToImplement = 15                            

# 2 to show early loss
generationToImplementMChange = 31                       

# 6 to show between 2nd and 3rd century (dropped 2nd-3rd century)
generationToImplementSChange = 31                       

# 8 to show latter part of 300AD (standard in latter part of 2nd century and before 4th)
generationToImplementAEChange = 31                      

# 15 to show halfway point (idealized)
generationToImplementSecondChange = 31                  

# 18 (--> 34) to show Slavs coming in approximately 850AD
generationToIntroduceSlavic = 18                        

# Drop at 8 (3rd century AD)
generationToDropGen = 8                                 

# EzraPolinsky uses 3, HareEllman uses 10
epochs = 3                                             

# EzraPolinsky uses 30, HareEllman uses 10 for the first layer
hiddenNodes = 30                                        

# HareEllman uses 8 for the second layer
hiddenNodes2 = 8                                        

# Gender (3), Declension (5), Case (3), Number (2)
outputNodes = 13                                        

# Trial number
trial = 16                                               


out_files = [
    'trackchange_Gens',
    'info_Gens',
    'genstats_Gens',
    'decstats_Gens',
    'casestats_Gens',
    'numstats_Gens',
    'stats_Gens'
]

out_files = {'out' + str(i + 1): name + str(generationsToImplement) for i, name in enumerate(out_files)}

# Replaced with more pythonic version above
# out_files = {'out1':'trackchange_Gens'+str(generationsToImplement),
#              'out2':'info_Gens'+str(generationsToImplement),
#              'out3':'genstats_Gens'+str(generationsToImplement),
#              'out4':'decstats_Gens'+str(generationsToImplement),
#              'out5':'casestats_Gens'+str(generationsToImplement),
#              'out6':'numstats_Gens'+str(generationsToImplement),
#              'out7':'stats_Gens'+str(generationsToImplement)}

for key in out_files.keys():
    if generationToDropGen <= generationsToImplement:
        out_files[key] += '_GnvT'+str(generationToDropGen)
    else:
        out_files[key] += '_GnvF'
    if generationToImplementMChange <= generationsToImplement:
        out_files[key] += '_RomT'+str(generationToImplementMChange)+'_'+str(generationToImplementSChange)+'_'+str(generationToImplementAEChange)+'_'+str(generationToImplementSecondChange)
    else:
        out_files[key] += '_RomF'
    if SLAVICINFO:
        out_files[key] += '_SlavT'+str(generationToIntroduceSlavic)
    else:
        out_files[key] += '_SlavF'
    out_files[key] += '_Epochs%s_HidNodes%s_Trial%s.txt' % (str(epochs), str(hiddenNodes), str(trial))

# compute expected size

# 6 syllables with 6 potential phonemes each
stem_length = 36                                
phon_length = 11

# determine the length of the section of the input that includes this information
human_length = 8
slavic_length = 12

# determine the length of the input
inputNodes = (stem_length * phon_length) + human_length
inputNodesSlav = (stem_length * phon_length) + human_length + slavic_length


# Gender variables (unit vectors in three dimensions)
[m, f, n] = map(tuple, numpy.identity(3, int))

# Declension, Number and Case variables (unit vectors in 5 dimensions)
[d1, d2, d3, d4, d5] = map(tuple, numpy.identity(5, int))

# Manually change cases to reflect semantics
[nom, acc, gen] = map(tuple, numpy.identity(3, int))

nom = (1, 0, 0)
acc = (1, 1, 0)
gen = (1, 1, 1)

# Indicator of singular or plural (unit vectors in two dimensions)
[sg, pl] = map(tuple, numpy.identity(2, int))
# @tyler why not just use one bit--0 or 1 ?


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

decnum_to_declension = {str(key): eval('d' + str(key)) for key in range(1, 6)} 

# map numbers to roman
decnum_to_roman = {
    '1': 'I',
    '2': 'II',
    '3': 'III',
    '4': 'IV',
    '5': 'V'
}

# Map roman numerals to declensions
declensions = {value: decnum_to_declension[key] for key, value in decnum_to_roman.iteritems()}

# Map tuples back to declensions
tup_to_dec = invert(declensions)

# map tuples back to non-roman numbers
tup_to_decnum = {invert(decnum_to_roman)[key]: value for key, value in declensions.iteritems()}

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

# map number back to tuple
tup_to_num = invert(num)


# Human dictionary for assigning input values
input_human = {
    "mh": (1,) * (human_length / 2) + (0,) * (human_length / 2),
    "fh": (0,) * (human_length / 2) + (1,) * (human_length / 2),
    "m": (0,) * human_length,
    "f": (0,) * human_length,
    "n": (0,) * human_length
}

# pre-build usefule tuples
slavic_1 = (1,) * (slavic_length / 3)
slavic_0 = (0,) * (slavic_length / 3)

# Gender dictionary for assigning Slavic values
input_slavic = {
    "m": slavic_1 + slavic_0 * 2,
    "f": slavic_0 + slavic_1 + slavic_0,
    "n": slavic_0 * 2 + slavic_1
}

# Dictionary for predicting outcome values
outputs = {
    # Instead of justadding the gender dictionary, we modify them here 
    "m": m,                            
    "mh": m,
    "f": f,
    "fh": f,
    # @ TYLER IS THIS RIGHT?
    "n": n,
}

# Insert the rest of the computed dictionaries
outputs.update(cases)
outputs.update(decnum_to_declension)
outputs.update(num)                            

# Adjust frequencies depending on case and human/nonhuman

# First numbers are the original human case frequencies that Polinsky and Van Everbroeck implemented
human_case_freq = {
    "nomsg": 4, 
    "nompl": 2, 
    "accsg": 7, 
    "accpl": 2, 
    "gensg": 2, 
    "genpl": 1 
}

nhuman_case_freq = {
    "nomsg": 4,
    "nompl": 2,
    "accsg": 7,
    "accpl": 2,
    "gensg": 2,
    "genpl": 1
}

# The output dictionary should map (418) tuples to (3) tuples

# corpus contains every word mapped to its latin gender
corpus = {}

# frequencies contains every word mapped to its frequency
frequencies = {}

# Map phonemes to Jakobson, Fant, Halle values (1952)
phonemes = {
    "p": (-0.9, 0.9, -0.9, -0.9, -0.9, -0.9, 0.9, -0.9, 0.9, -0.9, 0.9),
    "t": (-0.9, 0.9, -0.9, -0.9, -0.9, -0.9, 0.9, -0.9, -0.9, -0.9, 0.9),
    "k": (-0.9, 0.9, -0.9, -0.9, -0.9, -0.9, -0.9, -0.9, 0.9, -0.9, 0.9),
    "b": (-0.9, 0.9, 0.9, -0.9, -0.9, -0.9, 0.9, -0.9, 0.9, -0.9, -0.9),
    "d": (-0.9, 0.9, 0.9, -0.9, -0.9, -0.9, 0.9, -0.9, -0.9, -0.9, -0.9),
    "g": (-0.9, 0.9, 0.9, -0.9, -0.9, -0.9, 0.9, -0.9, 0.9, -0.9, -0.9),
    "f": (-0.9, 0.9, -0.9, 0.9, 0.9, -0.9, 0.9, -0.9, 0.9, -0.9, 0.9),
    "v": (-0.9, 0.9, 0.9, 0.9, 0.9, -0.9, 0.9, -0.9, 0.9, -0.9, -0.9),
    "s": (-0.9, 0.9, -0.9, 0.9, 0.9, -0.9, 0.9, -0.9, -0.9, -0.9, 0.9),
    "z": (-0.9, 0.9, 0.9, 0.9, 0.9, -0.9, 0.9, -0.9, -0.9, -0.9, -0.9),
    "h": (-0.9, 0.9, -0.9, 0.9, -0.9, -0.9, -0.9, -0.9, 0.9, -0.9, 0.9),
    "m": (-0.9, 0.9, 0.9, -0.9, -0.9, 0.9, 0.9, -0.9, 0.9, -0.9, -0.9),
    "n": (-0.9, 0.9, 0.9, -0.9, -0.9, 0.9, 0.9, -0.9, -0.9, -0.9, -0.9),
    "w": (-0.9, -0.9, 0.9, 0.9, -0.9, -0.9, -0.9, -0.9, 0.9, 0.9, -0.9),
    "r": (-0.9, -0.9, 0.9, 0.9, -0.9, -0.9, 0.9, -0.9, -0.9, -0.9, -0.9),
    "l": (0.9, 0.9, 0.9, 0.9, -0.9, -0.9, 0.9, -0.9, -0.9, -0.9, -0.9),
    "y": (-0.9, -0.9, 0.9, 0.9, -0.9, -0.9, -0.9, -0.9, -0.9, -0.9, -0.9),
    "i": (0.9, -0.9, 0.9, 0.9, -0.9, -0.9, 0.9, -0.9, -0.9, -0.9, -0.9),    # (wick)
    "u": (0.9, -0.9, 0.9, 0.9, -0.9, -0.9, 0.9, -0.9, 0.9, 0.9, 0.9),   # (woo)
    "e": (0.9, -0.9, 0.9, 0.9, -0.9, -0.9, -0.9, -0.9, -0.9, -0.9, -0.9),  # (wed)
    "o": (0.9, -0.9, 0.9, 0.9, -0.9, -0.9, -0.9, 0.9, 0.9, 0.9, -0.9),  # (cot)
    "a": (0.9, -0.9, 0.9, 0.9, -0.9, -0.9, -0.9, 0.9, 0.9, -0.9, 0.9),  # (card)
    "*": (0.9, -0.9, 0.9, 0.9, -0.9, -0.9, 0.9, -0.9, 0.9, -0.9, -0.9),     # (about)
    "-": (0,) * 11
}


def print_phons_pretty(*args):
    return tuple([phonemes[arg] for arg in args])


# turn a syllable into its phonemic representation
# takes a six tuple
def print_phons((a, b, c, d, e, f)):
    return print_phons_pretty(a, b, c, d, e, f)
    return(phonemes[a] + phonemes[b] + phonemes[c] + phonemes[d] + phonemes[e] + phonemes[f])


def manipulateForMSoundChange(*args):
    last_syllable = args[-1]
    next_to_last_syllable = args[-2]

    def change(s):
        if s[-1] is "m":
            s = s[:-1] + "-"
        return s

    # truncates the final letter
    # if no final syllable
    if last_syllable is "------":
        args[-2] = change(next_to_last_syllable)
    else:
        args[-1] = change(last_syllable)
    return tuple(args)


def manipulateForSSoundChange(*args):
    def change(s):
        if s[-1] == "s":
            s = s[:-1] + "-"

    if args[-1] is "------":
        args[-2] = change(args[-2])
    else:
        args[-1] = change(args[-1])
    return tuple(args)


def manipulateForAESoundChange(s1, s2, s3, s4, s5, s6):
    if s6 == "------":
        return(s1, s2, s3, s4, findFinalVowel2(s5), s6)
    else:
        return(s1, s2, s3, s4, s5, findFinalVowel2(s6))       


def manipulateForSecondSoundChange(s1, s2, s3, s4, s5, s6):
    if s6 == "------":
        return(s1, s2, s3, s4, findFinalVowel(s5), s6)
    else:
        return(s1, s2, s3, s4, s5, findFinalVowel(s6))


def findFinalVowel(syllable):
    syllableArray = list(syllable)
    syllableArray.reverse()
    for i, character in enumerate(syllableArray):
        if character != '-':
            if character == 'u' or character == 'i':
                syllableArray[i] = '-'
                break
    syllableArray.reverse()
    return "".join(syllableArray)


def findFinalVowel2(syllable):
    syllableArray = list(syllable)
    syllableArray.reverse()
    for i in range(len(syllableArray)):
        if syllableArray[i] != "-":
            if syllableArray[i] == "i":
                if syllableArray[i+1] == "a":
                    syllableArray[i:i+2] = "ee"
                    break
    syllableArray.reverse()
    return "".join(syllableArray)
