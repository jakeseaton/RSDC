import objects
import constants


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

                                # moved all of this functionality to the Token object
                                currentToken.updateCounters(case, counters)
        return (result, counters)
