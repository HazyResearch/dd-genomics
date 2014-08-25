#! /usr/bin/env python3
""" A Sentence class

Basically a container for an array of Word objects, plus doc_id and sent_id.

Originally obtained from the 'pharm' repository, but modified.
"""

from dstruct.Word import Word

class Sentence(object):
    _MAX_DEP_PATH_LEN = 1000 # to avoid bad parse tree that have self-recursion
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
            word = Word(self.doc_id, self.sent_id, wordidxs[i], words[i],
                    poses[i], ners[i], lemmas[i], dep_paths[i], dep_parents[i],
                    bounding_boxes[i])
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

    ## Return a list of the indexes of all words in the dependency path from
    ## the word at index word_index to the root
    def get_path_till_root(self, word_index):
        path = []
        c = word_index
        MAX_DEP_PATH_LEN = self._MAX_DEP_PATH_LEN
        while MAX_DEP_PATH_LEN > 0:
            MAX_DEP_PATH_LEN = MAX_DEP_PATH_LEN -1
            try:
                # c == -1 means we found the root
                if c == -1: 
                    break
                path.append(c)
                c = self.words[c].dep_parent
            except:
                break
        return path

    ## Given two paths returned by get_path_till_root, find the least common
    ## ancestor, i.e., the one farthest away from the root. If there is no
    ## common ancestor, return None
    def get_common_ancestor(self, path1, path2):
        # The paths are sorted from leaf to root, so reverse them
        path1_rev = path1[:]
        path1_rev.reverse() 
        path2_rev = path2[:]
        path2_rev.reverse()
        i = 0
        while i < min(len(path1_rev), len(path2_rev)) and \
                path1_rev[i] == path2_rev[i]:
            i += 1
        if  path1_rev[i-1] != path2_rev[i-1]:
            # No common ancestor found
            return None
        else:
            return path1_rev[i-1]
        # XXX (Matteo) The following is the function as it was in pharma.
        # The logic seemed more complicated to understand for me.
       # parent = None
       # for i in range(max(len(path1), len(path2))):
       #     tovisit = 0 - i - 1
       #     if i >= len(path1) or i >= len(path2):
       #         break
       #     if path1[tovisit] != path2[tovisit]:
       #         break
       #     parent = path1[tovisit]
       # return parent

    ## Given two word idx1 and idx2, where idx2 is an ancestor of idx1, return,
    ## for each word 'w' on the dependency path between idx1 and idx2, the label
    ## on the edge to 'w' and the NER tag of 'w' or its lemma if the NER tag
    ## is 'O' (see Word.get_feature())
    # the dependency path labels on the path from idx1 to idx2 
    def get_direct_dependency_path_between_words(self, idx1, idx2):
        words_on_path = []
        c = idx1
        MAX_DEP_PATH_LEN = self._MAX_DEP_PATH_LEN
        while MAX_DEP_PATH_LEN > 0:
            MAX_DEP_PATH_LEN -= 1 
            try:
                if c == -1: 
                    break
                elif c == idx2: 
                    break
                elif c == idx1: 
                    # we do not include the NER tag/lemma for idx1
                    words_on_path.append(str(self.words[c].dep_path)) 
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

    ## Given a mention, return the word before the first word of the mention, if present
    def get_prev_wordobject(self, mention):
        begin = mention.words[0].in_sent_idx
        if begin - 1 < 0: 
            return None
        else: 
            return self.words[begin - 1]

    ## Given a mention, return the word after the last word of the mention, if present
    def get_next_wordobject(self, mention):
        end = mention.words[-1].in_sent_idx
        if end == len(self.words) - 1: 
            return None
        else: 
            return self.words[end + 1]

    def dep_parent(self, mention):
        begin = mention.words[0].in_sent_idx
        end = mention.words[-1].in_sent_idx

        paths = []
        for i in range(begin, end+1):
            for j in range(0, len(self.words)):
                if j >= begin and j <= end: continue

                path = self.get_word_dep_path(i, j)
                paths.append(path)

        return sorted(paths, key=len)[0:min(5,len(paths))]
        
    ## Given two entities, return the feature of the shortest dependency path
    ## between word from one of to a word of the other.
    def dep_path(self, entity1, entity2):
        begin1 = entity1.words[0].in_sent_idx
        end1 = entity1.words[-1].in_sent_idx
        begin2 = entity2.words[0].in_sent_idx
        end2 = entity2.words[-1].in_sent_idx
    
        paths = []
        for idx1 in range(begin1, end1+1):
            for idx2 in range(begin2, end2+1):
                paths.append(self.get_word_dep_path(idx1, idx2))

        # we pick the one that is shortest
        path = ""
        ll = 100000000 # Just a very large number
        for p in paths:
            if len(p) < ll:
                path = p
            ll = len(p)
        return path

