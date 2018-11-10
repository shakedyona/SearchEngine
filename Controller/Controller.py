import os
import time
from Model.Indexer import Indexer
from Model.Parse import Parse
import configparser

from Model.ReadFile import ReadFile
from Model.Stemmer import Stemmer

config = configparser.ConfigParser()
config.read('ViewConfig.ini')
dir_path = str(config['Controller']['corpus_path'])
percentage_of_division = float(config['Controller']['percentage_of_division'])

print("second commit")
def start_search_engine():
    list = os.listdir(dir_path)
    the_total_number_of_files = len(list)
    number_files_in_packet = round((the_total_number_of_files*percentage_of_division)+0.5)
    the_final_terms_dictionary = {} # [term] = (df,idf,sum_tf, the_abc_posting_name,line_in_file)
    #all_document_term_freq = {} # [doc id] = { (t1, 2), (t2, 1), (t3, 1) },  nf[1]
    all_document = {} # [doc_id] = (file_id , doc_maxtf , length)
    posting_terms_packet_dictionary = {} # [posting_temp_id] = terms_packet
    posting_id = 0
    start_time = time.time()
    # This loop performs for each file - saving its list of file names. And for each list, read the list in the ReadFile
    for number_of_file in range(1, the_total_number_of_files, number_files_in_packet):
        send_list_to_read_file = []
        for i in range(number_of_file, number_of_file + number_files_in_packet):
            if i <= the_total_number_of_files:
                print(i)
                path = dir_path + "\\" + list[i-1]
                send_list_to_read_file.append(path)
        # read files

        read_file_packet = ReadFile.read_packet(send_list_to_read_file)
        terms_packet = {} # [term] = {[doc_id] = freq , [doc_id] = freq .... }
        # update the terms_packet and all_document dictionary after parsing and stamming
        parse_and_stemming_and_update(all_document,read_file_packet,terms_packet)
        # posting
        posting_id = posting_id + 1
        Indexer.create_temp_posting_packet(posting_id,terms_packet,posting_terms_packet_dictionary)

    # Outside the loop
    # merge all posting
    Indexer.merge_all_posting(posting_id,len(all_document),posting_terms_packet_dictionary,the_final_terms_dictionary)
    end_time = time.time()
    print("total time: " + str(end_time - start_time))


def parse_and_stemming_and_update(all_document,read_file_packet,terms_packet):
    print("parse_and_stemming_and_update")
    for id , value in read_file_packet.items():
        doc_len = 0
        doc_maxtf = 0
        doc_city = value[3].upper()
        parse_terms_doc = Parse.parser(value[2])
        stemm_term_doc = Stemmer.stemming(parse_terms_doc)
        doc_id = value[1]
        doc_file_is = value[0]
        #all_document_term_freq[doc_id] = stemm_term_doc
        # key = the , value = 11
        for term, freq in stemm_term_doc.items():
            if doc_maxtf < freq:
                doc_maxtf = freq
            doc_len = doc_len+freq

            if term in terms_packet:
                terms_packet[term][doc_id] = freq
            else:
                terms_packet[term] = {}
                terms_packet[term][doc_id] = freq

        all_document[doc_id] = [doc_file_is, doc_maxtf, doc_len , doc_city]
