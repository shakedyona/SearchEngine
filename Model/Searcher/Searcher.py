'''
The role of this class is to return results to queries
'''
from collections import Counter

from Model.Parse import Parse
from Model.Ranker import Ranker
from Model.Stemmer import Stemmer


class Searcher:
    def __init__(self,stemm_mode, path_folder, the_final_dictionary, all_document,selected_cities_from_user,semantic_mode):
        self.ranker = Ranker.Ranker(stemm_mode,selected_cities_from_user)
        self.semantic_mode = semantic_mode
        self.stemm_mode = stemm_mode
        self.path_folder = path_folder
        self.final_dic = the_final_dictionary
        self.all_document = all_document

        if stemm_mode == "yes":
            self.denominator = 1.9
            self.weight_idf = 0.6
            self.weight_df = 0.5
        else:
            self.denominator = 1
            self.weight_idf = 0.2
            self.weight_df = 0.1


    # Query and return the most relevant documents to a query
    def results_relevant_documents_to_one_query(self,query):
        print("results_relevant_documents_to_one_query")
        if (self.final_dic):
            dictionary_parser = Parse.parse_text(query)
            dictionary_stemm = Stemmer.stemming(dictionary_parser, self.stemm_mode)

            final_dictionary_query = {}
            for term, details in dictionary_stemm.items():
                freq = details[0]
                final_dictionary_query[term] = freq

            result_rank = self.ranker.rank(self.stemm_mode, self.all_document, self.final_dic, self.path_folder,
                                           final_dictionary_query,self.semantic_mode)

        else:
            return []

        print("finish")
        self.ranker.reset_rank()
        return list(result_rank.keys())


    # Query and return the most relevant documents to many queries
    def results_relevant_documents(self,queries_dictionary):
        print("results_relevant_documents")
        results = []
        if (self.final_dic):
            for number, value in queries_dictionary.items():
                # this is the dictionary of all terms in this query
                query_dictionary_description = {}
                query_title = value[0]
                query_description = value[1]
                query_narrative = value[2]

                # title
                parse_title = Parse.parse_text(query_title)
                stemm_title = Stemmer.stemming(parse_title, self.stemm_mode)
                # narrative - break down sentences and remove not relevant
                query_narrative = Parse.parse_query_narrative(query_narrative)
                # description + narrative
                query_description_narrative = query_narrative + ' ' + query_description
                parse_description_narrative = Parse.parse_text(query_description_narrative)
                stemm_description_narrative = Stemmer.stemming(parse_description_narrative, self.stemm_mode)

                # Normalize the number of occurrences of the term
                for term, details in stemm_description_narrative.items():
                    freq = details[0]
                    if term in self.final_dic:
                        idf = self.final_dic[term][1]
                        # new freq with idf
                        query_dictionary_description[term] = (self.weight_idf * idf) + (self.weight_df * freq)

                number_of_term_in_query = len(query_dictionary_description)
                normalized_number_of_results = number_of_term_in_query / self.denominator
                normalized_number_of_results = int(normalized_number_of_results)
                # Dictionary with the normalized_number_of_results most common terms
                query_dictionary_description_most_common = dict(Counter(query_dictionary_description).most_common(normalized_number_of_results))
                query_dictionary_description.clear()

                # chang dictionary
                final_dictionary_query = {}
                for term, details in stemm_title.items():
                    freq = details[0]
                    final_dictionary_query[term] = freq


                # merge dictionary_rank_title and query_dictionary_description_most_common to final_dictionary_query
                for term, val in query_dictionary_description_most_common.items():
                    if term in final_dictionary_query:
                        final_dictionary_query[term] = final_dictionary_query[term] + val
                    else:
                        final_dictionary_query[term] = val

                # send the number of occurrences of a word in a document to the ranker
                # The ranker return dictionary with [term] = [(d1,tf1),(d2,tf2)...]
                result_rank = self.ranker.rank(self.stemm_mode,self.all_document, self.final_dic,self.path_folder,final_dictionary_query,self.semantic_mode)
                # [ query1 , {term1: [(d1,tf1),(d2,tf2)...] , term2: [(d1,tf1),(d2,tf2)...]} ]
                results.append((number,list(result_rank.keys())))

        print("finish")
        self.ranker.reset_rank()
        return results




