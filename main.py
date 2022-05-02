# -*- coding: utf-8 -*-
"""

Note - This can be run from anaconda prompt using -  streamlit run "hello.py"

"""


import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd

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

institution = requests.get(
    'https://api.openalex.org/institutions?filter=display_name.search:university of florida').json()['results'][0]

st.write(institution['display_name'])
st.write(institution['id'])

def update_results()
    if len(searchedterm) != 0:
        searchresults = requests.get('https://api.openalex.org/autocomplete/concepts?q=' + searchedterm).json()['results']
        for result in searchresults:
            st.write(result['display_name'])
            st.caption(result['hint'])
    return true

searchedterm = st.text_input("Search concepts:", value="", on_change=update_results)
# if len(searchedterm) != 0:
#    searchresults = requests.get('https://api.openalex.org/autocomplete/concepts?q=' + searchedterm).json()['results']
#    for result in searchresults:
#        st.write(result['display_name'])
#        st.caption(result['hint'])