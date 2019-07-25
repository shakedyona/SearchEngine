import configparser

from nltk.stem.snowball import EnglishStemmer

terms_previously_read = {} # [parse_term] = stemming_term
terms_previously_read_without_stemming = {} # [term] = freq only needed stemming
dic_upper_term_stemming = {} # [stemming_term] = 1
stemmer = EnglishStemmer()

def stemming(parse_terms_doc,stemming_mode):

    #parse_terms_doc = {'POLITICIANS': [1, False, '0'], 'PARTY': [1, False, '1'],'mar': [1, True, '0'], 'Mar': [1, False, '0'], 'MAR': [1, False, '0'], '10.00': [1, False, '609'], 'birth': [1, True, '479'],'Policies': [1, False, '479'],'Polici': [1, False, '479'],'polici': [1, True, '479']}
    result_stamming = {} # [stemming_term] = freq
    if stemming_mode == 'yes':
        for term,arr in parse_terms_doc.items():
            freq = arr[0]
            stemm_bool =arr[1]
            position = arr[2]
            if term[0].isupper():
                term = term.upper()
            if stemm_bool:
                if term in terms_previously_read:
                    stemming_word = terms_previously_read[term]
                    if stemming_word in result_stamming:
                        curr_freq = result_stamming[stemming_word][0]
                        curr_position = result_stamming[stemming_word][1]
                        result_stamming[stemming_word] = (curr_freq + freq, str(curr_position) + "|" + str(position))
                    else:
                        result_stamming[stemming_word] = (freq,position)

                    dic_upper_term_stemming[stemming_word] = 1

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

                    dic_upper_term_stemming[new_stem] = 1

                    if new_stem in result_stamming:
                        curr_freq = result_stamming[new_stem][0]
                        curr_position = result_stamming[new_stem][1]
                        result_stamming[new_stem] = (curr_freq + freq, str(curr_position) + "|" + str(position))
                    else:
                        result_stamming[new_stem] = (freq,position)
            else:
                #print(term)
                if term[0].isupper():
                    term = term.upper()

                if term in result_stamming:
                    curr_freq = result_stamming[term][0]
                    curr_position = result_stamming[term][1]
                    result_stamming[term] = (curr_freq + freq, str(curr_position) + "|" + str(position))

                else:
                    result_stamming[term] = (freq,position)


    elif stemming_mode == 'no':
        result_stamming = {}  # [stemming_term] = freq

        for term, arr in parse_terms_doc.items():
            freq = arr[0]
            position = arr[2]
            if term[0].isupper():
                term = term.upper()
            if term in terms_previously_read_without_stemming:
                if term in result_stamming:
                    curr_freq = result_stamming[term][0]
                    curr_position = result_stamming[term][1]
                    result_stamming[term] = (curr_freq + freq, str(curr_position) + "|" + str(position))

                else:
                    result_stamming[term] = (freq,position)
            else:
                terms_previously_read_without_stemming[term] = freq
                if term in result_stamming:
                    curr_freq = result_stamming[term][0]
                    curr_position = result_stamming[term][1]
                    result_stamming[term] = (curr_freq + freq, str(curr_position) + "|" + str(position))
                else:
                    result_stamming[term] = (freq,position)

    return result_stamming


def get_dictionary():
    return terms_previously_read


def get_dictionary_without_stemming():
    return terms_previously_read_without_stemming


def get_dictionary_value():
    return dic_upper_term_stemming


def reset():
    print("reset - stemmer")
    terms_previously_read.clear()
    terms_previously_read_without_stemming.clear()
    dic_upper_term_stemming.clear()
