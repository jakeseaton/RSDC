import objects
import constants
from constants import FILENAMETOCONVERT


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
                                currentToken.addCase(case, currentCase)
        return result
