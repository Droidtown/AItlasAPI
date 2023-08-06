import os
import jsonlines
import re
import nltk
from nltk.stem import WordNetLemmatizer

#lemmatize verbs to ignore tenses
def lemmatize_verb(verb):
    lemmatizer = WordNetLemmatizer()
    return lemmatizer.lemmatize(verb, pos='v')

def process_json_files(directory, target_verbs):
    verb_sentences = {verb: [] for verb in target_verbs}
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".json"):
                filepath = os.path.join(root, filename)
                with jsonlines.open(filepath) as reader:
                    for obj in reader:
                        if "text" in obj and isinstance(obj["text"], str):
                            sentences = re.split(r"[.!?]", obj["text"])
                            for sentence in sentences:
                                words = sentence.strip().split()
                                if words and len(words) > 1:
                                    # Use nltk to get POS tags
                                    pos_tags = nltk.pos_tag(words)
                                    for word, pos in pos_tags:
                                        if pos.startswith('VB'):  # Identify verbs (VB, VBD, VBG, VBN, VBP, VBZ)
                                            verb = lemmatize_verb(word.lower())
                                            if verb in target_verbs:
                                                verb_sentences[verb].append(sentence.strip())
                                            break  # Only consider the first verb in the sentence
                                        elif re.match(r"[.!?]", word):  # Skip if the word is a punctuation mark at the beginning
                                            continue
    return verb_sentences

def write_output(verb_sentences):
    for verb, sentences in verb_sentences.items():
        output_file = f"{verb}_output.txt"
        with open(output_file, "w") as writer:
            for sentence in sentences:
                writer.write(sentence + "\n")

if __name__ == "__main__":
    #download additional nltk resources
    nltk.download('wordnet')

    #project directory
    json_en_directory = "./json_en"
    #list of target verbs to parse
    target_verbs = ["be", "become", "create", "develop", "direct", "establish", "lead", "make", "order", "produce", "publish", "receive", "reform", "secure", "set", "write"]  # Replace with your array of verbs

    verb_sentences = process_json_files(json_en_directory, target_verbs)
    write_output(verb_sentences)
