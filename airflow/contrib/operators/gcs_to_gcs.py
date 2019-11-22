# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
This module is deprecated. Please use `airflow.operators.gcs_to_gcs`.
"""

import warnings

# pylint: disable=unused-import
from airflow.operators.gcs_to_gcs import GoogleCloudStorageToGoogleCloudStorageOperator  # noqa

class GoogleCloudStorageToGoogleCloudStorageOperator(BaseOperator):
    """
    Copies an object from a bucket to another, with renaming if requested.

    :param source_bucket: The source Google cloud storage bucket where the object is.
    :type source_bucket: string
    :param source_object: The source name of the object to copy in the Google cloud
        storage bucket.
        If wildcards are used in this argument:
            You can use only one wildcard for objects (filenames) within your
            bucket. The wildcard can appear inside the object name or at the
            end of the object name. Appending a wildcard to the bucket name is
            unsupported.
    :type source_object: string
    :param destination_bucket: The destination Google cloud storage bucket
    where the object should be.
    :type destination_bucket: string
    :param destination_object: The destination name of the object in the
    destination Google cloud
        storage bucket.
        If a wildcard is supplied in the source_object argument, this is the
        folder that the files will be
        copied to in the destination bucket.
    :type destination_object: string
    :param move_object: When move object is True, the object is moved instead
    of copied to the new location.
                        This is the equivalent of a mv command as opposed to a
                        cp command.
    :type move_object: bool
    :param google_cloud_storage_conn_id: The connection ID to use when
        connecting to Google cloud storage.
    :type google_cloud_storage_conn_id: string
    :param delegate_to: The account to impersonate, if any.
        For this to work, the service account making the request must have
        domain-wide delegation enabled.
    :type delegate_to: string
    """
    template_fields = ('source_bucket', 'source_object', 'destination_bucket',
                       'destination_object',)
    ui_color = '#f0eee4'

    @apply_defaults
    def __init__(self,
                 source_bucket,
                 source_object,
                 destination_bucket=None,
                 destination_object=None,
                 move_object=False,
                 google_cloud_storage_conn_id='google_cloud_storage_default',
                 delegate_to=None,
                 *args,
                 **kwargs):
        super(GoogleCloudStorageToGoogleCloudStorageOperator, self).__init__(
            *args, **kwargs)
        self.source_bucket = source_bucket
        self.source_object = source_object
        self.destination_bucket = destination_bucket
        self.destination_object = destination_object
        self.move_object = move_object
        self.google_cloud_storage_conn_id = google_cloud_storage_conn_id
        self.delegate_to = delegate_to

    def execute(self, context):

        hook = GoogleCloudStorageHook(
            google_cloud_storage_conn_id=self.google_cloud_storage_conn_id,
            delegate_to=self.delegate_to
        )

        if '*' in self.source_object:
            wildcard_position = self.source_object.index('*')
            objects = hook.list(self.source_bucket,
                                prefix=self.source_object[:wildcard_position],
                                delimiter=self.source_object[wildcard_position + 1:])
            for source_object in objects:
                self.log.info('Executing copy of gs://{0}/{1} to '
                              'gs://{2}/{3}/{1}'.format(self.source_bucket,
                                                        source_object,
                                                        self.destination_bucket,
                                                        self.destination_object,
                                                        source_object))
                hook.copy(self.source_bucket, source_object,
                          self.destination_bucket, "{}/{}".format(self.destination_object,
                                                                  source_object))
                if self.move_object:
                    hook.delete(self.source_bucket, source_object)

        else:
            self.log.info('Executing copy: %s, %s, %s, %s', self.source_bucket,
                          self.source_object,
                          self.destination_bucket or self.source_bucket,
                          self.destination_object or self.source_object)
            hook.copy(self.source_bucket, self.source_object,
                      self.destination_bucket, self.destination_object)

            if self.move_object:
                hook.delete(self.source_bucket, self.source_object)
warnings.warn(
    "This module is deprecated. Please use `airflow.operators.gcs_to_gcs`.",
    DeprecationWarning, stacklevel=2
)

