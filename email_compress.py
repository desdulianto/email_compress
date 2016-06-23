#!/usr/bin/env python

import os
import signal
import sys
from os.path import join
import subprocess
import gzip
import shutil

for root, dirs, files in os.walk('.'):
	loc = os.path.abspath(root)
	lockpid = open('/tmp/lockpid', 'wt')
	returnval = subprocess.call(['/usr/lib/dovecot/maildirlock', loc, '15'], stdout=lockpid)

	if returnval != 0:
		print 'Cannot lock directory %s. exit' % loc
		lockpid.close()
		continue

	lockpid.close()
	lockpid = int(open('/tmp/lockpid', 'rt').read())

	for f in files:
		name = join(root, f)
		if 'S=' not in name:
			continue
		p = subprocess.Popen(['file', '-i', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		if 'message/rfc822' in out:
			print 'processing %s' % name
			#print name.strip()
			tmpname = '/tmp/' + os.path.basename(name) + '.gz'
			with open(name, 'rb') as f_in, gzip.open(tmpname, 'wb') as f_out:
				shutil.copyfileobj(f_in, f_out)
			if not os.path.isfile(tmpname):
				print 'compressed file %s not found!' % tmpname
				continue
			if os.path.isfile(name):
				shutil.copystat(name, tmpname)
				shutil.copy2(tmpname, name)
				os.remove(tmpname)
			else:
				print '%s: not found!' % name
	# release lock
	os.kill(lockpid, signal.SIGTERM)
