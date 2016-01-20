from IPython.core.display import display_html, HTML, display_javascript, Javascript
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
    self.json = self._to_json(self.root)

    # create a unique id for e.g. canvas id in notebook
    self.id = str(abs(hash(self.to_str())))

  def _to_json(self, root):
    js = {
      'attrib': dict(root.attrib),
      'children': []
    }
    for i,c in enumerate(root):
      js['children'].append(self._to_json(c))
    return js

  def to_str(self):
    return et.tostring(self.root)

  def render_tree(self):
    """
    Renders d3 visualization of the d3 tree, for IPython notebook display
    Depends on html/js files in vis/ directory, which is assumed to be in same dir...
    """
    # TODO: Make better control over what format / what attributes displayed @ nodes!
    # HTML
    html = open('vis/tree-chart.html').read() % self.id
    display_html(HTML(data=html))

    # JS
    JS_LIBS = ["http://d3js.org/d3.v3.min.js"]
    js = open('vis/tree-chart.js').read() % (json.dumps(self.json), self.id)
    display_javascript(Javascript(data=js, lib=JS_LIBS))


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
