# coding=utf-8
from Sandbox import *


class NetworkingHealthCheck():
    def __init__(self, sandbox):
        """
        :param SandboxBase sandbox:  The sandbox health check will be done in
        """
        self.sandbox = sandbox


    # ----------------------------------
    # Set alias to valid/mismatch on routes that require validation
    # ----------------------------------
    def routes_validation(self):
        """
        Set alias to valid/mismatch on routes that require validation
        """
        try:
            updated_routes = []
            """:type : list[UpdateRouteAliasRequest]"""

            # loop over the root resources and in case this is a device that requires route validation
            # set its Adjacent attribute with value
            root_resources = self.sandbox.get_root_resources()
            for root_rsc in root_resources:
                # Check if this devices requires route validation
                RunRoutesValidationAttr = root_rsc.get_attribute('RunRoutesValidation')
                if RunRoutesValidationAttr == 'True':
                    root_rsc.get_neighbors(self.id)
            # go over the connectors list and validate the routes
            details = self.sandbox.get_details()
            for conn in details.ReservationDescription.Connectors:
                status = self._get_route_status(conn.Source, conn.Target)
                if status != "":
                    updated_routes.append(UpdateRouteAliasRequest(conn.Source, conn.Target, status))

            # Update the aliases in the topology
            self.sandbox.api_session.UpdateRouteAliasesInReservation(self.id, updated_routes)
        except QualiError as qe:
            err = "Failed to validate routes. " + str(qe)
            self.sandbox.report_error(err)
        except:
            err = "Failed to validate routes. Unexpected error: " + str(sys.exc_info()[0])
            self.sandbox.report_error(err)

    # ----------------------------------
    # ----------------------------------
    def _get_route_status(self, resource1, resource2):
        """
        Find if the route is valid. Valid means the two devices can see each other
        The Adjacent attribute on the port will hold the data of the other device's port connected to it
        :param resource1: First resource in route
        :param resource2: Second resource in route
        """
        # check route validation is set to true on both resources
        # Routes are only validated between 2 devices that require validation
        source_resource = ResourceBase(resource1)
        target_resource = ResourceBase(resource2)
        targetRunRoutesValidation = target_resource.get_attribute('RunRoutesValidation')
        sourceRunRoutesValidation = source_resource.get_attribute('RunRoutesValidation')
        if targetRunRoutesValidation == 'False' or not sourceRunRoutesValidation == 'False':
            return ""
        # check that the target value equals the value in the Adjacent attribute
        for portAttr in self.sandbox.api_session.GetResourceDetails(resource2).ResourceAttributes:
            if portAttr.Name == "Adjacent":
                if resource1 == portAttr.Value:
                    return "Valid"
                else:
                    return "Mismatch"
        # If we got here this means those are devices that need validation, but the Adjacent attribute was not found
        return "Mismatch"
