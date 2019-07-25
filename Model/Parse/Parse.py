
# import configparser

from Controller import Controller

# config = configparser.ConfigParser()
# config.read('config.ini')
date_characters = {'st', 'nd', 'rd', 'th'}
dictionary_Letters ={'A' ,'B' ,'C' ,'D' ,'E' ,'F' ,'G' ,'H' ,'I' ,'J' ,'K' ,'L' ,'M' ,'N' ,'O' ,'P' ,'Q' 'R' ,'S' ,'T' ,'U' ,'V' ,'W' ,'X' ,'Y' ,'Z' ,'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h','i', 'j', 'k', 'l','m','n','o','p', 'q','r','s','t','u','v','w','x','y','z'}
dictionary_month_name_to_numbers = {'january': '01', 'jan': '01', 'february': '02', 'feb': '02', 'march': '03', 'mar': '03', 'april': '04',
                                    'apr': '04', 'may': '05', 'june': '06', 'jun': '06', 'july': '07', 'jul': '07', 'august': '08',
                                    'aug': '08', 'september': '09', 'sep': '09', 'october': '10', 'oct': '10', 'november': '11', 'nov': '11', 'december': '12', 'dec': '12',
                                    'JANUARY': '01', 'JAN': '01', 'FEBRUARY': '02', 'FEB': '02', 'MARCH': '03', 'MAR': '03', 'APRIL': '04',
                                    'APR': '04', 'MAY': '05', 'JUNE': '06', 'JUN': '06', 'JULY': '07', 'JUL': '07', 'AUGUST': '08',
                                    'AUG': '08', 'SEPTEMBER': '09', 'SEP': '09', 'OCTOBER': '10', 'OCT': '10', 'NOVEMBER': '11', 'NOV': '11', 'DECEMBER': '12', 'DEC': '12'}
functional_characters = {'[', '(', '|', '`', ')', '?', '@', '&', '~', '+', '^', '.', '*', '=', '{', '<', ']', ';', '_', '\'', ':',
                         '#', '/', '\\', "}", '>', '$', ',', '\"', '!'}
functional_characters_inside = {'[', '(', ')', '?', '@', '~', '^' , '=', '{', '<', ']', ';', '\'',
                         '#', '/', '\\', "}", '>', '$', '\"', '!'}
months_names = {'january', 'jan', 'february', 'feb', 'march', 'mar', 'april', 'apr', 'may', 'june', 'jun', 'july', 'jul', 'august', 'aug', 'september', 'sep', 'october', 'oct', 'november', 'nov', 'december', 'dec'}
extension_of_million = {'Bn', 'bn', 'BN', 'B', "bil"}
percent_dictionary = {'percent', 'percentage', '%'}
dictionary_dollars = {"$", "Dollars", "dollars", "Dollar", "dollar"}
dictionary_M_B_T = {"Thousand", "thousand" ,"bn", "billion", "million", "trillion", "Billion", "Million", "Trillion", "BN", "bn","B" ,"m" ,"M" , "T", "t", "b" }
valid_numbers = {".", ",", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
dictionary_upper_case = {}
# clean numeric tokens - from 68.67999999 tp 68.67


def parse_query_narrative(text):
    list_of_sentences = []
    not_rel = False
    rel = True
    list_rel = []

    # Set of words that we don't want to
    words_dots = {'mr.', 'ms.', 'lt.', 'col.', 'minister.','etc.','i.e.'}
    word_remove = {'Documents','discussing','following','issues','i.e.','etc.','documents', 'document', 'discuss', 'discussing',
                                      'information', 'considered'}
    set_of_punctuations= {'[', '(', '{', '`', ')', '<', '|', '&', '~', '+', '^', '@', '*', '?', '$', '.',
                          '>', ';', '_', '\'', ':', ']', '/', '\\', "}", '!', '=', '#', ',', '\"', '-'}

    text = text.split("-")
    for item in text:
        if "not relevant:" in item :
            list_rel.append(item.replace("not relevant:",""))
            not_rel = True
            rel = False
        elif "relevant:" in item:
            rel = True
            not_rel = False
        else:
            if rel:
                list_rel.append(item)

    for item in list_rel:
        new_text = item.split()
        sentence = ''
        for word in new_text:
            one_last_char = word[-1:]
            index = 2

            while one_last_char in set_of_punctuations and len(word) >= index and one_last_char is not '.':
                one_last_char = word[-index:][0]
                index += 1

            # check if this is the end or not
            if word.count(".") > 1 and word not in word_remove:
                sentence += word + ' '

            # check if remove from sets
            elif one_last_char is '.' and word.lower() not in words_dots and word not in word_remove:
                sentence += word + ' '
                list_of_sentences.append(sentence)
                sentence = ''
            else:
                if word not in word_remove:
                    sentence += word + ' '

        if not sentence == '':
            list_of_sentences.append(sentence)

    new_narrative = ''
    for sentence in list_of_sentences:
        if "not relevant" not in sentence:
            new_narrative += " " + sentence
        elif "are relevant" in sentence:
            new_narrative += " " + sentence

    return new_narrative


def func_dictionary_upper_case():
    return dictionary_upper_case


def clean_numeric(token):
    if len(token) > 1:
        if token[-1] == "/" or token[-1] == ".":
            token = token[:-1]
    token = token.replace(',', '')
    token = ' '.join(token.split())
    token = "{:.2f}".format(float(token))
    return token


def set_stop_words_file():
    path =  Controller.get_peth_corpus() +'/'+"stop_words.txt"
    global stop_words
    with open(path) as note:
        stop_words = set(word.strip() for word in note)
'''

def set_stop_words_file():
    config = configparser.ConfigParser()
    config.read('ViewConfig.ini')
    path = str(config['Parse']['stop_words_path'])
    global stop_words
    with open(path) as note:
        stop_words = set(word.strip() for word in note)
'''
# remove all the characters like <,&,^....... and (functional_characters)
def remove_other_characters(token):
    len_token = len(token)
    while (len_token > 0) and (token[0] in functional_characters):
        token = token[1:]
        len_token = len_token-1

    while (len_token > 1) and (token[len_token-1] in functional_characters):
        token = token[:-1]
        len_token = len_token - 1

    return token


# insert token to dic terms and amount in the text
def insert_to_dictionary_terms(dictionary_terms_all_text, token, stem_mode, index_of_term):
    flag_stop_words = True
    if token in stop_words:
        flag_stop_words = False
    if token.lower() in stop_words:
        flag_stop_words = False
    if flag_stop_words:
        stem = True
        if stem_mode == 0:
            stem = False
        else:
            stem = True
        if token != '':
            if token in dictionary_terms_all_text:
                dictionary_terms_all_text[token][0] += 1
                dictionary_terms_all_text[token][2] = dictionary_terms_all_text[token][2] +"|" + str(index_of_term)
            else:
                dictionary_terms_all_text[token] = [1, stem, str(index_of_term)]


# insert the date to dic
def insert_date_to_dictionary_terms(dictionary_terms_all_text, month, day, year, index_text):
    #print("insert_to_dictionary_terms:  " + month)
    month = month.lower()
    month = dictionary_month_name_to_numbers[month]
    if len(year) == 0 and len(day) != 0:
        if len(day) == 1:
            day = "0" + day
            insert_to_dictionary_terms(dictionary_terms_all_text, day + "-" + month, 0, index_text)
        else:
            insert_to_dictionary_terms(dictionary_terms_all_text, day + "-" + month, 0, index_text)
    elif len(year) != 0:
        year_int = float(year)
        if year_int < 100 and year_int > 0:
            year = "19" + year
        if len(day) != 0:
            if len(day) == 1:
                day = "0" + day
            insert_to_dictionary_terms(dictionary_terms_all_text, day + "-" + month + "-" + year, 0, index_text)
        else:
            insert_to_dictionary_terms(dictionary_terms_all_text, year + "-" + month, 0, index_text)


def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


def parse_text(text):
    tex = text
    dictionary_terms_all_text = {}
    set_stop_words_file()
    text = text.split()
    # the index that im going to work whit
    index_text = 0
    index_last_text = len(text)
    index_last_text = index_last_text - 1

    while index_text <= index_last_text:
        token = text[index_text]
        #print("token:  " + token)
        if ',' in token:
            token_splited = token.split(',')
            token = "".join(token_splited)
        if '(' in token:
            token_splited = token.split('(')
            token = "".join(token_splited)
        if ')' in token:
            token_splited = token.split(')')
            token = "".join(token_splited)
        if '}' in token:
            token_splited = token.split('}')
            token = "".join(token_splited)
        if '{' in token:
            token_splited = token.split('{')
            token = "".join(token_splited)
        if '"' in token:
            token_splited = token.split('"')
            token = "".join(token_splited)
        # is_cleaned_suffix = token_and_bool[1] ////////////////////
        token_len = len(token)

        if token_len > 0:
            token_lower_case = token.lower()
            if token == ',':
                index_text += 1
                continue
            #  between 18 and 24
            elif token == "between" and index_text+2 < index_last_text and text[index_text+2] == "and" and text[index_text+1].isdigit() and text[index_text+3].isdigit():
                num_one = clean_numeric(text[index_text+1])
                num_two = clean_numeric(text[index_text+3])
                insert_to_dictionary_terms(dictionary_terms_all_text, num_one, 0, index_text)
                insert_to_dictionary_terms(dictionary_terms_all_text, num_two, 0, index_text)
                insert_to_dictionary_terms(dictionary_terms_all_text, num_one + "-" + num_two, 0, index_text)
                index_text += 3
            # word-word , word-word-word, number-number,
            elif "-" in token:
                i = 0
                split_token = token.split("-")
                tokens_len = len(split_token)
                while i < tokens_len:
                    if split_token[i].isdigit():
                        split_token[i] = clean_numeric(split_token[i])
                    if split_token[i] != '':
                        insert_to_dictionary_terms(dictionary_terms_all_text, split_token[i], 0, index_text)
                    i += 1
                if len(split_token) == 2 and isfloat(split_token[0]) and isfloat(split_token[1]) and split_token[0] != '' and split_token[1] != '':
                    insert_to_dictionary_terms(dictionary_terms_all_text, clean_numeric(split_token[0]) + "-" + clean_numeric(split_token[1]), 0, index_text)
                elif token_len > 0:
                    i = 1
                    sentence = split_token[0]
                    while i < tokens_len:
                        if split_token[i] != '':
                            sentence = sentence + "-" + split_token[i]
                        i += 1
                    if sentence != '':
                        insert_to_dictionary_terms(dictionary_terms_all_text, sentence, 0, index_text)
            # 2 : the token is month - october
            elif token_lower_case in months_names:
                if index_text < index_last_text:
                    # bring the next token and clean it from caracters
                    next_token = index_text + 1
                    next_token = text[next_token]
                    if next_token[-1:] ==',':
                        next_token = next_token[:-1]
                    if next_token[:1] ==',':
                        next_token = next_token[1:]
                    # 2.1 - the next token is number
                    if isfloat(next_token):
                        next_token = clean_numeric(next_token)
                        int_next_token = float(next_token)
                        # 2.1.1 - the next token is a day and there is one more token
                        if int_next_token > 0 and 32 > int_next_token and index_text+2 <= index_last_text:
                            next_next_token = index_text + 2
                            next_next_token = text[next_next_token]
                            next_next_token = remove_other_characters(next_next_token)
                            # case 1.1.1.1 - the next next token is a year
                            if (str.isnumeric(next_next_token) and int(next_next_token) > 0 and 3000 > int(next_next_token)):
                                next_next_token = str(next_next_token)
                                next_next_token = next_next_token[:-3]
                                insert_date_to_dictionary_terms(dictionary_terms_all_text, token_lower_case, next_token, next_next_token, index_text)
                                index_text += 2
                            # 1.1.1.2 - if its not a year , so we have only day and month
                            else:
                                year = ''
                                insert_date_to_dictionary_terms(dictionary_terms_all_text, token_lower_case, next_token, year, index_text)
                                index_text += 1
                        # 2.1.2 - it is a day and there is no more token
                        elif int_next_token > 0 and 32 > int_next_token and index_text+2 > index_last_text:
                            year = ''
                            insert_date_to_dictionary_terms(dictionary_terms_all_text, token_lower_case, next_token, year, index_text)
                            index_text += 1
                        # 2.1.3 if the next token is numeric and it is year (so there is no day)
                        elif int_next_token > 0 and 3000 > int_next_token:
                            year = next_token
                            year = str(year)
                            year = year[:-3]
                            day = ''
                            insert_date_to_dictionary_terms(dictionary_terms_all_text, token_lower_case, day, year, index_text)
                            index_text += 1
                        # 2.1.4 if the next token is a number but there is on day or year , jast regular number so we send the start token to dic
                        else:
                            insert_to_dictionary_terms(dictionary_terms_all_text, token_lower_case, 0, index_text)
                    # 2.2 if the next token is not a number
                    else:
                        if token_lower_case in stop_words:
                            pass
                        else:
                            insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
            # 3 - the first character is digit bun i now that is not a date
            elif token[0].isdigit() or (len(token) > 1 and token[1].isdigit()):
                # for tokens that lok like "5bm dollares" or "54m dollares"
                is_suffix_m = False
                #  verifying number

                is_valid_number = True
                word_extension = token[-2:]
                one_word_extension = token[-1:]
                # %
                amount_of_percentage_sign = 0
                amount_of_division_sign = 0
                amount_of_points = 0

                if word_extension in extension_of_million:
                    is_suffix_m = True
                    token = token[:-2]
                    if "." not in token:
                        token = token + "000"
                    else:
                        token_splited = token.split('.')
                        if len(token_splited) >1:
                            token = token_splited[0] + "000." + token_splited[1]
                        else:
                            token = token_splited[0] + "000"
                elif one_word_extension == 'm' or one_word_extension == "M":
                    is_suffix_m = True
                    token = token[:-1]
                elif word_extension == 'th':
                    token = token[:-2]
                for character in token:
                    punctuation_mark = False
                    numeric_character = character.isnumeric()
                    if character == '.' or character == '%' or character == '/' or character == ',':
                        punctuation_mark = True
                        if character == '%':
                            amount_of_percentage_sign += 1
                        if character == '/':
                            amount_of_division_sign += 1
                        if character == '.':
                            amount_of_points += 1
                    if (not numeric_character) and (not punctuation_mark):
                        is_valid_number = False

                if amount_of_points > 1:
                    is_valid_number = False
                if amount_of_division_sign > 1:
                    is_valid_number = False
                if amount_of_division_sign > 0:
                    token_split = token.split('/')
                    if not token_split[1].isnumeric():
                        is_valid_number = False
                if amount_of_percentage_sign > 1:
                    is_valid_number = False
                if amount_of_percentage_sign > 0:
                    i = 0
                    while i < (len(token) - 1):
                        if token[i] == '%':
                            is_valid_number = False
                        i += 1
                # end verify number - if the num is valid num so "is_valid_number" = True
                # 3.1 -  the case that the num is valid
                if is_valid_number:
                    slash_in_token = False
                    tok = token[len(token) - 1]
                    # 3.1.1 - the number contain '/'
                    if ('/' in token) and ('%' not in token):
                        slash_in_token = True
                        split_token = token.split('/')
                        if len(split_token) == 2 and split_token[0] != '' and split_token[0] != '' :
                            num_one = float(clean_numeric(split_token[0]))
                            num_two = float(clean_numeric(split_token[1]))
                            if num_two != 0:
                                token = "{:.2f}".format(num_one / num_two)
                                token = str(token)
                                token = clean_numeric(token)
                            else:
                                token = num_one
                                token = str(token)
                                token = clean_numeric(token)
                    # 3.1.2 - the number contain '%'
                    if tok == '%':
                        token = token[:-1]
                        if "/" not in token:
                            token = remove_other_characters(token)
                            token = clean_numeric(token)
                            # insert the word "precent" insted of "%"
                            insert_to_dictionary_terms(dictionary_terms_all_text, token + "%", 0, index_text)
                        else:
                            split_present = token.split('/')  # split the token by decimeter '/'
                            if len(split_present) == 2:  # check if it is fraction
                                num_one = float(remove_other_characters(split_present[0]))
                                num_two = float(remove_other_characters(split_present[1]))
                                if num_two != 0:
                                    token = "{:.2f}".format(num_one / num_two)
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token + "%", 0, index_text)
                                else:
                                    insert_to_dictionary_terms(dictionary_terms_all_text, "{:.2f}".format(num_one) + "%", 0, index_text)
                                    insert_to_dictionary_terms(dictionary_terms_all_text, "{:.2f}".format(num_two) + "%", 0, index_text)
                                    index_text += 1
                                    continue
                    # 3.1.4 - regular number or date or price
                    elif(len(token) >1 and token[:1] != '/' and token[-1:] != '/'):
                        token = clean_numeric(token)
                        # 3.1.4.1 - there is next token
                        if index_text < index_last_text:
                            next_token = index_text + 1
                            next_token = text[next_token]
                            next_token = remove_other_characters(next_token)
                            token_lower_case = next_token.lower()
                            if next_token in percent_dictionary:
                                token = clean_numeric(token)
                                insert_to_dictionary_terms(dictionary_terms_all_text, token + "%", 0, index_text)
                                index_text += 1
                            elif (token_lower_case in months_names) and ((str.isnumeric(token)and (0 < int(token)) and (int(token) < 32)) or (token_len > 2 and (token[-2:] in date_characters) and str.isnumeric(token[:-2]) and (0 < int(token[:-2])) and (int(token[:-2]) < 32))):
                                if token[-2:] in date_characters:
                                    token = token[:-2]
                                    token_lower_case = token.lower()
                                token_len = len(token)
                                # 1.1.1.1 - there is next next token
                                if index_text + 1 < index_last_text:
                                    next_next_token = index_text + 2
                                    next_next_token = text[next_next_token]
                                    next_next_token = remove_other_characters(next_next_token).lower()
                                    # 1.1.1.1.1 - the next next token is a year
                                    if str.isnumeric(next_next_token) and int(next_next_token) > 0 and 3000 > int(
                                            next_next_token):
                                        insert_date_to_dictionary_terms(dictionary_terms_all_text, next_token, token, next_next_token, index_text)
                                        index_text += 2
                                    # 1.1.1.1.2 - the next next token not recognis
                                    else:
                                        year = ''
                                        insert_date_to_dictionary_terms(dictionary_terms_all_text, next_token, token, year, index_text)
                                        index_text += 1
                                # 1.1.1.2 - there is no next next token
                                else:
                                    year = ''
                                    insert_date_to_dictionary_terms(dictionary_terms_all_text, next_token, token, year, index_text)
                                    index_text += 1

                            # if the next token in dollars and i have just dollar befur
                            elif next_token in dictionary_dollars:
                                token_len = len(token) - 3  # i remove the .00 in the end of the number
                                if token_len < 7:  # under million
                                    if(is_suffix_m == True):
                                        insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                    else:
                                        insert_to_dictionary_terms(dictionary_terms_all_text, token + " Dollars", 0, index_text)
                                    index_text += 1
                                else:  # beteen million to trilion 33,456,000.00 -> 33.45 M , 33,456,000.00m
                                    if (is_suffix_m == True):
                                        insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                    else:
                                        tok = token[:-9]  # 33
                                        division = token[:-7]  # 3345
                                        division = division[-2:]  # 45
                                        token = tok + '.' + division
                                        insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                    index_text += 1
                            # if the next token is B M N
                            elif next_token in dictionary_M_B_T:
                                # if there is next next token
                                if index_text + 1 < index_last_text:
                                    next_next_token = index_text + 2
                                    next_next_token = text[next_next_token]
                                    next_next_token = remove_other_characters(next_next_token)
                                    # first case - Price m/bn Dollars
                                    if next_next_token in dictionary_dollars and next_token in extension_of_million:
                                        if next_token == "million" or next_token == "Million" or next_token == "m" or next_token == "M" or next_token == "bn":
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                            index_text += 2
                                        # 100.22 billion dollars
                                        elif next_token == "billion" or next_token == "Billion" or next_token == "B" or next_token == "b":
                                            tok = token[-2:]  # 22
                                            token = token[:-3]  # 100
                                            token = token + tok + "000.00"
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                            index_text += 2
                                        elif next_token == "trillion" or next_token == "Trillion" or next_token == "T" or next_token == "t":
                                            tok = token[-2:]  # 22
                                            token = token[:-3]  # 100
                                            token = token + tok + "000000.00"
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                            index_text += 2
                                    # chack if it is - 45 million u.s dollars
                                    elif index_text + 2 < index_last_text:
                                        next_next_next_token = index_text + 3
                                        next_next_next_token = text[next_next_next_token]
                                        next_next_next_token = remove_other_characters(next_next_next_token)
                                        # first case - Price m/bn U.S Dollars
                                        if next_next_next_token in dictionary_dollars and next_next_token == "U.S":
                                            if next_token == "million" or next_token == "Million" or next_token == "m" or next_token == "M" or next_token == "bn":
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                                index_text += 3
                                            # 100.22 billion dollars
                                            elif next_token == "billion" or next_token == "Billion" or next_token == "B" or next_token == "b":
                                                tok = token[-2:]  # 22
                                                token = token[:-3]  # 100
                                                token = token + tok + "000.00"
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                                index_text += 3
                                            elif next_token == "Trillion" or next_token == "trillion" or next_token == "T" or next_token == "t":
                                                tok = token[-2:]  # 22
                                                token = token[:-3]  # 100
                                                token = token + tok + "000000.00"
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                                index_text += 3
                                        # 13 M ___ ____ - not dollar
                                        else:
                                            if next_token == "thousand" or next_token == "Thousand":
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + "K", 0, index_text)
                                                index_text += 1
                                            if next_token == "million" or next_token == "Million" or next_token == "m" or next_token == "M" or next_token == "bn":
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + "M", 0, index_text)
                                                index_text += 1
                                            # 100.22 billion dollars
                                            elif next_token == "billion" or next_token == "Billion" or next_token == "B" or next_token == "b":
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + "B", 0, index_text)
                                                index_text += 1
                                            # 100.22 trillion dollars
                                            elif next_token == "trillion" or next_token == "Trillion" or next_token == "T" or next_token == "t":
                                                tok = token[-2:]  # 22
                                                token = token[:-3]  # 100
                                                token = token + tok + ".00"
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + "B", 0, index_text)
                                                index_text += 1
                                    else:  # there is no next next next
                                        if next_token == "thousand" or next_token == "Thousand":
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + "K", 0, index_text)
                                            index_text += 1
                                        if next_token == "million" or next_token == "Million" or next_token == "m" or next_token == "M" or next_token == "bn":
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + "M", 0, index_text)
                                            index_text += 1
                                        # 100.22 billion dollars
                                        elif next_token == "billion" or next_token == "Billion" or next_token == "B" or next_token == "b":
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + "B", 0, index_text)
                                            index_text += 1
                                        # 100.22 trillion dollars
                                        elif next_token == "trillion" or next_token == "Trillion" or next_token == "T" or next_token == "t":
                                            tok = token[-2:]  # 22
                                            token = token[:-3]  # 100
                                            token = token + tok + ".00"
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + "B", 0, index_text)
                                            index_text += 1
                                else:
                                    if next_token == "thousand" or next_token == "Thousand":
                                        insert_to_dictionary_terms(dictionary_terms_all_text, token + "K", 0, index_text)
                                        index_text += 1
                                    if next_token == "million" or next_token == "Million" or next_token == "m" or next_token == "M" or next_token == "bn":
                                        insert_to_dictionary_terms(dictionary_terms_all_text, token + "M", 0, index_text)
                                        index_text += 1
                                    # 100.22 billion dollars
                                    elif next_token == "billion" or next_token == "Billion" or next_token == "B" or next_token == "b":
                                        insert_to_dictionary_terms(dictionary_terms_all_text, token + "B", 0, index_text)
                                        index_text += 1
                                    # 100.22 trillion dollars
                                    elif next_token == "trillion" or next_token == "Trillion" or next_token == "T" or next_token == "t":
                                        tok = token[-2:]  # 22
                                        token = token[:-3]  # 100
                                        token = token + tok + ".00"
                                        insert_to_dictionary_terms(dictionary_terms_all_text, token + "B", 0, index_text)
                                        index_text += 1
                            # 5 5/6 DOLLARS
                            elif(slash_in_token == False and '/' in next_token):
                                split_next_token = next_token.split('/')
                                if len(split_next_token) == 2:
                                    if isfloat(split_next_token[0]) and isfloat(split_next_token[1]):
                                        num_one = float(split_next_token[0])
                                        num_two = float(split_next_token[1])
                                        if num_two != 0:
                                            next_token = "{:.2f}".format(num_one / num_two)
                                            if (isfloat(next_token) and float(next_token) < 1):
                                                if index_text + 1 < index_last_text:
                                                    next_next_token = index_text + 2
                                                    next_next_token = text[next_next_token]
                                                    next_next_token = remove_other_characters(next_next_token)
                                                    # first case - 45 2/3 Dollars
                                                    if next_next_token in dictionary_dollars:
                                                        insert_to_dictionary_terms(dictionary_terms_all_text, token +" "+ next_token + " Dollars", 0, index_text)
                                                        index_text += 2
                                                    else:
                                                        insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                                                else:
                                                    insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                                            else:
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                                        else:
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                                    else:
                                        insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                            else:  # 34 ___ - not recognize
                                # the case $45 or 45$
                                if token[-1:] == "$":
                                    token = token[:-1]
                                    token = clean_numeric(token)
                                    token_len = len(token) - 3  # i remove the .00 in the end of the number
                                    if index_text < index_last_text:
                                        next_token = index_text + 1
                                        next_token = text[next_token]
                                        next_token = remove_other_characters(next_token)
                                        if next_token in dictionary_M_B_T:
                                            if next_token == "million" or next_token == "Million" or next_token == "m" or next_token == "M" or next_token == "bn":
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                                index_text += 3
                                            # 100.22 billion dollars
                                            elif next_token == "billion" or next_token == "Billion" or next_token == "B" or next_token == "b":
                                                tok = token[-2:]  # 22
                                                token = token[:-3]  # 100
                                                token = token + tok + "000.00"
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                                index_text += 3
                                            elif next_token == "Trillion" or next_token == "trillion" or next_token == "T" or next_token == "t":
                                                tok = token[-2:]  # 22
                                                token = token[:-3]  # 100
                                                token = token + tok + "000000.00"
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                                index_text += 3
                                        else:
                                            if token_len < 7:  # under million
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + " Dollars", 0, index_text)
                                                index_text += 1
                                            else:  # beteen million to trilion 33,456,000.00
                                                tok = token[:-9]  # 33
                                                division = token[:-7]  # 3345
                                                division = division[-2:]  # 45
                                                token = tok + '.' + division
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                                index_text += 1
                                elif token[0:1] == '$':
                                    token = token[1:]
                                    token = clean_numeric(token)
                                    token_len = len(token) - 3  # i remove the .00 in the end of the number
                                    if index_text < index_last_text:
                                        next_token = index_text + 1
                                        next_token = text[next_token]
                                        next_token = remove_other_characters(next_token)
                                        if next_token in dictionary_M_B_T:
                                            if next_token == "million" or next_token == "Million" or next_token == "m" or next_token == "M" or next_token == "bn":
                                                insert_to_dictionary_terms(dictionary_terms_all_text,token + " M Dollars", 0, index_text)
                                                index_text += 3
                                            # 100.22 billion dollars
                                            elif next_token == "billion" or next_token == "Billion" or next_token == "B" or next_token == "b":
                                                tok = token[-2:]  # 22
                                                token = token[:-3]  # 100
                                                token = token + tok + "000.00"
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                                index_text += 3
                                            elif next_token == "Trillion" or next_token == "trillion" or next_token == "T" or next_token == "t":
                                                tok = token[-2:]  # 22
                                                token = token[:-3]  # 100
                                                token = token + tok + "000000.00"
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                                index_text += 3
                                        else:
                                            if token_len < 7:  # under million
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + " Dollars", 0, index_text)
                                                index_text += 1
                                            else:  # beteen million to trilion 33,456,000.00
                                                tok = token[:-9]  # 33
                                                division = token[:-7]  # 3345
                                                division = division[-2:]  # 45
                                                token = tok + '.' + division
                                                insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                                index_text += 1
                                else:
                                    token_len = len(token) - 3  # without the .00
                                    if token_len < 4:
                                        insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                                    elif token_len < 7: # 87,999.00
                                        start = token[:-6]  # 87
                                        div = token[:-4]  # 8799
                                        div = div[-2:]  # 99
                                        token = start + "." + div + "K"
                                        insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                                    elif token_len < 10:  # 100,230,000.00
                                        start = token[:-9]  # 100
                                        div = token[:-7]  # 10023
                                        div = div[-2:]  # 23
                                        token = start + "." + div + "M"
                                        insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                                    else:  # 105,230,000,000.00
                                        start = token[:-12]  # 105
                                        div = token[:-10]  # 230
                                        div = div[-2:]  # 23
                                        token = start + "." + div + "B"
                                        insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                        else:  # the token is number and there is no more tokens
                            # the case $45 or 45$
                            if token[-1:] == "$":
                                token = token[:-1]
                                token = clean_numeric(token)
                                token_len = len(token) - 3  # i remove the .00 in the end of the number
                                if index_text < index_last_text:
                                    next_token = index_text + 1
                                    next_token = text[next_token]
                                    next_token = remove_other_characters(next_token)
                                    if next_token in dictionary_M_B_T:
                                        if next_token == "million" or next_token == "Million" or next_token == "m" or next_token == "M" or next_token == "bn":
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                            index_text += 3
                                        # 100.22 billion dollars
                                        elif next_token == "billion" or next_token == "Billion" or next_token == "B" or next_token == "b":
                                            tok = token[-2:]  # 22
                                            token = token[:-3]  # 100
                                            token = token + tok + "000.00"
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars",0 , index_text)
                                            index_text += 3
                                        elif next_token == "Trillion" or next_token == "trillion" or next_token == "T" or next_token == "t":
                                            tok = token[-2:]  # 22
                                            token = token[:-3]  # 100
                                            token = token + tok + "000000.00"
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                            index_text += 3
                                    else:
                                        if token_len < 7:  # under million
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + " Dollars", 0, index_text)
                                            index_text += 1
                                        else:  # beteen million to trilion 33,456,000.00
                                            tok = token[:-9]  # 33
                                            division = token[:-7]  # 3345
                                            division = division[-2:]  # 45
                                            token = tok + '.' + division
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                            index_text += 1
                            elif token[0:1] == '$':
                                token = token[1:]
                                token = clean_numeric(token)
                                token_len = len(token) - 3  # i remove the .00 in the end of the number
                                if index_text < index_last_text:
                                    next_token = index_text + 1
                                    next_token = text[next_token]
                                    next_token = remove_other_characters(next_token)
                                    if next_token in dictionary_M_B_T:
                                        if next_token == "million" or next_token == "Million" or next_token == "m" or next_token == "M" or next_token == "bn":
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars",0, index_text)
                                            index_text += 3
                                        # 100.22 billion dollars //
                                        elif next_token == "billion" or next_token == "Billion" or next_token == "B" or next_token == "b":
                                            tok = token[-2:]  # 22
                                            token = token[:-3]  # 100
                                            token = token + tok + "000.00"
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars",
                                                                       0, index_text)
                                            index_text += 3
                                        elif next_token == "Trillion" or next_token == "trillion" or next_token == "T" or next_token == "t":
                                            tok = token[-2:]  # 22
                                            token = token[:-3]  # 100
                                            token = token + tok + "000000.00"
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars",
                                                                       0, index_text)
                                            index_text += 3
                                    else:
                                        if token_len < 7:  # under million
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + " Dollars", 0, index_text)
                                            index_text += 1
                                        else:  # beteen million to trilion 33,456,000.00
                                            tok = token[:-9]  # 33
                                            division = token[:-7]  # 3345
                                            division = division[-2:]  # 45
                                            token = tok + '.' + division
                                            insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars",
                                                                       0, index_text)
                                            index_text += 1
                            else:
                                token_len = len(token) - 3  # without the .00
                                if token_len < 4:
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                                elif token_len < 7:  # 87,999.00
                                    start = token[:-6]  # 87
                                    div = token[:-4]  # 8799
                                    div = div[-2:]  # 99
                                    token = start + "." + div + "K"
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                                elif token_len < 10:  # 100,230,000.00
                                    start = token[:-9]  # 100
                                    div = token[:-7]  # 10023
                                    div = div[-2:]  # 23
                                    token = start + "." + div + "M"
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                                else:  # 105,230,000,000.00
                                    start = token[:-12]  # 105
                                    div = token[:-10]  # 230
                                    div = div[-2:]  # 23
                                    token = start + "." + div + "B"
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                    else:
                        insert_to_dictionary_terms(dictionary_terms_all_text, token, 0, index_text)
                #3.2 -  the number is not valid. "is_valid_number" = False
                else:
                    flag_list = True
                    flag_point = 0
                    for i in token:
                        if (flag_point == 0 and (i in {'0', '1', '2', '3', '4', '5', '6', '7','8', '9'})):
                            continue
                        elif i == '.' or i==')':
                            flag_point = flag_point+ 1
                        elif (flag_point == 1 and (i in dictionary_Letters)):
                            continue
                        else:
                            flag_list = False
                    if (flag_list):
                        token_splited = token.split('.')
                        tok_one = clean_numeric(token_splited[0])
                        tok_two = (token_splited[1])
                        insert_to_dictionary_terms(dictionary_terms_all_text, tok_one , 0, index_text)
                        insert_to_dictionary_terms(dictionary_terms_all_text, tok_two , 1, index_text)
                    # the case $45 or 45$
                    elif token[-1:] == "$" and isfloat(token[:-1]):
                        token = token[:-1]
                        token = clean_numeric(token)
                        token_len = len(token) - 3  # i remove the .00 in the end of the number
                        if index_text < index_last_text:
                            next_token = index_text + 1
                            next_token = text[next_token]
                            next_token = remove_other_characters(next_token)
                            if next_token in dictionary_M_B_T:
                                if next_token == "million" or next_token == "Million" or next_token == "m" or next_token == "M" or next_token == "bn":
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                    index_text += 3
                                # 100.22 billion dollars
                                elif next_token == "billion" or next_token == "Billion" or next_token == "B" or next_token == "b":
                                    tok = token[-2:]  # 22
                                    token = token[:-3]  # 100
                                    token = token + tok + "000.00"
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                    index_text += 3
                                elif next_token == "Trillion" or next_token == "trillion" or next_token == "T" or next_token == "t":
                                    tok = token[-2:]  # 22
                                    token = token[:-3]  # 100
                                    token = token + tok + "000000.00"
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                    index_text += 3
                            else:
                                if token_len < 7:  # under million
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token + " Dollars", 0, index_text)
                                else:  # beteen million to trilion 33,456,000.00
                                    tok = token[:-9]  # 33
                                    division = token[:-7]  # 3345
                                    division = division[-2:]  # 45
                                    token = tok + '.' + division
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                    elif token[0:1] == '$' and isfloat(token[1:]):
                        token = token[1:]
                        token = clean_numeric(token)
                        token_len = len(token) - 3  # i remove the .00 in the end of the number
                        if index_text < index_last_text:
                            next_token = index_text + 1
                            next_token = text[next_token]
                            next_token = remove_other_characters(next_token)
                            if next_token in dictionary_M_B_T:
                                if next_token == "million" or next_token == "Million" or next_token == "m" or next_token == "M" or next_token == "bn":
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                    index_text += 3
                                # 100.22 billion dollars
                                elif next_token == "billion" or next_token == "Billion" or next_token == "B" or next_token == "b":
                                    tok = token[-2:]  # 22
                                    token = token[:-3]  # 100
                                    token = token + tok + "000.00"
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                    index_text += 3
                                elif next_token == "Trillion" or next_token == "trillion" or next_token == "T" or next_token == "t":
                                    tok = token[-2:]  # 22
                                    token = token[:-3]  # 100
                                    token = token + tok + "000000.00"
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
                                    index_text += 3
                            else:
                                if token_len < 7:  # under million
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token + " Dollars", 0, index_text)
                                else:  # beteen million to trilion 33,456,000.00
                                    tok = token[:-9]  # 33
                                    division = token[:-7]  # 3345
                                    division = division[-2:]  # 45
                                    token = tok + '.' + division
                                    insert_to_dictionary_terms(dictionary_terms_all_text, token + " M Dollars", 0, index_text)
            # case : the first character is upper case
            elif token[0].isupper():
                stem_mode = 0
                # stop words
                token_lower = token.lower()
                if token[0:1] in functional_characters:
                    token = token[-1:]
                if token[-1] in functional_characters:
                    token = token[0:-1]
                flag_ligal_word = True
                for i in token:
                    if i in functional_characters_inside:
                        flag_ligal_word = False
                if flag_ligal_word:
                        token = remove_other_characters(token)
                        if token in dictionary_upper_case:
                            dictionary_upper_case[token] += 1
                        else:
                            dictionary_upper_case[token] = 1
                        insert_to_dictionary_terms(dictionary_terms_all_text, token, stem_mode, index_text)
            # case : regular token
            else:
                regular_token = True
                if token[0:1] in functional_characters:
                    token = token[-1:]
                if token[-1] in functional_characters:
                    token = token[0:-1]
                for i in token:
                    if i in functional_characters_inside or i == '%':
                        regular_token = False
                if regular_token:
                    stem_mode = 1
                    # stop word
                    token = remove_other_characters(token)
                    insert_to_dictionary_terms(dictionary_terms_all_text, token, stem_mode, index_text)

        # jump to next token
        index_text += 1

    return dictionary_terms_all_text
