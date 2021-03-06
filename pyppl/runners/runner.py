"""
The base runner class
"""
import sys
from os import devnull
from multiprocessing import Lock
from subprocess import Popen, list2cmdline

from ..helpers import utils

lock = Lock()

class runner (object):
	"""
	The base runner class
	"""

	def __init__ (self, job):
		"""
		Constructor
		@params:
			`job`:    The job object
			`config`: The properties of the process
		"""
		self.job       = job
		self.script    = utils.chmodX(self.job.script)
		self.cmd2run   = list2cmdline (self.script)
		self.ntry      = 0
		self.p         = None

	def submit (self):
		"""
		Try to submit the job use Popen
		"""
		self.job.reset()
		try:
			self.job.proc.log ('Submitting job #%-3s ...' % self.job.index)
			self.p = Popen (self.script, stderr=open(self.job.errfile, "w"), stdout=open(self.job.outfile, "w"), close_fds=True)
		except Exception as ex:
			self.job.proc.log ('Failed to run job #%s: %s' % (self.job.index, str(ex)), 'error')
			open (self.job.errfile, 'a').write(str(ex))
			self.job.rc(self.job.FAILED_RC)
			self.p = None
	
	def getpid (self):
		"""
		Get the job id
		"""
		self.job.id (str(self.p.pid))

	def wait(self):
		"""
		Wait for the job to finish
		"""
		if self.job.rc() == self.job.FAILED_RC: 
			return

		if self.p:
			self.getpid()
			retcode = self.p.wait()
			if self.job.proc.echo:
				lock.acquire()
				sys.stderr.write (open(self.job.errfile).read())
				sys.stdout.write (open(self.job.outfile).read())
				lock.release()
			self.job.rc(retcode)

	def finish (self):
		"""
		Do some cleanup work when jobs finish
		"""
		self.job.done ()
		self.p = None
		self.retry ()

	def retry (self):
		"""
		Retry to submit and run the job if failed
		"""
		self.ntry += 1
		if self.job.succeed() or self.job.proc.errorhow != 'retry' or self.ntry > self.job.proc.errorntry:
			return

		self.job.proc.log ("Retrying job #%s ... (%s)" % (self.job.index, self.ntry))

		self.submit()
		self.wait()
		self.finish()

	def isRunning (self):
		"""
		Try to tell whether the job is still running.
		@returns:
			`True` if yes, otherwise `False`
		"""
		jobid = self.job.id()
		if not jobid:
			return False
		return Popen (['kill', '-s', '0', jobid], stderr=open(devnull, 'w'), stdout=open(devnull, 'w')).wait() == 0
