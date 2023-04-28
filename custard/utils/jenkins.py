# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  jenkins.py
@Time    :  2022/5/30 1:35 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  Jenkins工具驱动
"""

import contextlib
import json
import logging
import operator
import os
import re
import socket
import sys
import time
import warnings
import xml.etree.ElementTree as ET
from urllib import parse
from urllib.parse import quote

import pkg_resources
import requests
import requests.exceptions as req_exc

from custard.utils.multi import MultiKeyDict

try:
    import requests_kerberos
except ImportError:
    requests_kerberos = None

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logging.getLogger(__name__).addHandler(NullHandler())

if sys.version_info < (2, 7, 0):
    warnings.warn("Support for python 2.6 is deprecated and will be removed.")

LAUNCHER_SSH = "hudson.plugins.sshslaves.SSHLauncher"
LAUNCHER_COMMAND = "hudson.slaves.CommandLauncher"
LAUNCHER_JNLP = "hudson.slaves.JNLPLauncher"
LAUNCHER_WINDOWS_SERVICE = "hudson.os.windows.ManagedWindowsServiceLauncher"
DEFAULT_HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# REST Endpoints
INFO = "api/json"
PLUGIN_INFO = "pluginManager/api/json?depth=%(depth)s"
CRUMB_URL = "crumbIssuer/api/json"
WHOAMI_URL = "me/api/json?depth=%(depth)s"
JOBS_QUERY = "?tree=%s"
JOBS_QUERY_TREE = "jobs[url,color,name,%s]"
JOB_INFO = "%(folder_url)sjob/%(short_name)s/api/json?depth=%(depth)s"
JOB_NAME = "%(folder_url)sjob/%(short_name)s/api/json?tree=name"
ALL_BUILDS = "%(folder_url)sjob/%(short_name)s/api/json?tree=allBuilds[number,url]"
Q_INFO = "queue/api/json?depth=0"
Q_ITEM = "queue/item/%(number)d/api/json?depth=%(depth)s"
CANCEL_QUEUE = "queue/cancelItem?id=%(id)s"
CREATE_JOB = "%(folder_url)screateItem?name=%(short_name)s"  # also post config.xml
CONFIG_JOB = "%(folder_url)sjob/%(short_name)s/config.xml"
DELETE_JOB = "%(folder_url)sjob/%(short_name)s/doDelete"
ENABLE_JOB = "%(folder_url)sjob/%(short_name)s/enable"
DISABLE_JOB = "%(folder_url)sjob/%(short_name)s/disable"
CHECK_JENKINSFILE_SYNTAX = "pipeline-model-converter/validateJenkinsfile"
SET_JOB_BUILD_NUMBER = "%(folder_url)sjob/%(short_name)s/nextbuildnumber/submit"
COPY_JOB = "%(from_folder_url)screateItem?name=%(to_short_name)s&mode=copy&from=%(from_short_name)s"
RENAME_JOB = "%(from_folder_url)sjob/%(from_short_name)s/doRename?newName=%(to_short_name)s"
BUILD_JOB = "%(folder_url)sjob/%(short_name)s/build"
STOP_BUILD = "%(folder_url)sjob/%(short_name)s/%(number)s/stop"
BUILD_WITH_PARAMS_JOB = "%(folder_url)sjob/%(short_name)s/buildWithParameters"
BUILD_INFO = "%(folder_url)sjob/%(short_name)s/%(number)d/api/json?depth=%(depth)s"
BUILD_CONSOLE_OUTPUT = "%(folder_url)sjob/%(short_name)s/%(number)d/consoleText"
BUILD_ENV_VARS = "%(folder_url)sjob/%(short_name)s/%(number)d/injectedEnvVars/api/json" + "?depth=%(depth)s"
BUILD_TEST_REPORT = "%(folder_url)sjob/%(short_name)s/%(number)d/testReport/api/json" + "?depth=%(depth)s"
DELETE_BUILD = "%(folder_url)sjob/%(short_name)s/%(number)s/doDelete"
WIPEOUT_JOB_WORKSPACE = "%(folder_url)sjob/%(short_name)s/doWipeOutWorkspace"
NODE_LIST = "computer/api/json?depth=%(depth)s"
CREATE_NODE = "computer/doCreateItem"
DELETE_NODE = "computer/%(name)s/doDelete"
NODE_INFO = "computer/%(name)s/api/json?depth=%(depth)s"
NODE_TYPE = "hudson.slaves.DumbSlave$DescriptorImpl"
TOGGLE_OFFLINE = "computer/%(name)s/toggleOffline?offlineMessage=%(msg)s"
CONFIG_NODE = "computer/%(name)s/config.xml"
VIEW_NAME = "%(folder_url)sview/%(short_name)s/api/json?tree=name"
VIEW_JOBS = "view/%(name)s/api/json?tree=jobs[url,color,name]"
CREATE_VIEW = "%(folder_url)screateView?name=%(short_name)s"
CONFIG_VIEW = "%(folder_url)sview/%(short_name)s/config.xml"
DELETE_VIEW = "%(folder_url)sview/%(short_name)s/doDelete"
SCRIPT_TEXT = "scriptText"
NODE_SCRIPT_TEXT = "computer/%(node)s/scriptText"
PROMOTION_NAME = "%(folder_url)sjob/%(short_name)s/promotion/process/%(name)s/api/json?tree=name"
PROMOTION_INFO = "%(folder_url)sjob/%(short_name)s/promotion/api/json?depth=%(depth)s"
DELETE_PROMOTION = "%(folder_url)sjob/%(short_name)s/promotion/process/%(name)s/doDelete"
CREATE_PROMOTION = "%(folder_url)sjob/%(short_name)s/promotion/createProcess?name=%(name)s"
CONFIG_PROMOTION = "%(folder_url)sjob/%(short_name)s/promotion/process/%(name)s/config.xml"
LIST_CREDENTIALS = (
    "%(folder_url)sjob/%(short_name)s/credentials/store/folder/" "domain/%(domain_name)s/api/json?tree=credentials[id]"
)
CREATE_CREDENTIAL = (
    "%(folder_url)sjob/%(short_name)s/credentials/store/folder/" "domain/%(domain_name)s/createCredentials"
)
CONFIG_CREDENTIAL = (
    "%(folder_url)sjob/%(short_name)s/credentials/store/folder/" "domain/%(domain_name)s/credential/%(name)s/config.xml"
)
CREDENTIAL_INFO = (
    "%(folder_url)sjob/%(short_name)s/credentials/store/folder/"
    "domain/%(domain_name)s/credential/%(name)s/api/json?depth=0"
)
QUIET_DOWN = "quietDown"


class JenkinsException(Exception):
    """General exception type for jenkins-API-related failures."""


class NotFoundException(JenkinsException):
    """A special exception to call out the case of receiving a 404."""


class EmptyResponseException(JenkinsException):
    """A special exception to call out the case receiving an empty response."""


class BadHTTPException(JenkinsException):
    """A special exception to call out the case of a broken HTTP response."""


class TimeoutException(JenkinsException):
    """A special exception to call out in the case of a socket timeout."""


class WrappedSession(requests.Session):
    """A wrapper for requests.Session to override 'verify' property, ignoring REQUESTS_CA_BUNDLE environment variable."""

    def mergeEnvSettings(self, url, proxies, stream, verify, *args, **kwargs):
        if self.verify is False:
            verify = False

        return super(WrappedSession, self).merge_environment_settings(url, proxies, stream, verify, *args, **kwargs)


class Plugin(dict):
    """Dictionary object containing plugin metadata."""

    def __init__(self, *args, **kwargs):
        """Populates dictionary using json object input.

        accepts same arguments as python `dict` class.
        """
        version = kwargs.pop("version", None)

        super(Plugin, self).__init__(*args, **kwargs)
        self["version"] = version

    def __setitem__(self, key, value):
        """Overrides default setter to ensure that the version key is always
        a PluginVersion class to abstract and simplify version comparisons
        """
        if key == "version":
            value = PluginVersion(value)
        super(Plugin, self).__setitem__(key, value)


class PluginVersion(str):
    """Class providing comparison capabilities for plugin versions."""

    _VERSION_RE = re.compile(r"(.*)-(?:SNAPSHOT|BETA)")

    def __init__(self, version):
        """Parse plugin version and store it for comparison."""

        self._version = version
        self.parsed_version = pkg_resources.parse_version(self.__convert_version(version))

    def __convert_version(self, version):
        return self._VERSION_RE.sub(r"\g<1>.preview", str(version))

    def __compare(self, op, version):
        return op(
            self.parsed_version,
            pkg_resources.parse_version(self.__convert_version(version)),
        )

    def __le__(self, version):
        return self.__compare(operator.le, version)

    def __lt__(self, version):
        return self.__compare(operator.lt, version)

    def __ge__(self, version):
        return self.__compare(operator.ge, version)

    def __gt__(self, version):
        return self.__compare(operator.gt, version)

    def __eq__(self, version):
        return self.__compare(operator.eq, version)

    def __ne__(self, version):
        return self.__compare(operator.ne, version)

    def __str__(self):
        return str(self._version)

    def __repr__(self):
        return str(self._version)


class Jenkins(object):
    timeoutWarningIssued = False

    def __init__(self, url, username=None, password=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """Create handle to Jenkins instance.

        All methods will raise :class:`JenkinsException` on failure.

        :param url: URL of Jenkins server, ``str``
        :param username: Server username, ``str``
        :param password: Server password, ``str``
        :param timeout: Server connection timeout in secs (default: not set), ``int``
        """
        if url[-1] == "/":
            self.server = url
        else:
            self.server = url + "/"

        self._auths = [("anonymous", None)]
        self._auth_resolved = False
        if username is not None and password is not None:
            self._auths[0] = (
                "basic",
                requests.auth.HTTPBasicAuth(username.encode("utf-8"), password.encode("utf-8")),
            )

        if requests_kerberos is not None:
            self._auths.append(("kerberos", requests_kerberos.HTTPKerberosAuth()))

        self.auth = None
        self.crumb = None
        self.timeout = timeout
        self._session = WrappedSession()

        extra_headers = os.environ.get("JENKINS_API_EXTRA_HEADERS", "")
        if extra_headers:
            logging.warning(
                "JENKINS_API_EXTRA_HEADERS adds these HTTP headers: %s",
                extra_headers.split("\n"),
            )
        for token in extra_headers.split("\n"):
            if ":" in token:
                header, value = token.split(":", 1)
                self._session.headers[header] = value.strip()

        if os.getenv("PYTHONHTTPSVERIFY", "1") == "0":
            logging.debug(
                "PYTHONHTTPSVERIFY=0 detected so we will "
                "disable requests library SSL verification to keep "
                "compatibility with older versions.",
            )
            requests.packages.urllib3.disable_warnings()
            self._session.verify = False

    def getEncodedParams(self, params):
        for k, v in params.items():
            if k in [
                "name",
                "msg",
                "short_name",
                "from_short_name",
                "to_short_name",
                "folder_url",
                "from_folder_url",
                "to_folder_url",
            ]:
                params[k] = quote(v.encode("utf8"))
        return params

    def buildUrl(self, format_spec, variables=None):
        url_path = format_spec % self.getEncodedParams(variables) if variables else format_spec

        return str(parse.urljoin(self.server, url_path))

    def maybeAddCrumb(self, req):
        # We don't know yet whether we need a crumb
        if self.crumb is None:
            try:
                response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(CRUMB_URL)), add_crumb=False)
                if not response:
                    raise EmptyResponseException("Empty response for crumb")
            except (NotFoundException, EmptyResponseException):
                self.crumb = False
            else:
                self.crumb = json.loads(response)
        if self.crumb:
            req.headers[self.crumb["crumbRequestField"]] = self.crumb["crumb"]

    def maybeAddAuth(self):
        if self._auth_resolved:
            return

        if len(self._auths) == 1:
            # If we only have one auth mechanism specified, just require it
            self._session.auth = self._auths[0][1]
        else:
            # Attempt the list of auth mechanisms and keep the first that works
            # otherwise default to the first one in the list (last popped).
            # This is a hack to allow the transparent use of kerberos to work
            # in future, we should require explicit request to use kerberos
            failures = []
            for name, auth in reversed(self._auths):
                try:
                    self.jenkinsOpen(
                        requests.Request("GET", self.buildUrl(INFO), auth=auth),
                        add_crumb=False,
                        resolve_auth=False,
                    )
                    self._session.auth = auth
                    break
                except TimeoutException:
                    raise
                except Exception as exc:
                    # assume authentication failure
                    failures.append("auth(%s) %s" % (name, exc))
                    continue
            else:
                raise JenkinsException("Unable to authenticate with any scheme:\n%s" % "\n".join(failures))

        self._auth_resolved = True
        self.auth = self._session.auth

    def addMissingBuilds(self, data):
        """Query Jenkins to get all builds of a job.

        The Jenkins API only fetches the first 100 builds, with no
        indicator that there are more to be fetched. This fetches more
        builds where necessary to get all builds of a given job.

        Much of this code borrowed from
        which is MIT licensed.
        """
        if not data.get("builds"):
            return data
        oldest_loaded_build_number = data["builds"][-1]["number"]
        first_build_number = oldest_loaded_build_number if not data["firstBuild"] else data["firstBuild"]["number"]
        all_builds_loaded = oldest_loaded_build_number == first_build_number
        if all_builds_loaded:
            return data
        folder_url, short_name = self.getJobFolder(data["fullName"])
        response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(ALL_BUILDS, locals())))
        if response:
            data["builds"] = json.loads(response)["allBuilds"]
        else:
            raise JenkinsException("Could not fetch all builds from job[%s]" % data["fullName"])
        return data

    def getJobInfo(self, name, depth=0, fetch_all_builds=False):
        """Get job information dictionary.

        :param name: Job name, ``str``
        :param depth: JSON depth, ``int``
        :param fetch_all_builds: If true, all builds will be retrieved
                                 from Jenkins. Otherwise, Jenkins will
                                 only return the most recent 100
                                 builds. This comes at the expense of
                                 an additional API call which may
                                 return significant amounts of
                                 data. ``bool``
        :returns: dictionary of job information
        """
        folder_url, short_name = self.getJobFolder(name)
        try:
            response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(JOB_INFO, locals())))
            if response:
                if fetch_all_builds:
                    return self.addMissingBuilds(json.loads(response))
                else:
                    return json.loads(response)
            else:
                raise JenkinsException("job[%s] does not exist" % name)
        except (req_exc.HTTPError, NotFoundException):
            raise JenkinsException("job[%s] does not exist" % name)
        except ValueError:
            raise JenkinsException("Could not parse JSON info for job[%s]" % name)

    def getJobInfoRegex(self, pattern, depth=0, folder_depth=0, folder_depth_per_request=10):
        """Get a list of jobs information that contain names which match the
           regex pattern.

        :param pattern: regex pattern, ``str``
        :param depth: JSON depth, ``int``
        :param folder_depth: folder level depth to search ``int``
        :param folder_depth_per_request: Number of levels to fetch at once,
            ``int``. See :func:`getAllJobs`.
        :returns: List of jobs info, ``list``
        """
        result = []
        jobs = self.getAllJobs(folder_depth=folder_depth, folder_depth_per_request=folder_depth_per_request)
        for job in jobs:
            if re.search(pattern, job["name"]):
                result.append(self.getJobInfo(job["name"], depth=depth))

        return result

    def getJobName(self, name):
        """Return the name of a job using the API.

        That is roughly an identity method which can be used to quickly verify
        a job exists or is accessible without causing too much stress on the
        server side.

        :param name: Job name, ``str``
        :returns: Name of job or None
        """
        folder_url, short_name = self.getJobFolder(name)
        try:
            response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(JOB_NAME, locals())))
        except NotFoundException:
            return None
        else:
            actual = json.loads(response)["name"]
            if actual != short_name:
                raise JenkinsException("Jenkins returned an unexpected job name %s " "(expected: %s)" % (actual, name))
            return actual

    def debugJobInfo(self, job_name):
        """Print out job info in more readable format."""
        for k, v in self.getJobInfo(job_name).items():
            print(k, v)

    def responseHandler(self, response):
        """Handle response objects"""

        # raise exceptions if occurred
        response.raise_for_status()

        # Response objects will automatically return unicode encoded
        # when accessing .text property
        return response

    def _request(self, req):
        r = self._session.prepare_request(req)
        # requests.Session.send() does not honor env settings by design
        _settings = self._session.mergeEnvSettings(r.url, {}, None, self._session.verify, None)
        _settings["timeout"] = self.timeout
        return self._session.send(r, **_settings)

    def jenkinsOpen(self, req, add_crumb=True, resolve_auth=True):
        """Return the HTTP response body from a ``requests.Request``.

        :returns: ``str``
        """
        return self.jenkinsRequest(req, add_crumb, resolve_auth).text

    def jenkinsRequest(self, req, add_crumb=True, resolve_auth=True):
        """Utility routine for opening an HTTP request to a Jenkins server.

        :param req: A ``requests.Request`` to submit.
        :param add_crumb: If True, try to add a crumb header to this ``req``
                          before submitting. Defaults to ``True``.
        :param resolve_auth: If True, maybe add authentication. Defaults to
                             ``True``.
        :returns: A ``requests.Response`` object.
        """
        try:
            if resolve_auth:
                self.maybeAddAuth()
            if add_crumb:
                self.maybeAddCrumb(req)

            return self.responseHandler(self._request(req))

        except req_exc.HTTPError as e:
            # Jenkins's funky authentication means its nigh impossible to
            # distinguish errors.
            if e.response.status_code in [401, 403, 500]:
                msg = "Error in request. " + "Possibly authentication failed [%s]: %s" % (
                    e.response.status_code,
                    e.response.reason,
                )
                if e.response.text:
                    msg += "\n" + e.response.text
                raise JenkinsException(msg)
            elif e.response.status_code == 404:
                raise NotFoundException("Requested item could not be found")
            else:
                raise
        except req_exc.Timeout as e:
            raise TimeoutException("Error in request: %s" % (e))
        except ConnectionError as e:
            # python 2.6 compatibility to ensure same exception raised
            # since URLError wraps a socket timeout on python 2.6.
            if str(e.reason) == "timed out":
                raise TimeoutException("Error in request: %s" % (e.reason))
            raise JenkinsException("Error in request: %s" % (e.reason))

    def getQueueItem(self, number, depth=0):
        """Get information about a queued item (to-be-created job).

        The returned dict will have a "why" key if the queued item is still
        waiting for an executor.

        The returned dict will have an "executable" key if the queued item is
        running on an executor, or has completed running. Use this to
        determine the job number / URL.

        :param name: queue number, ``int``
        :returns: dictionary of queued information, ``dict``
        """
        url = self.buildUrl(Q_ITEM, locals())
        try:
            response = self.jenkinsOpen(requests.Request("GET", url))
            if response:
                return json.loads(response)
            else:
                raise JenkinsException("queue number[%d] does not exist" % number)
        except (req_exc.HTTPError, NotFoundException):
            raise JenkinsException("queue number[%d] does not exist" % number)
        except ValueError:
            raise JenkinsException("Could not parse JSON info for queue number[%d]" % number)

    def getBuildInfo(self, name, number, depth=0):
        """Get build information dictionary.

        :param name: Job name, ``str``
        :param number: Build number, ``int``
        :param depth: JSON depth, ``int``
        :returns: dictionary of build information, ``dict``

        Example::
            >>> next_build_number = server.getJobInfo('build_name')['nextBuildNumber']
            >>> output = server.buildJob('build_name')
            >>> from time import sleep; sleep(10)
            >>> build_info = server.getBuildInfo('build_name', next_build_number)
            >>> print(build_info)
            {u'building': False, u'changeSet': {u'items': [{u'date': u'2011-12-19T18:01:52.540557Z', u'msg': u'test', u'revision': 66, u'user': u'unknown', u'paths': [{u'editType': u'edit', u'file': u'/branches/demo/index.html'}]}], u'kind': u'svn', u'revisions': [{u'module': u'http://eaas-svn01.i3.level3.com/eaas', u'revision': 66}]}, u'builtOn': u'', u'description': None, u'artifacts': [{u'relativePath': u'dist/eaas-87-2011-12-19_18-01-57.war', u'displayPath': u'eaas-87-2011-12-19_18-01-57.war', u'fileName': u'eaas-87-2011-12-19_18-01-57.war'}, {u'relativePath': u'dist/eaas-87-2011-12-19_18-01-57.war.zip', u'displayPath': u'eaas-87-2011-12-19_18-01-57.war.zip', u'fileName': u'eaas-87-2011-12-19_18-01-57.war.zip'}], u'timestamp': 1324317717000, u'number': 87, u'actions': [{u'parameters': [{u'name': u'SERVICE_NAME', u'value': u'eaas'}, {u'name': u'PROJECT_NAME', u'value': u'demo'}]}, {u'causes': [{u'userName': u'anonymous', u'shortDescription': u'Started by user anonymous'}]}, {}, {}, {}], u'id': u'2011-12-19_18-01-57', u'keepLog': False, u'url': u'http://eaas-jenkins01.i3.level3.com:9080/job/build_war/87/', u'culprits': [{u'absoluteUrl': u'http://eaas-jenkins01.i3.level3.com:9080/user/unknown', u'fullName': u'unknown'}], u'result': u'SUCCESS', u'duration': 8826, u'fullDisplayName': u'build_war #87'}
        """  # noqa: E501
        folder_url, short_name = self.getJobFolder(name)
        try:
            response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(BUILD_INFO, locals())))
            if response:
                return json.loads(response)
            else:
                raise JenkinsException("job[%s] number[%d] does not exist" % (name, number))
        except (req_exc.HTTPError, NotFoundException):
            raise JenkinsException("job[%s] number[%d] does not exist" % (name, number))
        except ValueError:
            raise JenkinsException("Could not parse JSON info for job[%s] number[%d]" % (name, number))

    def getBuildEnvVars(self, name, number, depth=0):
        """Get build environment variables.

        :param name: Job name, ``str``
        :param number: Build number, ``int``
        :param depth: JSON depth, ``int``
        :returns: dictionary of build env vars, ``dict`` or None for workflow jobs,
            or if InjectEnvVars plugin not installed
        """
        folder_url, short_name = self.getJobFolder(name)
        try:
            response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(BUILD_ENV_VARS, locals())))
            if response:
                return json.loads(response)
            else:
                raise JenkinsException("job[%s] number[%d] does not exist" % (name, number))
        except req_exc.HTTPError:
            raise JenkinsException("job[%s] number[%d] does not exist" % (name, number))
        except ValueError:
            raise JenkinsException("Could not parse JSON info for job[%s] number[%d]" % (name, number))
        except NotFoundException:
            # This can happen on workflow jobs, or if InjectEnvVars plugin not installed
            return None

    def getBuildTestReport(self, name, number, depth=0):
        """Get test results report.

        :param name: Job name, ``str``
        :param number: Build number, ``int``
        :returns: dictionary of test report results, ``dict`` or None if there is no Test Report
        """
        folder_url, short_name = self.getJobFolder(name)
        try:
            response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(BUILD_TEST_REPORT, locals())))
            if response:
                return json.loads(response)
            else:
                raise JenkinsException("job[%s] number[%d] does not exist" % (name, number))
        except req_exc.HTTPError:
            raise JenkinsException("job[%s] number[%d] does not exist" % (name, number))
        except ValueError:
            raise JenkinsException("Could not parse JSON info for job[%s] number[%d]" % (name, number))
        except NotFoundException:
            # This can happen if the test report wasn't generated for any reason
            return None

    def getQueueInfo(self):
        """:returns: list of job dictionaries, ``[dict]``

        Example::
            >>> queue_info = server.getQueueInfo()
            >>> print(queue_info[0])
            {u'task': {u'url': u'http://your_url/job/my_job/', u'color': u'aborted_anime', u'name': u'my_job'}, u'stuck': False, u'actions': [{u'causes': [{u'shortDescription': u'Started by timer'}]}], u'buildable': False, u'params': u'', u'buildableStartMilliseconds': 1315087293316, u'why': u'Build #2,532 is already in progress (ETA:10 min)', u'blocked': True}
        """  # noqa: E501
        return json.loads(self.jenkinsOpen(requests.Request("GET", self.buildUrl(Q_INFO))))["items"]

    def cancelQueue(self, id):
        """Cancel a queued build.

        :param id: Jenkins job id number for the build, ``int``
        """
        # Jenkins seems to always return a 404 when using this REST endpoint
        # https://issues.jenkins-ci.org/browse/JENKINS-21311
        with contextlib.suppress(NotFoundException):
            self.jenkinsOpen(
                requests.Request(
                    "POST",
                    self.buildUrl(CANCEL_QUEUE, locals()),
                    headers={"Referer": self.server},
                ),
            )

    def getInfo(self, item="", query=None):
        """Get information on this Master or item on Master.

        This information includes job list and view information and can be
        used to retreive information on items such as job folders.

        :param item: item to get information about on this Master
        :param query: xpath to extract information about on this Master
        :returns: dictionary of information about Master or item, ``dict``

        Example::

            >>> info = server.getInfo()
            >>> jobs = info['jobs']
            >>> print(jobs[0])
            {u'url': u'http://your_url_here/job/my_job/', u'color': u'blue',
            u'name': u'my_job'}

        """
        url = "/".join((item, INFO)).lstrip("/")
        url = quote(url)
        if query:
            url += query
        try:
            return json.loads(self.jenkinsOpen(requests.Request("GET", self.buildUrl(url))))
        except req_exc.HTTPError:
            raise BadHTTPException("Error communicating with server[%s]" % self.server)
        except ValueError:
            raise JenkinsException("Could not parse JSON info for server[%s]" % self.server)

    def getWhoami(self, depth=0):
        """Get information about the user account that authenticated to
        Jenkins. This is a simple way to verify that your credentials are
        correct.

        :returns: Information about the current user ``dict``

        Example::

            >>> me = server.getWhoami()
            >>> print me['fullName']
            >>> 'John'

        """
        try:
            response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(WHOAMI_URL, locals())))
            if response is None:
                raise EmptyResponseException("Error communicating with server[%s]: " "empty response" % self.server)

            return json.loads(response)

        except req_exc.HTTPError:
            raise BadHTTPException("Error communicating with server[%s]" % self.server)

    def getVersion(self):
        """Get the version of this Master.

        :returns: This master's version number ``str``

        Example::

            >>> info = server.getVersion()
            >>> print (info)
            >>> 1.541

        """
        try:
            request = requests.Request("GET", self.buildUrl(""))
            request.headers["X-Jenkins"] = "0.0"
            response = self.responseHandler(self._request(request))

            return response.headers["X-Jenkins"]

        except req_exc.HTTPError:
            raise BadHTTPException("Error communicating with server[%s]" % self.server)

    def getPluginsInfo(self, depth=2):
        """Get all installed plugins information on this Master.

        This method retrieves information about each plugin that is installed
        on master returning the raw plugin data in a JSON format.

        .. deprecated:: 0.4.9
           Use :func:`getPlugin` instead.

        :param depth: JSON depth, ``int``
        :returns: info on all plugins ``[dict]``

        Example::

            >>> info = server.getPluginsInfo()
            >>> print(info)
            [{u'backupVersion': None, u'version': u'0.0.4', u'deleted': False,
            u'supportsDynamicLoad': u'MAYBE', u'hasUpdate': True,
            u'enabled': True, u'pinned': False, u'downgradable': False,
            u'dependencies': [], u'url':
            u'http://wiki.jenkins-ci.org/display/JENKINS/Gearman+Plugin',
            u'longName': u'Gearman Plugin', u'active': True, u'shortName':
            u'gearman-plugin', u'bundled': False}, ..]

        """
        warnings.warn("getPluginsInfo() is deprecated, use getPlugin()", DeprecationWarning)
        return list(self.getPlugin(depth).values())

    def getPluginInfo(self, name, depth=2):
        """Get an installed plugin information on this Master.

        This method retrieves information about a specific plugin and returns
        the raw plugin data in a JSON format.
        The passed in plugin name (short or long) must be an exact match.

        .. note:: Calling this method will query Jenkins fresh for the
            information for all plugins on each call. If you need to retrieve
            information for multiple plugins it's recommended to use
            :func:`getPlugin` instead, which will return a multi key
            dictionary that can be accessed via either the short or long name
            of the plugin.

        :param name: Name (short or long) of plugin, ``str``
        :param depth: JSON depth, ``int``
        :returns: a specific plugin ``dict``

        Example::

            >>> info = server.getPluginInfo("Gearman Plugin")
            >>> print(info)
            {u'backupVersion': None, u'version': u'0.0.4', u'deleted': False,
            u'supportsDynamicLoad': u'MAYBE', u'hasUpdate': True,
            u'enabled': True, u'pinned': False, u'downgradable': False,
            u'dependencies': [], u'url':
            u'http://wiki.jenkins-ci.org/display/JENKINS/Gearman+Plugin',
            u'longName': u'Gearman Plugin', u'active': True, u'shortName':
            u'gearman-plugin', u'bundled': False}

        """
        plugins_info = self.getPlugin(depth)
        try:
            return plugins_info[name]
        except KeyError:
            pass

    def getPlugin(self, depth=2):
        """Return plugins info using helper class for version comparison

        This method retrieves information about all the installed plugins and
        uses a Plugin helper class to simplify version comparison. Also uses
        a multi key dict to allow retrieval via either short or long names.

        When printing/dumping the data, the version will transparently return
        a unicode string, which is exactly what was previously returned by the
        API.

        :param depth: JSON depth, ``int``
        :returns: info on all plugins ``[dict]``

        Example::

            >>> j = Jenkins()
            >>> info = j.getPlugin()
            >>> print(info)
            {('gearman-plugin', 'Gearman Plugin'):
              {u'backupVersion': None, u'version': u'0.0.4',
               u'deleted': False, u'supportsDynamicLoad': u'MAYBE',
               u'hasUpdate': True, u'enabled': True, u'pinned': False,
               u'downgradable': False, u'dependencies': [], u'url':
               u'http://wiki.jenkins-ci.org/display/JENKINS/Gearman+Plugin',
               u'longName': u'Gearman Plugin', u'active': True, u'shortName':
               u'gearman-plugin', u'bundled': False}, ...}

        """

        try:
            plugins_info_json = json.loads(
                self.jenkinsOpen(requests.Request("GET", self.buildUrl(PLUGIN_INFO, locals()))),
            )
        except req_exc.HTTPError:
            raise BadHTTPException("Error communicating with server[%s]" % self.server)
        except ValueError:
            raise JenkinsException("Could not parse JSON info for server[%s]" % self.server)

        plugins_data = MultiKeyDict()
        for plugin_data in plugins_info_json["plugins"]:
            keys = (str(plugin_data["shortName"]), str(plugin_data["longName"]))
            plugins_data[keys] = Plugin(**plugin_data)

        return plugins_data

    def getJobs(self, folder_depth=0, folder_depth_per_request=10, view_name=None):
        """Get list of jobs.

        Each job is a dictionary with 'name', 'url', 'color' and 'fullname'
        keys.

        If the ``view_name`` parameter is present, the list of
        jobs will be limited to only those configured in the
        specified view. In this case, the job dictionary 'fullname' key
        would be equal to the job name.

        :param folder_depth: Number of levels to search, ``int``. By default
            0, which will limit search to toplevel. None disables the limit.
        :param folder_depth_per_request: Number of levels to fetch at once,
            ``int``. See :func:`getAllJobs`.
        :param view_name: Name of a Jenkins view for which to
            retrieve jobs, ``str``. By default, the job list is
            not limited to a specific view.
        :returns: list of jobs, ``[{str: str, str: str, str: str, str: str}]``

        Example::

            >>> jobs = server.getJobs()
            >>> print(jobs)
            [{
                u'name': u'all_tests',
                u'url': u'http://your_url.here/job/all_tests/',
                u'color': u'blue',
                u'fullname': u'all_tests'
            }]

        """

        if view_name:
            return self.getViewJobs(name=view_name)
        else:
            return self.getAllJobs(
                folder_depth=folder_depth,
                folder_depth_per_request=folder_depth_per_request,
            )

    def getAllJobs(self, folder_depth=None, folder_depth_per_request=10):
        """Get list of all jobs recursively to the given folder depth.

        Each job is a dictionary with 'name', 'url', 'color' and 'fullname'
        keys.

        :param folder_depth: Number of levels to search, ``int``. By default
            None, which will search all levels. 0 limits to toplevel.
        :param folder_depth_per_request: Number of levels to fetch at once,
            ``int``. By default 10, which is usually enough to fetch all jobs
            using a single request and still easily fits into an HTTP request.
        :returns: list of jobs, ``[ { str: str} ]``

        .. note::

            On instances with many folders it would not be efficient to fetch
            each folder separately, hence `folder_depth_per_request` levels
            are fetched at once using the ``tree`` query parameter::

                ?tree=jobs[url,color,name,jobs[...,jobs[...,jobs[...,jobs]]]]

            If there are more folder levels than the query asks for, Jenkins
            returns empty [#]_ objects at the deepest level::

                {"name": "folder", "url": "...", "jobs": [{}, {}, ...]}

            This makes it possible to detect when additional requests are
            needed.

            .. [#] Actually recent Jenkins includes a ``_class`` field
                everywhere, but it's missing the requested fields.
        """
        jobs_query = "jobs"
        for _ in range(folder_depth_per_request):
            jobs_query = JOBS_QUERY_TREE % jobs_query
        jobs_query = JOBS_QUERY % jobs_query

        jobs_list = []
        jobs = [(0, [], self.getInfo(query=jobs_query)["jobs"])]
        for lvl, root, lvl_jobs in jobs:
            if not isinstance(lvl_jobs, list):
                lvl_jobs = [lvl_jobs]
            for job in lvl_jobs:
                path = [*root, job["name"]]
                # insert fullname info if it doesn't exist to
                # allow callers to easily reference unambiguously
                if "fullname" not in job:
                    job["fullname"] = "/".join(path)
                jobs_list.append(job)
                if "jobs" in job and isinstance(job["jobs"], list):  # folder
                    if folder_depth is None or lvl < folder_depth:
                        children = job["jobs"]
                        # once folder_depth_per_request is reached, Jenkins
                        # returns empty objects
                        if any("url" not in child for child in job["jobs"]):
                            url_path = "".join(["/job/" + p for p in path])
                            children = self.getInfo(url_path, query=jobs_query)["jobs"]
                        jobs.append((lvl + 1, path, children))
        return jobs_list

    def copyJob(self, from_name, to_name):
        """Copy a Jenkins job.

        Will raise an exception whenever the source and destination folder
        for this jobs won't be the same.

        :param from_name: Name of Jenkins job to copy from, ``str``
        :param to_name: Name of Jenkins job to copy to, ``str``
        :throws: :class:`JenkinsException` whenever the source and destination
            folder are not the same
        """
        from_folder_url, from_short_name = self.getJobFolder(from_name)
        to_folder_url, to_short_name = self.getJobFolder(to_name)
        if from_folder_url != to_folder_url:
            raise JenkinsException(
                "copy[%s to %s] failed, source and destination " "folder must be the same" % (from_name, to_name),
            )

        self.jenkinsOpen(requests.Request("POST", self.buildUrl(COPY_JOB, locals())))
        self.assertJobExists(to_name, "create[%s] failed")

    def renameJob(self, from_name, to_name):
        """Rename an existing Jenkins job

        Will raise an exception whenever the source and destination folder
        for this jobs won't be the same.

        :param from_name: Name of Jenkins job to rename, ``str``
        :param to_name: New Jenkins job name, ``str``
        :throws: :class:`JenkinsException` whenever the source and destination
            folder are not the same
        """
        from_folder_url, from_short_name = self.getJobFolder(from_name)
        to_folder_url, to_short_name = self.getJobFolder(to_name)
        if from_folder_url != to_folder_url:
            raise JenkinsException(
                "rename[%s to %s] failed, source and destination folder " "must be the same" % (from_name, to_name),
            )
        self.jenkinsOpen(requests.Request("POST", self.buildUrl(RENAME_JOB, locals())))
        self.assertJobExists(to_name, "rename[%s] failed")

    def deleteJob(self, name):
        """Delete Jenkins job permanently.

        :param name: Name of Jenkins job, ``str``
        """
        folder_url, short_name = self.getJobFolder(name)
        self.jenkinsOpen(requests.Request("POST", self.buildUrl(DELETE_JOB, locals())))
        if self.jobExists(name):
            raise JenkinsException("delete[%s] failed" % (name))

    def enableJob(self, name):
        """Enable Jenkins job.

        :param name: Name of Jenkins job, ``str``
        """
        folder_url, short_name = self.getJobFolder(name)
        self.jenkinsOpen(requests.Request("POST", self.buildUrl(ENABLE_JOB, locals())))

    def disableJob(self, name):
        """Disable Jenkins job.

        To re-enable, call :meth:`Jenkins.enableJob`.

        :param name: Name of Jenkins job, ``str``
        """
        folder_url, short_name = self.getJobFolder(name)
        self.jenkinsOpen(requests.Request("POST", self.buildUrl(DISABLE_JOB, locals())))

    def setNextbBuildNumber(self, name, number):
        """Set a job's next build number.

        The current next build number is contained within the job
        information retrieved using :meth:`Jenkins.getJobInfo`.  If
        the specified next build number is less than the last build
        number, Jenkins will ignore the request.

        Note that the `Next Build Number Plugin
        <https://wiki.jenkins-ci.org/display/JENKINS/Next+Build+Number+Plugin>`_
        must be installed to enable this functionality.

        :param name: Name of Jenkins job, ``str``
        :param number: Next build number to set, ``int``

        Example::

            >>> next_bn = server.getJobInfo('job_name')['nextBuildNumber']
            >>> server.setNextbBuildNumber('job_name', next_bn + 50)
        """
        folder_url, short_name = self.getJobFolder(name)
        self.jenkinsOpen(
            requests.Request(
                "POST",
                self.buildUrl(SET_JOB_BUILD_NUMBER, locals()),
                data=("nextBuildNumber=%d" % number).encode("utf-8"),
            ),
        )

    def jobExists(self, name):
        """Check whether a job exists

        :param name: Name of Jenkins job, ``str``
        :returns: ``True`` if Jenkins job exists
        """
        folder_url, short_name = self.getJobFolder(name)
        if self.getJobName(name) == short_name:
            return True
        return None

    def jobs_count(self):
        """Get the number of jobs on the Jenkins server

        :returns: Total number of jobs, ``int``
        """
        return len(self.getAllJobs())

    def assertJobExists(self, name, exception_message="job[%s] does not exist"):
        """Raise an exception if a job does not exist

        :param name: Name of Jenkins job, ``str``
        :param exception_message: Message to use for the exception. Formatted
                                  with ``name``
        :throws: :class:`JenkinsException` whenever the job does not exist
        """
        if not self.jobExists(name):
            raise JenkinsException(exception_message % name)

    def createFolder(self, folder_name, ignore_failures=False):
        """Create a new Jenkins folder

        :param folder_name: Name of Jenkins Folder, ``str``
        :param ignore_failures: if True, don't raise if it was not possible to create the folder, ``bool``
        """
        folder_url, short_name = self.getJobFolder(folder_name)
        url = self.buildUrl(CREATE_JOB, locals())
        data = {
            "name": folder_name,
            "mode": "com.cloudbees.hudson.plugins.folder.Folder",
        }
        try:
            response = self.jenkinsRequest(requests.Request("POST", url, data=data))
        except requests.exceptions.HTTPError:
            if not ignore_failures:
                raise JenkinsException("Error creating folder [%s]. Probably it already exists." % (folder_name))

    def upsertJob(self, name, config_xml):
        """Create a new Jenkins job or reconfigures it if it exists

        :param name: Name of Jenkins job, ``str``
        :param config_xml: config file text, ``str``
        """

        if self.jobExists(name):
            self.reconfigJob(name, config_xml)
        else:
            self.createJob(name, config_xml)

    def checkJenkinsfileSyntax(self, jenkinsfile):
        """Checks if a Pipeline Jenkinsfile has a valid syntax

        :param jenkinsfile: Jenkinsfile text, ``str``
        :returns: List of errors in the Jenkinsfile. Empty list if no errors.
        """
        # https://jenkins.io/doc/book/pipeline/development/#linter
        # JENKINS_CRUMB=`curl "$JENKINS_URL/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)"
        # curl -X POST -H $JENKINS_CRUMB -F "jenkinsfile=<Jenkinsfile" $JENKINS_URL/pipeline-model-converter/val
        url = self.buildUrl(CHECK_JENKINSFILE_SYNTAX, locals())
        the_data = {"jenkinsfile": jenkinsfile}
        response = self.jenkinsRequest(requests.Request("POST", url, data=the_data))
        return response.json().get("data", {}).get("errors", [])

    def createJob(self, name, config_xml):
        """Create a new Jenkins job

        :param name: Name of Jenkins job, ``str``
        :param config_xml: config file text, ``str``
        """
        folder_url, short_name = self.getJobFolder(name)
        if self.jobExists(name):
            raise JenkinsException("job[%s] already exists" % (name))

        try:
            self.jenkinsOpen(
                requests.Request(
                    "POST",
                    self.buildUrl(CREATE_JOB, locals()),
                    data=config_xml.encode("utf-8"),
                    headers=DEFAULT_HEADERS,
                ),
            )
        except NotFoundException:
            raise JenkinsException("Cannot create job[%s] because folder " "for the job does not exist" % (name))
        self.assertJobExists(name, "create[%s] failed")

    def getJobConfig(self, name):
        """Get configuration of existing Jenkins job.

        :param name: Name of Jenkins job, ``str``
        :returns: job configuration (XML format)
        """
        folder_url, short_name = self.getJobFolder(name)
        request = requests.Request("GET", self.buildUrl(CONFIG_JOB, locals()))
        return self.jenkinsOpen(request)

    def reconfigJob(self, name, config_xml):
        """Change configuration of existing Jenkins job.

        To create a new job, see :meth:`Jenkins.createJob`.

        :param name: Name of Jenkins job, ``str``
        :param config_xml: New XML configuration, ``str``
        """
        folder_url, short_name = self.getJobFolder(name)
        reconfig_url = self.buildUrl(CONFIG_JOB, locals())
        self.jenkinsOpen(
            requests.Request(
                "POST",
                reconfig_url,
                data=config_xml.encode("utf-8"),
                headers=DEFAULT_HEADERS,
            ),
        )

    def buildJobUrl(self, name, parameters=None, token=None):
        """Get URL to trigger build job.

        Authenticated setups may require configuring a token on the server
        side.

        Use ``list of two membered tuples`` to supply parameters with multi
        select options.

        :param name: Name of Jenkins job, ``str``
        :param parameters: parameters for job, or None., ``dict`` or
            ``list of two membered tuples``
        :param token: (optional) token for building job, ``str``
        :returns: URL for building job
        """
        folder_url, short_name = self.getJobFolder(name)
        if parameters:
            if token:
                if isinstance(parameters, list):
                    parameters.append(
                        (
                            "token",
                            token,
                        ),
                    )
                elif isinstance(parameters, dict):
                    parameters.update({"token": token})
                else:
                    raise JenkinsException(
                        "build parameters can be a dictionary "
                        'like {"param_key": "param_value", ...} '
                        "or a list of two membered tuples "
                        'like [("param_key", "param_value",), ...]',
                    )
            return self.buildUrl(BUILD_WITH_PARAMS_JOB, locals()) + "?" + parse.urlencode(parameters)
        elif token:
            return self.buildUrl(BUILD_JOB, locals()) + "?" + parse.urlencode({"token": token})
        else:
            return self.buildUrl(BUILD_JOB, locals())

    def buildJob(self, name, parameters=None, token=None):
        """Trigger build job.

        This method returns a queue item number that you can pass to
        :meth:`Jenkins.getQueueItem`. Note that this queue number is only
        valid for about five minutes after the job completes, so you should
        get/poll the queue information as soon as possible to determine the
        job's URL.

        :param name: name of job
        :param parameters: parameters for job, or ``None``, ``dict``
        :param token: Jenkins API token
        :returns: ``int`` queue item
        """
        response = self.jenkinsRequest(requests.Request("POST", self.buildJobUrl(name, parameters, token)))

        if "Location" not in response.headers:
            raise EmptyResponseException("Header 'Location' not found in " "response from server[%s]" % self.server)

        location = response.headers["Location"]
        # location is a queue item, eg. "http://jenkins/queue/item/25/"
        if location.endswith("/"):
            location = location[:-1]
        parts = location.split("/")
        number = int(parts[-1])
        return number

    def runScript(self, script, node=None):
        """Execute a groovy script on the jenkins master or on a node if
        specified..

        :param script: The groovy script, ``string``
        :param node: Node to run the script on, defaults to None (master).
        :returns: The result of the script run.

        Example::
            >>> info = server.runScript("println(Jenkins.instance.pluginManager.plugins)")
            >>> print(info)
            u'[Plugin:windows-slaves, Plugin:ssh-slaves, Plugin:translation,
            Plugin:cvs, Plugin:nodelabelparameter, Plugin:external-monitor-job,
            Plugin:mailer, Plugin:jquery, Plugin:antisamy-markup-formatter,
            Plugin:maven-plugin, Plugin:pam-auth]'
        """
        magic_str = ")]}."
        print_magic_str = 'print("{}")'.format(magic_str)
        data = {"script": "{0}\n{1}".format(script, print_magic_str).encode("utf-8")}
        url = self.buildUrl(NODE_SCRIPT_TEXT, locals()) if node else self.buildUrl(SCRIPT_TEXT, locals())

        result = self.jenkinsOpen(requests.Request("POST", url, data=data))

        if not result.endswith(magic_str):
            raise JenkinsException(result)

        return result[: result.rfind("\n")]

    def installPlugin(self, name, include_dependencies=True):
        """Install a plugin and its dependencies from the Jenkins public
        repository at http://repo.jenkins-ci.org/repo/org/jenkins-ci/plugins

        :param name: The plugin short name, ``string``
        :param include_dependencies: Install the plugin's dependencies, ``bool``
        :returns: Whether a Jenkins restart is required, ``bool``

        Example::
            >>> info = server.installPlugin("jabber")
            >>> print(info)
            True
        """
        # using a groovy script because Jenkins does not provide a REST endpoint
        # for installing plugins.
        install = 'Jenkins.instance.updateCenter.getPlugin("' + name + '")' ".deploy();"
        if include_dependencies:
            install = (
                'Jenkins.instance.updateCenter.getPlugin("' + name + '")' ".getNeededDependencies().each{it.deploy()};"
            ) + install

        self.runScript(install)
        # runScript is an async call to run groovy. we need to wait a little
        # before we can get a reliable response on whether a restart is needed
        time.sleep(2)
        is_restart_required = "Jenkins.instance.updateCenter" ".isRestartRequiredForCompletion()"

        # response is a string (i.e. u'Result: true\n'), return a bool instead
        response_str = self.runScript(is_restart_required)
        response = response_str.split(":")[1].strip().lower() == "true"
        return response

    def stopBuild(self, name, number):
        """Stop a running Jenkins build.

        :param name: Name of Jenkins job, ``str``
        :param number: Jenkins build number for the job, ``int``
        """
        folder_url, short_name = self.getJobFolder(name)
        self.jenkinsOpen(requests.Request("POST", self.buildUrl(STOP_BUILD, locals())))

    def deleteBuild(self, name, number):
        """Delete a Jenkins build.

        :param name: Name of Jenkins job, ``str``
        :param number: Jenkins build number for the job, ``int``
        """
        folder_url, short_name = self.getJobFolder(name)
        self.jenkinsOpen(requests.Request("POST", self.buildUrl(DELETE_BUILD, locals()), b""))

    def wipeoutJobWorkspace(self, name):
        """Wipe out workspace for given Jenkins job.

        :param name: Name of Jenkins job, ``str``
        """
        folder_url, short_name = self.getJobFolder(name)
        self.jenkinsOpen(requests.Request("POST", self.buildUrl(WIPEOUT_JOB_WORKSPACE, locals()), b""))

    def getRunningBuilds(self):
        """Return list of running builds.

        Each build is a dict with keys 'name', 'number', 'url', 'node',
        and 'executor'.

        :returns: List of builds,
          ``[ { str: str, str: int, str:str, str: str, str: int} ]``

        Example::
            >>> builds = server.getRunningBuilds()
            >>> print(builds)
            [{'node': 'foo-slave', 'url': 'https://localhost/job/test/15/',
              'executor': 0, 'name': 'test', 'number': 15}]
        """
        builds = []
        nodes = self.getNodes()
        for node in nodes:
            # the name returned is not the name to lookup when
            # dealing with master :/
            node_name = "(master)" if node["name"] == "master" else node["name"]
            try:
                info = self.getNodeInfo(node_name, depth=2)
            except JenkinsException as e:
                # Jenkins may 500 on depth >0. If the node info comes back
                # at depth 0 treat it as a node not running any jobs.
                if "[500]" in str(e) and self.getNodeInfo(node_name, depth=0):
                    continue
                else:
                    raise
            for executor in info["executors"]:
                executable = executor["currentExecutable"]
                if executable and "number" in executable:
                    executor_number = executor["number"]
                    build_number = executable["number"]
                    url = executable["url"]
                    m = re.search(r"/job/([^/]+)/.*", parse.urlparse(url).path)
                    job_name = m.group(1)
                    builds.append(
                        {
                            "name": job_name,
                            "number": build_number,
                            "url": url,
                            "node": node_name,
                            "executor": executor_number,
                        },
                    )
        return builds

    def getNodes(self, depth=0):
        """Get a list of nodes connected to the Master

        Each node is a dict with keys 'name' and 'offline'

        :returns: List of nodes, ``[ { str: str, str: bool} ]``
        """
        try:
            nodes_data = json.loads(self.jenkinsOpen(requests.Request("GET", self.buildUrl(NODE_LIST, locals()))))
            return [{"name": c["displayName"], "offline": c["offline"]} for c in nodes_data["computer"]]
        except req_exc.HTTPError:
            raise BadHTTPException("Error communicating with server[%s]" % self.server)
        except ValueError:
            raise JenkinsException("Could not parse JSON info for server[%s]" % self.server)

    def getNodeInfo(self, name, depth=0):
        """Get node information dictionary

        :param name: Node name, ``str``
        :param depth: JSON depth, ``int``
        :returns: Dictionary of node info, ``dict``
        """
        try:
            response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(NODE_INFO, locals())))
            if response:
                return json.loads(response)
            else:
                raise JenkinsException("node[%s] does not exist" % name)
        except (req_exc.HTTPError, NotFoundException):
            raise JenkinsException("node[%s] does not exist" % name)
        except ValueError:
            raise JenkinsException("Could not parse JSON info for node[%s]" % name)

    def nodeExists(self, name):
        """Check whether a node exists

        :param name: Name of Jenkins node, ``str``
        :returns: ``True`` if Jenkins node exists
        """
        try:
            self.getNodeInfo(name)
            return True
        except JenkinsException:
            return False

    def assertNodeExists(self, name, exception_message="node[%s] does not exist"):
        """Raise an exception if a node does not exist

        :param name: Name of Jenkins node, ``str``
        :param exception_message: Message to use for the exception. Formatted
                                  with ``name``
        :throws: :class:`JenkinsException` whenever the node does not exist
        """
        if not self.nodeExists(name):
            raise JenkinsException(exception_message % name)

    def deleteNode(self, name):
        """Delete Jenkins node permanently.

        :param name: Name of Jenkins node, ``str``
        """
        self.getNodeInfo(name)
        self.jenkinsOpen(requests.Request("POST", self.buildUrl(DELETE_NODE, locals())))
        if self.nodeExists(name):
            raise JenkinsException("delete[%s] failed" % (name))

    def disableNode(self, name, msg=""):
        """Disable a node

        :param name: Jenkins node name, ``str``
        :param msg: Offline message, ``str``
        """
        info = self.getNodeInfo(name)
        if info["offline"]:
            return
        self.jenkinsOpen(requests.Request("POST", self.buildUrl(TOGGLE_OFFLINE, locals())))

    def enableNode(self, name):
        """Enable a node

        :param name: Jenkins node name, ``str``
        """
        info = self.getNodeInfo(name)
        if not info["offline"]:
            return
        msg = ""
        self.jenkinsOpen(requests.Request("POST", self.buildUrl(TOGGLE_OFFLINE, locals())))

    def createNode(
        self,
        name,
        numExecutors=2,
        nodeDescription=None,
        remoteFS="/var/lib/jenkins",
        labels=None,
        exclusive=False,
        launcher=LAUNCHER_COMMAND,
        launcher_params={},
    ):
        """Create a node

        :param name: name of node to create, ``str``
        :param numExecutors: number of executors for node, ``int``
        :param nodeDescription: Description of node, ``str``
        :param remoteFS: Remote filesystem location to use, ``str``
        :param labels: Labels to associate with node, ``str``
        :param exclusive: Use this node for tied jobs only, ``bool``
        :param launcher: The launch method for the slave, ``jenkins.LAUNCHER_COMMAND``, \
        ``jenkins.LAUNCHER_SSH``, ``jenkins.LAUNCHER_JNLP``, ``jenkins.LAUNCHER_WINDOWS_SERVICE``
        :param launcher_params: Additional parameters for the launcher, ``dict``
        """
        if self.nodeExists(name):
            raise JenkinsException("node[%s] already exists" % (name))

        mode = "NORMAL"
        if exclusive:
            mode = "EXCLUSIVE"

        launcher_params["stapler-class"] = launcher

        inner_params = {
            "nodeDescription": nodeDescription,
            "numExecutors": numExecutors,
            "remoteFS": remoteFS,
            "labelString": labels,
            "mode": mode,
            "retentionStrategy": {"stapler-class": "hudson.slaves.RetentionStrategy$Always"},
            "nodeProperties": {"stapler-class-bag": "true"},
            "launcher": launcher_params,
        }

        params = {"name": name, "type": NODE_TYPE, "json": json.dumps(inner_params)}

        self.jenkinsOpen(requests.Request("POST", self.buildUrl(CREATE_NODE, locals()), data=params))

        self.assertNodeExists(name, "create[%s] failed")

    def getNodeConfig(self, name):
        """Get the configuration for a node.

        :param name: Jenkins node name, ``str``
        """
        get_config_url = self.buildUrl(CONFIG_NODE, locals())
        return self.jenkinsOpen(requests.Request("GET", get_config_url))

    def reconfigNode(self, name, config_xml):
        """Change the configuration for an existing node.

        :param name: Jenkins node name, ``str``
        :param config_xml: New XML configuration, ``str``
        """
        reconfig_url = self.buildUrl(CONFIG_NODE, locals())
        self.jenkinsOpen(
            requests.Request(
                "POST",
                reconfig_url,
                data=config_xml.encode("utf-8"),
                headers=DEFAULT_HEADERS,
            ),
        )

    def getBuildConsoleOutput(self, name, number):
        """Get build console text.

        :param name: Job name, ``str``
        :param number: Build number, ``int``
        :returns: Build console output,  ``str``
        """
        folder_url, short_name = self.getJobFolder(name)
        try:
            response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(BUILD_CONSOLE_OUTPUT, locals())))
            if response:
                return response
            else:
                raise JenkinsException("job[%s] number[%d] does not exist" % (name, number))
        except (req_exc.HTTPError, NotFoundException):
            raise JenkinsException("job[%s] number[%d] does not exist" % (name, number))

    def getJobFolder(self, name):
        """Return the name and folder (see cloudbees plugin).

        This is a method to support cloudbees folder plugin.
        Url request should take into account folder path when the job name specify it
        (ex.: 'folder/job')

        :param name: Job name, ``str``
        :returns: Tuple [ 'folder path for Request', 'Name of job without folder path' ]
        """

        a_path = name.split("/")
        short_name = a_path[-1]
        folder_url = ("job/" + "/job/".join(a_path[:-1]) + "/") if len(a_path) > 1 else ""

        return folder_url, short_name

    def getViewJobs(self, name):
        """Get list of jobs on the view specified.

        Each job is a dictionary with 'name', 'url', 'color' and 'fullname'
        keys.

        The list of jobs is limited to only those configured in the
        specified view. Each job dictionary 'fullname' key
        is equal to the job name.

        :param view_name: Name of a Jenkins view for which to
            retrieve jobs, ``str``.
        :returns: list of jobs, ``[{str: str, str: str, str: str, str: str}]``
        """

        folder_url, short_name = self.getJobFolder(name)
        try:
            response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(VIEW_JOBS, locals())))
            if response:
                jobs = json.loads(response)["jobs"]
            else:
                raise JenkinsException("view[%s] does not exist" % name)
        except NotFoundException:
            raise JenkinsException("view[%s] does not exist" % name)
        except ValueError:
            raise JenkinsException("Could not parse JSON info for view[%s]" % name)

        for job_dict in jobs:
            job_dict.update({"fullname": job_dict["name"]})

        return jobs

    def getViewName(self, name):
        """Return the name of a view using the API.

        That is roughly an identity method which can be used to quickly verify
        a view exists or is accessible without causing too much stress on the
        server side.

        :param name: View name, ``str``
        :returns: Name of view or None
        """
        folder_url, short_name = self.getJobFolder(name)
        try:
            response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(VIEW_NAME, locals())))
        except NotFoundException:
            return None
        else:
            actual = json.loads(response)["name"]
            if actual != short_name:
                raise JenkinsException(
                    "Jenkins returned an unexpected view name %s " "(expected: %s)" % (actual, short_name),
                )
            return name

    def assertViewExists(self, name, exception_message="view[%s] does not exist"):
        """Raise an exception if a view does not exist

        :param name: Name of Jenkins view, ``str``
        :param exception_message: Message to use for the exception. Formatted
                                  with ``name``
        :throws: :class:`JenkinsException` whenever the view does not exist
        """
        if not self.viewExists(name):
            raise NotFoundException(exception_message % name)

    def viewExists(self, name):
        """Check whether a view exists

        :param name: Name of Jenkins view, ``str``
        :returns: ``True`` if Jenkins view exists
        """
        if self.getViewName(name) == name:
            return True
        return None

    def viewExists(self):
        """Get list of views running.

        Each view is a dictionary with 'name' and 'url' keys.

        :returns: list of views, ``[ { str: str} ]``
        """
        return self.getInfo()["views"]

    def deleteView(self, name):
        """Delete Jenkins view permanently.

        :param name: Name of Jenkins view, ``str``
        """
        folder_url, short_name = self.getJobFolder(name)
        self.jenkinsOpen(requests.Request("POST", self.buildUrl(DELETE_VIEW, locals())))
        if self.viewExists(name):
            raise JenkinsException("delete[%s] failed" % (name))

    def createView(self, name, config_xml):
        """Create a new Jenkins view

        :param name: Name of Jenkins view, ``str``
        :param config_xml: config file text, ``str``
        """
        folder_url, short_name = self.getJobFolder(name)
        if self.viewExists(name):
            raise JenkinsException("view[%s] already exists" % (name))

        self.jenkinsOpen(
            requests.Request(
                "POST",
                self.buildUrl(CREATE_VIEW, locals()),
                data=config_xml.encode("utf-8"),
                headers=DEFAULT_HEADERS,
            ),
        )
        self.assertViewExists(name, "create[%s] failed")

    def reconfigView(self, name, config_xml):
        """Change configuration of existing Jenkins view.

        To create a new view, see :meth:`Jenkins.createView`.

        :param name: Name of Jenkins view, ``str``
        :param config_xml: New XML configuration, ``str``
        """
        folder_url, short_name = self.getJobFolder(name)
        reconfig_url = self.buildUrl(CONFIG_VIEW, locals())
        self.jenkinsOpen(
            requests.Request(
                "POST",
                reconfig_url,
                data=config_xml.encode("utf-8"),
                headers=DEFAULT_HEADERS,
            ),
        )

    def getViewConfig(self, name):
        """Get configuration of existing Jenkins view.

        :param name: Name of Jenkins view, ``str``
        :returns: view configuration (XML format)
        """
        folder_url, short_name = self.getJobFolder(name)
        request = requests.Request("GET", self.buildUrl(CONFIG_VIEW, locals()))
        return self.jenkinsOpen(request)

    def getPromotionName(self, name, job_name):
        """Return the name of a promotion using the API.

        That is roughly an identity method which can be used to
        quickly verify a promotion exists for a job or is accessible
        without causing too much stress on the server side.

        :param name: Promotion name, ``str``
        :param job_name: Job name, ``str``
        :returns: Name of promotion or None
        """
        folder_url, short_name = self.getJobFolder(job_name)
        try:
            response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(PROMOTION_NAME, locals())))
        except NotFoundException:
            return None
        else:
            actual = json.loads(response)["name"]
            if actual != name:
                raise JenkinsException(
                    "Jenkins returned an unexpected promotion name %s " "(expected: %s)" % (actual, name),
                )
            return actual

    def assertPromotionExists(
        self,
        name,
        job_name,
        exception_message="promotion[%s] does not " "exist for job[%s]",
    ):
        """Raise an exception if a job lacks a promotion

        :param name: Name of Jenkins promotion, ``str``
        :param job_name: Job name, ``str``
        :param exception_message: Message to use for the exception. Formatted
                                  with ``name`` and ``job_name``
        :throws: :class:`JenkinsException` whenever the promotion
            does not exist on a job
        """
        if not self.promotionExists(name, job_name):
            raise JenkinsException(exception_message % (name, job_name))

    def promotionExists(self, name, job_name):
        """Check whether a job has a certain promotion

        :param name: Name of Jenkins promotion, ``str``
        :param job_name: Job name, ``str``
        :returns: ``True`` if Jenkins promotion exists
        """
        return self.getPromotionName(name, job_name) == name

    def getPromotionsInfo(self, job_name, depth=0):
        """Get promotion information dictionary of a job

        :param job_name: job_name, ``str``
        :param depth: JSON depth, ``int``
        :returns: Dictionary of promotion info, ``dict``
        """
        folder_url, short_name = self.getJobFolder(job_name)
        try:
            response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(PROMOTION_INFO, locals())))
            if response:
                return json.loads(response)
            else:
                raise JenkinsException("job[%s] does not exist" % job_name)
        except req_exc.HTTPError:
            raise JenkinsException("job[%s] does not exist" % job_name)
        except ValueError:
            raise JenkinsException("Could not parse JSON info for " "promotions of job[%s]" % job_name)

    def getPromotions(self, job_name):
        """Get list of promotions running.

        Each promotion is a dictionary with 'name' and 'url' keys.

        :param job_name: Job name, ``str``
        :returns: list of promotions, ``[ { str: str} ]``
        """
        return self.getPromotionsInfo(job_name)["processes"]

    def deletePromotion(self, name, job_name):
        """Delete Jenkins promotion permanently.

        :param name: Name of Jenkins promotion, ``str``
        :param job_name: Job name, ``str``
        """
        folder_url, short_name = self.getJobFolder(job_name)
        self.jenkinsOpen(requests.Request("POST", self.buildUrl(DELETE_PROMOTION, locals())))
        if self.promotionExists(name, job_name):
            raise JenkinsException("delete[%s] from job[%s] failed" % (name, job_name))

    def createPromotion(self, name, job_name, config_xml):
        """Create a new Jenkins promotion

        :param name: Name of Jenkins promotion, ``str``
        :param job_name: Job name, ``str``
        :param config_xml: config file text, ``str``
        """
        if self.promotionExists(name, job_name):
            raise JenkinsException("promotion[%s] already exists at job[%s]" % (name, job_name))

        folder_url, short_name = self.getJobFolder(job_name)
        self.jenkinsOpen(
            requests.Request(
                "POST",
                self.buildUrl(CREATE_PROMOTION, locals()),
                data=config_xml.encode("utf-8"),
                headers=DEFAULT_HEADERS,
            ),
        )
        self.assertPromotionExists(name, job_name, "create[%s] at " "job[%s] failed")

    def reconfigPromotion(self, name, job_name, config_xml):
        """Change configuration of existing Jenkins promotion.

        To create a new promotion, see :meth:`Jenkins.createPromotion`.

        :param name: Name of Jenkins promotion, ``str``
        :param job_name: Job name, ``str``
        :param config_xml: New XML configuration, ``str``
        """
        folder_url, short_name = self.getJobFolder(job_name)
        reconfig_url = self.buildUrl(CONFIG_PROMOTION, locals())
        self.jenkinsOpen(
            requests.Request(
                "POST",
                reconfig_url,
                data=config_xml.encode("utf-8"),
                headers=DEFAULT_HEADERS,
            ),
        )

    def getPromotionConfig(self, name, job_name):
        """Get configuration of existing Jenkins promotion.

        :param name: Name of Jenkins promotion, ``str``
        :param job_name: Job name, ``str``
        :returns: promotion configuration (XML format)
        """
        folder_url, short_name = self.getJobFolder(job_name)
        request = requests.Request("GET", self.buildUrl(CONFIG_PROMOTION, locals()))
        return self.jenkinsOpen(request)

    def getTagText(self, name, xml):
        """Get text of tag from xml

        :param name: XML tag name, ``str``
        :param xml: XML configuration, ``str``
        :returns: Text of tag, ``str``
        :throws: :class:`JenkinsException` whenever tag does not exist
            or has invalidated text
        """
        tag = ET.fromstring(xml).find(name)
        try:
            text = tag.text.strip()
            if text:
                return text
            raise JenkinsException("tag[%s] is invalidated" % name)
        except AttributeError:
            raise JenkinsException("tag[%s] is invalidated" % name)

    def assertFolder(self, name, exception_message="job[%s] is not a folder"):
        """Raise an exception if job is not Cloudbees Folder

        :param name: Name of job, ``str``
        :param exception_message: Message to use for the exception.
        :throws: :class:`JenkinsException` whenever the job is
            not Cloudbees Folder
        """
        if not self.isFolder(name):
            raise JenkinsException(exception_message % name)

    def isFolder(self, name):
        """Check whether a job is Cloudbees Folder

        :param name: Job name, ``str``
        :returns: ``True`` if job is folder, ``False`` otherwise
        """
        return self.getJobInfo(name)["_class"] == "com.cloudbees.hudson.plugins.folder.Folder"

    def assertCredentialExists(
        self,
        name,
        folder_name,
        domain_name="_",
        exception_message="credential[%s] does not " "exist in the domain[%s] of [%s]",
    ):
        """Raise an exception if credential does not exist in domain of folder

        :param name: Name of credential, ``str``
        :param folder_name: Folder name, ``str``
        :param domain_name: Domain name, default is '_', ``str``
        :param exception_message: Message to use for the exception.
                                  Formatted with ``name``, ``domain_name``,
                                  and ``folder_name``
        :throws: :class:`JenkinsException` whenever the credentail
            does not exist in domain of folder
        """
        if not self.credentialExists(name, folder_name, domain_name):
            raise JenkinsException(exception_message % (name, domain_name, folder_name))

    def credentialExists(self, name, folder_name, domain_name="_"):
        """Check whether a credentail exists in domain of folder

        :param name: Name of credentail, ``str``
        :param folder_name: Folder name, ``str``
        :param domain_name: Domain name, default is '_', ``str``
        :returns: ``True`` if credentail exists, ``False`` otherwise
        """
        try:
            return self.getCredentialInfo(name, folder_name, domain_name)["id"] == name
        except JenkinsException:
            return False

    def getCredentialInfo(self, name, folder_name, domain_name="_"):
        """Get credential information dictionary in domain of folder

        :param name: Name of credentail, ``str``
        :param folder_name: folder_name, ``str``
        :param domain_name: Domain name, default is '_', ``str``
        :returns: Dictionary of credential info, ``dict``
        """
        self.assertFolder(folder_name)
        folder_url, short_name = self.getJobFolder(folder_name)
        try:
            response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(CREDENTIAL_INFO, locals())))
            if response:
                return json.loads(response)
            else:
                raise JenkinsException(
                    "credential[%s] does not exist " "in the domain[%s] of [%s]" % (name, domain_name, folder_name),
                )
        except (req_exc.HTTPError, NotFoundException):
            raise JenkinsException(
                "credential[%s] does not exist " "in the domain[%s] of [%s]" % (name, domain_name, folder_name),
            )
        except ValueError:
            raise JenkinsException(
                "Could not parse JSON info for credential[%s] "
                "in the domain[%s] of [%s]" % (name, domain_name, folder_name),
            )

    def getCredentialConfig(self, name, folder_name, domain_name="_"):
        """Get configuration of credential in domain of folder.

        :param name: Name of credentail, ``str``
        :param folder_name: Folder name, ``str``
        :param domain_name: Domain name, default is '_', ``str``
        :returns: Credential configuration (XML format)
        """
        self.assertFolder(folder_name)
        folder_url, short_name = self.getJobFolder(folder_name)
        return self.jenkinsOpen(requests.Request("GET", self.buildUrl(CONFIG_CREDENTIAL, locals())))

    def createCredential(self, folder_name, config_xml, domain_name="_"):
        """Create credentail in domain of folder

        :param folder_name: Folder name, ``str``
        :param config_xml: New XML configuration, ``str``
        :param domain_name: Domain name, default is '_', ``str``
        """
        folder_url, short_name = self.getJobFolder(folder_name)
        name = self.getTagText("id", config_xml)
        if self.credentialExists(name, folder_name, domain_name):
            raise JenkinsException(
                "credential[%s] already exists " "in the domain[%s] of [%s]" % (name, domain_name, folder_name),
            )

        self.jenkinsOpen(
            requests.Request(
                "POST",
                self.buildUrl(CREATE_CREDENTIAL, locals()),
                data=config_xml.encode("utf-8"),
                headers=DEFAULT_HEADERS,
            ),
        )
        self.assertCredentialExists(
            name,
            folder_name,
            domain_name,
            "create[%s] failed in the " "domain[%s] of [%s]",
        )

    def deleteCredential(self, name, folder_name, domain_name="_"):
        """Delete credential from domain of folder

        :param name: Name of credentail, ``str``
        :param folder_name: Folder name, ``str``
        :param domain_name: Domain name, default is '_', ``str``
        """
        folder_url, short_name = self.getJobFolder(folder_name)
        self.jenkinsOpen(requests.Request("DELETE", self.buildUrl(CONFIG_CREDENTIAL, locals())))
        if self.credentialExists(name, folder_name, domain_name):
            raise JenkinsException(
                "delete credential[%s] from " "domain[%s] of [%s] failed" % (name, domain_name, folder_name),
            )

    def reconfigCredential(self, folder_name, config_xml, domain_name="_"):
        """Reconfig credential with new config in domain of folder

        :param folder_name: Folder name, ``str``
        :param config_xml: New XML configuration, ``str``
        :param domain_name: Domain name, default is '_', ``str``
        """
        folder_url, short_name = self.getJobFolder(folder_name)
        name = self.getTagText("id", config_xml)
        self.assertCredentialExists(name, folder_name, domain_name)

        reconfig_url = self.buildUrl(CONFIG_CREDENTIAL, locals())

        self.jenkinsOpen(
            requests.Request(
                "POST",
                reconfig_url,
                data=config_xml.encode("utf-8"),
                headers=DEFAULT_HEADERS,
            ),
        )

    def listCredentials(self, folder_name, domain_name="_"):
        """List credentials in domain of folder

        :param folder_name: Folder name, ``str``
        :param domain_name: Domain name, default is '_', ``str``
        :returns: Credentials list, ``list``
        """
        self.assertFolder(folder_name)
        folder_url, short_name = self.getJobFolder(folder_name)
        response = self.jenkinsOpen(requests.Request("GET", self.buildUrl(LIST_CREDENTIALS, locals())))
        return json.loads(response)["credentials"]

    def quietDown(self):
        """Prepare Jenkins for shutdown.

        No new builds will be started allowing running builds to complete
        prior to shutdown of the server.
        """
        request = requests.Request("POST", self.buildUrl(QUIET_DOWN))
        self.jenkinsOpen(request)
        info = self.getInfo()
        if not info["quietingDown"]:
            raise JenkinsException("quiet down failed")

    def waitForNormalOp(self, timeout):
        """Wait for jenkins to enter normal operation mode.

        :param timeout: number of seconds to wait, ``int``
            Note this is not the same as the connection timeout set via
            __init__ as that controls the socket timeout. Instead this is
            how long to wait until the status returned.
        :returns: ``True`` if Jenkins became ready in time, ``False``
                   otherwise.

        Setting timeout to be less than the configured connection timeout
        may result in this waiting for at least the connection timeout
        length of time before returning. It is recommended that the timeout
        here should be at least as long as any set connection timeout.
        """
        if timeout < 0:
            raise ValueError("Timeout must be >= 0 not %d" % timeout)

        if not self.timeoutWarningIssued and self.timeout != socket._GLOBAL_DEFAULT_TIMEOUT and timeout < self.timeout:
            warnings.warn(
                "Requested timeout to wait for jenkins to resume "
                "normal operations is less than configured "
                "connection timeout. Unexpected behaviour may "
                "occur.",
            )
            self.timeoutWarningIssued = True

        start_time = time.time()

        def isReady():
            # only call getVersion until it returns without exception
            while True:
                if self.getVersion():
                    while True:
                        # json API will only return valid info once Jenkins
                        # is ready, so just check any known field exists
                        # when not in normal mode, most requests will
                        # be ignored or fail
                        yield "mode" in self.getInfo()
                else:
                    yield False

        while True:
            try:
                if next(isReady()):
                    return True
            except (KeyError, JenkinsException):
                # key missing from JSON, empty response or errors in
                # getInfo due to incomplete HTTP responses
                pass
            # check time passed as the communication will also
            # take time
            if time.time() > start_time + timeout:
                break
            time.sleep(1)

        return False


if __name__ == "__main__":
    jk = Jenkins(url=r"http://localhost:8080/jenkins", username="kamalyes", password="QINg0201$")
    print(jk.getAllJobs())
    print(jk.getBuildInfo(name="YamlInterfaceTests", number=9))
