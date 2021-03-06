import copy
from os import devnull
from subprocess import Popen
from re import search

from .runner_queue import runner_queue


class runner_sge (runner_queue):
	"""
	The sge runner
	"""
	
	def __init__ (self, job):
		"""
		Constructor
		@params:
			`job`:    The job object
			`config`: The properties of the process
		"""
		super(runner_sge, self).__init__(job)

		# construct an sge script
		sgefile = self.job.script + '.sge'
		# get suffix
		suffix  = job.proc._suffix()
		sgesrc  = ['#!/usr/bin/env bash']
		self.jobname = '%s.%s.%s.%s' % (
			self.job.proc.id,
			self.job.proc.tag,
			suffix,
			self.job.index
		)

		conf = {}
		if hasattr(self.job.proc, 'sgeRunner'):
			conf = copy.copy (self.job.proc.sgeRunner)

		if not conf.has_key ('sge.N'):
			sgesrc.append('#$ -N %s' % self.jobname) 
		else:
			self.jobname = conf['sge.N']
			sgesrc.append('#$ -N %s' % self.jobname)
			del conf['sge.N']
		
		if conf.has_key('sge.q'):
			sgesrc.append('#$ -q %s' % conf['sge.q'])
			del conf['sge.q']
			
		if conf.has_key('sge.j'):
			sgesrc.append('#$ -j %s' % conf['sge.j'])
			del conf['sge.j']
		
		if conf.has_key('sge.o'):
			sgesrc.append('#$ -o %s' % conf['sge.o'])
			del conf['sge.o']
		else:
			sgesrc.append('#$ -o %s' % self.job.outfile)
			
		if conf.has_key('sge.e'):
			sgesrc.append('#$ -e %s' % conf['sge.e'])
			del conf['sge.e']
		else:
			sgesrc.append('#$ -e %s' % self.job.errfile)
			
		sgesrc.append('#$ -cwd')
		
		if conf.has_key('sge.M'):
			sgesrc.append('#$ -M %s' % conf['sge.M'])
			del conf['sge.M']
		
		if conf.has_key('sge.m'):
			sgesrc.append('#$ -m %s' % conf['sge.m'])
			del conf['sge.m']
		
		for k in sorted(conf.keys()):
			if not k.startswith ('sge.'): continue
			v = conf[k]
			k = k[4:].strip()
			src = '#$ -' + k
			if v != True: # {'notify': True} ==> -notify
				src += ' ' + str(v)
			sgesrc.append(src)

		sgesrc.append ('')
		sgesrc.append ('trap "status=\\$?; echo \\$status > %s; exit \\$status" 1 2 3 6 7 8 9 10 11 12 15 16 17 EXIT' % self.job.rcfile)
		
		if conf.has_key('preScript'):
			sgesrc.append (conf['preScript'])

		sgesrc.append ('')
		sgesrc.append (self.cmd2run)

		if conf.has_key('postScript'):
			sgesrc.append (conf['postScript'])
		
		open (sgefile, 'w').write ('\n'.join(sgesrc) + '\n')
		
		self.script = ['qsub', sgefile]

	def getpid (self):
		# Your job 6556149 ("pSort.notag.3omQ6NdZ.0") has been submitted
		m = search (r"\s(\d+)\s", open(self.job.outfile).read())
		if not m:
			return
		self.job.id (m.group(1))

	def isRunning (self):
		"""
		Tell whether the job is still running
		"""
		jobid = self.job.id ()
		if not jobid:
			return False
		return Popen (['qstat', '-j', jobid], stdout=open(devnull, 'w'), stderr=open(devnull, 'w')).wait() == 0

