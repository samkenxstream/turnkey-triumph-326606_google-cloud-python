# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Define Logging API Sinks."""

from gcloud.exceptions import NotFound


class Sink(object):
    """Sinks represent filtered exports for log entries.

    See:
    https://cloud.google.com/logging/docs/api/ref_v2beta1/rest/v2beta1/projects.sinks

    :type name: string
    :param name: the name of the sink

    :type filter_: string
    :param filter_: the advanced logs filter expression defining the entries
                    exported by the sink.

    :type destination: string
    :param destination: destination URI for the entries exported by the sink.

    :type client: :class:`gcloud.logging.client.Client`
    :param client: A client which holds credentials and project configuration
                   for the sink (which requires a project).
    """
    def __init__(self, name, filter_, destination, client):
        self.name = name
        self.filter_ = filter_
        self.destination = destination
        self._client = client

    @property
    def client(self):
        """Clent bound to the sink."""
        return self._client

    @property
    def project(self):
        """Project bound to the sink."""
        return self._client.project

    @property
    def full_name(self):
        """Fully-qualified name used in sink APIs"""
        return 'projects/%s/sinks/%s' % (self.project, self.name)

    @property
    def path(self):
        """URL path for the sink's APIs"""
        return '/%s' % (self.full_name)

    def _require_client(self, client):
        """Check client or verify over-ride.
        :type client: :class:`gcloud.logging.client.Client` or ``NoneType``
        :param client: the client to use.  If not passed, falls back to the
                       ``client`` stored on the current sink.
        :rtype: :class:`gcloud.logging.client.Client`
        :returns: The client passed in or the currently bound client.
        """
        if client is None:
            client = self._client
        return client

    def create(self, client=None):
        """API call:  create the sink via a PUT request

        See:
        https://cloud.google.com/logging/docs/api/ref_v2beta1/rest/v2beta1/projects.sinks/create

        :type client: :class:`gcloud.logging.client.Client` or ``NoneType``
        :param client: the client to use.  If not passed, falls back to the
                       ``client`` stored on the current sink.
        """
        client = self._require_client(client)
        data = {
            'name': self.name,
            'filter': self.filter_,
            'destination': self.destination,
        }
        client.connection.api_request(method='PUT', path=self.path, data=data)

    def exists(self, client=None):
        """API call:  test for the existence of the sink via a GET request

        See
        https://cloud.google.com/logging/docs/api/ref_v2beta1/rest/v2beta1/projects.sinks/get

        :type client: :class:`gcloud.logging.client.Client` or ``NoneType``
        :param client: the client to use.  If not passed, falls back to the
                       ``client`` stored on the current sink.
        """
        client = self._require_client(client)

        try:
            client.connection.api_request(method='GET', path=self.path)
        except NotFound:
            return False
        else:
            return True

    def reload(self, client=None):
        """API call:  sync local sink configuration via a GET request

        See
        https://cloud.google.com/logging/docs/api/ref_v2beta1/rest/v2beta1/projects.sinks/get

        :type client: :class:`gcloud.logging.client.Client` or ``NoneType``
        :param client: the client to use.  If not passed, falls back to the
                       ``client`` stored on the current sink.
        """
        client = self._require_client(client)
        data = client.connection.api_request(method='GET', path=self.path)
        self.filter_ = data['filter']
        self.destination = data['destination']
