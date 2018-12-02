import configparser
'''
from nltk.stem.snowball import EnglishStemmer

terms_previously_read = {} # [parse_term] = stemming_term
terms_previously_read_without_stemming = {} # [term] = freq only needed stemming

stemmer = EnglishStemmer()

def stemming(parse_terms_doc):
    config = configparser.ConfigParser()
    config.read('ViewConfig.ini')
    stemming_mode = str(config['Controller']['stemming'])
    if stemming_mode == 'yes':
        result_stamming = {}  # [stemming_term] = freq
        for term, freq in parse_terms_doc.items():

            if term in terms_previously_read:
                stemming_word = terms_previously_read[term]
                if stemming_word in result_stamming:
                    result_stamming[stemming_word] = result_stamming[stemming_word] + freq
                else:
                    result_stamming[stemming_word] = freq
            else:
                term_splite = term.split(" ")
                number_of_word_in_term = len(term_splite)
                # if this one word:
                if (number_of_word_in_term == 1):
                    new_stem = stemmer.stem(term)
                # if this more then one word:
                else:
                    whole_stem = ""
                    for word in term_splite:
                        if word in terms_previously_read:
                            stem = terms_previously_read[word]
                        else:
                            stem = stemmer.stem(word)
                            terms_previously_read[word] = stem
                        whole_stem = whole_stem + stem + " "
                    new_stem = whole_stem.rstrip()

                terms_previously_read[term] = new_stem

                if new_stem in result_stamming:
                    result_stamming[new_stem] = result_stamming[new_stem] + freq
                else:
                    result_stamming[new_stem] = freq

    elif stemming_mode == 'no': #################################################################################################
        result_stamming = {}  # [stemming_term] = freq
        for term, freq in parse_terms_doc.items():
        #for term, arr in parse_terms_doc.items():
         #   freq = arr[0]
          #  stemm_bool = arr[1]
           # if stemm_bool:
                if term in terms_previously_read_without_stemming:
                    if term in result_stamming:
                        result_stamming[term] = result_stamming[term] + freq
                    else:
                        result_stamming[term] = freq
                else:
                    terms_previously_read_without_stemming[term] = freq
                    if term in result_stamming:
                        result_stamming[term] = result_stamming[term] + freq
                    else:
                        result_stamming[term] = freq
            # else:
            #     # print(term)
            #     if term in result_stamming:
            #         result_stamming[term] = result_stamming[term] + freq
            #     else:
            #         result_stamming[term] = freq
    print(result_stamming)
    print(terms_previously_read_without_stemming)
    return result_stamming


def get_dictionary():
    return terms_previously_read


def get_dictionary_without_stemming():
    return terms_previously_read_without_stemming


def reset():
    print("reset - stemmer")
    terms_previously_read.clear()
    terms_previously_read_without_stemming.clear()
'''

import configparser
from nltk.stem.snowball import EnglishStemmer

terms_previously_read = {} # [parse_term] = stemming_term
terms_previously_read_without_stemming = {} # [term] = freq only needed stemming
stemmer = EnglishStemmer()

def stemming(parse_terms_doc,stemming_mode):
    result_stamming = {} # [stemming_term] = freq
    if stemming_mode == 'yes':
        for term,arr in parse_terms_doc.items():
            freq = arr[0]
            stemm_bool =arr[1]
            # if term=="Thank": ###########################################################
            #     print(stemm_bool)
            #     print("Thank")
            # if term=="The": ###########################################################
            #     print(stemm_bool)
            #     print("The")
            if term[0].isupper():
                term = term.upper()
            if stemm_bool:
                if term in terms_previously_read:
                    stemming_word = terms_previously_read[term]
                    if stemming_word in result_stamming:
                        result_stamming[stemming_word] = result_stamming[stemming_word] + freq
                    else:
                        result_stamming[stemming_word] = freq
                else:
                    term_splite = term.split(" ")
                    number_of_word_in_term = len(term_splite)
                    # if this one word:
                    if(number_of_word_in_term == 1):
                        new_stem = stemmer.stem(term)
                    # if this more then one word:
                    else:
                        whole_stem = ""
                        for word in term_splite:
                            if word in terms_previously_read:
                                stem = terms_previously_read[word]
                            else:
                                stem = stemmer.stem(word)
                                terms_previously_read[word] = stem
                            whole_stem = whole_stem + stem + " "
                        new_stem = whole_stem.rstrip()

                    terms_previously_read[term] = new_stem

                    if new_stem in result_stamming:
                        result_stamming[new_stem] = result_stamming[new_stem] + freq
                    else:
                        result_stamming[new_stem] = freq
            else:
                #print(term)
                if term[0].isupper():
                    term = term.upper()
                if term in result_stamming:
                    result_stamming[term] = result_stamming[term] + freq
                else:
                    result_stamming[term] = freq

    elif stemming_mode == 'no':
        result_stamming = {}  # [stemming_term] = freq

        for term, arr in parse_terms_doc.items():
            freq = arr[0]
            if term[0].isupper():
                term = term.upper()
            if term in terms_previously_read_without_stemming:
                if term in result_stamming:
                    result_stamming[term] = result_stamming[term] + freq
                else:
                    result_stamming[term] = freq
            else:
                terms_previously_read_without_stemming[term] = freq
                if term in result_stamming:
                    result_stamming[term] = result_stamming[term] + freq
                else:
                    result_stamming[term] = freq

    return result_stamming


def get_dictionary():
    return terms_previously_read

def get_dictionary_without_stemming():
    return terms_previously_read_without_stemming


def reset():
    print("reset - stemmer")
    terms_previously_read.clear()
    terms_previously_read_without_stemming.clear()
