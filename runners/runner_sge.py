from runner_local import runner_local
from time import sleep
from subprocess import Popen, list2cmdline 
import os, shlex


class runner_sge (runner_local):

	def __init__ (self, script, config = {}):
		super(runner_sge, self).__init__(script, config)
		# construct an sge script
		sgefile = os.path.realpath(script + '.sge')
		
		sgesrc  = [
			'#!/usr/bin/env bash',
			''
			'#$ -N ' + self._config('id', os.path.basename (script)) + '.' + self._config('tag', 'notag'),
			'#$ -o ' + self.outfile,
			'#$ -e ' + self.errfile,
			'#$ -cwd'
		]

		for k, v in self._config('sgeRunner', {}).iteritems():
			if k == 'N': continue
			src = '#$ -' + k.strip()
			if v != True: # {'notify': True} ==> -notify
				src += ' ' + v
			sgesrc.append(src)
		sgesrc.append ('')
		sgesrc.append ('trap "status=\$?; echo \$status > %s; exit \$status" 1 2 3 6 7 8 9 10 11 12 15 16 17 EXIT' % self.rcfile)
		sgesrc.append ('')
		sgesrc.append (list2cmdline(self.script))
		
		with open (sgefile, 'w') as f:
			f.write ('\n'.join(sgesrc) + '\n')
		
		self.script = ['qsub', sgefile]

	def run (self):

		if os.path.exists(self.rcfile):
			os.remove(self.rcfile)

		try:
			p  = Popen (self.script)
			rc = p.wait()
			if rc != 0:
				raise RuntimeError ('Failed to submit job %s' % self._config('N', os.basename(self.rcfile)[:-3]))
			
			while self.rc() == -99:
				sleep (5)
		except Exception as ex:
			with open (self.rcfile, 'w') as f:
				f.write('1')
			import traceback
			traceback.print_exc()
			raise Exception(str(ex))
			
		self.ntry += 1
		if not self.isValid() and self._config('errorhow') == 'retry' and self.ntry < self._config('errorntry'):
			self._config('logger', logging).info ('[RETRY %s] %s.%s: %s' % (self.ntry, self._config('id'), self._config('tag'), self._config('workdir')))
			self.run()
		

