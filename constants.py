SLAVICINFO = False                                      # This variable tells us whether to introduce Slavic information or not
includeSlavic = SLAVICINFO
FILENAMETOCONVERT = "latin_corpus.txt"
declension_file = "declensions.txt"
generationsToImplement = 15                            # 48 to show time between 400AD and 1600AD (25 years to a generation)
generationToImplementMChange = 31                       # 2 to show early loss
generationToImplementSChange = 31                       # 6 to show between 2nd and 3rd century (dropped 2nd-3rd century)
generationToImplementAEChange = 31                      # 8 to show latter part of 300AD (standard in latter part of 2nd century and before 4th)
generationToImplementSecondChange = 31                  # 15 to show halfway point (idealized)
generationToIntroduceSlavic = 18                        # 18 (--> 34) to show Slavs coming in approximately 850AD
generationToDropGen = 8                                 # Drop at 8 (3rd century AD)
epochs = 3                                              # EzraPolinsky uses 3, HareEllman uses 10
hiddenNodes = 30                                        # EzraPolinsky uses 30, HareEllman uses 10 for the first layer
hiddenNodes2 = 8                                        # HareEllman uses 8 for the second layer
outputNodes = 13                                        # Gender (3), Declension (5), Case (3), Number (2)
trial = 16                                               # Trial number


out_files = {'out1':'trackchange_Gens'+str(generationsToImplement),
             'out2':'info_Gens'+str(generationsToImplement),
             'out3':'genstats_Gens'+str(generationsToImplement),
             'out4':'decstats_Gens'+str(generationsToImplement),
             'out5':'casestats_Gens'+str(generationsToImplement),
             'out6':'numstats_Gens'+str(generationsToImplement),
             'out7':'stats_Gens'+str(generationsToImplement)}

for i in range(1,len(out_files.keys())+1):
        if generationToDropGen <= generationsToImplement:
                out_files['out'+str(i)] += '_GnvT'+str(generationToDropGen)
        else:
                out_files['out'+str(i)] += '_GnvF'
        if generationToImplementMChange <= generationsToImplement:
                out_files['out'+str(i)] += '_RomT'+str(generationToImplementMChange)+'_'+str(generationToImplementSChange)+'_'+str(generationToImplementAEChange)+'_'+str(generationToImplementSecondChange)
        else:
                out_files['out'+str(i)] += '_RomF'
        if SLAVICINFO:
                out_files['out'+str(i)] += '_SlavT'+str(generationToIntroduceSlavic)
        else:
                out_files['out'+str(i)] += '_SlavF'
        out_files['out'+str(i)] += '_Epochs%s_HidNodes%s_Trial%s.txt' % (str(epochs),str(hiddenNodes),str(trial))

# compute expected size
stem_length = 36                                # 6 syllables with 6 potential phonemes each
phon_length = 11
human_length = 8
slavic_length = 12

# Gender variables
m = (1,0,0)
f = (0,1,0)
n = (0,0,1)

# Declension, Number and Case variables
d1 = (1,0,0,0,0)
d2 = (0,1,0,0,0)
d3 = (0,0,1,0,0)
d4 = (0,0,0,1,0)
d5 = (0,0,0,0,1)

nom = (1,0,0)
acc = (1,1,0)
gen = (1,1,1)
##gen = (0,1,0)
##acc = (0,0,1)

sg = (1,0)
pl = (0,1)

# Map tuples back to genders
tup_to_gen = {
        (1,0,0):'m',
        (0,1,0):'f',
        (0,0,1):'n'
        }

decnum_to_roman = {
        '1':'I',
        '2':'II',
        '3':'III',
        '4':'IV',
        '5':'V'
        }

# Map tuples back to declensions
tup_to_dec = {
        (1,0,0,0,0):'I',
        (0,1,0,0,0):'II',
        (0,0,1,0,0):'III',
        (0,0,0,1,0):'IV',
        (0,0,0,0,1):'V'
        }

# Map tuples back to case
tup_to_case = {
        (1,0,0):'nom',
##        (0,1,0):'gen',
##        (0,0,1):'acc',
        (1,1,0):'acc',
        (1,1,1):'gen'
        }

# Map tuples back to number
tup_to_num = {
        (1,0):'sg',
        (0,1):'pl',
        }

inputNodes= (stem_length * phon_length) + human_length
inputNodesSlav = (stem_length * phon_length) + human_length + slavic_length


# Human dictionary for assigning input values
input_human = {
	"mh":(1,1,1,1,0,0,0,0),
	"fh":(0,0,0,0,1,1,1,1),
	"m":(0,0,0,0,0,0,0,0),
        "f":(0,0,0,0,0,0,0,0),
        "n":(0,0,0,0,0,0,0,0)
}

# Gender dictionary for assigning Slavic values
input_slavic = {
	"m":(1,1,1,1,0,0,0,0,0,0,0,0),
	"f":(0,0,0,0,1,1,1,1,0,0,0,0),
        "n":(0,0,0,0,0,0,0,0,1,1,1,1)
}

# Gender dictionary for predicting outcome values
outputs = {
	"m":(1,0,0),                            # Genders
        "mh":(1,0,0),
	"f":(0,1,0),
        "fh":(0,1,0),
	"n":(0,0,1),                            
        "1":(1,0,0,0,0),                        # Declensions
        "2":(0,1,0,0,0),
        "3":(0,0,1,0,0),
        "4":(0,0,0,1,0),
        "5":(0,0,0,0,1),
        "nom":(1,0,0),                          # Case
##        "gen":(0,1,0),
##        "acc":(0,0,1),
        "acc":(1,1,0),
        "gen":(1,1,1),
        "sg":(1,0),                             # Number
        "pl":(0,1)
}

# Adjust frequencies depending on case and human/nonhuman

# First numbers are the original human case frequencies that Polinsky and Van Everbroeck implemented
human_case_freq = {
	"nomsg" : 4, #8
	"nompl" : 2, #3
	"accsg" : 7, #4 #we'll implement the random addition at runtime
	"accpl" : 2, #2 #we'll implement the random addition at runtime
	"gensg" : 2, #4
	"genpl" : 1, #2
}
nhuman_case_freq = {
	"nomsg" : 4,
	"nompl" : 2,
	"accsg" : 7,
	"accpl" : 2,
	"gensg" : 2,
	"genpl" : 1,
}

# The output dictionary should map (418) tuples to (3) tuples

# corpus contains every word mapped to its latin gender
corpus = {}

# frequencies contains every word mapped to its frequency
frequencies = {}

# Dictonary/hashtable that maps phonemes to chomsky values
phonemes = {
	"p" : (-0.9, 0.9, -0.9, -0.9, -0.9, -0.9, 0.9, -0.9, 0.9, -0.9, 0.9),
	"t" : (-0.9, 0.9, -0.9, -0.9, -0.9, -0.9, 0.9, -0.9, -0.9, -0.9, 0.9),
	"k" : (-0.9, 0.9, -0.9, -0.9, -0.9, -0.9, -0.9, -0.9, 0.9, -0.9, 0.9),
	"b" : (-0.9, 0.9, 0.9, -0.9, -0.9, -0.9, 0.9, -0.9, 0.9, -0.9, -0.9),
	"d" : (-0.9, 0.9, 0.9, -0.9, -0.9, -0.9, 0.9, -0.9, -0.9, -0.9, -0.9),
	"g" : (-0.9, 0.9, 0.9, -0.9, -0.9, -0.9, 0.9, -0.9, 0.9, -0.9, -0.9),
	"f" : (-0.9, 0.9, -0.9, 0.9, 0.9, -0.9, 0.9, -0.9, 0.9, -0.9, 0.9),
	"v" : (-0.9, 0.9, 0.9, 0.9, 0.9, -0.9, 0.9, -0.9, 0.9, -0.9, -0.9),
	"s" : (-0.9, 0.9, -0.9, 0.9, 0.9, -0.9, 0.9, -0.9, -0.9, -0.9, 0.9),
        "z" : (-0.9, 0.9, 0.9, 0.9, 0.9, -0.9, 0.9, -0.9, -0.9, -0.9, -0.9),
	"h" : (-0.9, 0.9, -0.9, 0.9, -0.9, -0.9, -0.9, -0.9, 0.9, -0.9, 0.9),
	"m" : (-0.9, 0.9, 0.9, -0.9, -0.9, 0.9, 0.9, -0.9, 0.9, -0.9, -0.9),
	"n" : (-0.9, 0.9, 0.9, -0.9, -0.9, 0.9, 0.9, -0.9, -0.9,-0.9, -0.9),
	"w" : (-0.9, -0.9, 0.9, 0.9, -0.9, -0.9, -0.9, -0.9, 0.9, 0.9, -0.9),
	"r" : (-0.9, -0.9, 0.9, 0.9, -0.9, -0.9, 0.9, -0.9, -0.9, -0.9, -0.9),
	"l" : (0.9, 0.9, 0.9, 0.9, -0.9, -0.9, 0.9, -0.9, -0.9, -0.9, -0.9),
	"y" : (-0.9, -0.9, 0.9, 0.9, -0.9, -0.9, -0.9, -0.9, -0.9, -0.9, -0.9),
	"i" : (0.9, -0.9, 0.9, 0.9, -0.9, -0.9, 0.9, -0.9, -0.9, -0.9, -0.9),	#(wick)
	"u" : (0.9, -0.9, 0.9, 0.9, -0.9, -0.9, 0.9, -0.9, 0.9, 0.9, 0.9),	#(woo)
	"e" : (0.9, -0.9, 0.9, 0.9, -0.9, -0.9, -0.9, -0.9, -0.9, -0.9, -0.9),  #(wed)
	"o" : (0.9, -0.9, 0.9, 0.9, -0.9, -0.9, -0.9, 0.9, 0.9, 0.9, -0.9),	#(cot)
	"a" : (0.9, -0.9, 0.9, 0.9, -0.9, -0.9, -0.9, 0.9, 0.9, -0.9, 0.9),	#(card)
	"*" : (0.9, -0.9, 0.9, 0.9, -0.9, -0.9, 0.9, -0.9, 0.9, -0.9, -0.9),	#(about)
	"-" : (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
}

# turn a syllable into its phonemic representation
# takes a six tuple
def print_phons((a,b,c,d,e,f)):
	return(phonemes[a] + phonemes[b] + phonemes[c] + phonemes[d] + phonemes[e] + phonemes[f])

##def manipulateForFirstSoundChange(s1,s2,s3,s4,s5,s6):
##	# truncates the final letter
##	# if no final syllable
##	if s6 == "------":
##		# check for end of m or s
##		if s5[5] == "m" or s5[5] == "s":
##			s5 = s5[0:5] + "-"
##	# else
##	else:
##		# check for end of m or s
##		if s6[5]== "m" or s6[5] == "s":
##			s6 = s6[0:5] + "-"
##	return s1, s2, s3, s4, s5, s6

def manipulateForMSoundChange(s1,s2,s3,s4,s5,s6):
	# truncates the final letter
	# if no final syllable
	if s6 == "------":
		# check for end of m or s
		if s5[5] == "m":
			s5 = s5[0:5] + "-"
	# else
	else:
		# check for end of m or s
		if s6[5]== "m":
			s6 = s6[0:5] + "-"
	return s1, s2, s3, s4, s5, s6

def manipulateForSSoundChange(s1,s2,s3,s4,s5,s6):
	# truncates the final letter
	# if no final syllable
	if s6 == "------":
		# check for end of m or s
		if s5[5] == "s":
			s5 = s5[0:5] + "-"
	# else
	else:
		# check for end of m or s
		if s6[5] == "s":
			s6 = s6[0:5] + "-"
	return s1, s2, s3, s4, s5, s6

def manipulateForAESoundChange(s1,s2,s3,s4,s5,s6):
	if s6 == "------":
		return(s1, s2, s3, s4, findFinalVowel2(s5), s6)
	else:
		return(s1, s2, s3, s4, s5, findFinalVowel2(s6))       

def manipulateForSecondSoundChange(s1,s2,s3,s4,s5,s6):
	if s6 == "------":
		return(s1, s2, s3, s4, findFinalVowel(s5), s6)
	else:
		return(s1, s2, s3, s4, s5, findFinalVowel(s6))

def findFinalVowel(syllable):
	syllableArray = list(syllable)
	syllableArray.reverse()
	for i in range(len(syllableArray)):
		if syllableArray[i] != "-":
			if syllableArray[i] == "u" or syllableArray[i] == "i":
				syllableArray[i] = "-"
			syllableArray.reverse()
			return "".join(syllableArray)
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
			syllableArray.reverse()
			return "".join(syllableArray)
	syllableArray.reverse()
	return "".join(syllableArray)
