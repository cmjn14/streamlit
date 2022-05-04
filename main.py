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

import requests as requests

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


def request_concepts(searchedterm):
    if len(searchedterm) != 0:
        searchresults = requests.get('https://api.openalex.org/autocomplete/concepts?q=' + searchedterm).json()['results']
        for result in searchresults:
            st.write(result['display_name'])
            st.caption(result['hint'])
    return True

def request_works(concept_name):
    if len(concept_name) != 0:
        search_works = requests.get('https://api.openalex.org/works?search=' + concept_name.replace(" ","%20") + '&filter=is_paratext:false').json()['results']
        for work in search_works:
            st.markdown("---")
            st.markdown(f"##### {work['display_name']}")
            st.caption("**" + (work['publication_date'] or work['publication_year'] or "** **") + "** _in_ **" + (work['host_venue']['display_name'] or "") + "** (" + str(work['host_venue']['publisher'] or "") + ")")
            st.caption(f"**{work['publication_date']}** in ***{work['host_venue']['display_name']}*** ({work['host_venue']['publisher']})".replace("***None***",""))
            if work['open_access']['is_oa']:
                oa_info = "**Open access**"
                if len(work['host_venue']['license'] or "") != 0:
                    oa_info += " (" + work['host_venue']['license'].upper() +")"
                st.markdown(oa_info)
            authors_list = []
            for authorship in work['authorships']:
                author = authorship['author']
                author_display_name = author['display_name']
                author_orcid = author['orcid'] or ""
                if len(author_orcid) > 0:
                    authors_list.append("[" + author_display_name + "](" + author_orcid +")")
                else:
                    authors_list.append(author_display_name)
            st.markdown(", ".join(authors_list))
            st.caption(urllib.parse.quote(work['doi'], safe=':/'))
            st.caption(f"{work['cited_by_count']} citations")
            for work_concept in work['concepts']:
                st.caption(work_concept['display_name'])
                st.progress(float(work_concept['score']))      
    return True

searched_concept = st.text_input("Search concepts:", value="")
if len(searched_concept) != 0:
    request_concepts(searched_concept)
    request_works(searched_concept)