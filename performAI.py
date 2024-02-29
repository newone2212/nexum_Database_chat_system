import pandas as pd
from pandasai import SmartDataframe
from pandasai import SmartDatalake
from pandasai.llm.openai import OpenAI
# from pandasai import PandasAII
import pyodbc
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from waitress import serve
import argparse
from langchain.llms import GPT4All, LlamaCpp
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
import json
from tabulate import tabulate

cnxn_str = ("Driver={SQL Server Native Client 11.0};"
            "Server=dbserver;"
            "Database=Timeverse;"
            "UID=amit;"
            "PWD=dcs@PL4278;")
cnxn = pyodbc.connect(cnxn_str)
cursor = cnxn.cursor()
#cursor.execute()
frames = []

def detDatainJSon(tablename):
    cursor.execute(r"select top 30 * from v_PowerBI order by TaskStartedAt desc")
    rows = [x for x in cursor]
    cols = [x[0] for x in cursor.description]
    print(cols)
    songs = []
    for row in rows:
        song = {}
        for prop, val in zip(cols, row):
            song[prop] = val
        songs.append(song)

    keys_to_extract = cols
    employees_data = {key: [] for key in keys_to_extract}

    for entry in songs:
        for key in keys_to_extract:
            employees_data[key].append(entry.get(key, None))
    print(employees_data)
    return employees_data


def performAI(question):
    orgFrame = pd.DataFrame(detDatainJSon("v_PowerBI"))
   
    llm = OpenAI(api_token="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")    
    print("Passing to Data Lake")
    dl = SmartDatalake([orgFrame], config={"llm": llm})

    # print("data frame = " +dl)
    answer =dl.chat(question)
    # print(answer)
    
    df = pd.DataFrame(answer)
    # print(df)
    json_data = df.to_json(orient="records", indent=2)
    print(json_data)
    # table_data = [[v] for d in json_data for v in d.values()]
    # table_md = tabulate(table_data, tablefmt="pipe")
    header = "| " + " | ".join(json_data[0].keys()) + " |"
    separator = "| " + " | ".join(["---"] * len(json_data[0])) + " |"

    # Create the rows
    rows = ""
    for item in json_data:
        row = "| " + " | ".join(map(str, item.values())) + " |"
        rows += row + "\n"

# Combine all parts to form the table
    markdown_table = f"{header}\n{separator}\n{rows}"

    print("tabular data = "+markdown_table)
    # print(df)
    
    # print("#################################################################")
    # print(answer)
    return markdown_table


import openai
openai.api_key = "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"
def formatting(json_data):
    json_string = "\n".join([f"- **{key}:** {value}" for key, value in json_data.items()])
    print(json_data)
    # Generate response using OpenAI Language Model
    prompt = f"Given the following JSON data:\n\n{json_string}\n\nGenerate a response in Markdown language that summarizes the data if required then in tabular format"
    response = openai.Completion.create(
        engine="text-davinci-003",  # You can choose the appropriate engine
        prompt=prompt,
        max_tokens=300  # Adjust as needed
    )

    # Extract the generated response
    generated_response = response   #.choices[0].text.strip()

    # Print the generated response
    print(generated_response)
    return generated_response


def json_to_markdown(json_data):
    markdown = ""
    
    def process_item(item, level=0):
        nonlocal markdown
        if isinstance(item, dict):
            for key, value in item.items():
                markdown += f"{'#' * (level + 1)} {key}\n"
                process_item(value, level + 1)
        elif isinstance(item, list):
            for value in item:
                process_item(value, level)
        else:
            markdown += f"{'  ' * level}- {item}\n"
    
    process_item(json_data)
    return markdown