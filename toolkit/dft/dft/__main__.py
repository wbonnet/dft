#
# The contents of this file are subject to the Apache 2.0 license you may not
# use this file except in compliance with the License.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
#
# Copyright 2016 DFT project (http://www.debianfirmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
# Debian Firmware Toolkit is the new name of Linux Firmware From Scratch
# Copyright 2014 LFFS project (http://www.linuxfirmwarefromscratch.org).
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

import cli
import sys

def main():
	"""
	Main entry point for the script. Create a parser, process the command line, 
	and run it
	"""

	# Create the Cli object in charge of parsing command line, then select and
	# call the run method
	parser = cli.Cli()

	# If a command has been passed on the cli, then forward it, otherwise use
	# default --help value to ensure to display help
	if (len(sys.argv) >= 2):
		parser.parse(sys.argv[1])
	else:
		args = ["__help__", "-h"]
		parser.parse(args)

	# Once parsed call the runner method
	return parser.run()
	

# That's all folks. All the processing has bee done in the run
#
# Check this is code is called from the __main__
#
if __name__ == '__main__':
  sys.exit(main())	
