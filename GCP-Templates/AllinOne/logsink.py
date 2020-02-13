# Copyright 2018 Google Inc. All rights reserved.
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

""" This template creates a logsink (logging sink). """

def create_pubsub(context, logsink_name):
    """ Create the pubsub destination. """

    dest_properties = []
    if 'pubsubProperties' in context.properties:
        dest_prop = context.properties['pubsubProperties']
        access_control = dest_prop.get('accessControl', [])
        access_control.append(
            {
                'role': 'roles/pubsub.admin',
                'members': ['$(ref.' + logsink_name + '.writerIdentity)']
            }
        )

        dest_prop['accessControl'] = access_control
        dest_properties = [
            {
                'name': context.properties['destinationName'],
                'type': 'pubsub.py',
                'properties': dest_prop
            }
        ]

    return dest_properties

def generate_config(context):
    """ Entry point for the deployment resources. """

    project_id = context.env['project']
    name = context.properties.get('name', context.env['name'])

    properties = {
        'name': name,
        'uniqueWriterIdentity': context.properties['uniqueWriterIdentity'],
        'sink': name
    }

    if 'projectId' in context.properties:
        source_id = context.properties.get('projectId')
        source_type = 'projects'

    properties['parent'] = '{}/{}'.format(source_type, source_id)

    dest_properties = []
    if context.properties['destinationType'] == 'pubsub':
        dest_properties = create_pubsub(context, name)
        destination = 'pubsub.googleapis.com/projects/{}/topics/{}'.format(
            project_id,
            context.properties['destinationName']
        )
   

    properties['destination'] = destination

    sink_filter = context.properties.get('filter')
    if sink_filter:
        properties['filter'] = sink_filter

    base_type = 'gcp-types/logging-v2:'
    resource = {
        'name': name,
        'type': base_type + source_type + '.sinks',
        'properties': properties
    }

    resources = [resource]

    if dest_properties:
        resources.extend(dest_properties)
        if context.properties['destinationType'] == 'pubsub':
            resource['metadata'] = {
                'dependsOn': [context.properties['destinationName']]
            }

    return {
        'resources':
            resources,
        'outputs':
            [
                {
                    'name': 'writerIdentity',
                    'value': '$(ref.{}.writerIdentity)'.format(name)
                }
            ]
    }
