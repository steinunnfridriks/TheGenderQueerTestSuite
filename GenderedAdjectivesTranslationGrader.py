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
    text examples. It additionally breaks down the gender distributions of
    the translated adjectives, specifying the proportion of each sentiment
    for each gender. This is intended to show whether negatively charged
    adjectives get translated as a specific gender more often than others. 

    The program asumes that the input comes from two txt files, one containing 
    the original, English sentences of the GenderQueer test suite and the other 
    containing the translations in the target language (in this case, Icelandic). 
    The program can easily be modified for other languages.
    
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


def analyze_adjective_translations(icelandic_text, adj_database, english_text):
    translation_counts = {
        "masculine": {"positive": 0, "negative": 0, "neutral": 0},
        "feminine": {"positive": 0, "negative": 0, "neutral": 0},
        "neuter": {"positive": 0, "negative": 0, "neutral": 0}
    }
    total_adjectives = 0
    eng_tokens = word_tokenize(english_text.lower())
    ice_tokens = word_tokenize(icelandic_text.lower())

    # Keep track of matched forms to avoid double counting
    matched_forms = set()

    for adj in adj_database:
        if adj['english'] in eng_tokens:
            total_adjectives += 1
        
        if "hún" in ice_tokens:
            for form in adj['female_singular']:
                if form in ice_tokens and form not in matched_forms:
                    translation_counts["feminine"][adj['sentiment']] += 1
                    matched_forms.add(form)
                    break
        else:
            for form in adj['male_plural'] + adj['male_singular']:
                if form in ice_tokens and form not in matched_forms:
                    translation_counts["masculine"][adj['sentiment']] += 1
                    matched_forms.add(form)
                    break
            
            if translation_counts["masculine"][adj['sentiment']] == 0:
                for form in adj['female_plural']:
                    if form in ice_tokens and form not in matched_forms:
                        translation_counts["feminine"][adj['sentiment']] += 1
                        matched_forms.add(form)
                        break
            
            if translation_counts["masculine"][adj['sentiment']] == 0 and translation_counts["feminine"][adj['sentiment']] == 0:
                for form in adj['neuter_plural'] + adj['neuter_singular']:
                    if form in ice_tokens and form not in matched_forms:
                        translation_counts["neuter"][adj['sentiment']] += 1
                        matched_forms.add(form)
                        break

    return translation_counts, total_adjectives


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
        pronoun = identify_subject_only_we_or_singular(eng_line.lower())
        ice_tokens = word_tokenize(ice_line.lower())
                
        if pronoun == "non-binary":
            true_count = 0
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['neuter_singular']):
                    if true_count == 2:
                        break
                    adjectives_correct += 1
                    true_count += 1
        elif pronoun == "female_singular":
            true_count = 0
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['female_singular']):
                    if true_count == 2:
                        break
                    adjectives_correct += 1
                    true_count += 1        
        elif pronoun == "male_singular":
            true_count = 0
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['male_singular']):
                    if true_count == 2:
                        break
                    adjectives_correct += 1
                    true_count += 1

        elif pronoun == "female_plural":
            true_count = 0
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['female_plural']):
                    if true_count == 2:
                        break
                    adjectives_correct += 1
                    true_count += 1        
        elif pronoun == "male_plural":
            true_count = 0
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['male_plural']):
                    if true_count == 2:
                        break
                    adjectives_correct += 1
                    true_count += 1
        elif pronoun == "mixed":
            true_count = 0
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['neuter_plural']):
                    if true_count == 2:
                        break
                    adjectives_correct += 1
                    true_count += 1        


        translation_counts, adj_count = analyze_adjective_translations(ice_line, adj_database, eng_line)
        total_adjectives += adj_count

        for gender in translation_counts:
            for sentiment in translation_counts[gender]:
                results["translation_analysis"][gender][sentiment] += translation_counts[gender][sentiment]
        
    for eng_line, ice_line in zip(english_lines_we_they, icelandic_lines_we_they):
        pronouns = identify_subject_we_and_they(eng_line)
        we_pronoun = pronouns[0]
        they_pronoun = pronouns[1]

        ice_tokens = word_tokenize(ice_line.lower())
        
        if we_pronoun == "female_we":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['female_plural']):
                    adjectives_correct += 1
                    break
        elif we_pronoun == "male_we":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['male_plural']):
                    adjectives_correct += 1
                    break
        elif we_pronoun == "mixed_we":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['neuter_plural']):
                    adjectives_correct += 1
                    break

        if they_pronoun == "female_they":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['female_plural']):
                    adjectives_correct += 1
                    break
        elif they_pronoun == "male_they":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['male_plural']):
                    adjectives_correct += 1
                    break
        elif they_pronoun == "mixed_they":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['neuter_plural']):
                    adjectives_correct += 1
                    break

        translation_counts, adj_count = analyze_adjective_translations(ice_line, adj_database, eng_line)
        total_adjectives += adj_count
        for gender in translation_counts:
            for sentiment in translation_counts[gender]:
                results["translation_analysis"][gender][sentiment] += translation_counts[gender][sentiment]


    for eng_line, ice_line in zip(english_lines_names, icelandic_lines_names):
        ice_tokens = word_tokenize(ice_line)
        pronouns = identify_subject_names(eng_line)
        we_pronoun = pronouns[0]
        group1 = pronouns[1]
        group2 = pronouns[2]

        if we_pronoun == "female_we":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['female_plural']):
                    adjectives_correct += 1
                    break        
        elif we_pronoun == "male_we":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['male_plural']):
                    adjectives_correct += 1
                    break
        elif we_pronoun == "mixed_we":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['neuter_plural']):
                    adjectives_correct += 1
                    break
        if group1 == "female_group1":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['female_plural']):
                    adjectives_correct += 1
                    break
        elif group1 == "male_group1":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['male_plural']):
                    adjectives_correct += 1
                    break
        elif group1 == "mixed_group1":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['neuter_plural']):
                    adjectives_correct += 1
                    break
        if group2 == "female_group2":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['female_plural']):
                    adjectives_correct += 1
                    break
        elif group2 == "male_group2":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['male_plural']):
                    adjectives_correct += 1
                    break
        elif group2 == "mixed_group2":
            for adj in adj_database:
                if any(form in ice_tokens for form in adj['neuter_plural']):
                    adjectives_correct += 1
                    break

        translation_counts, adj_count = analyze_adjective_translations(ice_line, adj_database, eng_line)
        total_adjectives += adj_count

        for gender in translation_counts:
            for sentiment in translation_counts[gender]:
                results["translation_analysis"][gender][sentiment] += translation_counts[gender][sentiment]


    results["adjectives_accuracy"] = (adjectives_correct / total_adjectives) * 100

    return results, adjectives_correct, total_adjectives

def main():
    adj_database = load_adjective_database('adjectives.json')

    icelandic_lines_singular_we, english_lines_singular_we, icelandic_lines_we_they, english_lines_we_they, icelandic_lines_names, english_lines_names = load_text_files("gold_standard.txt", "english_examples.txt")

    results, adjectives_correct, total_adjectives = analyze_translations(icelandic_lines_singular_we, english_lines_singular_we,icelandic_lines_we_they, english_lines_we_they, icelandic_lines_names, english_lines_names, adj_database)
    
    print(f"\nAdjectives translation accuracy with regards to gender form: {results['adjectives_accuracy']:.2f}")
    
    print(f"\nTotal adjectives analyzed: {total_adjectives}")
    print(f"Number of adjectives correctly translated with regards to gender: {adjectives_correct}")

    total_adjectives = sum(sum(gender_data.values()) for gender_data in results['translation_analysis'].values())

    print("\nOverall Gender Distribution for Translation of Adjectives:")
    for gender in results['translation_analysis']:
        gender_total = sum(results['translation_analysis'][gender].values())
        gender_percentage = (gender_total / total_adjectives * 100) if total_adjectives > 0 else 0
        print(f"  {gender.capitalize()}: {gender_total} ({gender_percentage:.2f}%)")

    print("\nDetailed Sentiment Analysis by Gender:")
    for gender in results['translation_analysis']:
        gender_total = sum(results['translation_analysis'][gender].values())
        print(f"  {gender.capitalize()}:")
        for sentiment, count in results['translation_analysis'][gender].items():
            gender_sentiment_percentage = (count / gender_total * 100) if gender_total > 0 else 0
            overall_sentiment_percentage = (count / total_adjectives * 100) if total_adjectives > 0 else 0
            print(f"    {sentiment.capitalize()}: {count} "
                  f"({gender_sentiment_percentage:.2f}% of {gender}, "
                  f"{overall_sentiment_percentage:.2f}% overall)")

if __name__ == "__main__":
   main()