
from nltk.stem.snowball import EnglishStemmer

terms_previously_read = {} # [parse_term] = stemming_term
stemmer = EnglishStemmer()

def stemming(parse_terms_doc):
    result_stamming = {} # [stemming_term] = freq
    for term,freq in parse_terms_doc.items():
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

    return result_stamming
    

def reset():
    print("reset - stemmer")
    terms_previously_read = {}  # [parse_term] = stemming_term
    stemmer = EnglishStemmer()