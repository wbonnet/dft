#!/usr/bin/env python2

# TODO : check arguments for valid date
# TODO : check arguments for emtpy strings

#
# The contents of this file are subject to the COMMON DEVELOPMENT AND
# DISTRIBUTION LICENSE (CDDL) (the "License"); you may not use this
# file except in compliance with the License.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 3 or later (the "GPL"),
# in which case the provisions of the GPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL, and not to allow others to
# use your version of this file under the terms of the CDDL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the CDDL, or the GPL.
#
# Copyright 2010 OpenCSW (http://www.opencsw.org).  All rights reserved.
# Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet wbonnet@opencsw.org
#
#

# Import all the needed modules
import sys
import string
import re
import os
import shutil
import subprocess
import pysvn
import MySQLdb
import datetime
import ConfigParser
import logging

from urllib2 import Request, urlopen, URLError
from optparse import OptionParser

# ---------------------------------------------------------------------------------------------------------------------
#
#
class InvalidSourceDirectoryContentException(Exception):
    """Exception raised when a method is called on the Abstract command class
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, message):
        self.message = message


# ---------------------------------------------------------------------------------------------------------------------
#
#
class AbstractCommandMethodCallException(Exception):
    """Exception raised when a method is called on the Abstract command class
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, message):
        self.message = message

# ---------------------------------------------------------------------------------------------------------------------
#
#
class SvnClientException(Exception):
    """Exception raised when an error occur while using svnClient
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, message):
        self.message = message

# ---------------------------------------------------------------------------------------------------------------------
#
#
class DatabaseConnectionException(Exception):
    """Exception raised when an error occur while connecting to the database
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, message):
        self.message = message

# ---------------------------------------------------------------------------------------------------------------------
#
#
class DuplicatePackageException(Exception):
    """Exception raised when an error occur while connecting to the database
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, message):
        self.message = message


# ---------------------------------------------------------------------------------------------------------------------
#
#
class UpstreamUrlRetrievalFailedException(Exception):
    """Exception raised when an unsuported protocol is specified in the upstream url
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, url):
        self.url  = url

# ---------------------------------------------------------------------------------------------------------------------
#
#
class NoUpstreamVersionFoundException(Exception):
    """Exception raised when searching the upstream page content does not match the regexp
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, url, regexp):
        self.url     = url
        self.regexp  = regexp


# ---------------------------------------------------------------------------------------------------------------------
#
#
class MissingArgumentException(Exception):
    """Exception raised when a command line argument is missing
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------------------------------------------------
#
#
class InvalidArgumentException(Exception):
    """Exception raised when a command line argument is invalid. For instance an invalid version or date
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------
#
#
class CommandLineParser(object):
    """This class is used to parse command line. It process only options. Command verb is parsed by the main procedure
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        # Create the parser object
        self.optionParser = OptionParser()

        # Add options to parser
        self.optionParser.add_option("--verbose",     help="Activate verbose mode", action="store_true", dest="verbose")
        self.optionParser.add_option("--current-version",    help="Current package version", action="store", dest="current_version")
        self.optionParser.add_option("--target-location",    help="Target location. This is the directory in which the branch will be created (parent of the branch directory). Default value is ../branches", action="store", dest="target_location")
        self.optionParser.add_option("--regexp",            help="Version matching regular expression", action="store", dest="regexp")
        self.optionParser.add_option("--source-directory",  help="Source directory (place from where the build is copied). Default value is current directory", action="store", dest="source_directory")
        self.optionParser.add_option("--target-version",    help="Package target version", action="store", dest="target_version")
        self.optionParser.add_option("--upstream-url",      help="Upstream version page url", action="store", dest="upstream_url")

        # Option used for reporting uwatch result
        self.optionParser.add_option("--uwatch-error",      help="Flag used to report a uwatch error", action="store_true", dest="uwatch_error")
        self.optionParser.add_option("--uwatch-output",     help="Flag used to report the uwatch output", action="store", dest="uwatch_output")
        self.optionParser.add_option("--uwatch-deactivated",help="Flag used to report a uwatch error", action="store_true", dest="uwatch_deactivated")
        self.optionParser.add_option("--uwatch-pkg-root",   help="Defines the uwatch package root working directory", action="store", dest="uwatch_pkg_root")

        # Option used for storing version information in the database
        self.optionParser.add_option("--gar-distfiles",     help="Gar version of the package", action="store", dest="gar_distfiles")
        self.optionParser.add_option("--gar-version",       help="Gar version of the package", action="store", dest="gar_version")
        self.optionParser.add_option("--upstream-version",  help="Upstream version of the package", action="store", dest="upstream_version")
        self.optionParser.add_option("--gar-path",          help="Relative path in svn repository", action="store", dest="gar_path")
        self.optionParser.add_option("--catalog-name",      help="Catalog name", action="store", dest="catalog_name")
        self.optionParser.add_option("--package-name",      help="Package name", action="store", dest="package_name")
        self.optionParser.add_option("--execution-date",    help="Check date to be stored in the database", action="store", dest="execution_date")

        self.optionParser.add_option("--database-schema",   help="Defines the database to use in the connection string", action="store", dest="database_schema")
        self.optionParser.add_option("--database-host",     help="Defines the database host to use in the connection string", action="store", dest="database_host")
        self.optionParser.add_option("--database-user",     help="Defines the database user to use in the connection string", action="store", dest="database_user")
        self.optionParser.add_option("--database-password", help="Defines the database password to use in the connection string", action="store", dest="database_password")

    # -----------------------------------------------------------------------------------------------------------------

    def parse(self):
        (self.options, self.args) = self.optionParser.parse_args()
        return self.options, self.args

# ---------------------------------------------------------------------------------------------------------------------
#
#
class UwatchConfiguration(object):
    """This handles parameters retrieved either from command line or configuration file.
    """

    # -----------------------------------------------------------------------------------------------------------------

    def initialize(self, args):
        """Initialize configuration object. If configurations contains files reference, values from the files are
        read and copied into this object. Next attempts to retrieve files stored information will read values from
        this object.
        """

        # Default is no file parser
        fileParser = None

        # Test if the .uwatchrc file exists
        if os.path.isfile( os.path.expanduser("~/.uwatchrc") ):
            # Yes thus load values from the configuration file before processing args parameter
            # This allow to override from the command line some values stored in the config file
            fileParser = ConfigParser.ConfigParser()
            fileParser.read( [os.path.expanduser("~/.uwatchrc") ] )

            # Read the database schema from the config file            
            try:
                self._database_schema = fileParser.get("main", "database-schema")
            except Config.NoOptionError:
                self._database_schema = None

            # Read the database hostname from the config file            
            try:
                self._database_host = fileParser.get("main", "database-host")
            except Config.NoOptionError:
                self._database_host = None

            # Read the database user from the config file            
            try:
                self._database_user = fileParser.get("main", "database-user")
            except Config.NoOptionError:
                self._database_user = None

            # Read the database password from the config file            
            try:
                self._database_password = fileParser.get("main", "database-password")
            except Config.NoOptionError:
                self._database_password = None

            # Read the package root working dir from the config file            
            try:
                self._uwatch_pkg_root = fileParser.get("main", "uwatch-pkg-root")
            except Config.NoOptionError:
                self._uwatch_pkg_root = None

        # This member variable is a flag which defines the status of the verbose mode (True : activated)
        logging_level = logging.INFO
        if args.verbose is not None:
            self._verbose = args.verbose
            logging_level = logging.DEBUG
        else:
            self._verbose = False
        logging.basicConfig(level=logging_level)

        # This member variable defines the value of the version of the package
        # Current revision is not passed as a separated argument. It is part of the opencsw version number. 
        # Package version are defined as follow : version[,REV=revision]*
        if args.current_version != None:
    
            # Parse the version string
            ver = re.split(r"(?P<version>.*),REV=(?P<revision>.*)", args.current_version)

            # Test if this is a match
            if ver == None:
                # No, thus raise an exception
                msg = "Unable to parse %(version)s as a valid package version" % { 'version' : args.current_version }
                raise InvalidArgumentException(msg)
            else:      
                # If the length of array is one, the no revision is provided
                if len(ver) == 1:
                    self._current_version = ver[0]
                    self._current_revision = ""
                else:
                    self._current_version = ver[1]
                    self._current_revision = ver[2]

                    # Attempt to split again the string. If len is greater than 1
                    # Then there are at least two rev string => raise exception
                    ver = re.split(r"(?P<version>.*),REV=(?P<revision>.*)", self._current_version)
                    if len(ver) > 1:
                        msg = "Unable to parse %(version)s as a valid package version. There are more than one revision string" % { 'version' : args.current_version }
                        raise InvalidArgumentException(msg)

        # This member variable defines the value of the regexp used to match the upstream web page
        if args.regexp != None:
            self._regexp = args.regexp

        # This member variable defines the url of the upstream web page used to check for new version
        if args.upstream_url != None:
            self._upstream_url = args.upstream_url

        # This member variable defines the target version of the package during upgrade
        if args.target_version != None:
            self._target_version = args.target_version

        # This member variable defines the target directory of the package during upgrade. This is the location of the new branch
        if args.target_location != None:
            self._target_location = args.target_location

        # This member variable defines the source directory of the package during upgrade. This is the location of the trunk (most of the time)
        if args.source_directory != None:
            self._source_directory = args.source_directory

        # This member variable defines the version of the package stored in the gar build description
        if args.gar_version != None:
            self._gar_version = args.gar_version

        # This member variable defines the upstream version of package
        if args.upstream_version != None:
            self._upstream_version = args.upstream_version

        # This member variable defines the relative path in the svn repository
        if args.gar_path != None:
            self._gar_path = args.gar_path

        # This member variable defines the catalog name of the package
        if args.catalog_name != None:
            self._catalog_name = args.catalog_name

        # This member variable defines the package name
        if args.package_name != None:
            self._package_name = args.package_name

        # This member variable defines the date of the execution (it is useful to be able to define a date to construct history of versions)
        if args.execution_date != None:
            self._execution_date = args.execution_date

        # This member variable defines the database to use in the connection string
        if args.database_schema != None:
            self._database_schema = args.database_schema

        # This member variable defines the database host to use in the connection string
        if args.database_host != None:
            self._database_host = args.database_host
	
        # This member variable defines the database user to use in the connection string
        if args.database_user != None:
            self._database_user = args.database_user

        # This member variable defines the database password to use in the connection string
        if args.database_password != None:
            self._database_password = args.database_password

        # This member variable defines the uwatch activation status
        if args.uwatch_deactivated != None:
            self._uwatch_deactivated = True
        else:
            self._uwatch_deactivated = False

        # This member variable defines the uwatch last report result
        if args.uwatch_error != None:
            self._uwatch_error = True
        else:
            self._uwatch_error = False

        # This member variable defines the uwatch last report result
        if args.uwatch_pkg_root != None:
            self._uwatch_pkg_root = args.uwatch_pkg_root

        # This member variable defines the uwatch last report output
        if args.uwatch_output != None:
            self._uwatch_output = args.uwatch_output

        # This member variable defines the gar distfiles
        if args.gar_distfiles != None:
            self._gar_distfiles = args.gar_distfiles

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self):

        # Initialize all variables to None. Even if useless, the purpose of this to keep up to date the list
        self._verbose = None
        self._uwatch_deactivated = False
        self._uwatch_error = False
        self._uwatch_pkg_root = None
        self._current_version = None
        self._current_revision = ""
        self._regexp = None
        self._upstream_url = None
        self._target_version = None
        self._source_directory = "."
        self._target_location = "../branches"
        self._gar_version = None
        self._upstream_version = None
        self._gar_path = None
        self._catalog_name = None
        self._package_name = None
        self._execution_date = None
        self._database_schema = None
        self._database_host = None
        self._database_user = None
        self._database_password = None
        self._gar_distfiles = None
        self._uwatch_output = None

    # -----------------------------------------------------------------------------------------------------------------

    def getCurrentVersion(self):
        return self._current_version

    # -----------------------------------------------------------------------------------------------------------------

    def getCurrentRevision(self):
        return self._current_revision

    # -----------------------------------------------------------------------------------------------------------------

    def getRegexp(self):
        # In case the regexp is not define, we try to guess it using the distfile
        if (self._regexp == None) & (self._gar_distfiles != None):
            # Instanciate a regexp generator
            urg = UwatchRegexGenerator()

            # Retrieve the regexp list
            auto_regex_list = urg.GenerateRegex(self._catalog_name, self._gar_distfiles)

            # Use the first item as current regexp
            self._regexp = auto_regex_list[0]

        return self._regexp

    # -----------------------------------------------------------------------------------------------------------------

    def getUpstreamURL(self):
        return self._upstream_url

    # -----------------------------------------------------------------------------------------------------------------

    def getVerbose(self):
        return self._verbose

    # -----------------------------------------------------------------------------------------------------------------

    def getSourceDirectory(self):
        return self._source_directory

    # -----------------------------------------------------------------------------------------------------------------

    def getTargetLocation(self):
        return self._target_location

    # -----------------------------------------------------------------------------------------------------------------

    def getTargetVersion(self):
        return self._target_version

    # -----------------------------------------------------------------------------------------------------------------

    def getGarVersion(self):
        return self._gar_version

    # -----------------------------------------------------------------------------------------------------------------

    def getUpstreamVersion(self):
        return self._upstream_version

    # -----------------------------------------------------------------------------------------------------------------

    def getGarPath(self):
        if self.getUwatchPkgRoot():
            return self._gar_path.replace(self.getUwatchPkgRoot(), "")
        else:
            return self._gar_path

    # -----------------------------------------------------------------------------------------------------------------

    def getCatalogName(self):
        return self._catalog_name

    # -----------------------------------------------------------------------------------------------------------------

    def getPackageName(self):
        return self._package_name

    # -----------------------------------------------------------------------------------------------------------------

    def getExecutionDate(self):
        return self._execution_date

    # -----------------------------------------------------------------------------------------------------------------

    def getDatabaseSchema(self):
        return self._database_schema

    # -----------------------------------------------------------------------------------------------------------------

    def getDatabaseHost(self):
        return self._database_host

    # -----------------------------------------------------------------------------------------------------------------

    def getDatabaseUser(self):
        return self._database_user

    # -----------------------------------------------------------------------------------------------------------------

    def getDatabasePassword(self):
        return self._database_password

    # -----------------------------------------------------------------------------------------------------------------

    def getUwatchError(self):
        return self._uwatch_error

    # -----------------------------------------------------------------------------------------------------------------

    def getUwatchDeactivated(self):
        return self._uwatch_deactivated

    # -----------------------------------------------------------------------------------------------------------------

    def getUwatchPkgRoot(self):
        return self._uwatch_pkg_root

    # -----------------------------------------------------------------------------------------------------------------

    def getGarDistfiles(self):
        return self._gar_distfiles

    # -----------------------------------------------------------------------------------------------------------------

    def getUwatchOutput(self):
        return self._uwatch_output


# ---------------------------------------------------------------------------------------------------------------------
#
#
class AbstractCommand(object):
    """Base class for command implementation. You should create a derived class per command to implemente.
       A "command" represent a concrete action verb given to the program.
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, name):
        self.config = UwatchConfiguration()
        self.name = name

    # -----------------------------------------------------------------------------------------------------------------

    def getName(self):
        return self.name

    # -----------------------------------------------------------------------------------------------------------------

    def execute(self, opts, arguments):
        print "Internal error : Abstract command method called\n"
        raise AbstractCommandMethodCallException("execute")

# ---------------------------------------------------------------------------------------------------------------------
#
#
class UpstreamWatchCommand(AbstractCommand):
    """UpstreamWatch command. This command is the base class used for all upstream watch commands. It provides argument checking
    url content retrieving, version comparison, etc.
    """

    # -----------------------------------------------------------------------------------------------------------------

    def UrlContentRetrieve(self, url):

        try:
            # Request the upstream URL and open it
            req = Request(url)
            response = urlopen(req)

        except URLError, e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server during retrieval of : ' + url
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request during retrieval of : ' + url
                print 'Error code: ', e.code

            # Check for response code value. We should get a 200
            raise UpstreamUrlRetrievalFailedException(url)

        else:
            # everything is fine, retrieve the page content
            return response.read()


    # -----------------------------------------------------------------------------------------------------------------

    def CompareVersionAndGetNewest(self, version1, version2):

        # we consider the version to be composed of several elements separated by '.' ',' '-' or '_'
        # an elements can be a string or a number
        # at each step we extract the next elements of the two version strings and compare them

        if isinstance(version1, str) == False:
            print "Version is not a string. Please check environnement variable UFILES_REGEX"
            print version1

        if isinstance(version2, str) == False:
            print "Version is not a string. Please check environnement variable UFILES_REGEX"
            print version2

        # Retrieve the tokens from both version. Use . - , and _ as splitters
    	splittingRegExp = "(?:[\.,_-])"
        tokens1 = re.split(splittingRegExp, version1)
        tokens2 = re.split(splittingRegExp, version2)

        # Iterates the toeksn of version 1, pop tokens one by one and compare to the token at same
        # in version 2
        while len(tokens1) > 0:
            # If we still have tokens in version 1 and version 2 is empty, then version 1 is newer
            # TODO: may have to deal with beta suffixes...
            if len(tokens2) == 0:
                return version1

            # Convert both elements to integer
            # TODO : handles chars in versions
            elem1 = tokens1.pop(0)
            elem2 = tokens2.pop(0)

            # If both elements are integer, then convert to int before comparison, otherwise compare strings
            try:
                elem1 = int(elem1)
                elem2 = int(elem2)
            except:
                elem1 = str(elem1)
                elem2 = str(elem2)
                # print "Doing string comparison"

            # print "Comparing %(elem1)s and %(elem2)s" % { 'elem1' : elem1 , 'elem2' : elem2 }

            # if elements are the same continue the loop
            if elem1 == elem2:
                continue

            # Test if elem1 is more recent
            if elem1 > elem2:
                # print "%(elem1)s > %(elem2)s" % { 'elem1' : elem1 , 'elem2' : elem2 }
                return version1
            else:
                # print "%(elem1)s < %(elem2)s" % { 'elem1' : elem1 , 'elem2' : elem2 }
                return version2

        return version1

# ---------------------------------------------------------------------------------------------------------------------
#
#
class CheckUpstreamCommand(UpstreamWatchCommand):
    """CheckUpstream command. This command retrieve the upstream web page and search for a new version. Version check is
    done by matching the regexp from the makefile on the page. Results are sorted to get the highest available and
    compared to current version
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, name):
        super(CheckUpstreamCommand, self).__init__(name)

    # -----------------------------------------------------------------------------------------------------------------

    def checkArgument(self):

        # Variable used to flag that we have a missing argument
        argsValid = True

        # Current version is mandatory
        if self.config.getCurrentVersion() == None:
            print "Error : Current version is not defined. Please use --current-version flag, or --help to display help"
            argsValid = False

        # Regexp is mandatory
        if self.config.getRegexp() == None:
            print "Error : Regexp is not defined. Please use --regexp flag, or --help to display help"
            argsValid = False

        # UpstreamURL is mandatory
        if self.config.getUpstreamURL() == None:
            print "Error : Upstream version page URL is not defined. Please use --upstream-url flag, or --help to display help"
            argsValid = False

        # If arguments are not valid raise an exception
        if argsValid == False:
            raise MissingArgumentException("Some mandatory arguments are missing. Unable to continue.")

    # -----------------------------------------------------------------------------------------------------------------

    def execute(self, opts, args):

        try:

            # Initialize configuration
            self.config.initialize(opts)

            # Need a way to check that all options needed are available
            self.checkArgument()

            # Call the method in charge of retrieving upstream content
            content = self.UrlContentRetrieve(self.config.getUpstreamURL())

            # Search the strings matching the regexp passed through command line arguments
            p = re.compile(self.config.getRegexp())
            matches = p.findall(content)
            logging.info("CheckUpstreamCommand.execute(): matches=%s",
                         repr(matches))

            # Check if we have found some results
            if len(matches) == 0:
                raise NoUpstreamVersionFoundException(self.config.getUpstreamURL(), self.config.getRegexp())
            else:
                newestVersion = self.config.getCurrentVersion()
                while len(matches) > 0:
                    newestVersion = self.CompareVersionAndGetNewest(newestVersion, matches.pop(0))

            # At the end of the processing loop, test if we have a newer version avail, if yes output it
            if newestVersion <>  self.config.getCurrentVersion():
                print newestVersion

            # Exit after processing, eveythin gis ok, return true to the command processor
            return True

        except MissingArgumentException, (instance):

            # Display a cool error message :)
            print instance.parameter

            # Exits through exception handling, thus return false to the command processor
            return False

        except UpstreamUrlRetrievalFailedException, (instance):

            # Exits through exception handling, thus return false to the command processor
            return False

        except NoUpstreamVersionFoundException, (instance):

            # Exits through exception handling, thus return false to the command processor
            return False


# ---------------------------------------------------------------------------------------------------------------------
#
#
class GetUpstreamLatestVersionCommand(UpstreamWatchCommand):
    """GetUpstreamLatestVersion command. This command retrieve the upstream web page and search for the latest version.
    Version check is done by matching the regexp from the makefile on the page. Results are sorted to get the newest version
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, name):
        super(GetUpstreamLatestVersionCommand, self).__init__(name)

    # -----------------------------------------------------------------------------------------------------------------

    def checkArgument(self):

        # Variable used to flag that we have a missing argument
        argsValid = True

        # Regexp is mandatory
        if self.config.getRegexp() == None:
            print "Error : Regexp is not defined. Please use --regexp flag, or --help to display help"
            argsValid = False

        # UpstreamURL is mandatory
        if self.config.getUpstreamURL() == None:
            print "Error : Upstream version page URL is not defined. Please use --upstream-url flag, or --help to display help"
            argsValid = False

        # If arguments are not valid raise an exception
        if argsValid == False:
            raise MissingArgumentException("Some mandatory arguments are missing. Unable to continue.")

    # -----------------------------------------------------------------------------------------------------------------

    def execute(self, opts, args):

        try:

            # Initialize configuration
            self.config.initialize(opts)

            # Need a way to check that all options needed are available
            self.checkArgument()
    
            # Call the method in charge of retrieving upstream content
            content = self.UrlContentRetrieve(self.config.getUpstreamURL())

            # Search the strings matching the regexp passed through command line arguments
            regex_str = self.config.getRegexp()
            p = re.compile(regex_str)
            matches = p.findall(content)
            logging.info("GetUpstreamLatestVersionCommand.execute(): "
                         "regex=%s",
                         repr(regex_str))
            logging.info("GetUpstreamLatestVersionCommand.execute(): "
                         "matches=%s",
                         repr(matches))

            # Check if we have found some results
            if len(matches) == 0:
                raise NoUpstreamVersionFoundException(self.config.getUpstreamURL(), self.config.getRegexp())
            else:
                newestVersion = matches.pop(0)                
                while len(matches) > 0:
                    newestVersion = self.CompareVersionAndGetNewest(newestVersion, matches.pop(0))

            # At the end of the processing loop, we print the version
            print newestVersion

            # Exit after processing, eveythin gis ok, return true to the command processor
            return True

        except MissingArgumentException, (instance):

            # Display a cool error message :)
            print instance.parameter

            # Exits through exception handling, thus return false to the command processor
            return False

        except UpstreamUrlRetrievalFailedException, (instance):

            # Exits through exception handling, thus return false to the command processor
            return False

        except NoUpstreamVersionFoundException, (instance):

            # Exits through exception handling, thus return false to the command processor
            return False

# ---------------------------------------------------------------------------------------------------------------------
#
#
class GetUpstreamVersionListCommand(UpstreamWatchCommand):
    """GetUpstreamVersionList command. This command retrieve the upstream web page and search for all the versions.
    Version check is done by matching the regexp from the makefile on the page. 
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, name):
        super(GetUpstreamVersionListCommand, self).__init__(name)

    # -----------------------------------------------------------------------------------------------------------------

    def checkArgument(self):

        # Variable used to flag that we have a missing argument
        argsValid = True

        # Regexp is mandatory
        if self.config.getRegexp() == None:
            print "Error : Regexp is not defined. Please use --regexp flag, or --help to display help"
            argsValid = False

        # UpstreamURL is mandatory
        if self.config.getUpstreamURL() == None:
            print "Error : Upstream version page URL is not defined. Please use --upstream-url flag, or --help to display help"
            argsValid = False

        # If arguments are not valid raise an exception
        if argsValid == False:
            raise MissingArgumentException("Some mandatory arguments are missing. Unable to continue.")

    # -----------------------------------------------------------------------------------------------------------------

    def compareAndSortVersion(self, a, b):
        """This function is a wrapper to the comparison function. CompareVersionAndGetNewest returns the string containing
        the newest version of the two arguments. Since sort method used on list need to have an integer return value, this
        wrapper do the call to CompareVersionAndGetNewest and returns an int
        """
    
        if self.CompareVersionAndGetNewest(a,b) == a:
            return 1
        else:
            return -1

    # -----------------------------------------------------------------------------------------------------------------

    def execute(self, opts, args):

        try:

            # Initialize configuration
            self.config.initialize(opts)

            # Need a way to check that all options needed are available
            self.checkArgument()

            # Call the method in charge of retrieving upstream content
            content = self.UrlContentRetrieve(self.config.getUpstreamURL())

            listURL = self.config.getUpstreamURL().split(' ')

            # Search the strings matching the regexp passed through command line arguments
            p = re.compile(self.config.getRegexp())
            matches = p.findall(content)

            # Check if we have found some results
            if len(matches) == 0:
                raise NoUpstreamVersionFoundException(self.config.getUpstreamURL(), self.config.getRegexp())
            else:
                # Remove duplicated entries
                myList = []
                for version in matches:
                    myList.append(version)

                l = list(set(myList))
                l.sort(self.compareAndSortVersion)

                # Print every version in the list
                for version in l:
                    print version

            # Exit after processing, eveythin gis ok, return true to the command processor
            return True

        except MissingArgumentException, (instance):

            # Display a cool error message :)
            print instance.parameter

            # Exits through exception handling, thus return false to the command processor
            return False

        except UpstreamUrlRetrievalFailedException, (instance):

            # Exits through exception handling, thus return false to the command processor
            return False

        except NoUpstreamVersionFoundException, (instance):

            # Exits through exception handling, thus return false to the command processor
            return False


# ---------------------------------------------------------------------------------------------------------------------
#
#
class UpgradeToVersionCommand(UpstreamWatchCommand):
    """UpgradeToVersion command. This command upgrade the build description from a version to another.
    Current files in trunk are copied to a new branch. Branch is named accord to the following pattern :
    PKG/branches/upgrade_from_CURRENTVERSION_to_DESTVERSION. After copy, version in the Makefile is modified.
    An optional argument can be passed to commit after branch creation.
    
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, name):
        super(UpgradeToVersionCommand, self).__init__(name)

    # -----------------------------------------------------------------------------------------------------------------

    def checkArgument(self):

        # Variable used to flag that we have a missing argument
        argsValid = True

        # FromVersion is mandatory
        if self.config.getCurrentVersion() == None:
            print "Error : Current version is not defined. Please use --current-version flag, or --help to display help"
            argsValid = False

        # ToVersion is mandatory
        if self.config.getTargetVersion() == None:
            print "Error : Target version is not defined. Please use --target-version flag, or --help to display help"
            argsValid = False

        # ToVersion is mandatory
        if self.config.getTargetLocation() == None:
            print "Error : Target directory is not defined. Please use --target-location flag, or --help to display help"
            argsValid = False

        # If arguments are not valid raise an exception
        if argsValid == False:
            raise MissingArgumentException("Some mandatory arguments are missing. Unable to continue.")

    # -----------------------------------------------------------------------------------------------------------------

    def checkWorkingDirectory(self):
        """ This method checks that the command is executed from a valid working directory. A valid working directory
            is a directory in which we find a package buildDescription that means a Makefile and a gar directory or symlink
        """

        # Check that the Makefile exist
        if os.path.isfile(self.config.getSourceDirectory() + "/Makefile") == False:
            # No it does not exist, thus generate an error message
            msg = "Error : there is no Makefile under %(src)s" % { "src" : os.path.abspath(self.config.getSourceDirectory()) }
    
            # Then raise an exception
            raise InvalidSourceDirectoryContentException(msg)

        # Check that the gar directory exists (can be a directory or symlink)
        if os.path.isdir(self.config.getSourceDirectory() + "/gar") == False:
            # No it does not exist, thus generate an error message
            msg = "Error : there is no gar directory under %(src)s" % { "src" : os.path.abspath(self.config.getSourceDirectory()) }
    
            # Then raise an exception
            raise InvalidSourceDirectoryContentException(msg)

    # -----------------------------------------------------------------------------------------------------------------

    def getGarRelativeTargetDirectory(self):
        """ This method return None if gar directory is an actual directory, or a relative path if gar is a symlink to 
            a real directory. In case of a symlink pointing to another symlink, we do not try to get the absolute path
            having one level of indirection is enough. 
            The target directory is a relative path. This path is adjusted to be consistent from the target directory. It
            has to be modified since it is basically a relative path from the source directory.            
        """

        # Get the newgar information
        garDir = self.config.getSourceDirectory() + "/gar"
        if os.path.islink(garDir):
            garTarget = os.path.relpath(os.path.abspath(os.readlink(garDir)), os.path.abspath(targetDir))
        else:
            garTarget = None
    
    # -----------------------------------------------------------------------------------------------------------------

    def getGarRelativeTargetDirectory(self):
        """ This method return None if gar directory is an actual directory, or a relative path if gar is a symlink to 
            a real directory. In case of a symlink pointing to another symlink, we do not try to get the absolute path
            having one level of indirection is enough. 
            The target directory is a relative path. This path is adjusted to be consistent from the target directory. It
            has to be modified since it is basically a relative path from the source directory.            
        """

        # Get the newgar information
        garDir = self.config.getSourceDirectory() + "/gar"
        if os.path.islink(garDir):
            garTarget = os.path.relpath(os.path.abspath(os.readlink(garDir)), os.path.abspath(self.getTargetDirectory()))
        else:
            garTarget = None

        return garTarget

    # -----------------------------------------------------------------------------------------------------------------

    def getTargetDirectory(self):
        """ This method return the target directory which is a computed value based on target location, current version
            and target version
        """

        return self.config.getTargetLocation() + "/upgrade_from_" + self.config.getCurrentVersion() + "_to_" + self.config.getTargetVersion()

    # -----------------------------------------------------------------------------------------------------------------

    def copySvnSourceToTarget(self, garRelativeTarget):
        """ This method copy sources from the working copy to the target in the same working copy. If garRelativeTarget is not 
            None, it means gar directory is a symlink. Then once copy is done it is deleted in the target directory and
            recreated to point to the new relative directory
        """

        try:
            # Create a new svn client
            svnClient = pysvn.Client()

            # Do the actual copy in the svn working copy
            svnClient.copy(os.path.abspath(self.config.getSourceDirectory()), self.getTargetDirectory())

            # Backup the current directory
            curDir = os.getcwd()

            # Change to target directory
            os.chdir(self.getTargetDirectory())

            # Test if gar relative path is defined
            if garRelativeTarget:
                # Test if gar directory is a symlink and 
                if os.path.islink("./gar"):
                    os.remove("./gar")
                    os.symlink(garRelativeTarget, "./gar")
                # No ... :( This a "should not happen error" since it was a symlink before the copy. Exit
                else:
                    print "Internal error : gar is not a symlink but garRelativeTarget is defined"
                    return False
            # No else but ... If gar relative path is not defined, we have copied a real directory. Nothing to do in this case

            # Restore the working directory
            os.chdir(curDir)

        # SVN client exception handling    
        except pysvn.ClientError , e:
            # Generate a cool error message
            msg = "SVN Client error : " + e.args[0] + "\n" + "Error occured when executing command svnClient.copy(%(src)s, %(dest)s)" \
                  % { 'src' : os.path.abspath(self.config.getSourceDirectory()), 'dest' : self.getTargetDirectory() }

            # Then raise the exception
            raise SvnClientException(msg)

    # -----------------------------------------------------------------------------------------------------------------

    def modifyVersion(self):
        """ This method modifies the version in the Makefile. It replaces current version by new version. 
            Version has to be defined on a single line strting by VERSION, having some spaces or tabs then 
            and egal sign = then some tabs or spaces and the version vaue to finish the line
        """

        # Backup the current directory
        curDir = os.getcwd()

        # Change to target directory
        os.chdir(self.getTargetDirectory())

        # Array storing the Makefile lines
        lines = []

        # Iterate each line in  the file                
        for line in open("./Makefile", 'r'):
            # Match the file line by line               
            m = re.match(r"\s*VERSION\s*=\s*(?P<version>.*)", line)

            # Test if this is a match
            if m == None:
                # No, thus output the current line without modifications
                lines.append(line)
            else:   
                # Yes it is a match, thus output the modified line
                lines.append("VERSION = " + self.config.getTargetVersion() + "\n")

        # Open the new Makefile for output
        f = open("./Makefile", 'w')

        # Iterates the array of lines and write each one to the Makefile 
        for element in lines:
            f.write(element)

        # Close the Makefile
        f.close()

        # Restore the working directory
        os.chdir(curDir)

    # -----------------------------------------------------------------------------------------------------------------

    def execute(self, opts, args):

        try:

            # Initialize configuration
            self.config.initialize(opts)

            # Need a way to check that all options needed are available
            self.checkArgument()

            # Check that the command is launched from a valid directory
            self.checkWorkingDirectory()

            # Generates the target directory
            self.getTargetDirectory()

            # Get the new gar information
            garRelativeTarget = self.getGarRelativeTargetDirectory()

            # Copy target directory to destination
            self.copySvnSourceToTarget(garRelativeTarget)

            # Modify the version inside the Makefile
            self.modifyVersion()

            # Exit after processing, eveythin gis ok, return true to the command processor
            return True

        # Handles exception that occurs when arguments are incorrect
        except MissingArgumentException, instance:

            # Display a cool error message :)
            print instance.parameter

            # Exits through exception handling, thus return false to the command processor
            return False

        # Handles SVN client exception
        except SvnClientException , e:
            
            # Display a cool error message :)
            print e.message

            # Exits through exception handling, thus return false to the command processor
            return False

        # Handles exceptions which might occur while checking source directory content
        except InvalidSourceDirectoryContentException , e:
            
            # Display a cool error message :)
            print e.message

            # Exits through exception handling, thus return false to the command processor
            return False

# ---------------------------------------------------------------------------------------------------------------------
#
#
class ReportPackageVersionCommand(UpstreamWatchCommand):
    """ReportPackageVersion command. This command report and store in the database the values of version and date passed 
    by arguments to upstream watch. Unique key is the composed by garpath and catalog name. It means the same package can
    lie into different path in the svn repository.
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, name):
        super(ReportPackageVersionCommand, self).__init__(name)
        self.conn = None

    # -----------------------------------------------------------------------------------------------------------------

    def openDatabaseConnection(self):
        """This method open a connection to the mysql database using value from the configuration parser. The result of 
        connect method is stored into a connection object
        """

        # Open the database connection
        try:
            self.conn = MySQLdb.connect(host   = self.config.getDatabaseHost(),
                                       passwd = self.config.getDatabasePassword(),
                                       db     = self.config.getDatabaseSchema(),
                                       user   = self.config.getDatabaseUser() )

        except MySQLdb.Error, e:
            msg = "Error %d: %s" % (e.args[0], e.args[1])
            raise DatabaseConnectionException(msg)

        # Check that the object we got in return if defiend
        if self.conn == None:
            # No, raise a DatabaseConnectionException
            msg = "Unable to connect to database using host = %(host)s, db = %(db)s, user = %(user)s, passwd = %(passwd)% " % { "host" : self.config.getDatabaseHost(), "passwd" : self.config.getDatabasePassword(), "db" : self.config.getDatabaseSchema(), "user" : self.config.getDatabaseUser() }
            raise DatabaseConnectionException(msg)

    # -----------------------------------------------------------------------------------------------------------------

    def closeDatabaseConnection(self):
        """This method close the connection opened by openDatabaseConnection. 
        """

        # Check that the connection object is valid
        if self.conn :
            # Yes, commit pending transactions
            self.conn.commit()

            # Close the connection
            self.conn.close()
        else:
            # No,  raise a DatabaseConnectionException
            msg = "Unable to disconnect from the database. Connection objet is not defined"
            raise DatabaseConnectionException(msg)

    # -----------------------------------------------------------------------------------------------------------------

    def updateVersionInDatabase(self):
        """This method updates the version in the database. First it checks for the package to update using a unique 
        key composed of gar svn path and catalog name. If not found the package is created, otherwise it is updated.
        In both case, if data are writtent to the database, entries in history table are created.
        """

        try:
            # Flag used to keep track of the fact we have created a new package. Used in some case to choose behavior
            isNewlyCreatedPackage = False
            
            # Check that the connection is defined
            if self.conn == None:
                # No,  raise a DatabaseConnectionException
                msg = "Unable to query the database. Connection objet is not defined"
                raise DatabaseConnectionException(msg)

            # Get a cursor object        
            cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

            # First retrieve the id_pkg and deletion flag from the database
            cursor.execute("select * from UWATCH_PKG_VERSION where PKG_CATALOGNAME = %s", (self.config.getCatalogName() ) )

            # if more than one row is found, then report an error
            if cursor.rowcount > 1:
                msg = self.config.getCatalogName()
                raise DuplicatePackageException(msg)

            # If rowcount = 0 then the package does not exist. It has to be inserted in the database
            if cursor.rowcount == 0:

                # Insert the package in the package version table
                cursor.execute("insert into UWATCH_PKG_VERSION (PKG_GAR_PATH, PKG_CATALOGNAME, PKG_NAME, PKG_GAR_VERSION, PKG_LAST_GAR_CHECK_DATE) \
                                values ( %s , %s , %s , %s , %s )" , (self.config.getGarPath(), self.config.getCatalogName(), \
                                self.config.getPackageName(), self.config.getGarVersion(), self.config.getExecutionDate() ) )

                # Flag that we have created a package
                isNewlyCreatedPackage = True

                # Output some more information if verbose mode is activated
                if self.config.getVerbose() == True:
                    print "Package %(pkg)s added to the database" % { 'pkg' : self.config.getCatalogName() }

                # Now the package is inserted. Retrieve the newly inserted package and update other versions
                cursor.execute("select * from UWATCH_PKG_VERSION where PKG_GAR_PATH = %s and PKG_CATALOGNAME = %s", \
                                (self.config.getGarPath(), self.config.getCatalogName() ) )

            # Retrieve package information
            pkg = cursor.fetchone()

            # Test if the deleted flag is set
            if pkg["PKG_IS_DELETED"] == 1:                
                # Yes thus package has to be undeleted
                cursor.execute("update UWATCH_PKG_VERSION set PKG_IS_DELETED = 0 where ID_PKG='%s'" , ( pkg["ID_PKG"] ) )

                # Output some more information if verbose mode is activated
                if self.config.getVerbose() == True:
                    print "Package %(pkg)s has been undeleted" % { 'pkg' : self.config.getCatalogName() }

            # Test if the package has just been created. If yes the history line for gar version has to be inserted 	 
            if isNewlyCreatedPackage: 	 
                cursor.execute("insert into UWATCH_VERSION_HISTORY ( ID_PKG , HIST_VERSION_TYPE , HIST_VERSION_VALUE , HIST_VERSION_DATE ) values ( %s, %s, %s, %s)" , ( pkg["ID_PKG"], "gar", self.config.getGarVersion() , self.config.getExecutionDate() ) )
                
            # In all cases (update or not) we update the last version check according to the argument
            cursor.execute("update UWATCH_PKG_VERSION set PKG_LAST_UPSTREAM_CHECK_DATE = %s , PKG_GAR_PATH = %s where ID_PKG= %s" , ( self.config.getExecutionDate(), self.config.getGarPath() , pkg["ID_PKG"] ) )

            # Test if uwatch deactivated flag is set
            if self.config.getUwatchDeactivated() == True:
                # Yes thus package has to be deactivated
                cursor.execute("update UWATCH_PKG_VERSION set PKG_UWATCH_ACTIVATED='0' where ID_PKG= %s" , ( pkg["ID_PKG"] ) )
                if self.config.getVerbose() == True:
                    print "%(pkg) uWatch is deactivated, updating database"  % { 'pkg' : self.config.getCatalogName() }
            else:
                cursor.execute("update UWATCH_PKG_VERSION set PKG_UWATCH_ACTIVATED='1' where ID_PKG= %s" , ( pkg["ID_PKG"] ) )
                # Change execution status only if activated
                if self.config.getUwatchError() == True:
                    # Yes thus package has to be updated
                    cursor.execute("update UWATCH_PKG_VERSION set PKG_LAST_UPSTREAM_CHECK_STATUS='0' where ID_PKG= %s" , ( pkg["ID_PKG"] ) )
                    if self.config.getVerbose() == True:
                        print "%(pkg)s uWatch reported an error, updating database"  % { 'pkg' : self.config.getCatalogName() }
                else:
                    cursor.execute("update UWATCH_PKG_VERSION set PKG_LAST_UPSTREAM_CHECK_STATUS='1' where ID_PKG= %s" , ( pkg["ID_PKG"] ) )
                    if self.config.getVerbose() == True:
                        print "%(pkg)s uWatch successfully ran, updating database"  % { 'pkg' : self.config.getCatalogName() }

                # Test if upstream version is passed
                if self.config.getUpstreamVersion():
                    # In all cases (update or not) we update the last version check according to the argument
                    cursor.execute("update UWATCH_PKG_VERSION set PKG_LAST_UPSTREAM_CHECK_DATE = %s , PKG_GAR_PATH = %s where ID_PKG= %s" , ( self.config.getExecutionDate(), self.config.getGarPath() , pkg["ID_PKG"] ) )

                    # Yes, compare current upstream version from commandline and database
                    if self.config.getUpstreamVersion() != pkg["PKG_UPSTREAM_VERSION"]:                
                        # Yes thus package has to be updated
                        cursor.execute("update UWATCH_PKG_VERSION set PKG_UPSTREAM_VERSION = %s  where ID_PKG= %s" , ( self.config.getUpstreamVersion(), pkg["ID_PKG"] ) )
                        cursor.execute("insert into UWATCH_VERSION_HISTORY ( ID_PKG , HIST_VERSION_TYPE , HIST_VERSION_VALUE , HIST_VERSION_DATE ) \
                                        values ( %s, %s, %s, %s)" , ( pkg["ID_PKG"], "upstream", self.config.getUpstreamVersion() , self.config.getExecutionDate() ) )

                        # Output some more information if verbose mode is activated
                        if self.config.getVerbose() == True:
                            print "Upgrading %(pkg)s upstream version from %(current)s to %(next)s" % { 'pkg' : self.config.getCatalogName(), \
                                    'next' : self.config.getUpstreamVersion() , 'current' : pkg["PKG_UPSTREAM_VERSION"] }
                    else:
                        # Output some more information if verbose mode is activated
                        if self.config.getVerbose() == True:
                            print "%(pkg) GAR version is up to date (%(current)s)" % { 'pkg' : self.config.getCatalogName(), 'current' : self.config.getUpstreamVersion() }         
    
            # Test if gar version is passed (it is mandatory to have a value in database)
            if self.config.getGarVersion():
                # In all cases (update or not) we update the last version check according to the argument
                cursor.execute("update UWATCH_PKG_VERSION set PKG_LAST_GAR_CHECK_DATE = %s  where ID_PKG= %s" , ( self.config.getExecutionDate(), pkg["ID_PKG"] ) )

                # Yes, compare current gar version from commandline and database
                if self.config.getGarVersion() != pkg["PKG_GAR_VERSION"]:                
                    # Yes thus package has to be updated
                    cursor.execute("update UWATCH_PKG_VERSION set PKG_GAR_VERSION = %s  where ID_PKG= %s" , ( self.config.getGarVersion(), pkg["ID_PKG"] ) )
                    cursor.execute("insert into UWATCH_VERSION_HISTORY ( ID_PKG , HIST_VERSION_TYPE , HIST_VERSION_VALUE , HIST_VERSION_DATE ) \
                                    values ( %s, %s, %s, %s)" , ( pkg["ID_PKG"], "gar", self.config.getGarVersion() , self.config.getExecutionDate() ) )

                    # Output some more information if verbose mode is activated
                    if self.config.getVerbose() == True:
                        print "Upgrading %(pkg)s gar version from %(current)s to %(next)s" % { 'pkg' : self.config.getCatalogName(), \
                                'next' : self.config.getGarVersion() , 'current' : pkg["PKG_GAR_VERSION"] }

            # Before closing the connection, there is a last thing to do... storing uwatch configuration into the database

            # Yes, compare current gar version from commandline and database
            cursor.execute("update UWATCH_PKG_VERSION set PKG_GAR_DISTFILES = %s, PKG_UFILES_REGEXP = %s, PKG_UPSTREAM_MASTER_SITES = %s, PKG_UWATCH_LAST_OUTPUT = %s where ID_PKG= %s" , ( self.config.getGarDistfiles(), self.config.getRegexp(), self.config.getUpstreamURL(), self.config.getUwatchOutput(), pkg["ID_PKG"] ) )

            # Close the cursor on the database
            cursor.close()

        except MySQLdb.Error, e:
            msg = "Error %d: %s" % (e.args[0], e.args[1])
            raise DatabaseConnectionException(msg)


    # -----------------------------------------------------------------------------------------------------------------

    def checkArgument(self):

        # Variable used to flag that we have a missing argument
        argsValid = True

        # Gar path is mandatory
        if self.config.getGarPath() == None:
            print "Error : Gar path is not defined. Please use --gar-path flag, or --help to display help"
            argsValid = False

        # Gar distfiles is mandatory
        if self.config.getGarDistfiles() == None:
            print "Error : Gar distfiles is not defined. Please use --gar-distfiles flag, or --help to display help"
            argsValid = False

        # Gar distfiles is mandatory
        if self.config.getUwatchOutput() == None:
            print "Error : uWatch output is not defined. Please use --uwatch-output flag, or --help to display help"
            argsValid = False

        # Catalog name is mandatory
        if self.config.getCatalogName() == None:
            print "Error : Catalog name is not defined. Please use --catalog-name flag, or --help to display help"
            argsValid = False

        # Package name is mandatory
        if self.config.getPackageName() == None:
            print "Error : Package name is not defined. Please use --package-name flag, or --help to display help"
            argsValid = False

        # Execution date is mandatory
        if self.config.getExecutionDate() == None:
            print "Error : Execution date is not defined. Please use --execution-date flag, or --help to display help"
            argsValid = False

        # Gar version is mandatory, other version are optional. Gar the version is the only mandatory in the database
        # It has to be passed in argument in case the package does not exist yet
        if self.config.getGarVersion() == None:
            print "Error : Gar version is not defined. Please use --gar-version flag, or --help to display help"
            argsValid = False

        # Database schema is mandatory
        if self.config.getDatabaseSchema() == None:
            print "Error : Database schema is not defined. Please define the value in the ~/.uwatchrc file, use --database-schema flag, or --help to display help"
            argsValid = False

        # Database host is mandatory
        if self.config.getDatabaseHost() == None:
            print "Error : Database host is not defined. Please define the value in the ~/.uwatchrc file, use --database-host flag, or --help to display help"
            argsValid = False

        # Database user is mandatory
        if self.config.getDatabaseUser() == None:
            print "Error : Database user is not defined. Please define the value in the ~/.uwatchrc file, use --database-user flag, or --help to display help"
            argsValid = False

        # Database password is mandatory
        if self.config.getDatabasePassword() == None:
            print "Error : Database password is not defined. Please define the value in the ~/.uwatchrc file, use --database-password flag, or --help to display help"
            argsValid = False

        # Regexp is mandatory
        if self.config.getRegexp() == None:
            print "Error : Regexp is not defined. Please use --regexp flag, or --help to display help"
            argsValid = False

        # UpstreamURL is mandatory
        if self.config.getUpstreamURL() == None:
            print "Error : Upstream version page URL is not defined. Please use --upstream-url flag, or --help to display help"
            argsValid = False
    
        # If arguments are not valid raise an exception
        if argsValid == False:
            raise MissingArgumentException("Some mandatory arguments are missing. Unable to continue.")

    # -----------------------------------------------------------------------------------------------------------------

    def execute(self, opts, args):

        try:

            # Initialize configuration
            self.config.initialize(opts)

            # Need a way to check that all options needed are available
            self.checkArgument()

            # Connection to the database
            self.openDatabaseConnection()

            # Connection to the database
            self.updateVersionInDatabase()

            # Connection to the database
            self.closeDatabaseConnection()

            # Exit after processing, eveythin gis ok, return true to the command processor
            return True

        except MissingArgumentException, (instance):

            # Display a cool error message :)
            print instance.parameter

            # Exits through exception handling, thus return false to the command processor
            return False

        except InvalidArgumentException, (instance):

            # Display a cool error message :)
            print instance.parameter

            # Exits through exception handling, thus return false to the command processor
            return False

        except DatabaseConnectionException, (instance):

            # Display a cool error message :)
            print instance.message

            # Exits through exception handling, thus return false to the command processor
            return False

# ---------------------------------------------------------------------------------------------------------------------
#
#
class CommandProcessor(object):
    """This class receive commands from the main loop and forward call to concrete command.
    """

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """Initialize the objects in charge of concrete command processing. Each object instance are stored in a
        map using a key which is the action verb used on the command line.
        """

        # Defines the map storing the concrete commands
        self.commandArray = {}

        # Creates all the concrete commands
        cmd = CheckUpstreamCommand("check-upstream")
        self.commandArray[cmd.getName()] = cmd

        cmd = GetUpstreamLatestVersionCommand("get-upstream-latest-version")
        self.commandArray[cmd.getName()] = cmd

        cmd = GetUpstreamVersionListCommand("get-upstream-version-list")
        self.commandArray[cmd.getName()] = cmd

        cmd = UpgradeToVersionCommand("upgrade-to-version")
        self.commandArray[cmd.getName()] = cmd

        cmd = ReportPackageVersionCommand("update-package-version-database")
        self.commandArray[cmd.getName()] = cmd

    # -----------------------------------------------------------------------------------------------------------------

    def execute(self, opts, arguments):
        """This method checks that an action is supplied and call the action handler
        """

        # Check that an action verb is supplied. If none an error is returned
        if len(arguments) == 0:
            print "Error : no action supplied"
            return 1

        # The first element in the arguments array is the action verb. Retrieve the command
        # using action verb as key
        if self.commandArray.has_key(arguments[0]):
            res =  self.commandArray[arguments[0]].execute(opts, arguments)
            if res:
                return 0
            else:
                return 1
        else:
            print "Error : %(action)s action is not supported" % { 'action' : arguments[0] }
            return 2


class UwatchRegexGenerator(object):
  """Guesses uwatch regexes based on distfiles."""

  WS_RE = re.compile(r'\s+')
  DIGIT_RE = re.compile(r'\d+')
  DIGIT_REMOVAL_RE = re.compile(r'\d+(?:\.\d+)*[a-z]?')
  DIGIT_MATCH_MAKE_RE_1 = r'(\d+(?:[\.-]\d+)*[a-z]?)'
  DIGIT_MATCH_MAKE_RE_2 = r'(\d+(?:[\.-]\d+)*)'
  DIGIT_MATCH_MAKE_RE_3 = r'(\d+(?:\.\d+)*[a-z]?)'
  DIGIT_MATCH_MAKE_RE_4 = r'(\d+(?:\.\d+)*)'
  ARCHIVE_RE = re.compile(r"\.(?:tar(?:\.(?:gz|bz2))|tgz)?$")

  def _ChooseDistfile(self, file_list):
    # First heuristic: files with numbers are distfiles
    for f in file_list:
      if self.ARCHIVE_RE.search(f):
        return f
    for f in file_list:
      if self.DIGIT_RE.search(f):
        return f

  def _SeparateSoftwareName(self, catalogname, filename):
    """Separate the software name from the rest of the file name.

    Software name sometimes contains digits, which we don't want to
    include in the regexes.
    """
    # The first approach is to split by '-'
    assert filename
    parts = filename.split('-')
    parts_c_or_v = map(
        lambda x: self._CanBeSoftwareName(x, catalogname),
        parts)
    if False in parts_c_or_v:
      i = parts_c_or_v.index(False)
    else:
      i = 1
    return '-'.join(parts[:i]), '-' + '-'.join(parts[i:])

  def _SeparateArchiveName(self, filename):
    if self.ARCHIVE_RE.search(filename):
      first_part = self.ARCHIVE_RE.split(filename)[0]
      archive_part = ''.join(self.ARCHIVE_RE.findall(filename))
      return first_part, archive_part
    return filename, ''

  def _CanBeSoftwareName(self, s, catalogname):
    if s == catalogname:
      return True
    if re.match(self.DIGIT_MATCH_MAKE_RE_1, s):
      return False
    # This is stupid.  But let's wait for a real world counterexample.
    return True

  def GenerateRegex(self, catalogname, distnames):
    dist_list = self.WS_RE.split(distnames)
    dist_file = self._ChooseDistfile(dist_list)
    if not dist_file:
      return []
    dist_file = dist_file.strip()
    softwarename, rest_of_filename = self._SeparateSoftwareName(
        catalogname, dist_file)
    rest_of_filename, archive_part = self._SeparateArchiveName(rest_of_filename)
    no_numbers = self.DIGIT_REMOVAL_RE.split(rest_of_filename)
    regex_list = [
      softwarename + self.DIGIT_MATCH_MAKE_RE_1.join(no_numbers) + archive_part,
      softwarename + self.DIGIT_MATCH_MAKE_RE_2.join(no_numbers) + archive_part,
      softwarename + self.DIGIT_MATCH_MAKE_RE_3.join(no_numbers) + archive_part,
      softwarename + self.DIGIT_MATCH_MAKE_RE_4.join(no_numbers) + archive_part,
    ]
    return regex_list



# ---------------------------------------------------------------------------------------------------------------------
#
# Fonction principale
#
def main():
    """Program main loop. Process args and call concrete command action.
    """

    # Create the command processor object
    commandProcessor = CommandProcessor()

    # Parse command line arguments
    cliParser  = CommandLineParser()

    # Call the command line parser
    (opts, args) = cliParser.parse()

    # Call the execute method on the command processor. This method is in charge to find the concrete command
    return commandProcessor.execute(opts, args)

# Exit with main return code
if __name__ == '__main__':
    res = main()
    sys.exit(res)

