import sys, unittest, os
rootdir = os.path.dirname (
	os.path.dirname (
		os.path.realpath (__file__)
	)
)
if rootdir not in sys.path:
	sys.path.append(rootdir)
from helpers.channel import channel

class TestChannel (unittest.TestCase):

	def testCreate (self):
		c1 = channel.create([("abc", "def"), ("ghi", "opq")])
		c2 = channel([("abc", "def"), ("ghi", "opq")])

		self.assertTrue (isinstance(c1, channel))
		self.assertTrue (isinstance(c2, channel))

		c3 = channel()
		self.assertEqual (c3, [])

	def testFromPath (self):
		c = channel.fromPath (os.path.join(rootdir, 'test', '*.py'))
		self.assertEqual (sorted(c), sorted([
			os.path.join (rootdir, 'test', 'runner.unittest.py'),
			os.path.join (rootdir, 'test', 'pyppl.unittest.py'),
			os.path.join (rootdir, 'test', 'proc.unittest.py'),
			os.path.join (rootdir, 'test', 'strtpl.unittest.py'),
			os.path.join (rootdir, 'test', 'channel.unittest.py'),
		]))
	
	def testFromPairs (self):
		files = [
			os.path.join (rootdir, 'test', 'a_1.txt'),
			os.path.join (rootdir, 'test', 'a_2.txt'),
			os.path.join (rootdir, 'test', 'b_1.txt'),
			os.path.join (rootdir, 'test', 'b_2.txt'),
			os.path.join (rootdir, 'test', 'c_1.txt'),
			os.path.join (rootdir, 'test', 'c_2.txt'),
		]
		for file in files:
			open(file, 'w').close()

		c = channel.fromPairs ( os.path.join(rootdir, 'test', '*_*.txt') )
	
		self.assertEqual (sorted(c), sorted([
			(os.path.join (rootdir, 'test', 'a_1.txt'), os.path.join (rootdir, 'test', 'a_2.txt')),
			(os.path.join (rootdir, 'test', 'b_1.txt'), os.path.join (rootdir, 'test', 'b_2.txt')),
			(os.path.join (rootdir, 'test', 'c_1.txt'), os.path.join (rootdir, 'test', 'c_2.txt')),

		]))

		for file in files:
			os.remove(file)
	
	def testFromArgv (self):
		sys.argv = ["0", "1", "2"]
		c = channel.fromArgv()
		self.assertEqual (c, ["1", "2"])

	def testFromChannels (self):
		c1 = channel.create([("abc", "def"), ("ghi", "opq")])
		c2 = channel([("abc", "def"), ("ghi", "opq")])
		c3 = channel.fromChannels (c1, c2)
		self.assertEqual (c3, [("abc", "def", "abc", "def"), ("ghi", "opq", "ghi", "opq")])

	def testTuplize (self):
		data = [
			(1, (1,)),
			((1, ), (1,)),
			("abc", ("abc", )),
			(("abc", ), ("abc", )),
		]
		for d in data:
			self.assertEqual (channel._tuplize(d[0]), d[1])

	def testMap (self):
		c1 = channel.create([("abc", "def"), ("ghi", "opq")])
		c2 = channel([("abc", "def"), ("ghi", "opq")])
		c1 = c1.map (lambda x: (x[0] + '.c1', x[1]))
		c2 = c2.map (lambda x: len(x[0]) + len(x[1]))
		self.assertEqual (c1, [("abc.c1", "def"), ("ghi.c1", "opq")])
		self.assertEqual (c2, [6, 6])

	def testFilter (self):
		c = channel.create([1,2,3,4,5]).filter(lambda x: x<3)
		self.assertEqual (c, [1, 2])
	
	def testReduce (self):
		c = channel.create([("abc", "def"), ("ghi", "opq")]).reduce(lambda x,y: (x[0]+y[0], x[1]+y[1]))
		self.assertEqual (c, ['abcghi', 'defopq'])

	def testMerge(self):
		c1 = channel.create ([("abc", "def"), ("ghi", "opq")])
		c2 = channel.create (["abc", "def", "ghi", "opq"])
		self.assertRaises (Exception, c1.merge, c2)

		c3 = channel.create(["1", '2', '3', '4'])	
		c4 = c2.mergeCopy(c3)
		self.assertEqual (c4, [("abc", "1"), ("def", '2'), ("ghi", '3'), ("opq", '4')])

		c5 = [5,6,7,8]
		self.assertEqual (c2.mergeCopy(c3,c5), [("abc", "1", 5), ("def", '2', 6), ("ghi", '3', 7), ("opq", '4', 8)])
		self.assertEqual (c4.mergeCopy(c5), [("abc", "1", 5), ("def", '2', 6), ("ghi", '3', 7), ("opq", '4', 8)])
		c6 = channel.create()
		c6.merge (c2, c3 ,c5)
		self.assertEqual (c6, [("abc", "1", 5), ("def", '2', 6), ("ghi", '3', 7), ("opq", '4', 8)])
		
		c = channel.create()
		cd = {"c":c}
		c.merge (c2, c3, c5)
		self.assertEqual (cd['c'], [("abc", "1", 5), ("def", '2', 6), ("ghi", '3', 7), ("opq", '4', 8)])
		self.assertEqual (c, [("abc", "1", 5), ("def", '2', 6), ("ghi", '3', 7), ("opq", '4', 8)])

		cc = channel()
		ccs = channel([(1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)])
		for cs in ccs.split():
			cc.merge(cs)
		self.assertEqual(cc, ccs)
	
	def testSplit(self):
		c2 = channel.create (["abc", "def", "ghi", "opq"])
		c3 = channel.create(["1", '2', '3', '4'])	
		c4 = channel()
		c4.merge(c2, c3)
		self.assertEqual (c4, [("abc", "1"), ("def", '2'), ("ghi", '3'), ("opq", '4')])

		c5 = [5,6,7,8]
		self.assertEqual (c4.mergeCopy(c5), [("abc", "1", 5), ("def", '2', 6), ("ghi", '3', 7), ("opq", '4', 8)])
		c4.merge(c5)
		self.assertEqual (c4, [("abc", "1", 5), ("def", '2', 6), ("ghi", '3', 7), ("opq", '4', 8)])

		c6,c7,c8 = c4.split()
		self.assertEqual (c6, c2)
		self.assertEqual (c7, c3)
		self.assertEqual (c8, c5)
		c8, c9, c10 = c2.mergeCopy(c3, c5).split()
		self.assertEqual (c8, c2)
		self.assertEqual (c9, c3)
		self.assertEqual (c10, c5)

	def testLengthAndWidth (self):
		c2 = channel.create (["abc", "def", "ghi", "opq"])
		c3 = channel.create(["1", '2', '3', '4'])
		c4 = c2.mergeCopy(c3)

		self.assertEqual (c2.width(), 1)
		self.assertEqual (c3.width(), 1)
		self.assertEqual (c4.width(), 2)
		self.assertEqual (c2.length(), 4)
		self.assertEqual (c3.length(), 4)
		self.assertEqual (c4.length(), 4)



if __name__ == '__main__':
	unittest.main()