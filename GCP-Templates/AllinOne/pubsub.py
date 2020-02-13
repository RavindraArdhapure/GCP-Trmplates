""" This template creates a Pub/Sub (publish-subscribe) service. """

def create_subscription(resource_name, spec, topic_resource_name, spec_index):
    """ Create a pull/push subscription from the simplified spec. """

    subscription = {
        'name': '{}-subscription-{}'.format(resource_name, spec_index),
        'type': 'pubsub.v1.subscription',
        'properties':{
            'subscription': spec['name'],
            'topic': '$(ref.{}.name)'.format(topic_resource_name)
        }
    }

    push_endpoint = spec.get('pushEndpoint')
    if push_endpoint is not None:
        subscription['properties']['pushConfig'] = {
            'pushEndpoint': push_endpoint
        }

    ack_deadline_seconds = spec.get('ackDeadlineSeconds')
    if ack_deadline_seconds is not None:
        subscription['properties']['ackDeadlineSeconds'] = ack_deadline_seconds

    return subscription


def create_pubsub(resource_name, pubsub_spec):
    """ Create a topic with subscriptions. """

    topic_name = pubsub_spec.get('topic', resource_name)
    topic_resource_name = '{}-topic'.format(resource_name)
    topic = {
        'name': topic_resource_name,
        'type': 'pubsub.v1.topic',
        'properties':{
            'topic': topic_name
        }
    }

    subscription_specs = pubsub_spec.get('subscriptions', [])
    subscriptions = [create_subscription(resource_name, spec,
                                         topic_resource_name, index)
                     for (index, spec)
                     in enumerate(subscription_specs, 1)]

    return [topic] + subscriptions

def create_topic_outputs(topic_resource):
    """ Create outputs for the topic. """

    return [
        {
            'name': 'topicName',
            'value': '$(ref.{}.name)'.format(topic_resource['name'])
        }
    ]

def generate_config(context):
    """ Entry point for the deployment resources. """

    resource_name = context.env['name']
    pubsub_resources = create_pubsub(resource_name, context.properties)
    pubsub_outputs = create_topic_outputs(pubsub_resources[0])

    return {
        'resources': pubsub_resources,
        'outputs':   pubsub_outputs
    }