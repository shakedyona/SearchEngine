'''
final_abc_posting_file: [term] - (doc_1,3) | (doc_8,2)......
'''
import ast
import configparser
import json

from numpy import log2
import os
import shutil
import glob

from Controller import Controller
from Model.Stemmer import Stemmer
sum_numbers =0

def init_path(stemming_mode):
    print("init_path - indexer")
    folder_path_save = Controller.get_peth_posting()

    if stemming_mode == 'yes':
        path_folder_posting = folder_path_save + '/Stemming/TempPostings'
        if not os.path.exists(path_folder_posting):
            os.makedirs(path_folder_posting)
        path_folder_abc_posting = folder_path_save + '/Stemming/ABC_Posting'
        if not os.path.exists(path_folder_abc_posting):
            os.makedirs(path_folder_abc_posting)

    elif stemming_mode == 'no':
        path_folder_posting = folder_path_save + '/WithoutStemming/TempPostings'
        if not os.path.exists(path_folder_posting):
            os.makedirs(path_folder_posting)
        path_folder_abc_posting = folder_path_save + '/WithoutStemming/ABC_Posting'
        if not os.path.exists(path_folder_abc_posting):
            os.makedirs(path_folder_abc_posting)

    city_path = Controller.get_peth_posting() + '/' + "citiesPosting.txt"

    print(path_folder_abc_posting)
    print(path_folder_posting)
    print(city_path)
    return path_folder_posting, path_folder_abc_posting, stemming_mode, city_path
    print("init")


def create_temp_posting_packet(stemming_mode,posting_id,terms_packet):
    path_folder_posting , path_folder_abc_posting ,stemming_mode,city_path = init_path(stemming_mode)
    print(path_folder_posting)
    print(path_folder_abc_posting)
    print(stemming_mode)
    print("posting_id: " + str(posting_id))
    save_temp_posting_on_disk(posting_id,terms_packet,path_folder_posting)
    print("final write packet")


def save_temp_posting_on_disk(posting_id,terms_packet,path_folder_posting):
    file_path = path_folder_posting + "\TempPostings" + str(posting_id) + '.txt'
    temp_terms_items = terms_packet.items()
    # sort by value term
    sort_terms = sorted(temp_terms_items, key=lambda term: term[0])
    try:
        posting_file = open(file_path, "w")

    except IOError:
        return "fail"

    with posting_file:
        for term, value in sort_terms:
            total_freq = 0
            doc_freq_str = ""
            temp_terms_value = value.items()
            sort_value = list(reversed(sorted(temp_terms_value, key=lambda freq: freq[1])))
            for doc,freq in sort_value:
                freq_str = str(freq)
                freq_str = freq_str.replace("'",'"')
                total_freq = total_freq + freq[0]
                if len(doc_freq_str) > 1:
                    doc_freq_str = doc_freq_str + r',"' + str(doc) + r'":' + str(freq_str)
                else:
                    doc_freq_str = doc_freq_str + r'"' + str(doc) + r'":' + str(freq_str)
                    
            posting_file.write(term + "-->" + str(total_freq) + "(#){" + doc_freq_str + "}" + '\n')

        posting_file.close()


# terms_packet = { t1 : { (d1, 2), (d3, 1), (d4, 2) }, t2 : { (d1, 2), (d3, 1), (d4, 2) }}
def merge_all_posting(stemming_mode,posting_id,number_doc_in_corpus,the_final_terms_dictionary,cach_dictionary,all_city,max_doc_city):
    #check_uppercase()
    path_folder_posting, path_folder_abc_posting,stemming_mode,city_path= init_path(stemming_mode)
    print("merge_all_posting")
    finish = False
    number_of_line_in_abc_posting = {}
    all_final_posting_path = create_final_posting(path_folder_abc_posting,number_of_line_in_abc_posting,city_path)
    term_first_line_postings = {}
    freq_sum_doc_first_line_postings = {}
    the_open_posting_file = {}
    stemm_dictionary_values = []
    if stemming_mode == 'yes':
        stemm_dictionary = Stemmer.get_dictionary()# all stemming_term
        stemm_dictionary_values = Stemmer.get_dictionary_value()
    elif stemming_mode == 'no':
        stemm_dictionary = Stemmer.get_dictionary_without_stemming()  # all stemming_term
    cach_dictionary.clear()
    terms_to_updated = {}  # The terms are in lower case letters



    close_file ={}
    # save the first line of each temp posting
    for index_file_of_posting in range(1, posting_id+1):
        file_path = path_folder_posting + "\TempPostings" + str(index_file_of_posting) + '.txt'
        curr_posting_file = open(file_path, "r")
        the_open_posting_file[index_file_of_posting] = curr_posting_file
        close_file[index_file_of_posting] = False
        find_first_line(curr_posting_file,index_file_of_posting,term_first_line_postings,freq_sum_doc_first_line_postings,close_file)

    while not finish:
        #min_temp_posting = min(term_first_line_postings.keys(), key=(lambda index_post: term_first_line_postings[index_post]))
        min_term = min(term_first_line_postings.values())
        all_posting_file_with_equal_term = []
        list_doc = {}
        sum_tf = 0
        df = 0
        for index, term in term_first_line_postings.items():
            if min_term == term:
                all_posting_file_with_equal_term.append(index)
                sum_tf = sum_tf + int((freq_sum_doc_first_line_postings[index])[0])
                df = df + int((freq_sum_doc_first_line_postings[index])[1])
                list_doc.update((freq_sum_doc_first_line_postings[index])[2])
        # Handling capitalization !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if min_term[0].isupper(): # Party # The
            lowercase_term = min_term.lower() # party # the
            if lowercase_term in stemm_dictionary:
                if stemming_mode == 'yes':
                    lowercase_term_after_stemm = stemm_dictionary[lowercase_term] # parti # the
                else:
                    lowercase_term_after_stemm = lowercase_term
                if lowercase_term_after_stemm in terms_to_updated:
                    sum_tf = sum_tf + terms_to_updated[lowercase_term_after_stemm][0]
                    list_doc.update(terms_to_updated[lowercase_term_after_stemm][1])
                    terms_to_updated[lowercase_term_after_stemm] = (sum_tf, list_doc)
                else:
                    terms_to_updated[lowercase_term_after_stemm] = (sum_tf,list_doc)
            elif stemming_mode == 'yes' and lowercase_term in stemm_dictionary_values:
                if lowercase_term in terms_to_updated:
                    sum_tf = sum_tf + terms_to_updated[lowercase_term][0]
                    list_doc.update(terms_to_updated[lowercase_term][1])
                    terms_to_updated[lowercase_term] = (sum_tf, list_doc)
                else:
                    terms_to_updated[lowercase_term] = (sum_tf,list_doc)
            else:
                cach_dictionary[min_term] = sum_tf
                calculations_and_income_to_final_dictionary(list_doc,sum_tf,df,number_doc_in_corpus,min_term,all_final_posting_path,number_of_line_in_abc_posting,the_final_terms_dictionary,all_city,max_doc_city)
        else:
            if min_term in terms_to_updated: # parti #the
                sum_tf = sum_tf + terms_to_updated[min_term][0]
                cach_dictionary[min_term] = sum_tf
                list_doc.update(terms_to_updated[min_term][1])
                #print("final posting: " + min_term)
                calculations_and_income_to_final_dictionary(list_doc,sum_tf,df,number_doc_in_corpus,min_term,all_final_posting_path,number_of_line_in_abc_posting,the_final_terms_dictionary,all_city,max_doc_city)
            else:
                #print("final posting: " + min_term)
                cach_dictionary[min_term] = sum_tf
                calculations_and_income_to_final_dictionary(list_doc,sum_tf,df,number_doc_in_corpus,min_term,all_final_posting_path,number_of_line_in_abc_posting,the_final_terms_dictionary,all_city,max_doc_city)

        for i in all_posting_file_with_equal_term:
            find_first_line(the_open_posting_file[i], i, term_first_line_postings,freq_sum_doc_first_line_postings, close_file)

        finish = check_if_finish(close_file)

    ## out while
    close_all_files(all_final_posting_path)
    Stemmer.reset()
    reset_temp_posting()
    return sum_numbers


def calculations_and_income_to_final_dictionary(list_doc,sum_tf,df,number_doc_in_corpus,min_term,all_final_posting_path,number_of_line_in_abc_posting,the_final_terms_dictionary,all_city,max_doc_city):
    # sumtf , df ,idf
    N = number_doc_in_corpus
    idf = log2(N / df)
    idf = "{:.3f}".format(float(idf))
    idf = float(idf)
    sort_list_doc = list(reversed(sorted(list_doc.items(), key=lambda freq: freq[1])))
    the_abc_posting_name = find_abc_posting(min_term)
    min_term_upper = min_term.upper()
    if min_term_upper in all_city:
        max_doc_city[min_term_upper] = (sum_tf, sort_list_doc)
        all_city[min_term_upper][5] = sum_tf
        create_posting_city(all_city,all_final_posting_path,number_of_line_in_abc_posting,min_term_upper,sort_list_doc,sum_tf)
    all_final_posting_path[the_abc_posting_name].write(min_term + "-->" + str(sum_tf) + str(sort_list_doc) + '\n')
    number_of_line_in_abc_posting[the_abc_posting_name] = number_of_line_in_abc_posting[the_abc_posting_name] + 1
    the_final_terms_dictionary[min_term] = (df, idf, sum_tf, the_abc_posting_name, number_of_line_in_abc_posting[the_abc_posting_name])


def create_final_posting(path_folder_abc_posting,number_of_line_in_abc_posting,city_path):
    all_final_posting = {}
    post1_path = path_folder_abc_posting + "\FinalPostings_a.txt"
    all_final_posting["a"] = open(post1_path, "w+")
    number_of_line_in_abc_posting["a"] = 0

    post2_path = path_folder_abc_posting + "\FinalPostings_bc.txt"
    all_final_posting["bc"] = open(post2_path, "w+")
    number_of_line_in_abc_posting["bc"] = 0

    post3_path = path_folder_abc_posting + "\FinalPostings_defg.txt"
    all_final_posting["defg"] = open(post3_path, "w+")
    number_of_line_in_abc_posting["defg"] = 0

    post4_path = path_folder_abc_posting + "\FinalPostings_hijkl.txt"
    all_final_posting["hijkl"] = open(post4_path, "w+")
    number_of_line_in_abc_posting["hijkl"] = 0

    post5_path = path_folder_abc_posting + "\FinalPostings_mnop.txt"
    all_final_posting["mnop"] = open(post5_path, "w+")
    number_of_line_in_abc_posting["mnop"] = 0

    post6_path = path_folder_abc_posting + "\FinalPostings_qrs.txt"
    all_final_posting["qrs"] = open(post6_path, "w+")
    number_of_line_in_abc_posting["qrs"] = 0

    post7_path = path_folder_abc_posting + "\FinalPostings_tuvwxyz.txt"
    all_final_posting["tuvwxyz"] = open(post7_path, "w+")
    number_of_line_in_abc_posting["tuvwxyz"] = 0

    post8_path = path_folder_abc_posting + "\FinalPostings_notLetters.txt"
    all_final_posting["notLetters"] = open(post8_path, "w+")
    number_of_line_in_abc_posting["notLetters"] = 0

    post9_path = city_path
    all_final_posting["citiesPosting"] = open(post9_path, "w+")
    number_of_line_in_abc_posting["citiesPosting"] = 0

    return all_final_posting


def find_first_line(curr_posting_file,index_file_of_posting,term_first_line_postings,freq_sum_doc_first_line_postings,close_file):
    curr_line = curr_posting_file.readline().strip()
    if curr_line:
        curr_line_split = curr_line.split("-->")
        term_in_first_line = curr_line_split[0]
        part_of_doc_freq = curr_line_split[1].split("(#)")
        total_freq_in_first_line = part_of_doc_freq[0]
        doc_freq = part_of_doc_freq[1]
        doc_freq = json.loads(doc_freq)
        number_doc = len(doc_freq)
        term_first_line_postings[index_file_of_posting] = term_in_first_line
        freq_sum_doc_first_line_postings[index_file_of_posting] = [total_freq_in_first_line.strip(), number_doc,doc_freq]
    else:  # end of posting file
        print("end!!!!!!!!!!!!!!!!: "+str(index_file_of_posting))
        curr_posting_file.close()
        close_file[index_file_of_posting] = True
        term_first_line_postings.pop(index_file_of_posting)
        freq_sum_doc_first_line_postings.pop(index_file_of_posting)


def check_if_finish(close_file):
    for i in close_file:
        if close_file[i] == False:
            return False
    return True


def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False



def find_abc_posting(min_term):
    global sum_numbers
    if isfloat(min_term):
        sum_numbers = sum_numbers + 1
    first_char = min_term[0]
    if first_char == 'a' or first_char == 'A':
        return "a"
    elif first_char in "bcBC":
        return "bc"
    elif first_char in "defgDEFG":
        return "defg"
    elif first_char in "hijklHIJKL":
        return "hijkl"
    elif first_char in "mnopMNOP":
        return "mnop"
    elif first_char in "qrsQRS":
        return "qrs"
    elif first_char in "tuvwxyzTUVWXYZ":
        return "tuvwxyz"
    else:
        return "notLetters"


def create_posting_city(all_city,all_final_posting_path,number_of_line_in_abc_posting,min_term_upper,sort_list_doc,sum_tf):
    # sort by value term
    all_final_posting_path["citiesPosting"].write(min_term_upper + "-->" + str(sum_tf) + "(#)[" + str(sort_list_doc) + "]" + '\n')
    number_of_line_in_abc_posting["citiesPosting"] = number_of_line_in_abc_posting["citiesPosting"] + 1
    all_city[min_term_upper][6] = "citiesPosting"
    all_city[min_term_upper][7] = number_of_line_in_abc_posting["citiesPosting"]


def close_all_files(all_final_posting_path):
    for id,file in all_final_posting_path.items():
        print("close- "+id)
        file.close()


def handling_capitalization(term):
    print("handling_capitalization")
    if term[0].isupper():
        lowercase_term = term.lower()


def reset_posting():
    print("reset_posting - indexer")
    folder_path_save = Controller.get_peth_posting()
    path_folder_posting_stemming = folder_path_save + '/Stemming'
    path_folder_posting_withoutStemming = folder_path_save + '/WithoutStemming'

    if os.path.exists(path_folder_posting_stemming):
        shutil.rmtree(path_folder_posting_stemming)
    if os.path.exists(path_folder_posting_withoutStemming):
        shutil.rmtree(path_folder_posting_withoutStemming)
    # if os.path.exists(folder_path_save):
    #     shutil.rmtree(folder_path_save)

    # for file in glob.glob(path_folder_abc_posting+ "/*"):
    #         os.remove(file)

    # if os.path.exists(path_folder_posting_withoutStemming):
    #     shutil.rmtree(path_folder_posting_withoutStemming)
    # for file in glob.glob(path_folder_abc_posting+ "/*"):
    #         os.remove(file)

    city_path = Controller.get_peth_posting() + '/' + "citiesPosting.txt"
    os.remove(city_path)


def reset_temp_posting():
    print("reset_temp_posting - indexer")
    path_folder_posting, path_folder_abc_posting,stemming_mode,city_path = init_path("yes")
    if os.path.exists(path_folder_posting):
        shutil.rmtree(path_folder_posting)

    # for file in glob.glob(path_folder_posting+ "/*"):
    #         os.remove(file)

    path_folder_posting, path_folder_abc_posting,stemming_mode,city_path = init_path("no")
    if os.path.exists(path_folder_posting):
        shutil.rmtree(path_folder_posting)
    # for file in glob.glob(path_folder_posting+ "/*"):
    #         os.remove(file)


