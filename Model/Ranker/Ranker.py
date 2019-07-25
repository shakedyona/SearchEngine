import json
from collections import Counter

from numpy.ma import sqrt
import urllib.request
from Controller import Controller
from numpy import log2


class Ranker:
    def __init__(self,stemm_mode,selected_cities_from_user):
        self.avg_bm25 = 225.9404708745569
        self.firstTime = False
        self.cities_set = list(selected_cities_from_user)
        self.cach_file = {} # [file_id] = lines
        if stemm_mode == "yes":
            self.k1_bm25 = 1.2
            self.b_bm25 = 0.1
            self.lambda_bm25 = 0.6
            self.weight_bm25 = 0.2
            self.weight_cos_sim = 0.8
            self.number_result_semantic = 5

        else:
            self.k1_bm25 = 1.2
            self.b_bm25 = 0.1
            self.lambda_bm25 = 0.3
            self.weight_bm25 = 0.3
            self.weight_cos_sim = 0.7
            self.number_result_semantic = 5

    def init_path(self,stemming_mode):
        if stemming_mode == 'yes':
            path_folder_abc_posting = Controller.get_peth_posting() + '/' + "Stemming/ABC_Posting"
        elif stemming_mode == 'no':
            path_folder_abc_posting = Controller.get_peth_posting() + '/' + "WithoutStemming/ABC_Posting"

        city_path = Controller.get_peth_posting() + '/' + "citiesPosting.txt"

        return path_folder_abc_posting, stemming_mode, city_path

    # one query : final_dictionary_query[term] = freq
    # multi queries : final_dictionary_query[term] = freq_after_normal_and_most_common
    def rank(self, stemm_mode, all_document, final_dic, path_folder, final_dictionary_query,semantic_mode):
        path_folder_abc_posting, stemming_mode, city_path = self.init_path(stemm_mode)

        if self.cities_set and not self.firstTime:
            self.firstTime = True
            print(self.cities_set)
            new_cities = []
            for city in self.cities_set:
                city_lower = city.lower()
                new_cities.append(city_lower)
            self.cities_set = self.cities_set + new_cities
            print(self.cities_set)
            for city in self.cities_set:
                final_dictionary_query[city] = 0
                final_dictionary_query[city_lower] = 0

        # dictionary_from_posting - this array with all data from posting by terms
        dictionary_from_posting = {}
        # create dictionary_from_posting
        # dictionary_from_posting: [term] = list [(doc_id, freq_in_doc, position_in_doc) , (doc_id, freq_in_doc, position_in_doc) ... ]
        for term,freq in final_dictionary_query.items():
            if term in final_dic:
                posting_file = final_dic[term][3]
                sum_tf = final_dic[term][2]
                line_in_posting_file = final_dic[term][4] -1
                filename = path_folder_abc_posting + '/' +"FinalPostings_"+ posting_file + ".txt"

                if filename in self.cach_file:
                    lines = self.cach_file[filename]
                else:
                    with open(filename, encoding='iso-8859-1') as file:
                        lines = file.readlines()
                    file.close()
                    self.cach_file[filename] = lines

                line_from_posting = lines[line_in_posting_file].rstrip()
                array_list_docs_of_term = self.get_array_list_by_line(line_from_posting)
                # [term] = list[(doc_id, freq_in_doc, position_in_doc), (doc_id, freq_in_doc, position_in_doc)...]
                dictionary_from_posting[term] = array_list_docs_of_term

            else:
                print(term + " not in final dictionary")

        # semantic
        if semantic_mode:
            list_semantic_word = self.find_semantic_words_by_query(final_dictionary_query,final_dic)
            for term,freq in list_semantic_word.items():
                final_dictionary_query[term] = freq
                if term in final_dic:
                    posting_file = final_dic[term][3]
                    sum_tf = final_dic[term][2]
                    line_in_posting_file = final_dic[term][4] - 1
                    filename = path_folder_abc_posting + '/' + "FinalPostings_" + posting_file + ".txt"

                    if filename in self.cach_file:
                        lines = self.cach_file[filename]
                    else:
                        with open(filename, encoding='iso-8859-1') as file:
                            lines = file.readlines()
                        file.close()
                        self.cach_file[filename] = lines

                    line_from_posting = lines[line_in_posting_file].rstrip()
                    array_list_docs_of_term = self.get_array_list_by_line(line_from_posting)
                    # [term] = list[(doc_id, freq_in_doc, position_in_doc), (doc_id, freq_in_doc, position_in_doc)...]
                    dictionary_from_posting[term] = array_list_docs_of_term
                else:
                    print(term + " not in final dictionary")
        # create document_dic_query
        # document_dic_query: [doc_id] = [(term1 , w1) , (term2 , w2) ,(term3 , w3)...)
        document_dic_query = {}
        for term, data in dictionary_from_posting.items():
            for item in data:
                doc_id = item[0].replace("'","")
                freq = item[1]
                if doc_id in document_dic_query:
                    document_dic_query[doc_id].append((term, freq))
                else:
                    document_dic_query[doc_id] = [(term, freq)]

        # Filter documents that do not represent the selected cities
        if self.cities_set:
            new_document_dic_query = {}
            print("selected cities")
            for doc,list_term_freq in document_dic_query.items():
                city_doc = all_document[doc][3]
                if city_doc:
                    city_doc = city_doc[0]
                    if city_doc in self.cities_set:
                        for term_freq in list_term_freq:
                            term_di = term_freq[0]
                            if term_di not in self.cities_set:
                                new_document_dic_query[doc] = list_term_freq
                                break
                    else:
                        for city in self.cities_set:
                            if city in list_term_freq:
                                for term_freq in list_term_freq:
                                    term_di = term_freq[0]
                                    if term_di not in self.cities_set:
                                        new_document_dic_query[doc] = list_term_freq
                                        break
                                break
                else:
                    for city in self.cities_set:
                        if city in list_term_freq:
                            for term_freq in list_term_freq:
                                term_di = term_freq[0]
                                if term_di not in self.cities_set:
                                    new_document_dic_query[doc] = list_term_freq
                                    break
                            break

            document_dic_query = new_document_dic_query

        # calc rank for all docs. use BM25+ AND COS SIM
        # BM25+
        doc_rank = {}
        number_of_docs_in_all_corpus = len(all_document)
        for doc_id,list_of_term_freq in document_dic_query.items():
            doc_from_all = all_document[doc_id]
            doc_len = doc_from_all[2]
            doc_max_tf = doc_from_all[1]
            doc_city = doc_from_all[3]
            bm25_score_di_q = 0
            for item_in_list in list_of_term_freq:
                term_doc = item_in_list[0]
                freq_term_in_doc = float(item_in_list[1])
                number_of_documents_containing_the_term = final_dic[term_doc][0]
                df_nq = number_of_documents_containing_the_term
                idf_bm25 = float(log2((number_of_docs_in_all_corpus - df_nq + 0.5)/(df_nq + 0.5)))
                freq_query_doc = float(freq_term_in_doc/doc_max_tf)

                numerator = idf_bm25 * freq_query_doc * (self.k1_bm25+1)
                denominator = freq_query_doc + (self.k1_bm25 * (1 - self.b_bm25 + (self.b_bm25 * (doc_len / self.avg_bm25))))

                bm25_score_di_q = bm25_score_di_q + (numerator/denominator) + self.lambda_bm25 * idf_bm25

            doc_rank[doc_id] = bm25_score_di_q * self.weight_bm25


        # COS SIM
        vector_query_len = 0
        max_tf_query = 0
        # Calculates the length of the query vector
        for term, freq in final_dictionary_query.items():
            if max_tf_query < freq:
                max_tf_query = freq
            vector_query_len = vector_query_len + pow(freq,2)

        denominator_vector_query_len = sqrt(vector_query_len)
        number_terms_in_query = len(final_dictionary_query)
        denominator_nf_doc = 0
        for doc_id, list_of_term_freq in document_dic_query.items():
            doc_from_all = all_document[doc_id]
            doc_len = doc_from_all[2]
            doc_max_tf = doc_from_all[1]
            doc_city = doc_from_all[3]
            denominator_nf_doc = sqrt(doc_from_all[5])

            numerator = 0
            for item_in_list in list_of_term_freq:
                term_doc = item_in_list[0]
                freq_term_in_doc = float(item_in_list[1])
                idf_term = final_dic[term_doc][1]
                #denominator_nf_doc = denominator_nf_doc + pow(freq_term_in_doc*idf_term,2)
                normal_freq_term_in_query = number_terms_in_query * final_dictionary_query[term_doc] / max_tf_query

                numerator = numerator + freq_term_in_doc * idf_term * normal_freq_term_in_query

            #sim_q_di = numerator * (1/denominator_vector_query_len) * (1/sqrt(denominator_nf_doc))
            sim_q_di = numerator * (1 / denominator_vector_query_len) * (1 / denominator_nf_doc)
            doc_rank[doc_id] = doc_rank[doc_id] + sim_q_di * self.weight_cos_sim


        doc_rank = dict(Counter(doc_rank).most_common(50))
        return doc_rank

    def get_array_list_by_line(self,line_from_posting):
        line_split = line_from_posting.split("-->")
        index_start_value = line_split[1].find('[')
        sum_freq = line_split[1][0:index_start_value]
        value_docs = line_split[1][index_start_value:]
        value_docs = value_docs[1:len(value_docs) - 1]
        list_docs = value_docs.split("),")
        array_list_docs_of_term = []
        for i in list_docs:
            i = i.replace(" ", "")
            i = i.replace("(", "")
            split_line_doc = i.split("[")
            doc_id = split_line_doc[0].replace(",", "")
            part_position = split_line_doc[1].split("]")[0]
            part_position_split = part_position.split(",")
            freq_in_doc = part_position_split[0]
            position_in_doc = part_position_split[1]
            single_doc = (doc_id, freq_in_doc, position_in_doc)
            array_list_docs_of_term.append(single_doc)

        return array_list_docs_of_term

    def rank_entities(self , all_entity,all_document,doc_len,doc_max_tf,final_dic):
        print("rank_entities")
        term_rank = {}
        number_entities = len(all_entity)
        for term, freq_min_position in all_entity.items():
            freq = freq_min_position[0]
            idf_all_corpus = final_dic[term][1]
            min_position = int(freq_min_position[1])
            numerator = freq * idf_all_corpus
            denominator = float(1 + float((min_position/doc_len)*(number_entities-1)))
            my_rank = (numerator / denominator)
            term_rank[term] = my_rank

        print(all_entity)
        print(term_rank)

        return term_rank
        # print("rank_entities")
        # # BM25+
        # term_rank = {}
        # number_of_docs_in_all_corpus = len(all_document)
        # for term, freq in all_entity.items():
        #     bm25_score_di_q = 0
        #     freq_term_in_doc = float(freq)
        #     number_of_documents_containing_the_term = final_dic[term][0]
        #     df_nq = number_of_documents_containing_the_term
        #     idf_bm25 = float(log2((number_of_docs_in_all_corpus - df_nq + 0.5) / (df_nq + 0.5)))
        #     freq_normal_doc = float(freq_term_in_doc / doc_max_tf)
        #
        #     numerator = idf_bm25 * freq_normal_doc * (self.k1_bm25 + 1)
        #     denominator = freq_normal_doc + (
        #                 self.k1_bm25 * (1 - self.b_bm25 + (self.b_bm25 * (doc_len / self.avg_bm25))))
        #     bm25_score_di_q = bm25_score_di_q + (numerator / denominator) + self.lambda_bm25 * idf_bm25
        #     term_rank[term] = bm25_score_di_q
        #
        # return term_rank

    def find_semantic_words_by_query(self,final_dictionary_query,final_dic):
        vec_most_semantic = {}
        for term, freq in final_dictionary_query.items():
            flag = True
            url = "https://api.datamuse.com/words?ml=" + term
            try:
                response = urllib.request.urlopen(url)
                html = response.read()
                try:
                    response = html.decode('utf8')
                except ValueError:
                    response = html.decode('latin-1')
                list_of_dic_vec = json.loads(response)
                #list_of_dic_vec = list_of_dic_vec[:self.number_result_semantic]
                for vec_dic in list_of_dic_vec:
                    if vec_dic['word'] in final_dic:
                        vec_most_semantic[vec_dic['word']] = freq

                #print("number words are match semantic in our dictionary: ",len(vec_most_semantic))
                # the list_of_dic_vec are sorted !! most common ok !
                #vec_most_semantic = dict(Counter(vec_most_semantic).most_common(self.number_result_semantic))
            except ValueError:
                print(term,"could not read semantics")

        vec_most_semantic = dict(Counter(vec_most_semantic).most_common(self.number_result_semantic))
        return vec_most_semantic

    def reset_rank(self):
        self.cach_file.clear()