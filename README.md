# The GenderQueer Test Suite

The GenderQueer Test Suite is a novel evaluation set for assessing machine translation (MT) systems' capabilities in handling gender-diverse and queer-inclusive content. It's designed for English to Icelandic translations but can be adapted for other languages quite easily. As MT quality improves, there is an increasing need for specialized evaluation methods that address nuanced aspects of language and identity. The suite evaluates MT systems on various aspects of gender-inclusive translation, including pronoun and adjective agreement, LGBTQIA+ terminology accuracy, and the impact of explicit gender specifications.

The test suite aims to address five key areas of evaluation:

1. Pronoun translation: Assessing translation accuracy when translating the third-person pronoun 'they' from English to Icelandic with respect to gender agreement.

2. The singular 'they': Assessing whether MT systems are able to translate the gender-neutral, singular 'they' as it is used in English to the more rigid grammatical gender system of Icelandic.

3. Adjective agreement: Evaluating the translation of adjectives with respect to gender forms in the target language. Additionally, the gender distribution of adjective translations is examined in order to see if a particular gender form is used more or less often than others, potentially indicating gender bias. Furthermore, gender distributions for translations of adjectives with a positive, negative and neutral connotations are evaluated.

4. LGBTQIA+ terminology: Examining the translation accuracy of LGBTQIA+-specific terms, including an assessment of whether translations are current and culturally appropriate or potentially outdated or inappropriate.

5. Influence of explicit gender information: Investigating whether explicitly specifying a subject as cis or trans affects the translation of 'they' compared to similar sentences without such specification.

The test suite primarily consists of short paragraphs (3-4 sentences long) designed to provide context and challenge MT systems across these five dimensions. Additionally, we include 16 single-sentence examples for comparison of sentence-level and paragraph-level translations. Each passage contains explicit information about the gender of the subject or subjects mentioned.

The test suite contains 331 text examples in English, stored in a single text file which is to be translated by the MT systems. The test suite also contains a gold standard translation meant for comparison where each example has been translated as expected into Icelandic.

Each example starts by explicitly referencing the gender of the subject or subjects in question. This is done in four ways:

1. "These (cis/trans) men/women are my neighbors / This (cis/trans) man and this (cis/trans) woman are my neighbors."
2. "This non-binary/genderqueer/genderfluid person is my neighbor." 
3. "I’m a woman/man. My friends are women/men/a man and a woman."
4. "I’m a woman/man. My friends X, Y and C are women/men / My friend X is a woman/man but my friends Z and Y are men/women / My friends X and Y are women/men but my friend Z is a man/woman."

Additionally, in the case of single-sentence examples, genders are explicitly stated in a similar format: "These men/women who live next door to me are my neighbors and they...". By explicitly stating the gender of the subject or subjects, we avoid problems that may arise when gender is assumed based of a person's name. 

Further information, including which publication to cite when referencing the GenderQueer Test Suite, will be made available shortly.
