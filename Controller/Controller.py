import glob
import json
import os
import time
from Model.Indexer import Indexer
from Model.Parse import Parse
import configparser
from restcountries import RestCountryApiV2 as rapi
from collections import Counter

from Model.ReadFile import ReadFile
from Model.Stemmer import Stemmer
import urllib.request

the_final_terms_dictionary = {} # [term] = (df,idf,sum_tf, the_abc_posting_name,line_in_file)
the_final_terms_dictionary_without_stemming = {} # [term] = (df,idf,sum_tf, the_abc_posting_name,line_in_file)
all_document = {} # [doc_id] = (file_id , doc_maxtf , length ,doc_city,unique_words)
all_city = {} # [city] = (country_name,coin,population_size,number_of_file)
cach_dictionary = {} # [term] = tf
start_time = 0
dir_path_corpus=""
dir_path_save=""
stemming_mode = "yes"


def init_path(path_corpus,path_save,stem):
    print("init_path")
    global dir_path_corpus
    global dir_path_save
    global stemming_mode
    dir_path_save = path_save
    print(dir_path_save)
    dir_path_corpus = path_corpus
    dir_path = path_corpus+'/'+"Temp_corpus"
    print(dir_path)
    config = configparser.ConfigParser()
    config.read('ViewConfig.ini')
    percentage_of_division = float(config['Controller']['percentage_of_division'])
    stemming_mode = stem
    print(stemming_mode)
    print("stemming mode: " + stemming_mode)
    return start_search_engine(stemming_mode,dir_path,percentage_of_division)


def start_search_engine(stemming_mode,dir_path,percentage_of_division):
    print("start_search_engine")
    string_city = {}
    list_of_folser = os.listdir(dir_path)
    the_total_number_of_files = len(list_of_folser)
    number_files_in_packet = round((the_total_number_of_files*percentage_of_division)+0.5)

    posting_id = 0
    global start_time
    start_time = time.time()
    # This loop performs for each file - saving its list of file names. And for each list, read the list in the ReadFile
    for number_of_file in range(1, the_total_number_of_files, number_files_in_packet):
        send_list_to_read_file = []
        for i in range(number_of_file, number_of_file + number_files_in_packet):
            if i <= the_total_number_of_files:
                print(i)
                path = dir_path + "\\" + list_of_folser[i-1]
                send_list_to_read_file.append(path)
        # read files

        read_file_packet = ReadFile.read_packet(send_list_to_read_file)
        terms_packet = {} # [term] = {[doc_id] = freq , [doc_id] = freq .... }
        # update the terms_packet and all_document dictionary after parsing and stamming
        parse_and_stemming_and_update(stemming_mode,read_file_packet,terms_packet,string_city)
        # posting
        posting_id = posting_id + 1
        Indexer.create_temp_posting_packet(stemming_mode,posting_id,terms_packet)

    # Outside the loop
    # merge all posting
    if stemming_mode=='yes':
        sum_numbers = Indexer.merge_all_posting(stemming_mode,posting_id,len(all_document),the_final_terms_dictionary,cach_dictionary)
    elif stemming_mode == 'no':
        sum_numbers = Indexer.merge_all_posting(stemming_mode,posting_id, len(all_document), the_final_terms_dictionary_without_stemming,cach_dictionary)

    save_dictionary(stemming_mode)
    #create_all_city(string_city)
    #create_posting_city()
    #get_answers(sum_numbers)
    #cach_dictionary.clear()
    return get_answers_start()
    #reset()


def parse_and_stemming_and_update(stemming_mode,read_file_packet,terms_packet,string_city):
    print("parse_and_stemming_and_update")
    for id , value in read_file_packet.items():
        doc_len = 0
        doc_maxtf = 0
        doc_city = []
        for city in value[3]:
            doc_city.append([city[0].upper(),city[1]])
        parse_terms_doc = Parse.parse_text(value[2])
        stemm_term_doc = Stemmer.stemming(parse_terms_doc,stemming_mode)
        doc_id = value[1]
        doc_file_is = value[0]
        if len(value[3])>1:
            print("more then 1 city")
            print(doc_file_is)
            print(doc_id)
        unique_words = len(stemm_term_doc)
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
        all_document[doc_id] = [doc_file_is, doc_maxtf, doc_len , doc_city,unique_words]


        if doc_city:
            for city in doc_city:
                curr_city = city[0]
                curr_position = city[1]

                if curr_city[0] == "(" and curr_city[len(curr_city)-1] == ")":
                    curr_city = curr_city[1:len(curr_city)-2]
                if curr_city in string_city:
                    string_city[curr_city][0] = string_city[curr_city][0]+1
                    details =  string_city[curr_city][1] + "|" +"("+doc_id+","+str(curr_position)+")"
                    string_city[curr_city][1] = details


                if curr_city not in string_city and "<" not in curr_city:
                    details ="("+doc_id+","+str(curr_position)+")"
                    string_city[curr_city] = [1,details]


def create_all_city(string_city):
    print("create_all_city")
    for city,val in string_city.items():
        number_of_file = val[0]
        all_doc = val[1]
        flag = True
        try:
            country_list = rapi.get_countries_by_capital(city)
            country = country_list[0]
            country_name = country.name
            coin = country.currencies[0]['code']
            population_size = country.population
            #population_size = str("%.2f" % (float(population_size) / 100))
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
                #population_size = str("%.2f" % (float(obj[u'geobytespopulation']) / 100))
                population_size = int(obj[u'geobytespopulation'])
            except ValueError:
                flag = False
            capital = str(obj[u'geobytescapital'])

        if flag:
            if city==capital:
                all_city[city] = [country_name, coin, population_size, capital, number_of_file,all_doc,0]
            else:
                all_city[city] = [country_name, coin, population_size, capital, number_of_file,all_doc,1]

def create_posting_city():
    print("create_posting_city")
    config = configparser.ConfigParser()
    config.read('ViewConfig.ini')
    file_path = str(config['Controller']['cities_path'])

    all_city_items = all_city.items()
    # sort by value term
    sort_terms = sorted(all_city_items, key=lambda term: term[0])
    try:
        posting_file = open(file_path, "w")

    except IOError:
        return "fail"

    with posting_file:
        for city, value in sort_terms:
            posting_file.write(city + "-->" + str(value[4]) + "(#)" + str(value[0:3])+"|"+str(value[5:6]) + '\n')

        posting_file.close()


def get_cach_dictionary():
    return cach_dictionary


def get_number_documents_indexed():
    return len(all_document)


def get_unique_words():
    return len(cach_dictionary)


def save_dictionary(stemming_mode):
    print("cach_dictionary")
    folder_name = dir_path_save + '/' + "json"
    if stemming_mode == "yes":
        file_path = folder_name + "/" + 'dictionary_stemming.json'
    else:
        file_path = folder_name + "/" + 'dictionary_without_stemming.json'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open(file_path, 'w') as fp:
        json.dump(cach_dictionary, fp)


def load_dictionary(stemming):
    print("load_dictionary")
    if stemming:
        stemming_mode = "yes"
    else:
        stemming_mode = "no"
    folder_name = dir_path_save + '/' + "json"
    if stemming_mode == "yes":
        file_path = folder_name + "/" + 'dictionary_stemming.json'
    else:
        file_path = folder_name + "/" + 'dictionary_without_stemming.json'

    if os.path.exists(file_path):
        with open(file_path, 'r') as openfile:
            result = json.load(openfile)
    return result


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
    dic_count = Counter(tok[6] for tok in all_city.values())
    list_of_capital = dict(dic_count.items())
    number_not_capital_city = list_of_capital[1]
    print("Number of cities that are not capital cities: " + str(number_not_capital_city))
    # 6

    # 7
    t = sorted(cach_dictionary, key=cach_dictionary.get, reverse=True)
    min_10 = t[len(cach_dictionary) - 10:]
    max_10 = t[:10]
    print("The 10 most common terms in the corpus: " + str(max_10))
    print("10 The least common terms in the database: "+ str(min_10))
    # my
    print("number_of_documents: " + str(len(all_document)))


def get_peth_corpus():
    return dir_path_corpus

def get_peth_posting():
    return dir_path_save


def reset():
    print("reset - controller")
    the_final_terms_dictionary.clear()
    the_final_terms_dictionary_without_stemming.clear()
    all_document.clear()
    all_city.clear()
    Indexer.reset_posting()
    Indexer.reset_temp_posting()
    Stemmer.reset()
    ReadFile.reset()


