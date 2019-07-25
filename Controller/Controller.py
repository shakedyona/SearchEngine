import glob
import json
import os
import time

import shutil

from Model.Indexer import Indexer
from Model.Parse import Parse
import configparser

from Model.Ranker import Ranker
from Model.Searcher import Searcher
from restcountries import RestCountryApiV2 as rapi
from collections import Counter

from Model.ReadFile import ReadFile
from Model.Stemmer import Stemmer
import urllib.request

from tkinter.filedialog import askopenfilename, asksaveasfilename

the_final_terms_dictionary = {}  # [term] = (df,idf,sum_tf, the_abc_posting_name,line_in_file)
the_final_terms_dictionary_without_stemming = {}  # [term] = (df,idf,sum_tf, the_abc_posting_name,line_in_file)
all_document = {}  # [doc_id] = (file_id , doc_maxtf , length ,doc_city,unique_words)
all_city = {}  # [city] = (country_name,coin,population_size,number_of_file)
cach_dictionary = {}  # [term] = tf
start_time = 0
dir_path_corpus = ""
dir_path_save = ""
stemming_mode = "yes"
max_doc_city = {}  # [city] -->  (sum_tf,sort_list_doc)
selected_cities_from_user = set()


def init_path(path_corpus, path_save, stem):
    print("init_path")
    global dir_path_corpus
    global dir_path_save
    global stemming_mode
    dir_path_save = path_save
    print(dir_path_save)
    dir_path_corpus = path_corpus
    dir_path = path_corpus + '/' + "corpus"
    print(dir_path)
    # config = configparser.ConfigParser()
    # config.read('ViewConfig.ini')
    # percentage_of_division = float(config['Controller']['percentage_of_division'])
    percentage_of_division = 0.1
    stemming_mode = stem
    print("stemming mode: " + stemming_mode)
    return start_search_engine(stemming_mode, dir_path, percentage_of_division)


def start_search_engine(stemming_mode, dir_path, percentage_of_division):
    print("start_search_engine")
    string_city = []
    list_of_folser = os.listdir(dir_path)
    the_total_number_of_files = len(list_of_folser)
    number_files_in_packet = round((the_total_number_of_files * percentage_of_division) + 0.5)
    if the_total_number_of_files == 1:
        the_total_number_of_files = 2
    posting_id = 0
    global start_time
    start_time = time.time()
    # This loop performs for each file - saving its list of file names. And for each list, read the list in the ReadFile
    for number_of_file in range(1, the_total_number_of_files, number_files_in_packet):
        send_list_to_read_file = []
        for i in range(number_of_file, number_of_file + number_files_in_packet):
            if i <= the_total_number_of_files:
                print(i)
                path = dir_path + "\\" + list_of_folser[i - 1]
                send_list_to_read_file.append(path)
        # read files

        read_file_packet = ReadFile.read_packet(send_list_to_read_file)
        terms_packet = {}  # [term] = {[doc_id] = freq , [doc_id] = freq .... }
        # update the terms_packet and all_document dictionary after parsing and stamming
        parse_and_stemming_and_update(stemming_mode, read_file_packet, terms_packet, string_city)
        # posting
        posting_id = posting_id + 1
        Indexer.create_temp_posting_packet(stemming_mode, posting_id, terms_packet)

    # Outside the loop

    # create_all_language()
    create_all_city(string_city)
    # avg = calc_avg_length_docs()
    # print("The average length of documents: " + str(avg) + " - stemming_mode:" + stemming_mode)

    # merge all posting
    if stemming_mode == 'yes':
        sum_numbers = Indexer.merge_all_posting(stemming_mode, posting_id, len(all_document),
                                                the_final_terms_dictionary, cach_dictionary, all_city, max_doc_city)
    elif stemming_mode == 'no':
        sum_numbers = Indexer.merge_all_posting(stemming_mode, posting_id, len(all_document),
                                                the_final_terms_dictionary_without_stemming, cach_dictionary, all_city,
                                                max_doc_city)

    save_dictionary(stemming_mode)
    # get_answers(sum_numbers)
    return get_answers_start()
    # reset()


def parse_and_stemming_and_update(stemming_mode, read_file_packet, terms_packet, string_city):
    print("parse_and_stemming_and_update")
    for id, value in read_file_packet.items():
        doc_len = 0
        doc_maxtf = 0
        doc_id = value[1]
        doc_city = []
        for city in value[3]:
            doc_city.append(city.upper())

        if doc_city:
            for curr_city in doc_city:
                if curr_city[0] == "(" and curr_city[len(curr_city) - 1] == ")":
                    curr_city = curr_city[1:len(curr_city) - 2]
                if curr_city not in string_city and "<" not in curr_city:
                    string_city.append(curr_city)

        parse_terms_doc = Parse.parse_text(value[4] + value[2])
        stemm_term_doc = Stemmer.stemming(parse_terms_doc, stemming_mode)

        # if doc_id == "FBIS3-3366":
        #     stemm_term_doc_items = stemm_term_doc.items()
        #     sort_stemm_term_doc_items = sorted(stemm_term_doc_items, key=lambda term: term[0])
        #     print("The terms of the document FBIS3-3366 : " + str(sort_stemm_term_doc_items))

        doc_file_is = value[0]
        if len(value[3]) > 1:
            print("more then 1 city")
            print(doc_file_is)
            print(doc_id)
        unique_words = len(stemm_term_doc)
        # key = the , value = 11
        denominator_of_normalization_factor_doc = 0
        for term, details in stemm_term_doc.items():
            freq = details[0]
            position = details[1]
            if doc_maxtf < freq:
                doc_maxtf = freq
            doc_len = doc_len + freq
            denominator_of_normalization_factor_doc = denominator_of_normalization_factor_doc + pow(freq, 2)

            if term in terms_packet:
                terms_packet[term][doc_id] = [freq, position]
            else:
                terms_packet[term] = {}
                terms_packet[term][doc_id] = [freq, position]

        all_document[doc_id] = [doc_file_is, doc_maxtf, doc_len, doc_city, unique_words,denominator_of_normalization_factor_doc]
        #all_document[doc_id] = [doc_file_is, doc_maxtf, doc_len, doc_city, unique_words]


def create_all_city(string_city):
    print("create_all_city")
    start_city = time.time()

    for city in string_city:
        flag = True
        try:
            country_list = rapi.get_countries_by_capital(city)
            country = country_list[0]
            country_name = country.name
            coin = country.currencies[0]['code']
            population_size = country.population
            capital = city

        except ValueError:
            url = "http://getcitydetails.geobytes.com/GetCityDetails?fqcn=" + city
            response = urllib.request.urlopen(url)
            html = response.read()
            try:
                response = html.decode('utf8')
            except ValueError:
                response = html.decode('latin-1')
            obj = json.loads(response)
            country_name = str(obj[u'geobytescountry'])
            coin = str(obj[u'geobytescurrencycode'])
            try:
                population_size = int(obj[u'geobytespopulation'])
                token = str(population_size)
                token_len = len(token)
                if token_len < 4:
                    new_token = token
                elif token_len < 7:  # 87,999.00
                    start = token[:-3]  # 87
                    div = token[:-1]  # 8799
                    div = div[-2:]  # 99
                    new_token = start + "." + div + "K"
                elif token_len < 10:  # 100,230,000.00
                    start = token[:-6]  # 100
                    div = token[:-4]  # 10023
                    div = div[-2:]  # 23
                    new_token = start + "." + div + "M"
                else:  # 105,230,000,000.00
                    start = token[:-9]  # 105
                    div = token[:-7]  # 230
                    div = div[-2:]  # 23
                    new_token = start + "." + div + "B"
                population_size = str(new_token)

            except ValueError:
                flag = False
            capital = str(obj[u'geobytescapital'])

        if flag:
            if city == capital:
                all_city[city] = [country_name, coin, population_size, capital, 0, 0, 0, 0]
            else:
                all_city[city] = [country_name, coin, population_size, capital, 1, 0, 0, 0]

    end_city = time.time()
    total_city = end_city - start_city
    print("Time city: " + str("{:.2f}".format(total_city / 60)) + " minutes")
    print("Time city: " + str("{:.2f}".format(total_city)) + " seconds")


def get_cach_dictionary(stemm):
    print("get_cach_dictionary")
    print("stemming",stemm)
    if stemm == "yes":
        print("get_cach_dictionary","the_final_terms_dictionary")
        return the_final_terms_dictionary
    else:
        print("get_cach_dictionary", "the_final_terms_dictionary_without_stemming")
        return the_final_terms_dictionary_without_stemming


def get_number_documents_indexed():
    return len(all_document)


def get_unique_words():
    return len(cach_dictionary)


def save_dictionary(stemming_mode):
    print("save_dictionary")
    folder_name = dir_path_save + '/' + "json"
    if stemming_mode == "yes":
        file_path = folder_name + "/" + 'dictionary_stemming.json'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_path, 'w') as file:
            json.dump(the_final_terms_dictionary, file)
    else:
        file_path = folder_name + "/" + 'dictionary_without_stemming.json'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_path, 'w') as file:
            json.dump(the_final_terms_dictionary_without_stemming, file)

    file_path = folder_name + "/" + 'dictionary_cities.json'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open(file_path, 'w') as file:
        json.dump(all_city, file)

    file_path = folder_name + "/" + 'dictionary_docs.json'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open(file_path, 'w') as file:
        json.dump(all_document, file)


def load_dictionary(stemming, path_folder_save):
    global the_final_terms_dictionary
    global the_final_terms_dictionary_without_stemming
    global all_city
    global all_document
    global stemming_mode
    print("load_dictionary")
    stemming_mode = stemming

    print("stemming_mode", stemming_mode)
    folder_name = path_folder_save + '/' + "json"
    if stemming_mode == "yes":
        file_path = folder_name + "/" + 'dictionary_stemming.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as openfile:
                the_final_terms_dictionary = json.load(openfile)
                print("load the_final_terms_dictionary")
    else:
        file_path = folder_name + "/" + 'dictionary_without_stemming.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as openfile:
                the_final_terms_dictionary_without_stemming = json.load(openfile)
                print("load the_final_terms_dictionary_without_stemming")

    file_path = folder_name + "/" + 'dictionary_cities.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as openfile:
            all_city = json.load(openfile)
            print("load all_city")

    file_path = folder_name + "/" + 'dictionary_docs.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as openfile:
            all_document = json.load(openfile)
            print("load all_document")

    # create_inpute_zip_law() ##############################################################


def get_answers_start():
    end_time = time.time()
    total_time = end_time - start_time
    print("Time: " + str("{:.2f}".format(total_time / 60)) + " minutes")
    print("Time: " + str("{:.2f}".format(total_time)) + " seconds")

    result = []
    result.append(str(len(all_document)))
    result.append(str(len(the_final_terms_dictionary_without_stemming)))
    result.append(str(len(the_final_terms_dictionary)))
    result.append(str("{:.2f}".format(total_time / 60)))
    result.append(str("{:.2f}".format(total_time)))
    return result


def get_answers(sum_numbers):
    print("get_answers")
    # 1
    print("Number of different terms without stemming: " + str(len(the_final_terms_dictionary_without_stemming)))
    # 2
    print("Number of different terms with stemming: " + str(len(the_final_terms_dictionary)))
    # 3
    print("Number of different number terms: " + str(sum_numbers))
    # 4
    dic_count = Counter(tok[0] for tok in all_city.values())
    list_of_countries = list(dic_count.items())
    number_countries = len(list_of_countries)
    print("Number of different countries: " + str(number_countries))
    # 5
    number_cities = len(all_city)
    print("Number of different cities: " + str(number_cities))
    dic_count = Counter(tok[4] for tok in all_city.values())
    list_of_capital = dict(dic_count.items())
    number_not_capital_city = list_of_capital[1]
    print("Number of cities that are not capital cities: " + str(number_not_capital_city))
    # 6
    city_max = ""
    freq_max = 0
    doc_max = ""
    doc_position_max = ""
    for city, value in max_doc_city.items():
        list_details = value[1]
        for i in list_details:
            freq = i[1][0]
            doc = i[0]
            position = i[1][1]
            if freq > freq_max:
                freq_max = freq
                doc_max = doc
                city_max = city
                doc_position_max = position
    print("Name the document with the most shows of a single city: \n" + "city: " + str(
        city_max) + " number of shows: " + str(freq_max) + " document: " + str(
        doc_max) + " poisition in document: " + str(doc_position_max))
    # 7
    t = sorted(cach_dictionary, key=cach_dictionary.get, reverse=True)
    min_10 = t[len(cach_dictionary) - 10:]
    max_10 = t[:10]
    print("The 10 most common terms in the corpus: " + str(max_10))
    print("10 The least common terms in the database: " + str(min_10))
    # my
    print("number_of_documents: " + str(len(all_document)))


def create_inpute_zip_law():
    print("create_inpute_zip_low")
    # sort by value term
    temp_terms_value = cach_dictionary.items()
    sort_value = list(reversed(sorted(temp_terms_value, key=lambda freq: freq[1])))
    max_50 = sort_value[:50]
    print(max_50)
    file_zip_stemming = r"C:\Users\shake\PycharmProjects\SearchEngineIR\Model\Indexer\file_zip_stemming.txt"
    file_zip_without_stemming = r"C:\Users\shake\PycharmProjects\SearchEngineIR\Model\Indexer\file_zip_without_stemming.txt"
    try:
        zip_file_stemm = open(file_zip_stemming, "w")

    except IOError:
        return "fail"

    with zip_file_stemm:
        for term, value in max_50:
            zip_file_stemm.write(term + ";" + str(value) + '\n')

        zip_file_stemm.close()

    # try:
    #     zip_file = open(file_zip_without_stemming, "w")
    #
    # except IOError:
    #     return "fail"
    #
    # with zip_file:
    #     for term, value in the_final_terms_dictionary_without_stemming.items():
    #         zip_file.write(term + ";" + str(value[2])+'\n')
    #
    #     zip_file.close()

    print("final create_inpute_zip_low")


def create_all_language():
    language = ReadFile.get_array_language()
    language = set(language)
    language = sorted(list(language))
    print(language)
    folder_name = r"C:\Users\shake\PycharmProjects\SearchEngineIR\Model\ReadFile"
    file_path = folder_name + "/" + 'languages.json'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open(file_path, 'w') as file:
        json.dump(language, file)


def get_peth_corpus():
    return dir_path_corpus


def get_peth_posting():
    return dir_path_save


def reset_dictionary_json():
    print("reset_dictionary_json")
    folder_name = dir_path_save + '/' + "json"
    file_path_stemming = folder_name + "/" + 'dictionary_stemming.json'
    file_path_not_stemming = folder_name + "/" + 'dictionary_without_stemming.json'
    file_path_cities = folder_name + "/" + 'dictionary_cities.json'
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)

    # os.remove(file_path_stemming)
    # os.remove(file_path_not_stemming)
    # os.remove(file_path_cities)


def calc_avg_length_docs(stemming_mode, dir_path_save):
    load_dictionary(stemming_mode, dir_path_save)
    sum_length = 0
    number_of_docs = len(all_document)
    for doc, value in all_document.items():
        sum_length = sum_length + value[2]

    result = sum_length / number_of_docs
    print(result)
    return result


def reset(path_to_save):
    global dir_path_save
    dir_path_save = path_to_save
    print("reset - controller")
    the_final_terms_dictionary.clear()
    the_final_terms_dictionary_without_stemming.clear()
    all_document.clear()
    all_city.clear()
    cach_dictionary.clear()
    max_doc_city.clear()
    reset_dictionary_json()
    Indexer.reset_temp_posting()
    Indexer.reset_posting()
    Stemmer.reset()
    ReadFile.reset()


def enter_query_text(query, stemming, path_corpus, path_save_folder, selected_cities, semantic_mode):
    print("enter_query_text")
    start_time_search = time.time()
    global stemming_mode
    stemming_mode = stemming
    global dir_path_corpus
    dir_path_corpus = path_corpus
    global dir_path_save
    dir_path_save = path_save_folder
    selected_cities_from_user = selected_cities

    load_dictionary(stemming_mode, dir_path_save)

    if stemming_mode == 'yes':
        the_searcher = Searcher.Searcher(stemming_mode, dir_path_corpus, the_final_terms_dictionary, all_document,
                                         selected_cities_from_user, semantic_mode)

    else:
        the_searcher = Searcher.Searcher(stemming_mode, dir_path_corpus, the_final_terms_dictionary_without_stemming,
                                         all_document, selected_cities_from_user, semantic_mode)

    list_of_docs = the_searcher.results_relevant_documents_to_one_query(query)

    end_time_search = time.time()
    total_time = end_time_search - start_time_search
    print("result load_query_file")
    print(total_time)
    # save_result_from_query_text_to_file(list_of_docs)
    return total_time, list_of_docs


def load_query_file(path_queries, stemming, path_corpus, path_save_folder, selected_cities, semantic_mode):
    print("load_query_file")
    start_time_search = time.time()
    global stemming_mode
    stemming_mode = stemming
    global dir_path_corpus
    dir_path_corpus = path_corpus
    global dir_path_save
    dir_path_save = path_save_folder
    selected_cities_from_user = selected_cities

    load_dictionary(stemming_mode, dir_path_save)
    # call searcher
    # merge all posting
    if stemming_mode == 'yes':
        # call reader
        queries_dictionary = ReadFile.read_queries_files(path_queries)
        the_searcher = Searcher.Searcher(stemming_mode, dir_path_corpus, the_final_terms_dictionary, all_document,
                                         selected_cities_from_user, semantic_mode)

    else:
        # call reader
        queries_dictionary = ReadFile.read_queries_files(path_queries)
        the_searcher = Searcher.Searcher(stemming_mode, dir_path_corpus, the_final_terms_dictionary_without_stemming,
                                         all_document, selected_cities_from_user, semantic_mode)

    # [(query,list),(query,list)...]
    list_of_docs = the_searcher.results_relevant_documents(queries_dictionary)

    end_time_search = time.time()
    total_time = end_time_search - start_time_search
    print("result load_query_file")
    print(total_time)
    #calc_score(list_of_docs)
    #save_result_from_load_query_to_file(list_of_docs)
    return total_time,list_of_docs


def entity_search(file_selected, stemming, path_save_folder, path_folder):
    print("entity_search")
    global stemming_mode
    stemming_mode = stemming
    global dir_path_corpus
    dir_path_corpus = path_folder
    global dir_path_save
    dir_path_save = path_save_folder
    load_dictionary(stemming_mode, dir_path_save)
    file_selected = file_selected.split(": ")[1]
    my_file = all_document[file_selected][0]
    dir_path = path_folder + '/' + "corpus" + "\\" + my_file + "\\" + my_file
    print(dir_path)
    read_doc = ReadFile.read_entity(dir_path, file_selected)
    # [file_id, doc_id, doc_text, doc_city]
    if stemming_mode == "yes":
        final_dic = the_final_terms_dictionary
    else:
        final_dic = the_final_terms_dictionary_without_stemming

    parse_terms_doc = Parse.parse_text(read_doc[2])
    stemm_term_doc = Stemmer.stemming(parse_terms_doc, stemming_mode)
    all_entity = {}
    for term, val in stemm_term_doc.items():
        freq = val[0]
        positions = val[1].split("|")
        min_position = positions[0]
        term_up = term.upper()
        if term_up in final_dic:
            if not isfloat(term_up) and not "TYPE:BFN" == term_up and not "TYPE:CSO" == term_up:
                all_entity[term_up] = (freq,min_position)

    the_ranker = Ranker.Ranker(stemming_mode, [])
    doc_len = all_document[file_selected][2]
    doc_max_tf = all_document[file_selected][1]
    all_entity = the_ranker.rank_entities(all_entity, all_document, doc_len, doc_max_tf, final_dic)
    all_entity = dict(Counter(all_entity).most_common(5))
    return all_entity


def isfloat(value):
    value = value[0]
    try:
        float(value)
        return True
    except ValueError:
        return False


def calc_score(list_of_docs):
    print("calc_score")
    query_relevant_docs = {}
    #relevant_doc_path = r"C:\Users\shake\Desktop\לימודים\סמסטר ז\אחזור מידע\חלק ב\qrels.csv"
    file_types = (("Comma Separated Value Document", "*.csv"),)
    relevant_doc_path = askopenfilename(title="Choose real results csv file", filetypes=file_types)
    docs_rel = open(relevant_doc_path).read()
    docs_rel = docs_rel.split('\n')
    docs_rel = docs_rel[:-1]
    for line in docs_rel:
        line_split = line.split(',')
        query_id = line_split[0]
        doc_id = line_split[1]
        if query_id in query_relevant_docs:
            query_relevant_docs[query_id].add(doc_id)
        else:
            query_relevant_docs[query_id] = set()
            query_relevant_docs[query_id].add(doc_id)

    score = 0
    for query_docs in list_of_docs:
        query_id = query_docs[0]
        rel_docs_set = query_relevant_docs[query_id]
        results_set = set(query_docs[1])
        intersection_set = rel_docs_set.intersection(results_set)
        score += len(intersection_set)

    print("number of all relevant: " + str(len(docs_rel)))
    print("number of relevant and return: " + str(score))


def save_result_from_query_text_to_file(list_of_docs,path_folder):
    print("save_result_from_query_text_to_file")
    query_id = "0"
    iter = "0"
    rank = "1"
    sim = "0"
    run_id = "runID"

    path_result = path_folder + '/' + "results.txt"
    with open(path_result, 'w') as srp:
        for docno in list_of_docs:
            line = "%s %s %s %s %s %s \n" % (query_id, iter, docno, rank, sim, run_id)
            srp.write(line)


def save_result_from_load_query_to_file(list_of_docs,path_folder):
    print("save_result_from_load_query_to_file")
    # query_id, iter, docno, rank, sim, run_id
    iter = "0"
    rank = "1"
    sim = "0"
    run_id = "runID"
    path_result = path_folder + '/' + "results.txt"
    with open(path_result, 'w') as srp:
        for query_result in list_of_docs:
            query_id = query_result[0]
            for docno in query_result[1]:
                line = "%s %s %s %s %s %s \n" % (query_id, iter, docno, rank, sim, run_id)
                srp.write(line)


# help function for calculating the optimal components of the rating
def calc_optimal_components(path_queries, stemming, path_folder, path_save_folder,selected_cities, semantic_mode):
    print("calc_optimal_components")
    global stemming_mode
    stemming_mode = stemming
    global dir_path_corpus
    dir_path_corpus = path_folder
    global dir_path_save
    dir_path_save = path_save_folder
    print("stemming_mode",stemming_mode)

    load_dictionary(stemming_mode, dir_path_save)
    if stemming_mode == 'yes':
        # call reader
        queries_dictionary = ReadFile.read_queries_files(path_queries)
        the_searcher = Searcher.Searcher(stemming_mode, dir_path_corpus, the_final_terms_dictionary, all_document,
                                         selected_cities,semantic_mode)

    else:
        # call reader
        queries_dictionary = ReadFile.read_queries_files(path_queries)
        the_searcher = Searcher.Searcher(stemming_mode, dir_path_corpus, the_final_terms_dictionary_without_stemming,
                                         all_document,selected_cities, semantic_mode)

    # [query] = set of only relevant document
    query_relevant_docs = {}
    file_types = (("Comma Separated Value Document", "*.csv"),)
    relevant_doc_path = askopenfilename(title="Choose real results csv file", filetypes=file_types)
    file_types = (("Any file", "*.*"),)
    save_path = asksaveasfilename(title="Choose where to save the test results", filetypes=file_types,
                                  initialfile="optimal_test.csv")
    docs_rel = open(relevant_doc_path).read()
    docs_rel = docs_rel.split('\n')
    docs_rel = docs_rel[:-1]
    for line in docs_rel:
        line_split = line.split(',')
        query_id = line_split[0]
        doc_id = line_split[1]
        if query_id in query_relevant_docs:
            query_relevant_docs[query_id].add(doc_id)
        else:
            query_relevant_docs[query_id] = set()
            query_relevant_docs[query_id].add(doc_id)

    # test 4 : denominator , weight_idf ,weight_df

    the_searcher.denominator = 1.0  # Range: [1.0 - 2.5] jump 0.3
    the_searcher.weight_idf = 0.0  # Range: [0.0 - 1.0] jump 0.2
    the_searcher.weight_df = 0.1  # Range: [0.1 - 1.0] jump 0.2

    the_searcher.ranker.weight_bm25 = 0.2
    the_searcher.ranker.weight_cos_sim = 0.8

    the_searcher.ranker.k1_bm25 = 1.2  # Range: [1.2 - 2.0]
    the_searcher.ranker.b_bm25 = 0.1  # Range: [0.45-1.0]

    the_searcher.ranker.lambda_bm25 = 0.5  # Range: [0-1.0]

    the_searcher.ranker.number_result_semantic = 5  # Range: [5-20]

    columns = 'bm25 weight, cos sim weight, bm25 k, bm25 b, bm25 lambda, Denominator, searcher idf, searcher df ,number result semantic, score\n'
    file_save_result = open(save_path, 'a')
    file_save_result.write(columns)
    file_save_result.close()

    while the_searcher.denominator <= 2.5:
        the_searcher.weight_idf = 0
        while the_searcher.weight_idf <= 1:
            the_searcher.weight_df = 0.1
            while the_searcher.weight_df <= 1:

                list_of_docs = the_searcher.results_relevant_documents(queries_dictionary)

                score = 0
                for query_docs in list_of_docs:
                    query_id = query_docs[0]
                    rel_docs_set = query_relevant_docs[query_id]
                    results_set = set(query_docs[1])
                    intersection_set = rel_docs_set.intersection(results_set)
                    score += len(intersection_set)

                result_score = "%f, %f, %f, %f, %f, %f, %f, %f, %f, %d\n" % \
                               (the_searcher.ranker.weight_bm25, the_searcher.ranker.weight_cos_sim,
                                the_searcher.ranker.k1_bm25,
                                the_searcher.ranker.b_bm25, the_searcher.ranker.lambda_bm25,
                                the_searcher.denominator, the_searcher.weight_idf, the_searcher.weight_df,
                                the_searcher.ranker.number_result_semantic, score)
                file_save_result = open(save_path, 'a')
                file_save_result.write(result_score)
                file_save_result.close()

                the_searcher.weight_df += 0.2
            the_searcher.weight_idf += 0.2
        the_searcher.denominator += 0.3

    '''
       # test 3 : lambda_bm25

    the_searcher.denominator = 1.0
    the_searcher.weight_idf = 0.5
    the_searcher.weight_df = 0.5

    the_searcher.ranker.weight_bm25 = 0.2
    the_searcher.ranker.weight_cos_sim = 0.8

    the_searcher.ranker.k1_bm25 = 1.2  # Range: [1.2 - 2.0]
    the_searcher.ranker.b_bm25 = 0.1  # Range: [0.45-1.0]

    the_searcher.ranker.lambda_bm25 = 0.0  # Range: [0-1.0]

    the_searcher.ranker.number_result_semantic = 5  # Range: [5-20]

    columns = 'bm25 weight, cos sim weight, bm25 k, bm25 b, bm25 lambda, Denominator, searcher idf, searcher df ,number result semantic, score\n'
    file_save_result = open(save_path, 'a')
    file_save_result.write(columns)
    file_save_result.close()

    while the_searcher.ranker.lambda_bm25 <= 1:

        list_of_docs = the_searcher.results_relevant_documents(queries_dictionary)

        score = 0
        for query_docs in list_of_docs:
            query_id = query_docs[0]
            rel_docs_set = query_relevant_docs[query_id]
            results_set = set(query_docs[1])
            intersection_set = rel_docs_set.intersection(results_set)
            score += len(intersection_set)

        result_score = "%f, %f, %f, %f, %f, %f, %f, %f, %f, %d\n" % \
                       (the_searcher.ranker.weight_bm25, the_searcher.ranker.weight_cos_sim,
                        the_searcher.ranker.k1_bm25,
                        the_searcher.ranker.b_bm25, the_searcher.ranker.lambda_bm25,
                        the_searcher.denominator, the_searcher.weight_idf, the_searcher.weight_df,
                        the_searcher.ranker.number_result_semantic, score)
        file_save_result = open(save_path, 'a')
        file_save_result.write(result_score)
        file_save_result.close()
        the_searcher.ranker.lambda_bm25 += 0.1
        #the_searcher.ranker.lambda_bm25 += 0.05
    '''

    '''
        # test 2 : weight_cos_sim , weight_bm25
    the_searcher.denominator = 1.0
    the_searcher.weight_idf = 0.5
    the_searcher.weight_df = 0.5

    the_searcher.ranker.weight_bm25 = 0.0
    the_searcher.ranker.weight_cos_sim = 0.0

    the_searcher.ranker.k1_bm25 = 1.2  # Range: [1.2 - 2.0]
    the_searcher.ranker.b_bm25 = 0.1  # Range: [0.45-1.0]

    the_searcher.ranker.lambda_bm25 = 0.25  # [Range: 0-1.0]

    the_searcher.ranker.number_result_semantic = 5  # Range: [5-20]

    columns = 'bm25 weight, cos sim weight, bm25 k, bm25 b, bm25 lambda, Denominator, searcher idf, searcher df ,number result semantic, score\n'
    file_save_result = open(save_path, 'a')
    file_save_result.write(columns)
    file_save_result.close()

    while the_searcher.ranker.weight_bm25 <= 1.01:
        the_searcher.ranker.weight_cos_sim = 1 - the_searcher.ranker.weight_bm25
        list_of_docs = the_searcher.results_relevant_documents(queries_dictionary)

        score = 0
        for query_docs in list_of_docs:
            query_id = query_docs[0]
            rel_docs_set = query_relevant_docs[query_id]
            results_set = set(query_docs[1])
            intersection_set = rel_docs_set.intersection(results_set)
            score += len(intersection_set)

        result_score = "%f, %f, %f, %f, %f, %f, %f, %f, %f, %d\n" % \
                       (the_searcher.ranker.weight_bm25, the_searcher.ranker.weight_cos_sim,
                        the_searcher.ranker.k1_bm25,
                        the_searcher.ranker.b_bm25, the_searcher.ranker.lambda_bm25,
                        the_searcher.denominator, the_searcher.weight_idf, the_searcher.weight_df,
                        the_searcher.ranker.number_result_semantic, score)
        file_save_result = open(save_path, 'a')
        file_save_result.write(result_score)
        file_save_result.close()
        print(the_searcher.ranker.weight_bm25, the_searcher.ranker.weight_cos_sim)
        the_searcher.ranker.weight_bm25 += 0.1
    '''

    '''
        # test 5 : number_result_semantic
    the_searcher.denominator = 1.9  # Range: [1.0 - 2.5] jump 0.3
    the_searcher.weight_idf = 0.6  # Range: [0.0 - 1.0] jump 0.2
    the_searcher.weight_df = 0.5  # Range: [0.1 - 1.0] jump 0.2

    the_searcher.ranker.weight_bm25 = 0.2
    the_searcher.ranker.weight_cos_sim = 0.8

    the_searcher.ranker.k1_bm25 = 1.2  # Range: [1.2 - 2.0]
    the_searcher.ranker.b_bm25 = 0.1  # Range: [0.45-1.0]

    the_searcher.ranker.lambda_bm25 = 0.6  # Range: [0-1.0]

    the_searcher.ranker.number_result_semantic = 5  # Range: [5-20]

    columns = 'bm25 weight, cos sim weight, bm25 k, bm25 b, bm25 lambda, Denominator, searcher idf, searcher df ,number result semantic, score\n'
    file_save_result = open(save_path, 'a')
    file_save_result.write(columns)
    file_save_result.close()

    while the_searcher.ranker.number_result_semantic <= 30:
        list_of_docs = the_searcher.results_relevant_documents(queries_dictionary)
        score = 0
        for query_docs in list_of_docs:
            query_id = query_docs[0]
            rel_docs_set = query_relevant_docs[query_id]
            results_set = set(query_docs[1])
            intersection_set = rel_docs_set.intersection(results_set)
            score += len(intersection_set)

        result_score = "%f, %f, %f, %f, %f, %f, %f, %f, %f, %d\n" % \
                       (the_searcher.ranker.weight_bm25, the_searcher.ranker.weight_cos_sim,
                        the_searcher.ranker.k1_bm25,
                        the_searcher.ranker.b_bm25, the_searcher.ranker.lambda_bm25,
                        the_searcher.denominator, the_searcher.weight_idf, the_searcher.weight_df,
                        the_searcher.ranker.number_result_semantic, score)
        file_save_result = open(save_path, 'a')
        file_save_result.write(result_score)
        file_save_result.close()
        the_searcher.ranker.number_result_semantic += 2

    '''

    '''
        # test 1 : b_bm25 , k1_bm25
    the_searcher.denominator = 1.0
    the_searcher.weight_idf = 0.5
    the_searcher.weight_df = 0.5

    the_searcher.ranker.weight_bm25 = 0.5
    the_searcher.ranker.weight_cos_sim = 0.5

    the_searcher.ranker.k1_bm25 = 1.2  # Range: [1.2 - 2.0]
    the_searcher.ranker.b_bm25 = 0.1  # Range: [0.45-1.0]

    the_searcher.ranker.lambda_bm25 = 0.25  # Range: [0-1.0]

    the_searcher.ranker.number_result_semantic = 5  # Range: [5-20]

    columns = 'bm25 weight, cos sim weight, bm25 k, bm25 b, bm25 lambda, Denominator, searcher idf, searcher df ,number result semantic, score\n'
    file_save_result = open(save_path, 'a')
    file_save_result.write(columns)
    file_save_result.close()

    while the_searcher.ranker.k1_bm25 <= 2.01:
        the_searcher.ranker.b_bm25 = 0.1
        while the_searcher.ranker.b_bm25 <= 1.01:

            list_of_docs = the_searcher.results_relevant_documents(queries_dictionary)

            score = 0
            for query_docs in list_of_docs:
                query_id = query_docs[0]
                rel_docs_set = query_relevant_docs[query_id]
                results_set = set(query_docs[1])
                intersection_set = rel_docs_set.intersection(results_set)
                score += len(intersection_set)

            result_score = "%f, %f, %f, %f, %f, %f, %f, %f, %f, %d\n" % \
                           (the_searcher.ranker.weight_bm25, the_searcher.ranker.weight_cos_sim,
                            the_searcher.ranker.k1_bm25,
                            the_searcher.ranker.b_bm25, the_searcher.ranker.lambda_bm25,
                            the_searcher.denominator, the_searcher.weight_idf, the_searcher.weight_df, the_searcher.ranker.number_result_semantic, score)
            file_save_result = open(save_path, 'a')
            file_save_result.write(result_score)
            file_save_result.close()
            the_searcher.ranker.b_bm25 += 0.1
            the_searcher.ranker.k1_bm25 += 0.1
    
    '''





    



















    













































