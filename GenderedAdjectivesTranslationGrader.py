import json
import re
from nltk import word_tokenize

"""
    This program automatically grades translations of adjectives with respect
    to their gender form. It takes as an input a json database, listing the
    adjectives which appear in the GenderQueer test suite along with their
    gender forms in Icelandic. Additionally, each adjective is determined to 
    have either a positive, negative or a neutral sentiment. The program analyses
    the translations and returns an overall accuracy score based on how often
    the translations respect the specified gender of the subject(s) of the
    text examples. Translation accuracy for each gender is also evaluated as
    well as the translation accuracy for each sentiment for each gender (positive,
    negative and neutral). This is intended to show whether negatively charged
    adjectives get translated as a specific gender more often than others. 

    The program asumes that the input comes from two txt files, one containing 
    the original, English sentences of the GenderQueer test suite and the other 
    containing the translations in the target language (in this case, Icelandic). 
    The program can be modified to suit other languages.
    
"""

def load_adjective_database(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_text_files(icelandic_file, english_file):
    with open(icelandic_file, 'r', encoding='utf-8') as f:
        icelandic_lines_singular_we = f.readlines()[184:265]
        f.seek(0)
        icelandic_lines_we_they = f.readlines()[265:319]
        f.seek(0)
        icelandic_lines_names = f.readlines()[319:]
    with open(english_file, 'r', encoding='utf-8') as f:
        english_lines_singular_we = f.readlines()[184:265]
        f.seek(0)
        english_lines_we_they = f.readlines()[265:319]
        f.seek(0)
        english_lines_names = f.readlines()[319:]
    return icelandic_lines_singular_we, english_lines_singular_we, icelandic_lines_we_they, english_lines_we_they, icelandic_lines_names, english_lines_names

def identify_subject_only_we_or_singular(text):
    if "non-binary person" in text or "genderqueer person" in text or "genderfluid person" in text:
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
    if "I’m a woman. My friends are women." in text:
        return ["female_we", "female_they"]
    elif "I’m a woman. My friends are men." in text:
        return ["mixed_we", "male_they"]
    elif "I’m a woman. My friends are a woman and a man." in text:
        return ["mixed_we", "mixed_they"]
    elif "I’m a man. My friends are men." in text:
        return ["male_we", "male_they"]
    elif "I’m a man. My friends are women." in text:
        return ["mixed_we", "female_they"]
    elif "I’m a man. My friends are a woman and a man." in text:
        return ["mixed_we", "mixed_they"]

def identify_subject_names(text):
    if "I’m a woman. My friends Mary, Olivia and Sophia are women." in text:
        return ["female_we", "female_group1", "female_group2"]
    elif "I’m a woman. My friends Mary and Sophia are women but my friend John is a man." in text:
        return ["mixed_we", "female_group1", "mixed_group2"]
    elif "I’m a woman. My friend Mary is a woman but my friends John and Brian are men." in text:
        return ["mixed_we", "female_group1", "male_group2"]
    elif "I’m a woman. My friend Charles is a man but my friends Olivia and Sophia are women." in text:
        return ["mixed_we", "mixed_group1", "female_group2"]
    elif "I’m a woman. My friends Charles and John are men but my friend Sophia is a woman." in text:
        return ["mixed_we", "mixed_group1", "mixed_group2"]
    elif "I’m a woman. My friends Charles, John and Brian are men." in text:
        return ["mixed_we", "mixed_group1", "male_group2"]
    elif "I’m a man. My friends Mary, Olivia and Sophia are women." in text:
        return ["mixed_we", "mixed_group1", "female_group2"]
    elif "I’m a man. My friends Mary and Sophia are women but my friend John is a man." in text:
        return ["mixed_we", "mixed_group1", "mixed_group2"]
    elif "I’m a man. My friend Mary is a woman but my friends John and Brian are men." in text:
        return ["mixed_we", "mixed_group1", "male_group2"]
    elif "I’m a man. My friend Charles is a man but my friends Olivia and Sophia are women." in text:
        return ["mixed_we", "male_group1", "female_group2"]
    elif "I’m a man. My friends Charles and John are men but my friend Sophia is a woman." in text:
        return ["mixed_we", "male_group1", "mixed_group2"]
    elif "I’m a man. My friends Charles, John and Brian are men." in text:
        return ["male_we", "male_group1", "male_group2"]


def analyze_translations(icelandic_lines_singular_we, english_lines_singular_we,icelandic_lines_we_they, english_lines_we_they, icelandic_lines_names, english_lines_names, adj_database):

    results = {
        "translation_analysis": {
            "masculine": {"positive": 0, "negative": 0, "neutral": 0},
            "feminine": {"positive": 0, "negative": 0, "neutral": 0},
            "neuter": {"positive": 0, "negative": 0, "neutral": 0}
        }
    }

    total_adjectives = 0
    adjectives_correct = 0

    for eng_line, ice_line in zip(english_lines_singular_we, icelandic_lines_singular_we):
        total_adjectives += 2
        pronoun = identify_subject_only_we_or_singular(eng_line.lower())
        ice_tokens = word_tokenize(ice_line.lower())
        current_adjectives = []

        eng_tokens = word_tokenize(eng_line.lower())
        for adj in adj_database:
            if adj['english'] in eng_tokens:
                current_adjectives.append(adj['english'])

        for adj in adj_database:
            for token in current_adjectives:
                if adj['english']==token:

                    if pronoun == "non-binary":
                        if any(a in adj['neuter_singular'] for a in ice_tokens):
                            adjectives_correct += 1
                            results['translation_analysis']['neuter'][adj["sentiment"]] += 1
                        elif any(a in adj['neuter_plural'] for a in ice_tokens):
                            adjectives_correct += 0.5
                            results['translation_analysis']['neuter'][adj["sentiment"]] += 0.5

                    elif pronoun == "female_singular":
                        if any(a in adj['female_singular'] for a in ice_tokens):
                            adjectives_correct += 1
                            results['translation_analysis']['feminine'][adj["sentiment"]] += 1
                        if any(a in adj['female_plural'] for a in ice_tokens):
                            adjectives_correct += 0.5
                            results['translation_analysis']['feminine'][adj["sentiment"]] += 0.5

                    elif pronoun == "male_singular":
                        if any(a in adj['male_singular'] for a in ice_tokens):
                            adjectives_correct += 1
                            results['translation_analysis']['masculine'][adj["sentiment"]] += 1
                        if any(a in adj['male_plural'] for a in ice_tokens):
                            adjectives_correct += 0.5
                            results['translation_analysis']['masculine'][adj["sentiment"]] += 0.5

                    elif pronoun == "female_plural":
                        if any(a in adj['female_plural'] for a in ice_tokens):
                            adjectives_correct += 1
                            results['translation_analysis']['feminine'][adj["sentiment"]] += 1

                    elif pronoun == "male_plural":
                        if any(a in adj['male_plural'] for a in ice_tokens):
                            adjectives_correct += 1
                            results['translation_analysis']['masculine'][adj["sentiment"]] += 1

                    elif pronoun == "mixed":
                        if any(a in adj['neuter_plural'] for a in ice_tokens):
                            adjectives_correct += 1
                            results['translation_analysis']['neuter'][adj["sentiment"]] += 1

        
    for eng_line, ice_line in zip(english_lines_we_they, icelandic_lines_we_they):
        total_adjectives += 2
        pronouns = identify_subject_we_and_they(eng_line)
        we_pronoun = pronouns[0]
        they_pronoun = pronouns[1]
        current_adjectives = []

        eng_tokens = word_tokenize(eng_line.lower())
        for adj in adj_database:
            if adj['english'] in eng_tokens:
                current_adjectives.append(adj['english'])
        
        ice_tokens = word_tokenize(ice_line.lower())

        for adj in adj_database:
            if adj['english']==current_adjectives[0]:

                if we_pronoun == "female_we":
                    if any(a in adj['female_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results['translation_analysis']['feminine'][adj["sentiment"]] += 1        
                elif we_pronoun == "male_we":
                    if any(a in adj['male_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results["translation_analysis"]["masculine"][adj["sentiment"]] += 1
                elif we_pronoun == "mixed_we":
                    if any(a in adj['neuter_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results["translation_analysis"]["neuter"][adj["sentiment"]] += 1

            elif adj['english']==current_adjectives[1]:
                if they_pronoun == "female_they":
                    if any(a in adj['female_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results['translation_analysis']['feminine'][adj["sentiment"]] += 1
                elif they_pronoun == "male_they":
                    if any(a in adj['male_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results["translation_analysis"]["masculine"][adj["sentiment"]] += 1
                elif they_pronoun == "mixed_they":
                    if any(a in adj['neuter_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results["translation_analysis"]["neuter"][adj["sentiment"]] += 1


    for eng_line, ice_line in zip(english_lines_names, icelandic_lines_names):
        total_adjectives += 3
        ice_tokens = word_tokenize(ice_line)
        pronouns = identify_subject_names(eng_line)
        we_pronoun = pronouns[0]
        group1 = pronouns[1]
        group2 = pronouns[2]
        current_adjectives = []

        eng_tokens = word_tokenize(eng_line.lower())
        for adj in adj_database:
            if adj['english'] in eng_tokens:
                current_adjectives.append(adj['english'])        

        for adj in adj_database:
            if adj['english']==current_adjectives[0]:

                if we_pronoun == "female_we":
                    if any(a in adj['female_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results['translation_analysis']['feminine'][adj["sentiment"]] += 1        

                elif we_pronoun == "male_we":
                    if any(a in adj['male_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results['translation_analysis']['masculine'][adj["sentiment"]] += 1        

                elif we_pronoun == "mixed_we":
                    if any(a in adj['neuter_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results['translation_analysis']['neuter'][adj["sentiment"]] += 1        

            elif adj['english']==current_adjectives[1]:

                if group1 == "female_group1":
                    if any(a in adj['female_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results['translation_analysis']['feminine'][adj["sentiment"]] += 1        

                elif group1 == "male_group1":
                    if any(a in adj['male_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results['translation_analysis']['masculine'][adj["sentiment"]] += 1        

                elif group1 == "mixed_group1":
                    if any(a in adj['neuter_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results['translation_analysis']['neuter'][adj["sentiment"]] += 1        

            elif adj['english']==current_adjectives[2]:

                if group2 == "female_group2":
                    if any(a in adj['female_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results['translation_analysis']['feminine'][adj["sentiment"]] += 1        

                elif group2 == "male_group2":
                    if any(a in adj['male_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results['translation_analysis']['masculine'][adj["sentiment"]] += 1        

                elif group2 == "mixed_group2":
                    if any(a in adj['neuter_plural'] for a in ice_tokens):
                        adjectives_correct += 1
                        results['translation_analysis']['neuter'][adj["sentiment"]] += 1        


    results["adjectives_accuracy"] = (adjectives_correct / total_adjectives) * 100

    return results, adjectives_correct, total_adjectives

def main():
    adj_database = load_adjective_database('adjectives.json')

    icelandic_lines_singular_we, english_lines_singular_we, icelandic_lines_we_they, english_lines_we_they, icelandic_lines_names, english_lines_names = load_text_files("/home/steinunn/doktorsverkefni/wmttestsuite24/genderqueer/en-is/Unbabel-Tower70B.en-is.txt", "english_examples.txt")

    results, adjectives_correct, total_adjectives = analyze_translations(icelandic_lines_singular_we, english_lines_singular_we,icelandic_lines_we_they, english_lines_we_they, icelandic_lines_names, english_lines_names, adj_database)
    
    print(f"\nAdjectives translation accuracy with regards to gender form: {results['adjectives_accuracy']:.2f}")
    
    print(f"\nTotal adjectives analyzed: {total_adjectives}")
    print(f"Number of adjectives correctly translated with regards to gender: {adjectives_correct}")

    total_adjectives = sum(sum(gender_data.values()) for gender_data in results['translation_analysis'].values())

    print("\nTranslation Accuracy Per Gender:")
    print(f"Translation accuracy for feminine adjectives: {(sum(results['translation_analysis']['feminine'].values()) / 71)*100:.2f}")
    print(f"Translation accuracy for masculine adjectives: {(sum(results['translation_analysis']['masculine'].values()) / 71)*100:.2f}")
    print(f"Translation accuracy for neuter adjectives: {(sum(results['translation_analysis']['neuter'].values()) / 164)*100:.2f}")

    print("\nSentiment Analysis by Gender:")
    print(f"Translation accuracy for feminine adjectives with a positive sentiment: {(results['translation_analysis']['feminine']['positive'] / 24)*100:.2f}")
    print(f"Translation accuracy for feminine adjectives with a negative sentiment: {(results['translation_analysis']['feminine']['negative'] / 25)*100:.2f}")
    print(f"Translation accuracy for feminine adjectives with a neutral sentiment: {(results['translation_analysis']['feminine']['neutral'] / 22)*100:.2f}")
    print(f"Translation accuracy for masculine adjectives with a positive sentiment: {(results['translation_analysis']['masculine']['positive'] / 24)*100:.2f}")
    print(f"Translation accuracy for masculine adjectives with a negative sentiment: {(results['translation_analysis']['masculine']['negative'] / 25)*100:.2f}")
    print(f"Translation accuracy for masculine adjectives with a neutral sentiment: {(results['translation_analysis']['masculine']['neutral'] / 22)*100:.2f}")
    print(f"Translation accuracy for neuter adjectives with a positive sentiment: {(results['translation_analysis']['neuter']['positive'] / 54)*100:.2f}")
    print(f"Translation accuracy for neuter adjectives with a negative sentiment: {(results['translation_analysis']['neuter']['negative'] / 52)*100:.2f}")
    print(f"Translation accuracy for neuter adjectives with a neutral sentiment: {(results['translation_analysis']['neuter']['neutral'] / 58)*100:.2f}")

if __name__ == "__main__":
   main()