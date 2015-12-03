import objects
import constants

rows_variables = ['word', 'latinGender', 'maxFrequency', 'max10k', 'logMax', 'slavicGender', 'romanianGender', 'declension']
def convert_to_input(file1):
        # aray of token objects
        result = []

        #initialize bag of counters
        counters = objects.CounterBag()

        reader = open(file1, 'rU')

        for row in reader.readlines():
                # If this is the start of a new word
                if row[0] == "_":
                        # increment counters
                        counters.tokensCounter.increment()

                        # uncomment with new latin corpus
                        row_arr = row.strip('\n').split("\t")[1:]

                        row_dict = {constants.row_order[i]: value for i, value in enumerate(row_arr)}

                        currentToken = objects.Token(**row_dict)

                        if row_dict['latinGender'][-1] == 'h':
                                currentToken.human = True

                        # only return a token if we have all necessary info.
                        if currentToken.almostComplete():
                                result.append(currentToken)
                else:
                        # only calculate cases if token is complete
                        if currentToken.almostComplete():
##                      if currentToken.isComplete(): # We can calculate the Romanian accuracy anyway
                                [s1, s2, s3, s4, s5, s6, case, suf, dem, adj] = row.split("\t")
                                syllables = (s1, s2, s3, s4, s5, s6)
                                # initialize case
                                currentCase = objects.Case(currentToken, syllables, case, adj)
##                              # set syllables

##                              currentCase.setSyllables(generation, s1, s2, s3, s4, s5, s6)
                                # add to current token
##                              print (currentCase.modWord, currentCase.word)
                                currentToken.addCase(case, currentCase)
                                # Increment counters for Latin gender, Slavic gender, and Romanian gender
                                if logMax != '?': 
                                        counters.freqCounter.increment()
                                if romanianGender != '?':
                                        counters.rominfoCounter.increment()
                                        if romanianGender[0] == 'm': 
                                                counters.Romanian_M.increment()
                                        elif romanianGender[0] == 'f': 
                                                counters.Romanian_F.increment()
                                        elif romanianGender[0] == 'n':
                                                counters.Romanian_N.increment()
                                                # Split neuter (add to Romanian M and F count later)
                                                if case[-2:] == 'sg': 
                                                        counters.Romanian_NM.increment()
                                                elif case[-2:] == 'pl': 
                                                        counters.Romanian_NF.increment()
                                if slavicGender != '?':
                                        counters.slavinfoCounter.increment()
                                        if slavicGender[0] == 'm': 
                                                counters.Slavic_M.increment()
                                        elif slavicGender[0] == 'f': 
                                                counters.Slavic_F.increment()
                                        elif slavicGender[0] == 'n': 
                                                counters.Slavic_N.increment()
                                if latinGender[0] == 'm':
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
                                elif latinGender[0] == 'f':
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
                                elif latinGender[0] == 'n': #probably else but just in case
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
        return (result, counters)
