#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import requests
import re
import json

from pprint import pprint

alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|Mt)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
digits = "([0-9])"
multiple_dots = r'\.{2,}'

G_basePath = os.path.dirname(os.path.abspath(__file__))

G_url = "http://127.0.0.1:30100"

def runArticutEN(inputSTR, level="lv1", userDefinedDICT={}):
    payload = {"input_str": inputSTR,
               "level": level,
               "user_defined_dict_file": userDefinedDICT}
    respond = requests.post("{}/ArticutEN/API/".format(G_url), json=payload)
    resultDICT = respond.json()
    print(respond)
    #pprint(resultDICT)
    return resultDICT

def runArticutENBulk(inputLIST, level="lv1", userDefinedDICT={}):
    payload = {"input_list": inputLIST,
               "level": level,
               "user_defined_dict_file": userDefinedDICT}
    respond = requests.post("{}/ArticutEN/BulkAPI/".format(G_url), json=payload)
    resultDICT = respond.json()
    print(respond)
    #pprint(resultDICT)
    return resultDICT

#split sentences given wikipedia json entry summary, which is one line of huge text
def splitSentences(text: str) -ʡ list[str]:
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1ʢprdʡ",text)
    text = re.sub(digits + "[.]" + digits,"\\1ʢprdʡ\\2",text)
    text = re.sub(multiple_dots, lambda match: "ʢprdʡ" * len(match.group(0)) + "ʢstopʡ", text)
    if "Ph.D" in text: text = text.replace("Ph.D.","PhʢprdʡDʢprdʡ")
    text = re.sub("\s" + alphabets + "[.] "," \\1ʢprdʡ ",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1ʢprdʡ\\2ʢprdʡ\\3ʢprdʡ",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1ʢprdʡ\\2ʢprdʡ",text)
    text = re.sub(" "+suffixes+"[.]"," \\1ʢprdʡ",text)
    text = re.sub(" " + alphabets + "[.]"," \\1ʢprdʡ",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    if "..." in text: text = text.replace("...","ʢprdʡʢprdʡʢprdʡ")
    if "e.g." in text: text = text.replace("e.g.","eʢprdʡgʢprdʡ")
    if "i.e." in text: text = text.replace("i.e.","iʢprdʡeʢprdʡ")
    text = text.replace(".",".ʢstopʡ")
    text = text.replace("?","?ʢstopʡ")
    text = text.replace("!","!ʢstopʡ")
    text = text.replace("ʢprdʡ",".")
    sentences = text.split("ʢstopʡ")
    sentences = [s.strip() for s in sentences]
    if sentences and not sentences[-1]: sentences = sentences[:-1]
    return sentences

#run splitSentences for specified directory and generate txt files in new data directory for review
def splitBulkSentences(directory_path: str):
    
    #check if data directory exists to store results of splitSentences
    data_directory = os.path.join(directory_path, 'data')
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    
    #iterate through each file in the given directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                
                #from json file extract contents of summary (key is 'text')
                summary = data.get('text', '')
                sentences = splitSentences(summary)
                
                # Create a new txt file to store results of sentence split
                output_filename = os.path.splitext(filename)[0] + '.txt'
                output_path = os.path.join(data_directory, output_filename)
                with open(output_path, 'w') as txt_file:
                    for sentence in sentences:
                        txt_file.write(sentence + '\n')


if __name__ == "__main__":
    inputLIST = ["A farmer in Australia has just entered the record books for growing the world's biggest ever blueberry.",
                 "The giant berry weighed in at a mammoth 20.4 grams."]
    print("runArticutEN()")
    pprint(runArticutEN(inputLIST[0]))

    print("runArticutENBulk()")
    pprint(runArticutENBulk(inputLIST))

    #testing split sentences
    '''input = "Augusta Ada King, Countess of Lovelace (n\u00e9e Byron; 10 December 1815 \u2013 27 November 1852) was an English mathematician and writer, chiefly known for her work on Charles Babbage's proposed mechanical general-purpose computer, the Analytical Engine. She was the first to recognise that the machine had applications beyond pure calculation, and to have published the first algorithm intended to be carried out by such a machine. As a result, she is often regarded as the first computer programmer.Ada Byron was the only legitimate child of poet Lord Byron and Lady Byron. All of Byron's other children were born out of wedlock to other women. Byron separated from his wife a month after Ada was born and left England forever. Four months later, he commemorated the parting in a poem that begins, \"Is thy face like thy mother's my fair child! ADA! sole daughter of my house and heart?\" He died in Greece when Ada was eight. Her mother remained bitter and promoted Ada's interest in mathematics and logic in an effort to prevent her from developing her father's perceived insanity. Despite this, Ada remained interested in him, naming her two sons Byron and Gordon. Upon her death, she was buried next to him at her request. Although often ill in her childhood, Ada pursued her studies assiduously. She married William King in 1835. King was made Earl of Lovelace in 1838, Ada thereby becoming Countess of Lovelace.\nHer educational and social exploits brought her into contact with scientists such as Andrew Crosse, Charles Babbage, Sir David Brewster, Charles Wheatstone, Michael Faraday, and the author Charles Dickens, contacts which she used to further her education. Ada described her approach as \"poetical science\" and herself as an \"Analyst (& Metaphysician)\".When she was eighteen, her mathematical talents led her to a long working relationship and friendship with fellow British mathematician Charles Babbage, who is known as \"the father of computers\". She was in particular interested in Babbage's work on the Analytical Engine. Lovelace first met him in June 1833, through their mutual friend, and her private tutor, Mary Somerville.\nBetween 1842 and 1843, Ada translated an article by Italian military engineer Luigi Menabrea about the Analytical Engine, supplementing it with an elaborate set of notes, simply called \"Notes\". Lovelace's notes are important in the early history of computers, containing what many consider to be the first computer program\u2014that is, an algorithm designed to be carried out by a machine. Other historians reject this perspective and point out that Babbage's personal notes from the years 1836/1837 contain the first programs for the engine. She also developed a vision of the capability of computers to go beyond mere calculating or number-crunching, while many others, including Babbage himself, focused only on those capabilities. Her mindset of \"poetical science\" led her to ask questions about the Analytical Engine (as shown in her notes) examining how individuals and society relate to technology as a collaborative tool."
    print("split_sentences")
    print(splitSentences(input))'''

    #the plan:
    #go through each json file in people directory
    #for each file, take the contents after "summary", run it through split_sentences, returning list of str
    #run list of str through ArticutENBulk

    #test splitBulkSentences functionality
    '''test_folder = os.path.dirname(os.path.abspath(__file__))
    test_path = os.path.join(test_folder, 'test')
    splitBulkSentences(test_path) '''

    #generation of txt files with each sentence on its own line
    '''people_folder = os.path.dirname(os.path.abspath(__file__))
    people_path = os.path.join(people_folder, 'people') 
    splitBulkSentences(people_path)'''