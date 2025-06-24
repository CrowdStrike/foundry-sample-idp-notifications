from crowdstrike.foundry.function import APIError, Function, Request, Response
from typing import Dict, Optional
from falconpy import IdentityProtection

func = Function.instance()


@func.handler(method='GET', path='/identity-notifications')
def get_notifications(request: Request, config: Optional[Dict[str, any]] = None) -> Response:
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
            errors=[APIError(code=response.get("status_code"), message=response.get("body").get("errors")[0].get("message"))],
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
    
    except Exception as e:
        return Response(
            code=500,
            errors=[APIError(code=500, message=f"Internal server error: {str(e)}")],
        )

@func.handler(method='GET', path='/identity-dc-status')
def get_dc_status(request: Request, config: Optional[Dict[str, any]] = None) -> Response:
  
    try:
        # Getting input variables
        status = request.body.get("status")
        domains = request.body.get("domains")
        
        
        # Initialize client without explicit authentication parameters
        falcon = IdentityProtection()

        all_device_ids = []
        offset = ""
        limit = 100
        
        #Create filter string in FQL
        filter=[]
        if status is not None:
          filter_status = [f"status:'{s}'" for s in status]
          filter_status = ','.join(filter_status)
          filter_status = f"({filter_status})"
          filter.append(filter_status)
          
        if domains is not None:
          filter_domains = [f"machine_domain:'{d}'" for d in domains]
          filter_domains = ','.join(filter_domains)
          filter_domains = f"({filter_domains})"
          filter.append(filter_domains)
        
        filter='+'.join(filter)
        
        while True:
            response = falcon.query_sensors(
                limit=limit,
                offset=offset,
                filter=filter
            )
            
            if response.get("status_code") != 200:
              return Response(
                code=response.get("status_code"),
                errors=[APIError(code=response.get("status_code"), message=response.get("body").get("errors")[0].get("message"))],
              )
            
            # Add device IDs to our list
            device_ids = response["body"]["resources"]
            all_device_ids.append(device_ids)
            
            # Check if we need to paginate
            pagination = response["body"]["meta"]["pagination"]
            if pagination["total"] <= (pagination["offset"] + pagination["limit"]):
              break
            
            # Update offset for next page
            offset = pagination["offset"] + pagination["limit"]
        
        all_device_details = []
    
    # Process in batches of 5000 (API limit)
        batch_size = 5000
        for i in range(0, len(device_ids), batch_size):
            batch = device_ids[i:i+batch_size]
            
            response = falcon.get_sensor_details(ids=batch)
            
            if response.get("status_code") != 200:
              return Response(
                code=response.get("status_code"),
                errors=[APIError(code=response.get("status_code"), message=response.get("body").get("errors")[0].get("message"))],
              )
            
            # Add device details to our list
            device_details = response["body"]["resources"]
            all_device_details.append(device_details)
        # Prepare response body
        body = {
          "domain_controllers" : all_device_details
        }

        return Response(
            body=body,
            code=200,
        )
    
    except Exception as e:
        return Response(
            code=500,
            errors=[APIError(code=500, message=f"Internal server error: {str(e)}")],
        )

if __name__ == '__main__':
    func.run()
