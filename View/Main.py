from Controller import Controller


def main():

    path_queries = r"C:\Users\shake\queries.txt"
    stemming = "yes"
    semantic_mode = False
    path_folder = r"C:\Users\shake\corpus"
    path_save_folder = r"C:\Users\shake\index-cor"

    #controller = Controller.init_path(path_folder,path_save_folder,stemming)

    #selected_cities = list({'CHINA', 'TALLINN', 'PARIS', 'RIO', 'MILAN', 'MOSCOW'})
    selected_cities = list({})
    #print(selected_cities)

    #query = "Falkland petroleum exploration"
    #Controller.enter_query_text(query,stemming,path_folder,path_save_folder,selected_cities,semantic_mode)

    #Controller.load_query_file(path_queries,stemming,path_folder,path_save_folder,selected_cities,semantic_mode)

    #Controller.calc_avg_length_docs(stemming, path_save_folder)

    # file = ': FBIS3-10646'
    # all_entity = Controller.entity_search(file,stemming,path_save_folder,path_folder)
    # print(all_entity)

    #Controller.calc_optimal_components(path_queries,stemming,path_folder,path_save_folder,selected_cities,semantic_mode)

main()