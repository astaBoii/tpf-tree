import streamlit as st
import csv
import json
from collections import defaultdict
import os
import subprocess

# Set page configuration
st.set_page_config(
    page_title="Program Flow",
    page_icon="https://www.mphasis.com/content/dam/mphasis-com/common/icons/favicon.ico",
    layout="wide"
)
st.config.set_option("server.maxUploadSize", 2048)
def csv_to_json(csv_file, json_file, max_levels=7):
    data = {}
    data['parent'] = "null"
    data['name'] = "start"
    data['edge_name'] = "null"
    data['children'] = []

    calling_programs = defaultdict(list)

    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            calling_programs[row['Calling Program']].append((row['Calling Method'], row['Called Program']))

    def build_hierarchy(parent, name, edge_name, level, circular_reference=False):
        program_data = {'parent': parent, 'name': name, 'edge_name': edge_name, 'children': [], 'circular_reference': circular_reference}
        if level < max_levels and name in calling_programs:
            for calling_method, called_program in calling_programs[name]:
                if called_program == parent:  # Handle circular reference
                    child = build_hierarchy(name, called_program, calling_method, level + 1, circular_reference=True)
                else:
                    child = build_hierarchy(name, called_program, calling_method, level + 1)
                program_data['children'].append(child)
        return program_data



    for calling_program, value in calling_programs.items():
        program_data = build_hierarchy("start", calling_program, "null", 1)
        data['children'].append(program_data)

    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)


def main():
  uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

  if uploaded_file is not None:
    with open('temp_file.csv', 'wb') as f:
      f.write(uploaded_file.getvalue())
    csv_file = 'temp_file.csv'
    json_file = 'output.json'
    csv_to_json(csv_file, json_file)

    # Only display the HTML page after the conversion is successful
    html_file_path = 'http://localhost:8080/TPFtree.html'
    html_code = f'<iframe src="{html_file_path}" width="8000" height="1700" style="border:none;"></iframe>'
    st.markdown(html_code, unsafe_allow_html=True)

  # Run a simple HTTP server to serve TPFtree.html
  subprocess.Popen(["python", "-m", "http.server", "8080"])

if __name__ == '__main__':
  main()
