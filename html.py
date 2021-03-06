
csvcount=0

def tag(name, s):
  return "<%s>%s</%s>" % (name, s, name)


def style():
  return tag("style", """
    * { padding: 10px; margin: 10px; }
    thead { background: #eee }
    th { font-weight: bold; border: 1px solid black }
    td { border: 1px solid black }
    hr { padding: 0; margin: 0; border: 2px solid blue }
  """)

def script():
  return "<script type='text/javascript' src='dygraph-combined.js'></script>"

def b(s):
  return tag("b", s)

def td(s):
  return tag("td", s)

def tr(s):
  return tag("tr", s)

def join(l):
  return "\n".join(l)

def hr():
  return "<hr/>"

def section(name, s):
  return join([tag("h2", name), s, hr()])

def comments(l):
  return tag("pre",'\n'.join(l))

def csv(csv,title,opts=[]):
  global csvcount
  csvcount += 1
  opts.append("rightGap:250")

  csv = map(lambda x: r"'%s\n'" % x, csv)
  csvtxt = r"""
  <div style='float:left;border:1px solid black;'>
  %s
  <div id="graphdiv%d" style="width:1200px;height:500px"></div>
  <script type="text/javascript">
  g = new Dygraph(
    // containing div
    document.getElementById("graphdiv%d"),
    %s
    , {%s}
  );
  </script>
  </div>
  """ % (tag("h3",title), csvcount, csvcount, "+".join(csv), ",".join(opts))
  return csvtxt


def table(d):
  """
    'd' is a dictionary of {rowname : { colname : value } }
    Returns a string of the html form of the table
  """
  
  if type(d) == type({}):
    s = ""
    cols = d[d.keys()[0]]
    # first row, headings for cols
    s += join([td("")] + [td(b(colname)) for colname in cols])
    
    # every row
    for rowname in d.keys():
      s += tr(join( [ td(b(rowname)) ] +  [td(d[rowname][colname]) for colname in cols]))
  else:
    s = ""
    s += tr(join([td(x) for x in d]))

  return tag("table", s)

def html(fname, doc):
  f = open(fname, "w")
  f.write(tag("html", style() + script() + doc))
  f.close()

