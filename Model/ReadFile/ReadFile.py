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

            if "<F P=104>" in head_part:
                part_doc_city = head_part.split("<F P=104>")
                part_doc_city = part_doc_city[1:]
                for city in part_doc_city:
                    city = city.split()
                    city = city[0]
                    position = all_doc.find(city)
                    doc_city.append([city,position])
            single_document = [file_id, doc_id, doc_text, doc_city]
            the_all_doc_in_all_folders[doc_id] = single_document
            i = i + 1

def reset():
    print("reset - readfaile")