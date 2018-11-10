from Model.Indexer import Indexer

temp_terms_dic = {'the': 11, '22.00': 1, '23/01': 1, 'edition': 1, 'of': 5, 'skopje': 1, 'newspaper': 1, 'vecer': 2, 'in': 4, 'macedonian': 2, 'published': 1, 'on': 1, 'pages': 1, '6.00': 1, '7.00': 1, 'results': 2, 'an': 2, 'opinion': 1, 'poll': 2, 'conducted': 1, 'by': 2, 'brima': 1, 'agency': 1, '11/1993': 1, 'according': 1, 'to': 1, '1036.00': 1, 'respondents': 1, 'were': 2, 'classified': 1, 'age': 1, 'and': 1, 'residence': 1, 'but': 1, 'paper': 2, 'did': 1, 'not': 1, 'explain': 1, 'methodology': 1, 'or': 1, 'give': 1, 'margin': 1, 'error': 1, 'for': 2, 'purpose': 1, 'comparison': 1, 'cited': 1, 'unidentified': 1, 'made': 1, '05/1993': 1, 'percent': 1, 'ten': 1, 'the macedonian': 1, 'politicians': 1, 'approval': 2, 'disapproval': 2}
temp_terms_dic2 = {'vecer': 1, 'noted': 1, 'that': 1, 'president': 1, 'gligorov': 2, 'president gligorov': 1, 'very': 1, 'high': 2, 'approval': 1, 'rating': 1, 'of': 2, '90.00 percent': 1, 'among': 2, 'those': 1, 'over': 1, 'age': 1, '65.00': 1, 'fell': 1, 'off': 1, 'to': 1, 'a': 2, 'still': 1, '70.00 percent': 1, 'respondents': 1, 'between': 1, '18.00': 1, 'and': 2, '24.00': 1, 'residents': 1, 'skopje': 1, 'ranked': 1, 'the': 3, 'politicians': 1, 'in': 1, 'slightly': 1, 'different': 1, 'order': 1, 'from': 1, 'ranking': 1, 'given': 1, 'by': 1, 'whole': 1, 'sample': 1, 'tupurkovski': 1, 'frckovski': 1, 'andov': 1, 'gosev': 1, 'branko': 1, 'crvenkovski': 2, 'branko crvenkovski': 1, 'vlado': 1, 'popovski': 2, 'vlado popovski': 1, 'petrov': 1, 'nikola': 1, 'nikola popovski': 1, 'stevo': 1, 'stevo crvenkovski': 1}

print(temp_terms_dic)

index = Indexer.Indexer()
index.create_temp_posting(temp_terms_dic)
index.create_temp_posting(temp_terms_dic2)

index.merge_all_posting()