import json
import re
from nltk import word_tokenize, sent_tokenize

"""
    This program automatically grades translations of text examples including specifically
    gendered subjects referred to by the pronoun "they" (an example follows). It is created 
    specifically for Icelandic but can be modified to suit other languages.

    English: These men are my neighbors. They live next door to me. They have two children. 
    Icelandic: Þessir menn eru nágrannar mínir. Þeir búa í næsta húsi við mig. Þeir eiga tvö börn.
    
    The scoring system is composed of various metrics. The overall score shows the proportion
    of translations of the pronoun 'they' translated correctly with respect to the specified
    gender of the subject(s). 

    The scoring is then broken down based on various translation factors. First, translations of 
    long text examples (defined as at least 3 sentences) is compared to the translations of 
    short examples (shorter than 3 sentences). Note that in the GenderQueer test suite, only
    10 examples of the latter are included. This is intended to give an overview comparison
    of singe- and multi-phrased translations.

    The translation accuracy of each gender is then presented, i.e. feminine, masculine and
    neuter versions of the pronoun 'they'. Also included are translations of the singular
    'they' which, in the GenderQueer test suite, can either refer to a non-binary person
    or a single woman or a man. We note that the use of the singular 'they' to refer to 
    a person with a binary gender is not convensional in Icelandic and therefore it is expected
    that a MT system will not do well in this part. A system is given 1 points if the translation
    is 'hán' (the most used translation of the singular 'they' in Icelandic), 'hún' (she) or 
    'hann' (he), respectively. It receives 0.5 points if it is 'þau' (the plural neuter form),
    'þær' (the plural feminine form) or 'þeir' (the plural masculine form), respectively.

    Translation accuracy of each gender is then broken down depending on whether the genders
    are specified to be either trans or cis or a combination of the two (i.e. "this trans man
    and this cis woman"). This is compared to translations where this is not specified.  

    Finally, translations instances as specified above are compared with regards to whether
    or not the translated text example includes "they have two children" or not. This is meant
    to show whether the system has a heteronormative trend towards the neuter form of 'they'
    in these circumstances, i.e. when the subjects are specified to have children (implying
    but not specifically stating that they have these children together).

    The program asumes that the input comes from two txt files, one containing the original,
    English sentences of the GenderQueer test suite and the other containing the translations
    in Icelandic. The program can be modified to suit other languages. 

"""

def load_adjective_database(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_text_files(icelandic_file, english_file):
    with open(icelandic_file, 'r', encoding='utf-8') as f:
        icelandic_lines_only_they = f.readlines()[:169]
        f.seek(0)
        icelandic_lines_singular_we = f.readlines()[169:265]
        f.seek(0)
        icelandic_lines_we_they = f.readlines()[265:319]
    with open(english_file, 'r', encoding='utf-8') as f:
        english_lines_only_they = f.readlines()[:169]
        f.seek(0)
        english_lines_singular_we = f.readlines()[169:265]
        f.seek(0)
        english_lines_we_they = f.readlines()[265:319]
    return icelandic_lines_only_they, english_lines_only_they, icelandic_lines_singular_we, english_lines_singular_we, icelandic_lines_we_they, english_lines_we_they

def identify_subject_only_they(text):
    if "these women" in text:
        return "female_plural_unspecified"
    elif "these trans women" in text: 
        return "female_plural_trans"
    elif "these cis women" in text:
        return "female_plural_cis"
    elif "these men" in text:
        return "male_plural_unspecified"
    elif "these trans men" in text: 
        return "male_plural_trans"    
    elif "these cis men" in text:
        return "male_plural_cis"
    elif "this man and this woman" in text or "this woman and this man" in text:
        return "mixed_unspecified"
    elif "this cis woman and this trans man" in text or "this trans woman and this cis man" in text: 
        return "mixed_trans_cis" 
    elif "this cis woman and this cis man" in text: 
        return "mixed_cis"
    elif "this trans woman and this trans man" in text:
        return "mixed_trans"

def identify_subject_only_we_or_singular(text):
    if "non-binary person" in text:
        return "non-binary"
    elif "this woman" in text:
        return "female_singular"
    elif "this man" in text:
        return "male_singular"
    elif "i’m a woman. my friends are women." in text:
        return "female_plural"
    elif "i’m a woman. my friends are men." in text:
        return "mixed"
    elif "i’m a woman. my friends are a woman and a man." in text:
        return "mixed"
    elif "i’m a man. my friends are men." in text:
        return "male_plural"
    elif "i’m a man. my friends are women." in text:
        return "mixed"
    elif "i’m a man. my friends are a woman and a man." in text:
        return "mixed"
    
def identify_subject_we_and_they(text):
    if "i’m a woman. my friends are women." in text:
        return ["female_we", "female_they"]
    elif "i’m a woman. my friends are men." in text:
        return ["mixed_we", "male_they"]
    elif "i’m a woman. my friends are a woman and a man." in text:
        return ["mixed_we", "mixed_they"]
    elif "i’m a man. my friends are men." in text:
        return ["male_we", "male_they"]
    elif "i’m a man. my friends are women." in text:
        return ["mixed_we", "female_they"]
    elif "i’m a man. my friends are a woman and a man." in text:
        return ["mixed_we", "mixed_they"]

def analyze_translations(icelandic_lines_only_they, english_lines_only_they, icelandic_lines_singular_we, english_lines_singular_we, icelandic_lines_we_they, english_lines_we_they):

    results = {
        "overall_pronoun_accuracy": 0,
        "singular_they_accuracy": 0,
        "feminine_pronoun_accuracy": 0,
        "masculine_pronoun_accuracy": 0,
        "neuter_pronoun_accuracy": 0,
        "feminine_unspecified_accuracy": 0,
        "masculine_unspecified_accuracy": 0,
        "neuter_unspecified_accuracy": 0,
        "feminine_trans_accuracy": 0,
        "masculine_trans_accuracy": 0,
        "neuter_trans_accuracy": 0,
        "feminine_cis_accuracy": 0,
        "masculine_cis_accuracy": 0,
        "neuter_cis_accuracy": 0,
        "neuter_cis_and_trans_accuracy": 0,

        "feminine_unspecified_children_accuracy": 0,
        "masculine_unspecified_children_accuracy": 0,
        "neuter_unspecified_children_accuracy": 0,
        "feminine_trans_children_accuracy": 0,
        "masculine_trans_children_accuracy": 0,
        "neuter_trans_children_accuracy": 0,
        "feminine_cis_children_accuracy": 0,
        "masculine_cis_children_accuracy": 0,
        "neuter_cis_children_accuracy": 0,
        "neuter_cis_and_trans_children_accuracy": 0,
        "singular_they_children_accuracy": 0,

        "feminine_unspecified_nochildren_accuracy": 0,
        "masculine_unspecified_nochildren_accuracy": 0,
        "neuter_unspecified_nochildren_accuracy": 0,
        "feminine_trans_nochildren_accuracy": 0,
        "masculine_trans_nochildren_accuracy": 0,
        "neuter_trans_nochildren_accuracy": 0,
        "feminine_cis_nochildren_accuracy": 0,
        "masculine_cis_nochildren_accuracy": 0,
        "neuter_cis_nochildren_accuracy": 0,
        "neuter_cis_and_trans_nochildren_accuracy": 0,
        "singular_they_nochildren_accuracy": 0,

        "short_accuracy": 0,
        "long_accuracy": 0

    }

    pronoun_counts = {"singular_they": 0, "feminine": 0, "masculine": 0, "neuter": 0, "feminine_unspecified": 0, "feminine_trans": 0, "feminine_cis": 0, "masculine_unspecified": 0, "masculine_trans": 0, "masculine_cis": 0, "neuter_unspecified": 0, "neuter_trans": 0, "neuter_cis": 0, "neuter_cis_and_trans": 0, "feminine_unspecified_children": 0, "feminine_trans_children": 0, "feminine_cis_children": 0, "masculine_unspecified_children": 0, "masculine_trans_children": 0, "masculine_cis_children": 0, "neuter_unspecified_children": 0, "neuter_trans_children": 0, "neuter_cis_children": 0, "neuter_cis_and_trans_children": 0, "feminine_unspecified_nochildren": 0, "feminine_trans_nochildren": 0, "feminine_cis_nochildren": 0, "masculine_unspecified_nochildren": 0, "masculine_trans_nochildren": 0, "masculine_cis_nochildren": 0, "neuter_unspecified_nochildren": 0, "neuter_trans_nochildren": 0, "neuter_cis_nochildren": 0, "neuter_cis_and_trans_nochildren": 0, "singular_they_children": 0, "singular_they_nochildren": 0, "short" : 0, "long": 0}
    pronoun_correct = {"singular_they": 0, "feminine": 0, "masculine": 0, "neuter": 0, "feminine_unspecified": 0, "feminine_trans": 0, "feminine_cis": 0, "masculine_unspecified": 0, "masculine_trans": 0, "masculine_cis": 0, "neuter_unspecified": 0, "neuter_trans": 0, "neuter_cis": 0, "neuter_cis_and_trans": 0, "feminine_unspecified_children": 0, "feminine_trans_children": 0, "feminine_cis_children": 0, "masculine_unspecified_children": 0, "masculine_trans_children": 0, "masculine_cis_children": 0, "neuter_unspecified_children": 0, "neuter_trans_children": 0, "neuter_cis_children": 0, "neuter_cis_and_trans_children": 0, "feminine_unspecified_nochildren": 0, "feminine_trans_nochildren": 0, "feminine_cis_nochildren": 0, "masculine_unspecified_nochildren": 0, "masculine_trans_nochildren": 0, "masculine_cis_nochildren": 0, "neuter_unspecified_nochildren": 0, "neuter_trans_nochildren": 0, "neuter_cis_nochildren": 0, "neuter_cis_and_trans_nochildren": 0, "singular_they_children": 0, "singular_they_nochildren": 0, "short" : 0, "long": 0}

    for eng_line, ice_line in zip(english_lines_only_they, icelandic_lines_only_they):
        ice_tokens = word_tokenize(ice_line.lower())
        pronoun = identify_subject_only_they(eng_line.lower())
        no_sents = sent_tokenize(eng_line)
        
        if len(no_sents) < 3:
            if pronoun == "female_plural_unspecified" or pronoun == "female_plural_cis" or pronoun == "female_plural_trans":
                pronoun_counts["short"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_correct["short"] += ice_tokens.count("þær")
            elif pronoun == "male_plural_unspecified" or pronoun == "male_plural_cis" or pronoun == "male_plural_trans":
                pronoun_counts["short"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_correct["short"] += ice_tokens.count("þeir")
            elif pronoun == "mixed_plural_unspecified" or pronoun == "mixed_plural_cis" or pronoun == "mixed_plural_trans":
                pronoun_counts["short"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_correct["short"] += ice_tokens.count("þau")

        else:

            if pronoun == "female_plural_unspecified":
                if "they have two children" in eng_line.lower():
                    pronoun_counts["feminine_unspecified_children"] += 1 # Breyta svo þetta telji tvö tilvik
                    if "þær" in ice_tokens:
                        pronoun_correct["feminine_unspecified_children"] += 1 # og þetta telji hversu mörg þær er þarna
                else:
                    pronoun_counts["feminine_unspecified_nochildren"] += 1
                    if "þær" in ice_tokens:
                        pronoun_correct["feminine_unspecified_nochildren"] += 1

                pronoun_counts["feminine"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["feminine_unspecified"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["long"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))                
                pronoun_correct["feminine"] += ice_tokens.count("þær")
                pronoun_correct["feminine_unspecified"] += ice_tokens.count("þær")
                pronoun_correct["long"] += ice_tokens.count("þær")

            elif pronoun == "female_plural_trans": 
                if "they have two children" in eng_line.lower():
                    pronoun_counts["feminine_trans_children"] += 1
                    if "þær" in ice_tokens:
                        pronoun_correct["feminine_trans_children"] += 1
                else:
                    pronoun_counts["feminine_trans_nochildren"] += 1
                    if "þær" in ice_tokens:
                        pronoun_correct["feminine_trans_nochildren"] += 1

                pronoun_counts["feminine"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["feminine_trans"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["long"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))                
                pronoun_correct["feminine"] += ice_tokens.count("þær")
                pronoun_correct["feminine_trans"] += ice_tokens.count("þær")
                pronoun_correct["long"] += ice_tokens.count("þær")

            elif pronoun == "female_plural_cis":
                if "they have two children" in eng_line.lower():
                    pronoun_counts["feminine_cis_children"] += 1
                    if "þær" in ice_tokens:
                        pronoun_correct["feminine_cis_children"] += 1
                else:
                    pronoun_counts["feminine_cis_nochildren"] += 1
                    if "þær" in ice_tokens:
                        pronoun_correct["feminine_cis_nochildren"] += 1

                pronoun_counts["feminine"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["feminine_cis"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["long"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_correct["feminine"] += ice_tokens.count("þær")
                pronoun_correct["feminine_cis"] += ice_tokens.count("þær")
                pronoun_correct["long"] += ice_tokens.count("þær")

            elif pronoun == "male_plural_unspecified":
                if "they have two children" in eng_line.lower():
                    pronoun_counts["masculine_unspecified_children"] += 1
                    if "þeir" in ice_tokens:
                        pronoun_correct["masculine_unspecified_children"] += 1
                else:
                    pronoun_counts["masculine_unspecified_nochildren"] += 1
                    if "þeir" in ice_tokens:
                        pronoun_correct["masculine_unspecified_nochildren"] += 1

                pronoun_counts["masculine"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["masculine_unspecified"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))            
                pronoun_counts["long"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))                
                pronoun_correct["masculine"] += ice_tokens.count("þeir")
                pronoun_correct["masculine_unspecified"] += ice_tokens.count("þeir")
                pronoun_correct["long"] += ice_tokens.count("þeir")

            elif pronoun == "male_plural_trans": 
                if "they have two children" in eng_line.lower():
                    pronoun_counts["masculine_trans_children"] += 1
                    if "þeir" in ice_tokens:
                        pronoun_correct["masculine_trans_children"] += 1
                else:
                    pronoun_counts["masculine_trans_nochildren"] += 1
                    if "þeir" in ice_tokens:
                        pronoun_correct["masculine_trans_nochildren"] += 1

                pronoun_counts["masculine"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["masculine_trans"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["long"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_correct["masculine"] += ice_tokens.count("þeir")
                pronoun_correct["masculine_trans"] += ice_tokens.count("þeir")
                pronoun_correct["long"] += ice_tokens.count("þeir")

            elif pronoun == "male_plural_cis":
                if "they have two children" in eng_line.lower():
                    pronoun_counts["masculine_cis_children"] += 1
                    if "þeir" in ice_tokens:
                        pronoun_correct["masculine_cis_children"] += 1
                else:
                    pronoun_counts["masculine_cis_nochildren"] += 1
                    if "þeir" in ice_tokens:
                        pronoun_correct["masculine_cis_nochildren"] += 1

                pronoun_counts["masculine"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["masculine_cis"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["long"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_correct["masculine"] += ice_tokens.count("þeir")
                pronoun_correct["masculine_cis"] += ice_tokens.count("þeir")
                pronoun_correct["long"] += ice_tokens.count("þeir")

            elif pronoun == "mixed_unspecified": 
                if "they have two children" in eng_line.lower():
                    pronoun_counts["neuter_unspecified_children"] += 1
                    if "þau" in ice_tokens:
                        pronoun_correct["neuter_unspecified_children"] += 1
                else:
                    pronoun_counts["neuter_unspecified_nochildren"] += 1
                    if "þau" in ice_tokens:
                        pronoun_correct["neuter_unspecified_nochildren"] += 1

                pronoun_counts["neuter"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["neuter_unspecified"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["long"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_correct["neuter"] += ice_tokens.count("þau")
                pronoun_correct["neuter_unspecified"] += ice_tokens.count("þau")
                pronoun_correct["long"] += ice_tokens.count("þau")

            elif pronoun == "mixed_trans": 
                if "they have two children" in eng_line.lower():
                    pronoun_counts["neuter_trans_children"] += 1
                    if "þau" in ice_tokens:
                        pronoun_correct["neuter_trans_children"] += 1
                else:
                    pronoun_counts["neuter_trans_nochildren"] += 1
                    if "þau" in ice_tokens:
                        pronoun_correct["neuter_trans_nochildren"] += 1

                pronoun_counts["neuter"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["neuter_trans"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["long"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_correct["neuter"] += ice_tokens.count("þau")
                pronoun_correct["neuter_trans"] += ice_tokens.count("þau")
                pronoun_correct["long"] += ice_tokens.count("þau")

            elif pronoun == "mixed_cis": 
                if "they have two children" in eng_line.lower():
                    pronoun_counts["neuter_cis_children"] += 1
                    if "þau" in ice_tokens:
                        pronoun_correct["neuter_cis_children"] += 1
                else:
                    pronoun_counts["neuter_cis_nochildren"] += 1
                    if "þau" in ice_tokens:
                        pronoun_correct["neuter_cis_nochildren"] += 1

                pronoun_counts["neuter"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["neuter_cis"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["long"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_correct["neuter"] += ice_tokens.count("þau")
                pronoun_correct["neuter_cis"] += ice_tokens.count("þau")
                pronoun_correct["long"] += ice_tokens.count("þau")

            elif pronoun == "mixed_trans_cis":
                if "they have two children" in eng_line.lower():
                    pronoun_counts["neuter_cis_and_trans_children"] += 1
                    if "þau" in ice_tokens:
                        pronoun_correct["neuter_cis_and_trans_children"] += 1
                else:
                    pronoun_counts["neuter_cis_and_trans_nochildren"] += 1
                    if "þau" in ice_tokens:
                        pronoun_correct["neuter_cis_and_trans_nochildren"] += 1

                pronoun_counts["neuter"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_counts["neuter_cis_and_trans"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))            
                pronoun_counts["long"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))
                pronoun_correct["neuter"] += ice_tokens.count("þau")
                pronoun_correct["neuter_cis_and_trans"] += ice_tokens.count("þau")
                pronoun_correct["long"] += ice_tokens.count("þau")

    for eng_line, ice_line in zip(english_lines_singular_we, icelandic_lines_singular_we):
        pronoun = identify_subject_only_we_or_singular(eng_line.lower())
        ice_tokens = word_tokenize(ice_line.lower())

        if pronoun == "non-binary" or pronoun == "female_singular" or pronoun == "male_singular":
            pronoun_counts["singular_they"] += (ice_tokens.count("þær") + ice_tokens.count("þeir") + ice_tokens.count("þau") + ice_tokens.count("hán") + ice_tokens.count("hún")+ice_tokens.count("hann"))

        if pronoun == "non-binary":
            if "they have two children" in eng_line.lower():
                pronoun_counts["singular_they_children"] += 1
                if "hán" in ice_tokens:
                    pronoun_correct["singular_they_children"] += 1
                elif "þau" in ice_tokens:
                    pronoun_correct["singular_they_children"] += 0.5
            else:
                pronoun_counts["singular_they_nochildren"] += 1
                if "hán" in ice_tokens:
                    pronoun_correct["singular_they_nochildren"] += 1
                elif "þau" in ice_tokens:
                    pronoun_correct["singular_they_nochildren"] += 0.5

            if "hán" in ice_tokens:
                pronoun_correct["singular_they"] += ice_tokens.count("hán")
            if "þau" in ice_tokens:
                pronoun_correct["singular_they"] += sum((0.5 for p in ice_tokens if p == "þau"))

        elif pronoun == "female_singular":
            if "they have two children" in eng_line.lower():
                pronoun_counts["singular_they_children"] += 1
                if "hún" in ice_tokens:
                    pronoun_correct["singular_they_children"] += 1
                elif "þær" in ice_tokens:
                    pronoun_correct["singular_they_children"] += 0.5
            else:
                pronoun_counts["singular_they_nochildren"] += 1
                if "hún" in ice_tokens:
                    pronoun_correct["singular_they_nochildren"] += 1
                elif "þær" in ice_tokens:
                    pronoun_correct["singular_they_nochildren"] += 0.5

            if "hún" in ice_tokens:
                pronoun_correct["singular_they"] += ice_tokens.count("hún")
            if "þær" in ice_tokens:
                pronoun_correct["singular_they"] += sum((0.5 for p in ice_tokens if p == "þær"))

        elif pronoun == "male_singular":
            if "they have two children" in eng_line.lower():
                pronoun_counts["singular_they_children"] += 1
                if "hann" in ice_tokens:
                    pronoun_correct["singular_they_children"] += 1
                elif "þeir" in ice_tokens:
                    pronoun_correct["singular_they_children"] += 0.5
            else:
                pronoun_counts["singular_they_nochildren"] += 1
                if "hann" in ice_tokens:
                    pronoun_correct["singular_they_nochildren"] += 1
                elif "þeir" in ice_tokens:
                    pronoun_correct["singular_they_nochildren"] += 0.5

            if "hann" in ice_tokens:
                pronoun_correct["singular_they"] += ice_tokens.count("hann")
            if "þeir" in ice_tokens:
                pronoun_correct["singular_they"] += sum((0.5 for p in ice_tokens if p == "þeir"))

    for eng_line, ice_line in zip(english_lines_we_they, icelandic_lines_we_they):

        pronouns = identify_subject_we_and_they(eng_line.lower())
        they_pronoun = pronouns[1]

        ice_tokens = word_tokenize(ice_line.lower())

        if they_pronoun == "female_they":
            pronoun_counts["feminine"] += 1
            pronoun_counts["feminine_unspecified"] += 1
            pronoun_correct["feminine"] += ice_tokens.count("þær")
            pronoun_correct["feminine_unspecified"] += ice_tokens.count("þær")
        elif they_pronoun == "male_they":
            pronoun_counts["masculine"] += 1
            pronoun_counts["masculine_unspecified"] += 1
            pronoun_correct["masculine"] += ice_tokens.count("þeir")
            pronoun_correct["masculine_unspecified"] += ice_tokens.count("þeir")
        elif they_pronoun == "mixed_they":
            pronoun_counts["neuter"] += 1
            pronoun_counts["neuter_unspecified"] += 1
            pronoun_correct["neuter"] += ice_tokens.count("þau")
            pronoun_correct["neuter_unspecified"] += ice_tokens.count("þau")

    results["singular_they_accuracy"] = pronoun_correct["singular_they"] / pronoun_counts["singular_they"] * 100 if pronoun_counts["singular_they"] > 0 else 0

    results["feminine_pronoun_accuracy"] = pronoun_correct["feminine"] / pronoun_counts["feminine"] * 100 if pronoun_counts["feminine"] > 0 else 0
    results["masculine_pronoun_accuracy"] = pronoun_correct["masculine"] / pronoun_counts["masculine"] * 100 if pronoun_counts["masculine"] > 0 else 0
    results["neuter_pronoun_accuracy"] = pronoun_correct["neuter"] / pronoun_counts["neuter"] * 100 if pronoun_counts["neuter"] > 0 else 0
    results["overall_pronoun_accuracy"] = (pronoun_correct["feminine"] + pronoun_correct["masculine"] + pronoun_correct["neuter"] + pronoun_correct["singular_they"]) / (pronoun_counts["feminine"] + pronoun_counts["masculine"] + pronoun_counts["neuter"] + pronoun_counts["singular_they"]) * 100 if (pronoun_counts["feminine"] + pronoun_counts["masculine"] + pronoun_counts["neuter"] + pronoun_counts["singular_they"]) > 0 else 0
    
    results["feminine_unspecified_accuracy"] = pronoun_correct["feminine_unspecified"] / pronoun_counts["feminine_unspecified"] * 100 if pronoun_counts["feminine_unspecified"] > 0 else 0
    results["masculine_unspecified_accuracy"] = pronoun_correct["masculine_unspecified"] / pronoun_counts["masculine_unspecified"] * 100 if pronoun_counts["masculine_unspecified"] > 0 else 0
    results["neuter_unspecified_accuracy"] = pronoun_correct["neuter_unspecified"] / pronoun_counts["neuter_unspecified"] * 100 if pronoun_counts["neuter_unspecified"] > 0 else 0
    results["feminine_trans_accuracy"] = pronoun_correct["feminine_trans"] / pronoun_counts["feminine_trans"] * 100 if pronoun_counts["feminine_trans"] > 0 else 0
    results["masculine_trans_accuracy"] = pronoun_correct["masculine_trans"] / pronoun_counts["masculine_trans"] * 100 if pronoun_counts["masculine_trans"] > 0 else 0
    results["neuter_trans_accuracy"] = pronoun_correct["neuter_trans"] / pronoun_counts["neuter_trans"] * 100 if pronoun_counts["neuter_trans"] > 0 else 0    
    results["feminine_cis_accuracy"] = pronoun_correct["feminine_cis"] / pronoun_counts["feminine_cis"] * 100 if pronoun_counts["feminine_cis"] > 0 else 0
    results["masculine_cis_accuracy"] = pronoun_correct["masculine_cis"] / pronoun_counts["masculine_cis"] * 100 if pronoun_counts["masculine_cis"] > 0 else 0
    results["neuter_cis_accuracy"] = pronoun_correct["neuter_cis"] / pronoun_counts["neuter_cis"] * 100 if pronoun_counts["neuter_cis"] > 0 else 0
    results["neuter_cis_and_trans_accuracy"] = pronoun_correct["neuter_cis_and_trans"] / pronoun_counts["neuter_cis_and_trans"] * 100 if pronoun_counts["neuter_cis_and_trans"] > 0 else 0

    results["feminine_unspecified_children_accuracy"] = pronoun_correct["feminine_unspecified_children"] / pronoun_counts["feminine_unspecified_children"] * 100 if pronoun_counts["feminine_unspecified_children"] > 0 else 0
    results["masculine_unspecified_children_accuracy"] = pronoun_correct["masculine_unspecified_children"] / pronoun_counts["masculine_unspecified_children"] * 100 if pronoun_counts["masculine_unspecified_children"] > 0 else 0
    results["neuter_unspecified_children_accuracy"] = pronoun_correct["neuter_unspecified_children"] / pronoun_counts["neuter_unspecified_children"] * 100 if pronoun_counts["neuter_unspecified_children"] > 0 else 0
    results["feminine_trans_children_accuracy"] = pronoun_correct["feminine_trans_children"] / pronoun_counts["feminine_trans_children"] * 100 if pronoun_counts["feminine_trans_children"] > 0 else 0
    results["masculine_trans_children_accuracy"] = pronoun_correct["masculine_trans_children"] / pronoun_counts["masculine_trans_children"] * 100 if pronoun_counts["masculine_trans_children"] > 0 else 0
    results["neuter_trans_children_accuracy"] = pronoun_correct["neuter_trans_children"] / pronoun_counts["neuter_trans_children"] * 100 if pronoun_counts["neuter_trans_children"] > 0 else 0    
    results["feminine_cis_children_accuracy"] = pronoun_correct["feminine_cis_children"] / pronoun_counts["feminine_cis_children"] * 100 if pronoun_counts["feminine_cis_children"] > 0 else 0
    results["masculine_cis_children_accuracy"] = pronoun_correct["masculine_cis_children"] / pronoun_counts["masculine_cis_children"] * 100 if pronoun_counts["masculine_cis_children"] > 0 else 0
    results["neuter_cis_children_accuracy"] = pronoun_correct["neuter_cis_children"] / pronoun_counts["neuter_cis_children"] * 100 if pronoun_counts["neuter_cis_children"] > 0 else 0
    results["neuter_cis_and_trans_children_accuracy"] = pronoun_correct["neuter_cis_and_trans_children"] / pronoun_counts["neuter_cis_and_trans_children"] * 100 if pronoun_counts["neuter_cis_and_trans_children"] > 0 else 0

    results["feminine_unspecified_nochildren_accuracy"] = pronoun_correct["feminine_unspecified_nochildren"] / pronoun_counts["feminine_unspecified_nochildren"] * 100 if pronoun_counts["feminine_unspecified_nochildren"] > 0 else 0
    results["masculine_unspecified_nochildren_accuracy"] = pronoun_correct["masculine_unspecified_nochildren"] / pronoun_counts["masculine_unspecified_nochildren"] * 100 if pronoun_counts["masculine_unspecified_nochildren"] > 0 else 0
    results["neuter_unspecified_nochildren_accuracy"] = pronoun_correct["neuter_unspecified_nochildren"] / pronoun_counts["neuter_unspecified_nochildren"] * 100 if pronoun_counts["neuter_unspecified_nochildren"] > 0 else 0
    results["feminine_trans_nochildren_accuracy"] = pronoun_correct["feminine_trans_nochildren"] / pronoun_counts["feminine_trans_nochildren"] * 100 if pronoun_counts["feminine_trans_nochildren"] > 0 else 0
    results["masculine_trans_nochildren_accuracy"] = pronoun_correct["masculine_trans_nochildren"] / pronoun_counts["masculine_trans_nochildren"] * 100 if pronoun_counts["masculine_trans_nochildren"] > 0 else 0
    results["neuter_trans_nochildren_accuracy"] = pronoun_correct["neuter_trans_nochildren"] / pronoun_counts["neuter_trans_nochildren"] * 100 if pronoun_counts["neuter_trans_nochildren"] > 0 else 0    
    results["feminine_cis_nochildren_accuracy"] = pronoun_correct["feminine_cis_nochildren"] / pronoun_counts["feminine_cis_nochildren"] * 100 if pronoun_counts["feminine_cis_nochildren"] > 0 else 0
    results["masculine_cis_nochildren_accuracy"] = pronoun_correct["masculine_cis_nochildren"] / pronoun_counts["masculine_cis_nochildren"] * 100 if pronoun_counts["masculine_cis_nochildren"] > 0 else 0
    results["neuter_cis_nochildren_accuracy"] = pronoun_correct["neuter_cis_nochildren"] / pronoun_counts["neuter_cis_nochildren"] * 100 if pronoun_counts["neuter_cis_nochildren"] > 0 else 0
    results["neuter_cis_and_trans_nochildren_accuracy"] = pronoun_correct["neuter_cis_and_trans_nochildren"] / pronoun_counts["neuter_cis_and_trans_nochildren"] * 100 if pronoun_counts["neuter_cis_and_trans_nochildren"] > 0 else 0

    results["long_accuracy"] = pronoun_correct["long"] / pronoun_counts["long"] * 100 if pronoun_counts["long"] > 0 else 0
    results["short_accuracy"] = pronoun_correct["short"] / pronoun_counts["short"] * 100 if pronoun_counts["short"] > 0 else 0

    return results, pronoun_counts, pronoun_correct


def main():
    icelandic_lines_only_they, english_lines_only_they, icelandic_lines_singular_we, english_lines_singular_we, icelandic_lines_we_they, english_lines_we_they = load_text_files("gold_standard.txt", "english_examples.txt")

    results, pronoun_counts, pronoun_correct = analyze_translations(icelandic_lines_only_they, english_lines_only_they, icelandic_lines_singular_we, english_lines_singular_we, icelandic_lines_we_they, english_lines_we_they)
    
    print(f"Overall translation accuracy: {results['overall_pronoun_accuracy']:.2f}% (Correct: {(pronoun_correct['feminine'] + pronoun_correct['masculine'] + pronoun_correct['neuter'] + pronoun_correct['singular_they'])}, Total: {(pronoun_counts['feminine'] + pronoun_counts['masculine'] + pronoun_counts['neuter'] + pronoun_counts['singular_they'])}) \n")

    print(f"Translation accuracy for long text examples (> 3 sentences): {results['long_accuracy']:.2f}% (Correct: {pronoun_correct['long']}, Total: {pronoun_counts['long']})")
    print(f"Translation accuracy for short text examples (< 3 sentences): {results['short_accuracy']:.2f}% (Correct: {pronoun_correct['short']}, Total: {pronoun_counts['short']}) \n")

    print(f"Overall translation accuracy for singular 'they': {results['singular_they_accuracy']:.2f}% (Correct: {pronoun_correct['singular_they']}, Total: {pronoun_counts['singular_they']})")
    print(f"Overall translation accuracy for feminine 'they': {results['feminine_pronoun_accuracy']:.2f}% (Correct: {pronoun_correct['feminine']}, Total: {pronoun_counts['feminine']})")
    print(f"Overall translation accuracy for masculine 'they': {results['masculine_pronoun_accuracy']:.2f}% (Correct: {pronoun_correct['masculine']}, Total: {pronoun_counts['masculine']})")
    print(f"Overall translation accuracy for neuter 'they': {results['neuter_pronoun_accuracy']:.2f}% (Correct: {pronoun_correct['neuter']}, Total: {pronoun_counts['neuter']}) \n")
    
    print(f"Translation accuracy for feminine 'they' when unspecified: {results['feminine_unspecified_accuracy']:.2f}% (Correct: {pronoun_correct['feminine_unspecified']}, Total: {pronoun_counts['feminine_unspecified']})")
    print(f"Translation accuracy for masculine 'they' when unspecified: {results['masculine_unspecified_accuracy']:.2f}% (Correct: {pronoun_correct['masculine_unspecified']}, Total: {pronoun_counts['masculine_unspecified']})")
    print(f"Translation accuracy for neuter 'they' when unspecified: {results['neuter_unspecified_accuracy']:.2f}% (Correct: {pronoun_correct['neuter_unspecified']}, Total: {pronoun_counts['neuter_unspecified']}) \n")

    print(f"Translation accuracy for feminine 'they' when specified to be trans: {results['feminine_trans_accuracy']:.2f}% (Correct: {pronoun_correct['feminine_trans']}, Total: {pronoun_counts['feminine_trans']})")
    print(f"Translation accuracy for masculine 'they' when specified to be trans: {results['masculine_trans_accuracy']:.2f}% (Correct: {pronoun_correct['masculine_trans']}, Total: {pronoun_counts['masculine_trans']})")
    print(f"Translation accuracy for neuter 'they' when specified to be trans: {results['neuter_trans_accuracy']:.2f}% (Correct: {pronoun_correct['neuter_trans']}, Total: {pronoun_counts['neuter_trans']}) \n")

    print(f"Translation accuracy for feminine 'they' when specified to be cis: {results['feminine_cis_accuracy']:.2f}% (Correct: {pronoun_correct['feminine_cis']}, Total: {pronoun_counts['feminine_cis']})")
    print(f"Translation accuracy for masculine 'they' when specified to be cis: {results['masculine_cis_accuracy']:.2f}% (Correct: {pronoun_correct['masculine_cis']}, Total: {pronoun_counts['masculine_cis']})")
    print(f"Translation accuracy for neuter 'they' when specified to be cis: {results['neuter_cis_accuracy']:.2f}% (Correct: {pronoun_correct['neuter_cis']}, Total: {pronoun_counts['neuter_cis']})")
    print(f"Translation accuracy for neuter 'they' when specified to be cis and trans: {results['neuter_cis_and_trans_accuracy']:.2f}% (Correct: {pronoun_correct['neuter_cis_and_trans']}, Total: {pronoun_counts['neuter_cis_and_trans']}) \n")

    print(f"Translation accuracy for feminine 'they have two children' when unspecified: {results['feminine_unspecified_children_accuracy']:.2f}% (Correct: {pronoun_correct['feminine_unspecified_children']}, Total: {pronoun_counts['feminine_unspecified_children']})")
    print(f"Translation accuracy for masculine 'they have two children' when unspecified: {results['masculine_unspecified_children_accuracy']:.2f}% (Correct: {pronoun_correct['masculine_unspecified_children']}, Total: {pronoun_counts['masculine_unspecified_children']})")
    print(f"Translation accuracy for neuter 'they have two children' when unspecified: {results['neuter_unspecified_children_accuracy']:.2f}% (Correct: {pronoun_correct['neuter_unspecified_children']}, Total: {pronoun_counts['neuter_unspecified_children']}) \n")

    print(f"Translation accuracy for feminine 'they have two children' when specified to be trans: {results['feminine_trans_children_accuracy']:.2f}% (Correct: {pronoun_correct['feminine_trans_children']}, Total: {pronoun_counts['feminine_trans_children']})")
    print(f"Translation accuracy for masculine 'they have two children' when specified to be trans: {results['masculine_trans_children_accuracy']:.2f}% (Correct: {pronoun_correct['masculine_trans_children']}, Total: {pronoun_counts['masculine_trans_children']})")
    print(f"Translation accuracy for neuter 'they have two children' when specified to be trans: {results['neuter_trans_children_accuracy']:.2f}% (Correct: {pronoun_correct['neuter_trans_children']}, Total: {pronoun_counts['neuter_trans_children']}) \n")

    print(f"Translation accuracy for feminine 'they have two children' when specified to be cis: {results['feminine_cis_children_accuracy']:.2f}% (Correct: {pronoun_correct['feminine_cis_children']}, Total: {pronoun_counts['feminine_cis_children']})")
    print(f"Translation accuracy for masculine 'they have two children' when specified to be cis: {results['masculine_cis_children_accuracy']:.2f}% (Correct: {pronoun_correct['masculine_cis_children']}, Total: {pronoun_counts['masculine_cis_children']})")
    print(f"Translation accuracy for neuter 'they have two children' when specified to be cis: {results['neuter_cis_children_accuracy']:.2f}% (Correct: {pronoun_correct['neuter_cis_children']}, Total: {pronoun_counts['neuter_cis_children']})")
    print(f"Translation accuracy for neuter 'they have two children' when specified to be cis and trans: {results['neuter_cis_and_trans_children_accuracy']:.2f}% (Correct: {pronoun_correct['neuter_cis_and_trans_children']}, Total: {pronoun_counts['neuter_cis_and_trans_children']}) \n")


    print(f"Translation accuracy for feminine 'they' with no mention of having children when unspecified: {results['feminine_unspecified_nochildren_accuracy']:.2f}% (Correct: {pronoun_correct['feminine_unspecified_nochildren']}, Total: {pronoun_counts['feminine_unspecified_nochildren']})")
    print(f"Translation accuracy for masculine 'they' with no mention of having children when unspecified: {results['masculine_unspecified_nochildren_accuracy']:.2f}% (Correct: {pronoun_correct['masculine_unspecified_nochildren']}, Total: {pronoun_counts['masculine_unspecified_nochildren']})")
    print(f"Translation accuracy for neuter 'they' with no mention of having children when unspecified: {results['neuter_unspecified_nochildren_accuracy']:.2f}% (Correct: {pronoun_correct['neuter_unspecified_nochildren']}, Total: {pronoun_counts['neuter_unspecified_nochildren']}) \n")

    print(f"Translation accuracy for feminine 'they' with no mention of having children when specified to be trans: {results['feminine_trans_nochildren_accuracy']:.2f}% (Correct: {pronoun_correct['feminine_trans_nochildren']}, Total: {pronoun_counts['feminine_trans_nochildren']})")
    print(f"Translation accuracy for masculine 'they' with no mention of having children when specified to be trans: {results['masculine_trans_nochildren_accuracy']:.2f}% (Correct: {pronoun_correct['masculine_trans_nochildren']}, Total: {pronoun_counts['masculine_trans_nochildren']})")
    print(f"Translation accuracy for neuter 'they' with no mention of having children when specified to be trans: {results['neuter_trans_nochildren_accuracy']:.2f}% (Correct: {pronoun_correct['neuter_trans_nochildren']}, Total: {pronoun_counts['neuter_trans_nochildren']}) \n")

    print(f"Translation accuracy for feminine 'they' with no mention of having children when specified to be cis: {results['feminine_cis_nochildren_accuracy']:.2f}% (Correct: {pronoun_correct['feminine_cis_nochildren']}, Total: {pronoun_counts['feminine_cis_nochildren']})")
    print(f"Translation accuracy for masculine 'they' with no mention of having children when specified to be cis: {results['masculine_cis_nochildren_accuracy']:.2f}% (Correct: {pronoun_correct['masculine_cis_nochildren']}, Total: {pronoun_counts['masculine_cis_nochildren']})")
    print(f"Translation accuracy for neuter 'they' with no mention of having children when specified to be cis: {results['neuter_cis_nochildren_accuracy']:.2f}% (Correct: {pronoun_correct['neuter_cis_nochildren']}, Total: {pronoun_counts['neuter_cis_nochildren']})")
    print(f"Translation accuracy for neuter 'they' with no mention of having children when specified to be cis and trans: {results['neuter_cis_and_trans_nochildren_accuracy']:.2f}% (Correct: {pronoun_correct['neuter_cis_and_trans_nochildren']}, Total: {pronoun_counts['neuter_cis_and_trans_nochildren']}) \n")

if __name__ == "__main__":
   main()