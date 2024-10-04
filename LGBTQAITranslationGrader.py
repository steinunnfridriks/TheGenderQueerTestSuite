import json

class LGBTQAITranslationGrader:
    """
    This class automatically grades translations of LGBTQAI+ vocabulary based on a
    json database of English terms and their acceptable translations. The database
    also includes inappropriate or outdated translations of said terms, the occurence
    of which is kept as a separate score. The grades are calculated as the number of
    appropriately translated terms divided by the total occurences of LGBTQAI+ terms
    within a txt file containing the translations in the target language.
    
    The class asumes that the input comes from two txt files, one containing the original,
    English sentences of the GenderQueer test suite and the other containing the translations
    in the target language (in this case, Icelandic). The class can be modified to suit
    other languages.
    """

    def __init__(self, show_details=False):
        self.terminology_db = self.load_terminology_db()
        self.show_details = show_details # Determines the verbosity of the report

    def load_terminology_db(self):
        with open('terminology.json', 'r', encoding='utf-8') as file:
            return json.load(file)

    def identify_terms(self, english_text):
        identified_terms = []
        for term in self.terminology_db.keys():
            if term in english_text:
                if term == "bi":
                    eng_tokens = english_text.split()
                    if term in eng_tokens:
                        identified_terms.append(term)
                else:        
                    identified_terms.append(term)
        return identified_terms

    def grade_translation(self, english_text, icelandic_text):
        identified_terms = self.identify_terms(english_text)
        cis_trans_compounds = ["transkona", "transkonur", "transkvenmaður", "transkvenmenn", "transmaður", "transkarl", "transkarlmaður", "transmenn", "transkarlar", "transkarlmenn", "sískona", "cískona", "ciskona", "sískvenmaður", "cískvenmaður", "ciskvenmaður", "sís-kona", "sís-kvenmaður", "cis-kona", "cis-kvenmaður", "cís-kona", "cís-kvenmaður", "sískonur", "cískonur", "ciskonur", "sískvenmenn", "cískvenmenn", "ciskvenmenn", "sís-konur", "sís-kvenmenn", "cis-konur", "cis-kvenmenn", "cís-konur", "cís-kvenmenn", "sísmaður", "cismaður", "císmaður", "sískarl", "ciskarl", "cískarl", "sískarlmaður", "ciskarlmaður", "cískarlmaður", "sís-maður", "sís-karl", "sís-karlmaður", "cis-maður", "cis-karl", "cis-karlmaður", "cís-maður", "cís-karl", "cís-karlmaður", "sísmenn", "cismenn", "císmenn", "sískarlar", "ciskarlar", "cískarlar", "sískarlmenn", "ciskarlmenn", "sís-menn", "sís-karlar", "sís-karlmenn", "cis-menn", "cis-karlar", "cis-karlmenn", "cís-menn", "cís-karlar", "cís-karlmenn"]
        
        correct_terms = 0
        inappropriate_terms = 0
        term_details = []

        for term in identified_terms:
            translations = self.terminology_db[term]
            correct_found = False
            inappropriate_found = False

            for acceptable in translations['acceptable']:
                if acceptable in icelandic_text:
                    correct_found = True
                    if acceptable in cis_trans_compounds:
                        term_details.append(f"Warning: '{term}' translated as '{acceptable}' but should be written as two separate words with trans/cis as an adjective (not as a compound). Using the compound is considered inappropriate by many within the trans community as it implies that they are a separate kind of person. This translation is scored as half right (0.5 points).")
                        correct_terms += 0.5
                    elif "transkynja" in acceptable or "sískynja" in acceptable or "ciskynja" in acceptable or "cískynja" in acceptable:
                        term_details.append(f"Warning: '{term}' translated as '{acceptable}'. The adjectives 'transkynja' and 'sískynja' are generally not used though they do exist. A preferable translation of the adjective would be 'trans' or 'sís'. This translation is scored as half right (0.5 points).")
                        correct_terms += 0.5                               
                    elif acceptable=="lessur" or acceptable=="bæjarar":
                        term_details.append(f"Warning: '{term}' translated as '{acceptable}'. The appropriateness of this term is context-dependent. This translation is scored as half right (0.5 points).")
                        correct_terms += 0.5    
                    else:
                        term_details.append(f"Correct: '{term}' translated as '{acceptable}'")
                        correct_terms += 1
                    break

            for inappropriate in translations['inappropriate']:
                if inappropriate in icelandic_text:
                    inappropriate_terms += 1
                    inappropriate_found = True
                    term_details.append(f"Inappropriate: '{term}' translated as '{inappropriate}'")
                break
            if not correct_found and not inappropriate_found:
                term_details.append(f"Missing: No translation found for '{term}'")

        return correct_terms, inappropriate_terms, term_details

    def grade_files(self, english_file_path, icelandic_file_path):
        total_terms = 0
        total_correct = 0
        total_inappropriate = 0
        all_term_details = []

        try:
            with open(english_file_path, 'r', encoding='utf-8') as eng_file, \
                 open(icelandic_file_path, 'r', encoding='utf-8') as ice_file:
                for i, (eng_line, ice_line) in enumerate(zip(eng_file, ice_file), 1):
                    identified_terms = self.identify_terms(eng_line.strip())
                    total_terms += len(identified_terms)
                    correct, inappropriate, details = self.grade_translation(eng_line.strip(), ice_line.strip())
                    total_correct += correct
                    total_inappropriate += inappropriate
                    if self.show_details:
                        all_term_details.extend([f"Line {i}: {detail}" for detail in details])

            if total_terms > 0:
                correct_percentage = (total_correct / total_terms) * 100
            else:
                correct_percentage = 0

            report = f"""
LGBTQAI+ Terminology Translation Report:
---------------------------------------
Total LGBTQAI+ terms identified: {total_terms}
Correctly translated terms: {total_correct}
Inappropriate or outdated translations: {total_inappropriate} ({(total_inappropriate / total_terms)* 100:.2f}%)
Correct translation percentage: {correct_percentage:.2f}%

Overall Assessment:
{total_correct} out of {total_terms} LGBTQAI+ term(s) were correctly translated.
There were {total_inappropriate} instance(s) of inappropriate terminology.
                    """

            if self.show_details:
                report += "\nDetailed breakdown:\n"
                report += "\n".join(all_term_details)

            return report

        except FileNotFoundError as e:
            return f"Error: File not found - {str(e)}"
        except Exception as e:
            return f"An error occurred while processing the files: {str(e)}"


grader = LGBTQAITranslationGrader(show_details=False)  # Set to False to hide detailed breakdown
english_file_path = "english_examples.txt"
icelandic_file_path = "gold_standard.txt"
report = grader.grade_files(english_file_path, icelandic_file_path)
print(report)