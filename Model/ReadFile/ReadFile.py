import glob


class ReadFile:
    """
    A department whose job is to read the documents
    """
    def __init__(self, folder_path):
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
        self.the_all_doc_in_all_folders = [] #adadad
        for folder in glob.glob(folder_path):
            folder = folder+"/*"
            for document in glob.glob(folder):
                print(document)
                docs_in_file = self.read_doc(document)
                print(docs_in_file)
                self.the_all_doc_in_all_folders.append(docs_in_file)

        #check: can't write all
        '''
        try:
            outputFile = open("outputFile.txt", "a+")
        except IOError:
            return "fail"

        with outputFile:
            for file in the_all_doc_in_all_folders:
                for doc in file:
                    outputFile.write(str(doc))
            outputFile.close()
        '''




    def read_doc(self, doc_path):
        try:
            doc_file = open(doc_path, "r")

        except IOError:
            return "fail"

        with doc_file:
            arr_all_docs_in_file = []
            doc_id = ""
            doc_date = ""
            doc_title = ""
            doc_text = ""
            doc_title_ft = ""
            doc_title_la = ""
            index_date_start = False
            index_date_end = False
            index_head_line_start = False
            index_head_line_end = False
            index_title_start = False
            index_title_end = False
            index_text_start = False
            index_text_end = False
            all_doc = doc_file.read()
            all_doc_split = all_doc.split()
            for index, value in enumerate(all_doc_split):

                if "<DOCNO>" in value:
                    if "</DOCNO>" in value:
                        new_split1 = all_doc_split[index].split("<DOCNO>")
                        new_split2 = new_split1[1].split("</DOCNO>")
                        doc_id = new_split2[0]
                    else:
                        doc_id = all_doc_split[index+1]

                if "</HEADLINE>" in value and doc_id.startswith("FT"):
                    index_head_line_end = True
                    index_head_line_start = False
                    head_line_split = doc_title_ft.split("/")
                    doc_title = head_line_split[1]
                    head_line_split2 = head_line_split[0].split("FT ")
                    doc_date = doc_date + head_line_split2[1]
                if index_head_line_start == True and index_head_line_end == False and doc_id.startswith("FT"):
                    doc_title_ft = doc_title_ft + value + " "
                if "<HEADLINE>" in value and doc_id.startswith("FT"):
                    index_head_line_start = True

                if "</HEADLINE>" in value and doc_id.startswith("LA"):
                    index_head_line_end = True
                    index_head_line_start = False
                    head_line_split = doc_title_la.split("<P>")
                    head_line_split2 = head_line_split[1].split("</P>")
                    doc_title = head_line_split2[0]
                if index_head_line_start == True and index_head_line_end == False and doc_id.startswith("LA"):
                    doc_title_la = doc_title_la + value + " "
                if "<HEADLINE>" in value and doc_id.startswith("LA"):
                    index_head_line_start = True

                if ("<DATE1>" in value or "<DATE>" in value) and doc_id.startswith("LA"):
                    doc_date = all_doc_split[index+3].rstrip(",")+" "+ all_doc_split[index+2]+" "+ all_doc_split[index+4].rstrip(",")

                if ("</DATE1>" in value or "</DATE>" in value) and not doc_id.startswith("LA"):
                    index_date_end = True
                    index_date_start = False
                if index_date_start == True and index_date_end == False and not doc_id.startswith("LA"):
                    doc_date = doc_date + value + " "
                if ("<DATE1>" in value or "<DATE>" in value) and not doc_id.startswith("LA"):
                    index_date_start = True
                if "</TI>" in value:
                    index_title_end = True
                    index_title_start = False
                if index_title_start == True and index_title_end == False:
                    doc_title = doc_title + value + " "
                if "<TI>" in value:
                    index_title_start = True

                if "</TEXT>" in value:
                    index_text_end = True
                    index_text_start = False
                if index_text_start == True and index_text_end == False:
                    doc_text = doc_text + value + " "
                if "<TEXT>" in value:
                    index_text_start = True

                if "</DOC>" in value:
                    single_document = [doc_id,doc_date,doc_title,doc_text]
                    arr_all_docs_in_file.append(single_document)
                if "<DOC>" in value:
                    doc_id = ""
                    doc_date = ""
                    doc_title = ""
                    doc_text = ""
                    doc_title_ft = ""
                    doc_title_la = ""
                    index_date_start = False
                    index_date_end = False
                    index_head_line_start = False
                    index_head_line_end = False
                    index_title_start = False
                    index_title_end = False
                    index_text_start = False
                    index_text_end = False

            doc_file.close()

            return arr_all_docs_in_file
