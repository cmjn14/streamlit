# -*- coding: utf-8 -*-
"""

Note - This can be run from anaconda prompt using -  streamlit run "hello.py"

"""


import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import urllib as urllib
import traceback
import logging
import os
import json

import requests as requests

from zipfile import ZipFile

st.title('My first app')

st.write("Here's our first attempt at using data to create a table:")

df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

df

if st.checkbox('Show dataframe'):
    chart_data = pd.DataFrame(
       np.random.randn(20, 3),
       columns=['a', 'b', 'c'])

    st.line_chart(chart_data)

map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)

st.write("Modified in github.dev frame within Obsidian.")
st.write("Test with openalex API")


polite = "&mailto=cedric.lopez@free.fr"


def request_concepts(searchedterm):
    if len(searchedterm) != 0:
        searchresults = requests.get('https://api.openalex.org/autocomplete/concepts?q=' + searchedterm + polite).json()['results']
        for result in searchresults:
            st.markdown(f"**{result['display_name']}**<br/><small>{result['hint']}</small>", unsafe_allow_html=True)
    return True

def request_works(concept_name):
    if len(concept_name) != 0:
        search_works = requests.get('https://api.openalex.org/works?search=' + concept_name.replace(" ","%20") + '&filter=is_paratext:false' + polite).json()['results']
        for work in search_works:
            st.markdown("---")
            st.markdown(f"##### {work['display_name']}")

            authors_list = []
            for authorship in work['authorships']:
                author = authorship['author']
                author_display_name = author['display_name'] if author['orcid'] == None else (f"[{author['display_name']}]({author['orcid']})")
                authors_list.append(author_display_name)
            st.markdown(", ".join(authors_list))

            st.caption(f"Published on **{work['publication_date']}** in ***{work['host_venue']['display_name']}*** ({work['host_venue']['publisher']})".replace("in ***None***",""))

            oa_info = "🟩 **Open access**" if work['open_access']['is_oa'] == True else ""
            oa_info += " (" + work['host_venue']['license'].upper() +")" if (len(work['host_venue']['license'] or "") != 0) else ""
            st.markdown(oa_info)

            st.caption(urllib.parse.quote(work['doi'], safe=':/'))

            st.caption(f"{work['cited_by_count']} citations")

            with st.expander("Other sources"):
                for source in work["alternate_host_venues"]:
                    st.caption(f"- [{source['display_name']}]({source['url']})")

            with st.expander("Related concepts"):
                for work_concept in work['concepts']:
                    st.caption(work_concept['display_name']) 
                    st.progress(float(work_concept['score']))     
    return True


# def retrieve_concepts_as_csv(max_level=0):
#     file_list = []
#     up_list = []
#     request_url = urllib.parse.quote(f"https://api.openalex.org/concepts?filter=level:<{str(max_level + 1)}&sort=level,ancestors.id&per_page=200{polite}", safe=':/')
#     request_url
#     searchconcepts = requests.get(request_url).json()['results']
#     for concept in searchconcepts:
#         ancestors_list = []
#         for ancestor in concept['ancestors']:
#             file_list.append(concept['display_name'])
#             up_list.append(ancestor['display_name'])
#     data = {'file': file_list, 'up': up_list}
#     df = pd.DataFrame(data, columns= ['file', 'up'])
#     st.dataframe(df)
#     csv_file = df.to_csv().encode('utf-8')
#     st.download_button(
#         label="Download data as CSV",
#         data=csv_file,
#         file_name='concepts.csv',
#         mime='text/csv',
#     )

def make_zip(zip_name, files_list):
    st.write("Creating " + zip_name + " with " + str(len(files_list)) + " files ...")
    try:
        with ZipFile(zip_name, 'w') as zip_file:
            for f in files_list:
                f_name = os.path.basename(f.name)
                try:
                    zip_file.write(f_name)
                    if os.path.exists(f_name):
                        os.remove(f_name)
                except Exception as e1:
                    st.caption(f"Could not add {f_name} to zip.")         ### Should retry, probably due to timing
                    logging.error(traceback.format_exc())                    
        return zip_file
    except Exception as e:
        st.error("Could not create zip file.")
        logging.error(traceback.format_exc())
        return False

def make_md_file(md_name,md_content):
    try:
        with open(md_name, 'w') as md_file:
            md_file.write(md_content)
        return md_file
    except Exception as e:
        st.error(f"Could not create file {md_name}")
        logging.error(traceback.format_exc())
        return False

def get_kids(ancestor_id, cursor="*",kids_list=[]):
    if cursor == None:  
        st.write("done")                                # means last cursor was reached
        return kids_list
    else:
        kids_url = urllib.parse.quote(f"https://api.openalex.org/concepts?filter=ancestors.id:{ancestor_id}&per_page=200&cursor={cursor}{polite}", safe=':/')
        kids_json = requests.get(kids_url).json()
        next_cursor = kids_json['meta']['next_cursor'] 
        st.write(kids_json['meta']['count'])
        st.write(f'cursor: {next_cursor}')
        if 'results' in kids_json:
            for result in kids_json['results']:
                kids_list.append(result['id'])
            st.write(len(kids_list))
            get_kids(ancestor_id, next_cursor, kids_list)
        else:
            st.write("done, nothing more")
            return kids_list


#test get_kids()
st.write(f'result: {get_kids("C39432304")}')
st.stop()

def retrieve_concepts(max_level=0, current_page=1):
    files_list = []
    errors_list = []
    request_url = urllib.parse.quote(f"https://api.openalex.org/concepts?filter=level:<{str(max_level + 1)}&sort=level,ancestors.id&page={str(current_page)}&per_page=200{polite}", safe=':/')
    request_url
    response_json = requests.get(request_url).json()
    if not 'results' in response_json:  #happens if request exceeds last page of results (max 10,000 results from openalex api)
        return files_list

    searchconcepts = response_json['results']

    st.write(f"{response_json['meta']['count']} results found.")
    st.write(f"current page: {response_json['meta']['page']}")

    for concept in searchconcepts:
        ancestors_list = []
        for ancestor in concept['ancestors']:
            if ancestor['level'] == concept['level'] - 1:       # do not link directly to ancestors that are higher in hierarchy, for clarity of the graph view
                ancestors_list.append(f"[[{ancestor['display_name'].replace('/','-')}]]")
        parents_str = "parent:: " + ", ".join(ancestors_list) if len(ancestors_list) > 0 else  ""
        file_lines = ["---", "tags:", f"- level/{concept['level']}","---","",f"# {concept['display_name']}","",parents_str,"","#### Description",f"{concept['description']}"]
        file_name = concept['display_name'].replace('/','-') + ".md"
        file_content = "\r\n".join(file_lines)

        md_file = make_md_file(file_name,file_content)
        if md_file == False:
            errors_list.append(file_name)
        else:
            files_list.append(md_file)
    
    if len(errors_list) > 0 :
        st.error(f"The following files could not be created: {', '.join(errors_list)}")
    
    nb_files_created = len(files_list)
    st.write(f"{nb_files_created} files created.")
    return files_list

#retrieve_concepts(1)

def make_concepts_zip(max_level=0):
    current_page = 0
    files_full_list = []
    nb_new_files = -1
    counter = 0
    while nb_new_files != 0:
        counter +=1
        if counter > 200:    #security
            break;
        
        current_page +=1
        new_files_list = retrieve_concepts(max_level, current_page)
        nb_new_files = len(new_files_list)

        if nb_new_files > 0:
            files_full_list = files_full_list + new_files_list
            st.write(str(len(files_full_list)) + " files collected.")

    st.write("All files collected.")

    zip_file = make_zip('concepts.zip', files_full_list)
    if zip_file == False:
        st.error("The zip file could not be created.")
        return False
    else:
        st.success("Zip file created.")
        with open("concepts.zip", "rb") as final_zip:
            st.download_button(
                label="Download zipped files",
                data=final_zip,
                file_name='concepts.zip',
                mime='application/zip',
            )

if st.button('Get concepts'):
    make_concepts_zip(2)


st.stop()

searched_concept = st.text_input("Search concepts:", value="")

if len(searched_concept) != 0:
    request_concepts(searched_concept)
    request_works(searched_concept)