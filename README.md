# pyppl - A python lightweight pipeline framework
[Documentation][1] | [API][2] | [Github repos.][3]

<!-- toc -->
## Features
- Supports of any language to run you processes.
- Automatic deduction of input based on the process dependencies. [Details][4]
- Different ways of exporting output files (including `gzip`). [Details][5]
- Process caching. [Details][6]
- Flexible placeholder handling in output and script settings. [Details][7]
- APIs to modify channels. [Details][8]
- Different runners to run you processes on different platforms. [Details][9]
- Runner customization (you can define your own runner). [Details][10]
- Callbacks of processes. [Details][11]
- Error handling for processes. [Details][12]
- Configuration file support for pipelines. [Details][13]
- Flowchat in [DOT][14] for your pipelines. [Details][15]
- Aggregations (a set of processes predefined). [Details][16]
- Detailed [documentation][1] and [API documentation][2].

## Requirements
- Linux (Maybe works on OSX, not tested)
- Python 2.7

## Installation
```bash
# install latest version
git clone https://github.com/pwwang/pyppl.git
cd pyppl
python setup.py install
# install released version
pip install pyppl
```

## First script
```python
from pyppl import pyppl, proc

pSort         = proc()
# use sys.argv as input channel
pSort.input   = "infile:file"
pSort.output  = "outfile:file:{{infile.fn}}.sorted"
pSort.script  = """
  sort -k1r {{infile}} > {{outfile}}
""" 

pyppl().starts(pSort).run()
```

run `python test.py test1.txt test2.txt test3.txt test4.txt test5.txt` will output:
```
[2017-04-21 16:44:35,003] [  PyPPL] Version: 0.6.1
[2017-04-21 16:44:35,003] [   TIPS] beforeCmd and afterCmd only run locally
[2017-04-21 16:44:35,003] [ CONFIG] Read from /home/user/.pyppl
[2017-04-21 16:44:35,003] [  START] --------------------------------- pSort.notag ----------------------------------
[2017-04-21 16:44:35,007] [  DEBUG] pSort.notag: INPUT [4/4]: infile.ext => .txt
[2017-04-21 16:44:35,007] [  DEBUG] pSort.notag: INPUT [4/4]: # => 4
[2017-04-21 16:44:35,007] [  DEBUG] pSort.notag: INPUT [4/4]: infile.bn => test5.txt
[2017-04-21 16:44:35,007] [  DEBUG] pSort.notag: INPUT [4/4]: infile => /home/user/tests/workdir/PyPPL.pSort.notag.2BNAjwU1/input/test5.txt
[2017-04-21 16:44:35,007] [  DEBUG] pSort.notag: INPUT [4/4]: infile.fn => test5
[2017-04-21 16:44:35,007] [  DEBUG] pSort.notag: PROC_VARS: runner => local
[2017-04-21 16:44:35,007] [  DEBUG] pSort.notag: PROC_VARS: echo => False
[2017-04-21 16:44:35,008] [  DEBUG] pSort.notag: PROC_VARS: tag => notag
[2017-04-21 16:44:35,008] [  DEBUG] pSort.notag: PROC_VARS: tmpdir => /home/user/tests/workdir
[2017-04-21 16:44:35,008] [  DEBUG] pSort.notag: PROC_VARS: indir => /home/user/tests/workdir/PyPPL.pSort.notag.2BNAjwU1/input
[2017-04-21 16:44:35,008] [  DEBUG] pSort.notag: PROC_VARS: cache => True
[2017-04-21 16:44:35,008] [  DEBUG] pSort.notag: PROC_VARS: id => pSort
[2017-04-21 16:44:35,008] [  DEBUG] pSort.notag: PROC_VARS: forks => 1
[2017-04-21 16:44:35,008] [  DEBUG] pSort.notag: PROC_VARS: workdir => /home/user/tests/workdir/PyPPL.pSort.notag.2BNAjwU1
[2017-04-21 16:44:35,008] [  DEBUG] pSort.notag: PROC_VARS: outdir => /home/user/tests/workdir/PyPPL.pSort.notag.2BNAjwU1/output
[2017-04-21 16:44:35,008] [  DEBUG] pSort.notag: PROC_VARS: length => 5
[2017-04-21 16:44:35,009] [  DEBUG] pSort.notag: OUTPUT [0/4]: outfile => /home/user/tests/workdir/PyPPL.pSort.notag.2BNAjwU1/output/test1.sorted
[2017-04-21 16:44:35,011] [  DEBUG] pSort.notag: Not cached, cache file /home/user/tests/workdir/PyPPL.pSort.notag.2BNAjwU1/cached.jobs not exists.
[2017-04-21 16:44:35,011] [RUNNING] pSort.notag: /home/user/tests/workdir/PyPPL.pSort.notag.2BNAjwU1
[2017-04-21 16:44:35,011] [  DEBUG] pSort.notag: Submitting job #0 ...
[2017-04-21 16:44:35,011] [  DEBUG] pSort.notag: Submitting job #1 ...
[2017-04-21 16:44:35,011] [  DEBUG] pSort.notag: Submitting job #2 ...
[2017-04-21 16:44:35,011] [  DEBUG] pSort.notag: Submitting job #3 ...
[2017-04-21 16:44:35,011] [  DEBUG] pSort.notag: Submitting job #4 ...
[2017-04-21 16:44:36,069] [  DEBUG] pSort.notag: Successful jobs: ALL
[2017-04-21 16:44:36,069] [   INFO] pSort.notag: Done (time: 00:00:01,066).
[2017-04-21 16:44:36,070] [   DONE] Total time: 00:00:01,066
```

Then you will see your sorted files in `/home/user/tests/workdir/PyPPL.pSort.notag.2BNAjwU1/output/`:  
`test1.sorted  test2.sorted  test3.sorted  test4.sorted  test5.sorted`

## Using a different interpreter:
```python
pPlot = proc()
pPlot.input   = "infile:file"
pPlot.output  = "outfile:file:{{infile.fn}}.png"
pPlot.lang    = "Rscript"
# use the output of pSort as input
pPlot.depends = pSort
pPlot.script  = """
data <- read.table ("{{infile}}")
H    <- hclust(dist(data))
png (figure = “{{outfile}}”)
plot(H)
dev.off()
"""
```

## Using a different runner:
```python
pPlot = proc()
pPlot.input   = "infile:file"
pPlot.output  = "outfile:file:{{infile.fn}}.png"
pPlot.lang    = "Rscript"
pPlot.runner  = "sge"
# run 5 jobs at the same time
pPlot.forks   = 5
pPlot.depends = pSort
pPlot.script  = """
data <- read.table ("{{infile}}")
H    <- hclust(dist(data))
png (figure = “{{outfile}}”)
plot(H)
dev.off()
"""
pyppl({
	"proc": {
		"sgeRunner": {
			"sge_q" : "1-day"
		}
	}
}).starts(pPlot).run()
```

## Draw the pipeline chart
`pyppl` can generate the graph in [DOT language][14]. 
```python
ppl = pyppl()
p1 = proc("A")
p2 = proc("B")
p3 = proc("C")
p4 = proc("D")
p5 = proc("E")
p6 = proc("F")
p7 = proc("G")
p8 = proc("H")
p9 = proc("I")
p1.script = "echo 1"
p1.input  = {"input": channel.create(['a'])}
p8.input  = {"input": channel.create(['a'])}
p9.input  = {"input": channel.create(['a'])}
p2.input  = "input"
p3.input  = "input"
p4.input  = "input"
p5.input  = "input"
p6.input  = "input"
p7.input  = "input"
p1.output = "{{input}}" 
p2.script = "echo 1"
p2.output = "{{input}}" 
p3.script = "echo 1"
p3.output = "{{input}}" 
p4.script = "echo 1"
p4.output = "{{input}}" 
p5.script = "echo 1"
p5.output = "{{input}}" 
p6.script = "echo 1"
p6.output = "{{input}}" 
p7.script = "echo 1"
p7.output = "{{input}}" 
p8.script = "echo 1"
p8.output = "{{input}}" 
p9.script = "echo 1"
p9.output = "{{input}}" 
"""
			   1A         8H
			/      \      /
		 2B           3C
			\      /
			  4D(e)       9I
			/      \      /
		 5E          6F(e)
			\      /
			  7G(e)
"""
p2.depends = p1
p3.depends = [p1, p8]
p4.depends = [p2, p3]
p4.exportdir  = "./"
p5.depends = p4
p6.depends = [p4, p9]
p6.exportdir  = "./"
p7.depends = [p5, p6]
p7.exportdir  = "./"
ppl.starts(p1, p8, p9)
print ppl.dot() # save it in pyppl.dot
```
`pyppl.dot`:
```dot
digraph PyPPL {
	"p1.A" -> "p2.B"
	"p1.A" -> "p3.C"
	"p8.H" -> "p3.C"
	"p2.B" -> "p4.D"
	"p3.C" -> "p4.D"
	"p4.D" -> "p5.E"
	"p4.D" -> "p6.F"
	"p9.I" -> "p6.F"
	"p5.E" -> "p7.G"
	"p6.F" -> "p7.G"
	"p6.F" [shape=box, style=filled, color="#f0f998", fontcolor=red]
	"p1.A" [shape=box, style=filled, color="#c9fcb3"]
	"p8.H" [shape=box, style=filled, color="#c9fcb3"]
	"p9.I" [shape=box, style=filled, color="#c9fcb3"]
	"p7.G" [shape=box, style=filled, color="#fcc9b3" fontcolor=red]
	"p4.D" [shape=box, style=filled, color="#f0f998", fontcolor=red]
}
```
You can use different [dot renderers][17] to render and visualize it.

![PyPPL chart][18]

[1]: https://pwwang.gitbooks.io/pyppl/
[2]: https://pwwang.gitbooks.io/pyppl/api.html
[3]: https://github.com/pwwang/pyppl/
[4]: https://pwwang.gitbooks.io/pyppl/specify-input-and-output-of-a-process.html#specify-input-of-a-process
[5]: https://pwwang.gitbooks.io/pyppl/export-output-files.html
[6]: https://pwwang.gitbooks.io/pyppl/caching.html
[7]: https://pwwang.gitbooks.io/pyppl/placeholders.html
[8]: https://pwwang.gitbooks.io/pyppl/channels.html
[9]: https://pwwang.gitbooks.io/pyppl/runners.html
[10]: https://pwwang.gitbooks.io/pyppl/runners.html#define-your-own-runner
[11]: https://pwwang.gitbooks.io/pyppl/set-other-properties-of-a-process.html#use-callback-to-modify-the-process-pcallback
[12]: https://pwwang.gitbooks.io/pyppl/set-other-properties-of-a-process.html#error-handling-perrhowperrntry
[13]: https://pwwang.gitbooks.io/pyppl/configure-a-pipeline.html#use-a-configuration-file
[14]: https://en.wikipedia.org/wiki/DOT_(graph_description_language)
[15]: https://pwwang.gitbooks.io/pyppl/draw-flowchart-of-a-pipeline.html
[16]: https://pwwang.gitbooks.io/pyppl/aggregations.html
[17]: https://en.wikipedia.org/wiki/DOT_(graph_description_language)#Layout_programs
[18]: https://github.com/pwwang/pyppl/raw/master/docs/pyppl.png
