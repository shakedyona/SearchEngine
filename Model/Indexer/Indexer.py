'''
final_abc_posting_file: [term] - (doc_1,3) | (doc_8,2)......
'''
import configparser
from numpy import log2
import os
import shutil
import glob


def init_path(stemming_mode):
    config = configparser.ConfigParser()
    config.read('ViewConfig.ini')
    if stemming_mode == 'yes':
        path_folder_posting = str(config['Indexer']['path_folder_temp_posting_stemming'])
        path_folder_abc_posting = str(config['Indexer']['path_folder_abc_posting_stemming'])
    elif stemming_mode == 'no':
        path_folder_posting = str(config['Indexer']['path_folder_temp_posting_without_stemming'])
        path_folder_abc_posting = str(config['Indexer']['path_folder_abc_posting_without_stemming'])
    return path_folder_posting,path_folder_abc_posting
    print("init")


def create_temp_posting_packet(stemming_mode,posting_id,terms_packet):
    path_folder_posting , path_folder_abc_posting = init_path(stemming_mode)
    print("posting_id: " + str(posting_id))
    save_temp_posting_on_disk(posting_id,terms_packet,path_folder_posting,path_folder_abc_posting)
    print("final write packet")


def save_temp_posting_on_disk(posting_id,terms_packet,path_folder_posting,path_folder_abc_posting):
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
                total_freq = total_freq + freq
                doc_freq_str = doc_freq_str + "|(" + str(doc) + "," + str(freq) + ")"
            posting_file.write(term + "-->" + str(total_freq) + doc_freq_str + '\n')

        posting_file.close()


# terms_packet = { t1 : { (d1, 2), (d3, 1), (d4, 2) }, t2 : { (d1, 2), (d3, 1), (d4, 2) }}
def merge_all_posting(stemming_mode,posting_id,number_doc_in_corpus,the_final_terms_dictionary):
    path_folder_posting, path_folder_abc_posting = init_path(stemming_mode)
    print("merge_all_posting")
    finish = False
    number_of_line_in_abc_posting = {}
    all_final_posting_path = create_final_posting(path_folder_abc_posting,number_of_line_in_abc_posting)
    term_first_line_postings = {}
    freq_sum_doc_first_line_postings = {}
    the_open_posting_file = {}

    close_file ={}
    # save the first line of each temp posting
    for index_file_of_posting in range(1, posting_id+1):
        file_path = path_folder_posting + "\TempPostings" + str(index_file_of_posting) + '.txt'
        curr_posting_file = open(file_path, "r")
        the_open_posting_file[index_file_of_posting] = curr_posting_file
        close_file[index_file_of_posting] = False
        find_first_line(curr_posting_file,index_file_of_posting,term_first_line_postings,freq_sum_doc_first_line_postings,close_file)

    while not finish:
        min_temp_posting = min(term_first_line_postings.keys(), key=(lambda index_post: term_first_line_postings[index_post]))
        min_term = min(term_first_line_postings.values())
        # sumtf,df,idf
        sum_tf = 0
        N = number_doc_in_corpus
        df = 0
        list_doc = ""
        all_posting_file_with_equal_term = []
        for index,term in term_first_line_postings.items():
            if min_term == term:
                all_posting_file_with_equal_term.append(index)
                sum_tf = sum_tf + int((freq_sum_doc_first_line_postings[index])[0])
                df = df + int((freq_sum_doc_first_line_postings[index])[1])
                list_doc = list_doc + (freq_sum_doc_first_line_postings[index])[2]

        idf = log2(N / df)

        the_abc_posting_name = find_abc_posting(min_term)
        all_final_posting_path[the_abc_posting_name].write(min_term + "-->" + str(sum_tf)+ list_doc + '\n')
        number_of_line_in_abc_posting[the_abc_posting_name] = number_of_line_in_abc_posting[the_abc_posting_name] + 1
        the_final_terms_dictionary[min_term] = (df,idf,sum_tf,the_abc_posting_name,number_of_line_in_abc_posting[the_abc_posting_name])

        for i in all_posting_file_with_equal_term:
            find_first_line(the_open_posting_file[i], i, term_first_line_postings,freq_sum_doc_first_line_postings, close_file)
        finish = check_if_finish(close_file)
    close_all_files(all_final_posting_path)


def create_final_posting(path_folder_abc_posting,number_of_line_in_abc_posting):
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

    return all_final_posting


def find_first_line(curr_posting_file,index_file_of_posting,term_first_line_postings,freq_sum_doc_first_line_postings,close_file):
    curr_line = curr_posting_file.readline().strip()
    if curr_line:
        curr_line_split = curr_line.split("-->")
        term_in_first_line = curr_line_split[0]
        part_of_doc_freq = curr_line_split[1].split("|")
        total_freq_in_first_line = part_of_doc_freq[0]
        length = len(part_of_doc_freq)
        number_doc = length -1
        list_doc = "|".join(part_of_doc_freq[1:length])
        term_first_line_postings[index_file_of_posting] = term_in_first_line
        freq_sum_doc_first_line_postings[index_file_of_posting] = [total_freq_in_first_line.strip(),number_doc,list_doc.strip()]
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

def find_abc_posting(min_term):
    first_char = min_term[0]
    if first_char == 'a':
        return "a"
    elif first_char in "bc":
        return "bc"
    elif first_char in "defg":
        return "defg"
    elif first_char in "hijkl":
        return "hijkl"
    elif first_char in "mnop":
        return "mnop"
    elif first_char in "qrs":
        return "qrs"
    elif first_char in "tuvwxyz":
        return "tuvwxyz"
    else:
        return "notLetters"


def close_all_files(all_final_posting_path):
    for id,file in all_final_posting_path.items():
        print("close- "+id)
        file.close()


def reset():
    print("reset - indexer")
    path_folder_posting, path_folder_abc_posting = init_path("yes")

    for file in glob.glob(path_folder_posting+ "/*"):
            os.remove(file)
    for file in glob.glob(path_folder_abc_posting+ "/*"):
            os.remove(file)

    path_folder_posting, path_folder_abc_posting = init_path("no")
    for file in glob.glob(path_folder_posting+ "/*"):
            os.remove(file)
    for file in glob.glob(path_folder_abc_posting+ "/*"):
            os.remove(file)

