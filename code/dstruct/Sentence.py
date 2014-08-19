#! /usr/bin/env python3
""" A Sentence class

Originally obtained from the 'pharm' repository, but modified.
"""

from dstruct.Word import Word

class Sentence(object):
    _MAXLEN = 1000 # to avoid bad parse tree that have self-recursion
    doc_id = None
    sent_id = None
    words = []

    def __init__(self, _doc_id, _sent_id, _wordidxs, _words, _poses, _ners,
            _lemmas, _dep_paths, _dep_parents, _bounding_boxes):
        self.doc_id = _doc_id
        self.sent_id = _sent_id
        wordidxs = _wordidxs
        words = _words
        poses = _poses
        ners = _ners
        lemmas = _lemmas
        dep_paths = _dep_paths
        dep_parents = _dep_parents
        bounding_boxes = _bounding_boxes 
        self.words = []
        for i in range(len(wordidxs)):
            word = Word(self.sent_id, wordidxs[i], words[i], poses[i], ners[i], lemmas[i],
                    dep_paths[i], dep_parents[i], bounding_boxes[i])
            self.words.append(word)

    def __repr__(self):
        return " ".join([w.word for w in self.words])
  
    def push_word(self, word):
        if self.sent_id == None:
            self.sent_id = word.sent_id
            self.words.append(word)
            return True
        else:
            if self.sent_id == word.sent_id:
                self.words.append(word)
                return True
            else:
                return False

    ## Get all words in the dependency tree from word_index to the root
    def get_path_till_root(self, word_index):
        path = []
        c = word_index
        MAXLEN = self._MAXLEN
        while MAXLEN > 0:
            MAXLEN = MAXLEN -1
            try:
                if c == -1: 
                    break
                path.append(c)
                c = self.words[c].dep_parent
            except:
                break
        return path

    ## Given two paths returned by get_path_till_root, find the least common ancestor
    def get_common_ancestor(self, path1, path2):
        parent = None
        for i in range(0, max(len(path1), len(path2))):
            tovisit = 0 - i - 1
            if i >= len(path1) or i >= len(path2):
                break
            if path1[tovisit] != path2[tovisit]:
                break
            parent = path1[tovisit]
        return parent

    ## Given two word idx1 and idx2, where idx2 is the parent of idx1, return the
    # words on the dependency path
    def get_direct_dependency_path_between_words(self, idx1, idx2):
        words_on_path = []
        c = idx1
        MAXLEN = self._MAXLEN
        while MAXLEN > 0:
            MAXLEN = MAXLEN - 1
            try:
                if c == -1: break
                if c == idx2: break
                if c == idx1: 
                    words_on_path.append(str(self.words[c].dep_path)) # we do not include the word of idx1
                else:
                    words_on_path.append(str(self.words[c].dep_path) + "|" + self.words[c].get_feature())
                c = self.words[c].dep_parent
            except:
                break
        return words_on_path

    ## Given two word idx1 and idx2, return the dependency path feature between them
    def get_word_dep_path(self, idx1, idx2):
        path1 = self.get_path_till_root(idx1)
        path2 = self.get_path_till_root(idx2)

        parent = self.get_common_ancestor(path1, path2)

        words_from_idx1_to_parents = self.get_direct_dependency_path_between_words(idx1, parent)
        words_from_idx2_to_parents = self.get_direct_dependency_path_between_words(idx2, parent)

        return "-".join(words_from_idx1_to_parents) + "@" + "-".join(words_from_idx2_to_parents)

    ## Given two word idx1 and idx2, return the dependency path feature between them
    def get_prev_wordobject(self, mention):
        begin = mention.prov_words[0].insent_id
        if begin - 1 < 0: 
            return None
        else: 
            return self.words[begin - 1]

    def dep_parent(self, mention):
        begin = mention.prov_words[0].insent_id
        end = mention.prov_words[-1].insent_id

        paths = []
        for i in range(begin, end+1):
            for j in range(0, len(self.words)):
                if j >= begin and j <= end: continue

                path = self.get_word_dep_path(i, j)
                paths.append(path)

        return sorted(paths, key=len)[0:min(5,len(paths))]
        
        
    def dep_path(self, entity1, entity2):
  
        begin1 = entity1.prov_words[0].insent_id
        end1 = entity1.prov_words[-1].insent_id
        begin2 = entity2.prov_words[0].insent_id
        end2 = entity2.prov_words[-1].insent_id
    
        paths = []
        for idx1 in range(begin1, end1+1):
            for idx2 in range(begin2, end2+1):
                paths.append(self.get_word_dep_path(idx1, idx2))

        # we pick the one that is shortest
        path = ""
        ll = 100000000
        for p in paths:
            if len(p) < ll:
                path = p
            ll = len(p)
        return path

