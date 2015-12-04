#! /usr/bin/env python3

# extract_underage.py
#

from util import latticelib, memex

# Customized supervision code

# pos patterns
pos_patterns = [
    # New patterns
    # '[subj:she] -nsubj-> [cand] <-advmod- [dic:intensifiers]',
    '[dic:provider] -nsubj-> look <-acomp- much <-dep- [cand:younger]',
    '[cand] <-advmod- [dic:intensifiers]',
    '[subj:NNP] -nsubj-> [cand:younger]',
    'very _ young',
    'so _ young',
    'really _ young',
    'teenager body',
    '[cand:dic:young] <-advmod- [dic:intensifiers]',
    '[cand:dic:small_age] <-advmod- [dic:intensifiers]',
    '[subj:she] -nsubj-> [cand:dic:underage]',
    '[subj:NNP] -nsubj-> [cand:dic:underage]',
    '[dic:provider] -nsubj-> [cand:dic:underage]',
    '[subj:she] -nsubj-> look <-dobj- [cand:younger]',
    'way _ younger',
    '[dic:intensifiers] _ younger',
    '[subj:provider] <-prep_with- body <-nn- [cand:dic:underage]',
    '[dic:provider] <-num- [cand:dic:small_age]', # a xx year old girl

    # '[dic:intensifiers] <-advmod- young',
    'barely-legal',
    '[dic:barely] <-advmod- [dic:legal]',
    '[dic:legal] _ but _ young',
    '[reg:^so+$] <-advmod- young',
    '[reg:^so+$] _ young',
    '[dic:barely] _ [dic:small_age]',
    'senior -prep-in-> school',
    'in _ she _ teens',
    'underage',
    'she <-nsubj- minor',
    'how _ young _ she _ be',
    '[dic:legal] <-amod- [dic:provider]',
    # 'high _ school',
    'still _ [dic:small_age]',
    'look -nmod-> girl -advmod-> back -nmod-> school',
    'how _ young',
    'high _ school _ gfe',
    'gfe _ in _ high _ school',
    'if _ you _ like _ them _ young',
    'any _ young _ girl',
    'look _ like _ she _ be _ 15 _ year',
    #'look _ like _ a _ student',
    'look _ pretty _ young _ for _ her _ age',
    'she _ is _ 18',
]

# overrule conflicting neg patterns
strong_pos_patterns = [
    '[subj:she] -nsubj-> [cand:dic:young] <-advmod- [dic:intensifiers]',
    '[subj:NNP] -nsubj-> [cand:dic:young] <-advmod- [dic:intensifiers]',
    '[subj:NNP] -nsubj-> [cand] <-advmod- [dic:intensifiers]',
    '[dic:provider] -nsubj-> [cand:dic:young] <-advmod- [dic:intensifiers]',
    '[subj:I] -nsubj-> be <-prep_with- [cand:teenager]',
    '[subj:she] -nsubj-> look <-acomp- [cand:dic:young] <-advmod- [dic:intensifiers]',
    '[subj:NNP] -nsubj-> look <-acomp- [cand:dic:young] <-advmod- [dic:intensifiers]',
    '[dic:provider] -nsubj-> look <-acomp- [cand:dic:young] <-advmod- [dic:intensifiers]',
    '[subj:old] <-number- [cand]',
    '[subj:old] <-number- [cand:dic:small_age]',
    '[dic:customer] -nsubj-> like <-dobj- look <-nn- [cand:student]',
    '[dic:provider] -nsubj-> [cand:dic:small_age]',

]

# neg patterns
neg_patterns = [
    # '[dic:customer] -nsubj-> [cand:dic:young]',
    'older',
    'COLLEGE_IN_DOC',
    'NEGATED',
    'SUBJECT_IS_CUSTOMER',

    '[dic:provider] -nsubj-> [dic:older_age]',
    'that _ she _ be _ __',
    'when _ she _ be _ __',
    ', _ and _ young',
    'pussy _ be _ so _ young',
    'graduate _ student',
    'college _ student',
    # 'friendly _ and _ young',
    # 'that _ she _ be _ 18',
    # 'when _ she _ be _ 18',

    # "College" signals
    'college _ [dic:provider]',
    'college _ aged _ [dic:provider]',
    'college _ chick',
    'will _ start _ college',
    'save _ up _ for _ college',
    'graduate -prep_from-> [dic:school]',
    '__ <-nn- outfit',
    '[dic:customer] <-nsubj- _ -nmod:in-> [dic:school]',
    '[dic:pic] <-nsubj- _ -advcl-> _ ', # TODO
    # TODO:
    # I am quite a bit young than her .
    # you were too young or too stupid.

    # Original
    'not <-neg- young',
    'isnt _ very _ young',
    'not _ young',
    'not _ too _ young',
    'attractive _ young _ lady',
    'in _ college _ sweat',
    'young _ milf',
    'the _ young',
    'a _ young',
    'be _ young',
    'this _ young _ [dic:lady]',
    'type _ young _ [dic:lady]',
    'look _ young _ [dic:lady]',
    ', _ young _ [dic:lady]',
    ', _ pretty _ young',
    'cheerleader _ type',
    '[dic:attractive] _ young _ [dic:lady]',
    'sweet _ pretty _ young _ [dic:lady]',
    'a _ pretty _ young _ [dic:lady]',
    'pretty _ , _ young _ ebony',
    'a _ tall _ young _ stunning',
    'a _ cute _ young _ girl',
    'look _ young',
    'could _ have _ nail _ in _ high _ school',
    'like _ my _ old _ high _ school',
    'have _ a _ advanced _ college',
    'young _ like _ me',
    'look _ young',
    'very _ pretty _ young',
    'it _ be _ just _ a _ minor',
    'school _ teacher',
    'be _ legal _ and _ safe',
    'minor _ annoyance',
    'men _ and _ young _ college _ kids',
    'it _ be _ like _ two _ high _ school _ kid',
    'i _ feel _ like _ a _ college _ kid',
    'girl _ i _ know _ in _ high _ school',
    'at _ the _ mall _ or _ college',
    'not _ really _ young',
    'when _ she _ be _ younger',
    'college _ park',
    'beer _ girl _ in _ college',
    'i _ be _ relatively _ young',
    'like _ to _ be _ in _ high _ school',
    'remember _ high _ school',
    'make _ out _ like _ high _ school',
    'we _ be _ old _ high _ school',
    'dress _ from _ school _ girl',
    '15 _ year _ ago',
    'for _ 15 _ year',
    '15 _ minute',
    'i _ go _ to _ college'
]

# overrule conflicting pos patterns
strong_neg_patterns = [
    '[dic:provider] -nsubj-> [cand:dic:small_age] <-neg- [dic:negation]',
    'very _ pretty _ young',
    'really _ pretty _ young',
    '[dic:intensifiers] _ pretty _ young',
    'when _ she _ be _ __',
    'when _ she _ be _ [reg:^.*$]',
    '[cand] <-dep- under <-pobj- [dic:older_age]',
    'COLLEGE_IN_SENT',
]


candidate_patterns = [
    # underage
    'underage',
    '[dic:young]',
    # # extremely young
    # '[dic:intensifiers] <-advmod- young',
    # '[reg:^so+$] <-advmod- young',
    # '[reg:^so+$] _ young',
    # age ( we add age extractions from age extractor)
    '[dic:small_age]',
    # '[dic:barely] _ [dic:small_age]',
    # 'still _ [dic:small_age]',
    # legal
    'barely-legal',
    '[dic:legal]',
    'student',
    'coed',
    'co-ed',
    'senior',
    'graduate',
    'college',
    'school',
    'cheerleader',
    # 'in _ she _ teens',
    'minor',
    'kid',
    'child',
    'younger',
    'teen',
    'teens',
    'teenager',
    '15',
    '16',
    '17',
    '18',
    '19',
    'fifteen',
    'sixteen',
    'seventeen',
    'eighteen',
    'nineteen',
]

pos_phrases = [
]

neg_phrases = [
]

underage_dicts = {
    'small_age' : ['16', '17', '18', '19', 'sixteeen', 'seventeen', 'eighteen',
                'nineteen'],
    'older_age' : ['20', '21', '22', '23', '24', '20s', '30', '40', '30s', '40s'],
    'school' : ['school'],
    'high_school' : ['high school'],
    'college' : ['college', 'collage'],
    'customer': ['I', 'you', 'i'],
    'pic': ['photo', 'pic', 'picture', 'photograph', 'photos', 'pics',
        'pictures', 'photographs', 'website', 'ad', 'advertisement'],
    'provider' : ['she', 'gal', 'girl', 'slut', 'cutie', 'hottie', 'lady', 'woman', 'blonde', 'ebony'],
    'barely' : ['barely', 'bearly', 'barley'],
    'legal' : ['legal', 'legalll', 'legall', 'leagle'],
    'just' : ['just', 'recently'],
    'young' : ['young'],
    'underage' : ['underage', 'child', 'teen', 'teens', 'teenager', 'teenagers'],
    # These are not underage
    # 'shy', 'innocent', 'virgin', 'inexperienced', 'tight', 'petite',
    #     'little'
    'attractive' : ['beautiful', 'attractive', 'amazing', 'nice', 'talented',
        'sexy'],
    'go': ['go', 'attend'],

}

feature_patterns = [
    '[dic:provider] * [cand]',
    '[dic:provider] * [cand] * [dic:negation]',
    '[dic:provider] * [cand] * [dic:intensifiers]',
    '[dic:provider] * [cand:lemma]',
    '[dic:provider] * [cand:lemma] * [dic:negation]',
    '[dic:provider] * [cand:lemma] * [dic:intensifiers]',
    '[dic:customer] * [cand]',
    '[dic:customer] * [cand] * [dic:negation]',
    '[dic:customer] * [cand] * [dic:intensifiers]',
    '[dic:customer] * [cand:lemma]',
    '[dic:customer] * [cand:lemma] * [dic:negation]',
    '[dic:customer] * [cand:lemma] * [dic:intensifiers]',
    '[subj] * [cand]',
    '[subj] * [dic:go] * [dic:school]',
    '[subj] * [cand] * [dic:negation]',
    '[subj] * [cand] * [dic:intensifiers]',
    '[subj] * [cand:lemma]',
    '[subj] * [cand:lemma] * [dic:negation]',
    '[subj] * [cand:lemma] * [dic:intensifiers]',
    '[subj] * [dic:school]',
    '[subj] * [dic:school] * [dic:negation]',
    '[subj] * [dic:high_school]',
    '[subj] * [dic:high_school] * [dic:negation]',
    '[cand:lemma] * [dic:negation]',
    '[cand:lemma] * [dic:intensifiers]',
    '[cand:lemma] * [dic:intensifiers] * [dic:negation]',
    '[dic:provider] * [cand] * [dic:pic]', # picture are from when she is 19
    '[cand] * [dic:pic]',
    '[dic:provider] * [dic:older_age]', # picture are from when she is 19
    '[cand] * [dic:older_age]', # picture are from when she is 19
    '[cand:lemma] * when',  # when she was 18
    '__ <-__- __',
    '__ <-__- __ -__-> __',
    '__ _ __',
    '__ _ __ _ __',
    '__ _ __ _ __ _ __',
    '__ _ __ _ __ _ __ _ __',
    'NEGATED',
]

def additional_featurizer(mentions, sentence_index, doc, config):

    if 'college' in doc.text.lower() or 'collage' in doc.text.lower():
        for mention in mentions:
            mention.features.append('COLLEGE_IN_DOC')

    for mention in mentions:
        sentence = sentence_index[mention.sent_id]['sentence']
        if any(l.lower() == 'college' for l in sentence['lemmas']):
            mention.features.append('COLLEGE_IN_SENT')

        if any(f.startswith('[subj:you]' or f.startswith('[subj:i]')) for f in \
                mention.features):
            mention.features.append('SUBJECT_IS_CUSTOMER')
        
    return mentions
        



if __name__ == "__main__":

    # Configure the extractor
    config = latticelib.Config()

    config.add_dicts(underage_dicts)

    config.set_pos_patterns(pos_patterns)
    config.set_neg_patterns(neg_patterns)
    config.set_strong_pos_patterns(strong_pos_patterns)
    config.set_strong_neg_patterns(strong_neg_patterns)
    config.set_candidate_patterns(candidate_patterns)
    config.set_pos_supervision_phrases(pos_phrases)
    config.set_neg_supervision_phrases(neg_phrases)
    config.set_feature_patterns(feature_patterns)
    config.add_featurizer(additional_featurizer)
    config.NGRAM_WILDCARD = False
    config.PRINT_SUPV_RULE = True

    config.run()
