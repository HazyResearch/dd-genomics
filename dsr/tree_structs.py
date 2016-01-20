import json
import os
import re
import lxml.etree as et

class XMLTree:
  """
  A generic tree representation which takes XML as input
  Includes subroutines for conversion to JSON & for visualization based on js form
  """
  def __init__(self, xml_root):
    """Calls subroutines to generate JSON form of XML input"""
    self.root = xml_root

  def to_str(self):
    return et.tostring(self.root)


def sentence_to_xmltree(sentence_input, prune_root=True):
  """Transforms a util.SentenceInput object into an XMLTree"""
  root = sentence_to_xmltree_sub(sentence_input, 0)

  # Often the return tree will have several roots, where one is the actual root
  # And the rest are just singletons not included in the dep tree parse...
  # We optionally remove these singletons and then collapse the root if only one child left
  if prune_root:
    for c in root:
      if len(c) == 0:
        root.remove(c)
    if len(root) == 1:
      root = root.findall("./*")[0]
  return XMLTree(root)

def sentence_to_xmltree_sub(s, rid=0):
  """Recursive subroutine to construct XML tree from util.SentenceInput object"""
  i = rid - 1
  attrib = {}
  if i >= 0:
    for k,v in filter(lambda x : type(x[1]) == list, s._asdict().iteritems()):
      if v[i] is not None:
        attrib[singular(k)] = str(v[i])
  root = et.Element('node', attrib=attrib)
  for i,d in enumerate(s.dep_parents):
    if d == rid:
      root.append(sentence_to_xmltree_sub(s, i+1))
  return root

def singular(s):
  """Get singular form of word s (crudely)"""
  return re.sub(r'e?s$', '', s, flags=re.I)


def html_table_to_xmltree(html):
  """HTML/XML table to XMLTree object"""
  node = et.fromstring(re.sub(r'>\s+<', '><', html.strip()))
  xml = html_table_to_xmltree_sub(node)
  return XMLTree(xml)

def html_table_to_xmltree_sub(node):
  """
  Take the XML/HTML table and convert each word in leaf nodes into its own node
  Note: Ideally this text would be run through CoreNLP?
  """
  # Split text into Token nodes
  # NOTE: very basic token splitting here... (to run through CoreNLP?)
  if node.text is not None:
    for tok in re.split(r'\s+', node.text):
      node.append(et.Element('token', attrib={'word':tok}))
  
  # Recursively append children
  for c in node:
    node.append(html_table_to_xmltree_sub(c))
  return node
