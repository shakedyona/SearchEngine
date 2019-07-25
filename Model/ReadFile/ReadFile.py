import glob
import os

"""
A department whose job is to read the documents
"""

"""
The department will know to get a path of a folder in which to sit at all
The files (after making an unzip.) Each file has a lot of documents, required to identify the start of each
Document and separate the documents accordingly

<DOC> Start a document
<DOCNO> Symbolizes the document ID
<DATE1> Symbolizes the publication date of the document in the format of day month year
<TI> Symbolizes the title of the document.
<TEXT> Symbolizes the contents of the document.

"""
array_language = []

def read_packet(list_to_read):
    the_all_doc_in_all_folders = {}
    for folder in list_to_read:
        folder = folder + "/*"
        for file in glob.glob(folder):
            read_file(file, the_all_doc_in_all_folders)
    return the_all_doc_in_all_folders


def read_file(file_path, the_all_doc_in_all_folders):
    file_id = file_path.split("\\")
    file_id = file_id[len(file_id)-1]
    try:
        curr_file = open(file_path, "r")

    except IOError:
        return "fail"

    all_file = curr_file.read()
    curr_file.close()
    all_file = all_file.replace('\n', " ")
    list_of_doc = all_file.split("</DOC>")
    len_list = len(list_of_doc)
    i = 1
    for all_doc in list_of_doc:
        doc_text = ""
        doc_id = ""
        doc_city = []
        doc_title = ""
        if i < (len_list):

            # if "<F P=105>" in all_doc:
            #     part_doc_language = all_doc.split("<F P=105>")
            #     part_doc_language = part_doc_language[1].split("</F>")
            #     language = part_doc_language[0].replace(" ","")
            #     if not language.isnumeric():
            #         array_language.append(language)
            if "<TEXT>" in all_doc:
                all_doc_split = all_doc.split("<TEXT>")
                head_part = all_doc_split[0]
                text_part = all_doc_split[1]
                only_text = text_part.split("</TEXT>")
                only_text_part = only_text[0].split()
                doc_text = " ".join(word for word in only_text_part)

            else:
                head_part = all_doc
            part_doc_id = head_part.split("<DOCNO>")
            part_doc_id = part_doc_id[1]
            only_doc_id = part_doc_id.split("</DOCNO>")
            doc_id = only_doc_id[0].strip()

            if "</TI>" in head_part:
                part_T = head_part.split("<TI>")
                part_T = part_T[1]
                only_t = part_T.split("</TI>")
                doc_title = only_t[0].strip()

            if "<F P=104>" in head_part:
                part_doc_city = head_part.split("<F P=104>")
                part_doc_city = part_doc_city[1:]
                for city in part_doc_city:
                    city = city.split()
                    city = city[0]
                    #position = all_doc.find(city)
                    doc_city.append(city)

            doc_text = doc_text.replace("Language: <F P=105>", "")
            doc_text = doc_text.replace("English </F>", "")
            doc_text = doc_text.replace("</F>", "")
            doc_text = doc_text.replace("<F>", "")
            doc_text = doc_text.replace("</P>", "")
            doc_text = doc_text.replace("<P>", "")
            doc_text = doc_text.replace("<F P=106>", "")

            single_document = [file_id, doc_id, doc_text, doc_city,doc_title]
            the_all_doc_in_all_folders[doc_id] = single_document
            i = i + 1

#single_document = [file_id, doc_id, doc_text, doc_city,doc_title]
def get_array_language():
    return array_language


def read_queries_files(path_queries):
    print("read_queries_files")
    queries_dictionary = {} # [query_number] = title, description, narrative
    try:
        curr_file = open(path_queries, "r")

    except IOError:
        return "fail"

    all_file = curr_file.read()
    curr_file.close()
    all_file = all_file.replace('\n', " ")
    list_of_queries = all_file.split("</top>")
    len_list = len(list_of_queries)
    i = 1
    for query in list_of_queries:
        query_title = ""
        query_number = ""
        query_description = ""
        query_narrative = ""
        if i < (len_list):

            if "<num>" in query:
                split1 = query.split("<num>")
                head_part1 = split1[0]
                next_part1 = split1[1]
                split2 = next_part1.split("<title>")
                head_part2 = split2[0]
                next_part2 = split2[1]

                # num
                head_part2 = head_part2.replace("Number:",'')
                head_part2 = head_part2.replace(' ', '')
                query_number = head_part2

                split3 = next_part2.split("<desc>")
                head_part3 = split3[0]
                next_part3 = split3[1]

                # title
                head_part3 = head_part3.strip()
                head_part3 = head_part3.rstrip()
                query_title = head_part3


                split4 = next_part3.split("<narr>")
                head_part4 = split4[0]
                next_part4 = split4[1]

                # desc
                head_part4 = head_part4.replace("Description:", '')
                head_part4 = head_part4.strip()
                head_part4 = head_part4.rstrip()
                query_description = head_part4

                # narr
                next_part4 = next_part4.replace("Narrative:", '')
                next_part4 = next_part4.strip()
                next_part4 = next_part4.rstrip()
                query_narrative = next_part4

                single_query = [query_title, query_description, query_narrative]
                queries_dictionary[query_number] = single_query

            i = i + 1

    return queries_dictionary


def read_entity(my_file,my_doc):
    file_id = my_file.split("\\")
    file_id = file_id[len(file_id) - 1]
    try:
        curr_file = open(my_file, "r")

    except IOError:
        return "fail"

    all_file = curr_file.read()
    curr_file.close()
    all_file = all_file.replace('\n', " ")
    list_of_doc = all_file.split("</DOC>")
    len_list = len(list_of_doc)
    i = 1
    for all_doc in list_of_doc:
        if my_doc in all_doc:
            doc_text = ""
            doc_id = ""
            doc_city = []
            if i < (len_list):
                if "<TEXT>" in all_doc:
                    all_doc_split = all_doc.split("<TEXT>")
                    head_part = all_doc_split[0]
                    text_part = all_doc_split[1]
                    only_text = text_part.split("</TEXT>")
                    only_text_part = only_text[0].split()

                    doc_text = " ".join(word for word in only_text_part)

                else:
                    head_part = all_doc
                part_doc_id = head_part.split("<DOCNO>")
                part_doc_id = part_doc_id[1]
                only_doc_id = part_doc_id.split("</DOCNO>")
                doc_id = only_doc_id[0].strip()

                doc_text = doc_text.replace("Language: <F P=105>", "")
                doc_text = doc_text.replace("English </F>", "")
                doc_text = doc_text.replace("</F>", "")
                doc_text = doc_text.replace("<F>", "")
                doc_text = doc_text.replace("</P>", "")
                doc_text = doc_text.replace("<P>", "")
                doc_text = doc_text.replace("<F P=106>", "")

                if my_doc == doc_id:
                    single_document = [file_id, doc_id, doc_text, doc_city]
                    return single_document

                i = i + 1



def reset():
    print("reset - readfaile")
    #array_language.clear()

