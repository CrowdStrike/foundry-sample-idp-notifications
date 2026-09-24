"""Function to retrieve Falcon Identity Protection notifications and domain controller status."""
from typing import Dict, Optional

from crowdstrike.foundry.function import APIError, Function, Request, Response
from falconpy import IdentityProtection

FUNC = Function.instance()

# Number of sensor IDs to request per page
QUERY_LIMIT = 100
# Process sensor details in batches of 5000 (API limit)
BATCH_SIZE = 5000


def build_sensor_filter(status: Optional[list], domains: Optional[list]) -> str:
    """Build an FQL filter string for domain controller sensors.

    Args:
        status: Optional list of sensor statuses to match
        domains: Optional list of machine domains to match

    Returns:
        FQL filter string
    """
    sensor_filter = []
    if status is not None:
        filter_status = [f"status:'{s}'" for s in status]
        filter_status = ','.join(filter_status)
        filter_status = f"({filter_status})"
        sensor_filter.append(filter_status)

    if domains is not None:
        filter_domains = [f"machine_domain:'{d}'" for d in domains]
        filter_domains = ','.join(filter_domains)
        filter_domains = f"({filter_domains})"
        sensor_filter.append(filter_domains)

    return '+'.join(sensor_filter)


@FUNC.handler(method='GET', path='/identity-notifications')
def get_notifications(request: Request, _config: Optional[Dict[str, object]] = None) -> Response:
    """Retrieve Falcon Identity Protection timeline notifications.

    Args:
        request: Request object containing duration, notification_status, and categories in body
        _config: Function configuration (unused)

    Returns:
        Response object with notification events or error
    """
    if len(request.body) == 0:
        return Response(
            code=400,
            errors=[APIError(code=400, message='empty body')]
        )

    try:
        # Getting input variables
        duration = request.body.get("duration")
        notification_status = request.body.get("notification_status")
        categories = request.body.get("categories")

        # Validate required parameters
        if not all([duration, categories]):
            return Response(
                code=400,
                errors=[APIError(code=400, message="Missing required parameters: duration and categories are required")],
            )

        # Creating the GraphQL API query
        idp_query = '''
query ($categories: [TimelineEventCategory!], $open: Boolean, $startTime: DateTimeInput) {
  timeline(categories: $categories, first: 1000, open: $open, sortOrder: DESCENDING, startTime: $startTime) {
    ...TimelineNotificationEventDetails
  }
}

fragment TimelineNotificationEventDetails on TimelineEventConnection {
  edges {
    cursor
    node {
      eventType
      timestamp
      startTime
      endTime
      ... on TimelineNotificationEvent {
        state {
          dismissed
          resolved
        }
      }
      ... on TimelineDomainRemovalEvent {
        domain
      }
      ... on TimelineDomainControllerNotificationEvent {
        domainControllerEntity {
          ...MinimalEntityDescriptor
        }
      }
      ... on TimelineUncoveredDomainControllerEvent {
        domain
      }
      ... on TimelineConnectorFailureEvent {
        connectorType
        providerType
        connectorStatus
        errorDetails{
          message
        }
      }
    }
  }
}

fragment MinimalEntityDescriptor on Entity {
  entityId
  primaryDisplayName
  secondaryDisplayName
  archived
}
        '''

        # Creating the GraphQL API variables
        variables = {
            'categories': categories,
            'startTime': duration,
            'open': notification_status
        }

        # Initialize client without explicit authentication parameters
        falcon = IdentityProtection()

        response = falcon.graphql(query=idp_query, variables=variables)

        # Prepare response body
        body = {
        }

        if response.get("status_code") != 200:
            return Response(
                code=response.get("status_code"),
                errors=[
                    APIError(
                        code=response.get("status_code"),
                        message=response.get("body").get("errors")[0].get("message")
                    )
                ],
            )

        # Extract events from the correct path in the response
        events = []
        timeline_edges = response.get("body", {}).get("data", {}).get("timeline", {}).get("edges", [])
        for edge in timeline_edges:
            if edge and "node" in edge:
                events.append(edge["node"])

        body['events'] = events

        return Response(
            body=body,
            code=200,
        )

    except Exception as e:  # pylint: disable=broad-except
        return Response(
            code=500,
            errors=[APIError(code=500, message=f"Internal server error: {str(e)}")],
        )


@FUNC.handler(method='GET', path='/identity-dc-status')
def get_dc_status(request: Request, _config: Optional[Dict[str, object]] = None) -> Response:
    """Retrieve sensor details for domain controllers.

    Args:
        request: Request object containing optional status and domains lists in body
        _config: Function configuration (unused)

    Returns:
        Response object with domain controller details or error
    """
    try:
        # Getting input variables
        status = request.body.get("status")
        domains = request.body.get("domains")

        # Initialize client without explicit authentication parameters
        falcon = IdentityProtection()

        all_device_ids = []
        offset = ""

        # Create filter string in FQL
        sensor_filter = build_sensor_filter(status, domains)

        while True:
            response = falcon.query_sensors(
                limit=QUERY_LIMIT,
                offset=offset,
                filter=sensor_filter
            )

            if response.get("status_code") != 200:
                return Response(
                    code=response.get("status_code"),
                    errors=[
                        APIError(
                            code=response.get("status_code"),
                            message=response.get("body").get("errors")[0].get("message")
                        )
                    ],
                )

            # Add device IDs to our list
            all_device_ids.extend(response["body"]["resources"])

            # Check if we need to paginate
            pagination = response["body"]["meta"]["pagination"]
            if pagination["total"] <= (pagination["offset"] + pagination["limit"]):
                break

            # Update offset for next page
            offset = pagination["offset"] + pagination["limit"]

        all_device_details = []

        for i in range(0, len(all_device_ids), BATCH_SIZE):
            batch = all_device_ids[i:i+BATCH_SIZE]

            response = falcon.get_sensor_details(ids=batch)

            if response.get("status_code") != 200:
                return Response(
                    code=response.get("status_code"),
                    errors=[
                        APIError(
                            code=response.get("status_code"),
                            message=response.get("body").get("errors")[0].get("message")
                        )
                    ],
                )

            # Add device details to our list
            all_device_details.extend(response["body"]["resources"])

        return Response(
            body={
                "domain_controllers": all_device_details
            },
            code=200,
        )

    except Exception as e:  # pylint: disable=broad-except
        return Response(
            code=500,
            errors=[APIError(code=500, message=f"Internal server error: {str(e)}")],
        )


if __name__ == '__main__':
    FUNC.run()
