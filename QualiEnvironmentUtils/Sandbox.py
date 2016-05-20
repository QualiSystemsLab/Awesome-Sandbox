# coding=utf-8
from Resource import *
from cloudshell.core.logger.qs_logger import *

#dev.attach_to_cloudshell_as('admin', 'admin', 'Global', '2f01bb1d-7e4c-464e-9398-39f57e914153',
#                            server_address='localhost', cloudshell_api_port='8028', command_parameters={},
#                            resource_name=None)


# ===================================
# ===================================
class SandboxBase(object):
    def __init__(self, reservation_id, logger):
        try:
            self._logger = logger
            """:type : logging.Logger"""
            self.api_session = helpers.get_api_session()
            self.id = reservation_id
            #self.Blueprint_name = helpers.get_reservation_context_details().environment_name
            self.details = self.api_session.GetReservationDetails(self.id)
            self.Blueprint_name = self.details.ReservationDescription.TopologiesInfo[0].Name
            self.root_resources = []
            """:type : list[ResourceBase]"""
            self._GetRootResources()

        except:
            err = "Failed to initialize the Sandbox. Unexpected error:" + \
                  str(sys.exc_info()[0])
            self.ReportError(err)

    # ----------------------------------
    # ----------------------------------
    def WriteMessageToOutput(self,error_message, severity_level=0):
        """
            Write a message to the output window
        """
        #todo - format the message according ot the severity level
        # error level 1 in red
        self.api_session.WriteMessageToReservationOutput(self.id, error_message)

    # ----------------------------------
    def ReportError(self, error_message, raise_error = True, writeToOutputWindow = False):
        """
        Report on an error to the log file, output window is optional.There is also an option to raise the error up
        :param str error_message:  The error message you would like to present
        :param bool raise_error:  Do you want to throw an exception
        :param bool writeToOutputWindow:  Would you like to write the message to the output window
        """
        self._logger.error(error_message)
        if writeToOutputWindow:
            self.WriteMessageToOutput(error_message)
        if raise_error:
            raise QualiError(self.id, error_message)

    # ----------------------------------
    def ReportInfo(self, message, writeToOutputWindow = False):
        """
        Report information to the log file, output window is optional.
        :param str message:  The message you would like to present
        :param bool writeToOutputWindow:  Would you like to write the message to the output window?
        """
        self._logger.info(message)
        if writeToOutputWindow:
            self.WriteMessageToOutput(message)

    # ----------------------------------
    def _GetRootResources(self):
        #       """
        #       Get the root resources
        #       :rtype: list[ResourceBase]
        #       """
        #Clear the list and re-populate
        del self.root_resources[:]
        resources = self.api_session.GetReservationDetails(self.id).ReservationDescription.Resources

        # Loop over all devices in the topo for each device:
        for resource in resources:
            if resource.FullAddress.find('/') == -1:
           #     if resource.FolderFullPath != '':
           #         self.root_resources.append(ResourceBase(resource.FolderFullPath + '/' + resource.Name))
           #     else:
           #         self.root_resources.append(ResourceBase(resource.Name))
                self.root_resources.append(ResourceBase(resource.Name))

    # ----------------------------------
    # ----------------------------------
    def clear_all_resources_live_status(self):
        """
            Clear the live status from all the devices
        """
        self.ReloadDetails()
        for resource in self.root_resources:
                self.api_session.SetResourceLiveStatus(resource.full_path,'')


    # ----------------------------------
    # ----------------------------------
    def ReloadDetails(self):
        """
            Retrieves all details and parameters for a specified Sandbox, including its resources, routes and route segments, topologies, and Sandbox conflicts.
        """
        try:
            self.details = self.api_session.GetReservationDetails(self.id)
            self._GetRootResources()
        except QualiError as qe:
            err = "Failed to get the Sandbox's details. " + qe.__str__()
            self.ReportError(err)
        except:
            err = "Failed to get the Sandbox's details. Unexpected error: " + sys.exc_info()[0]
            self.ReportError(err)

    # ----------------------------------
    # ----------------------------------
    def ActivateRoutes(self,write_to_output=True):
        """
        Activate the routes in the topology
        """
        try:
            self.ReportInfo("Connecting routes",write_to_output)
            self.api_session.ActivateTopology(self.id, self.Blueprint_name)
            self.ReportInfo("Routes connected",write_to_output)
        except CloudShellAPIError as error:
            err = "Failed to activate routes. " + error.message
            self.ReportError(err,write_to_output)
        except:
            err = "Failed to activate routes. Unexpected error: " + sys.exc_info()[0]
            self.ReportError(err,write_to_output)

    # -----------------------------------------
    # -----------------------------------------
    def ExecuteCommand(self, commandName, commandInputs=[], printOutput=False):
        """
        Executes a command
        :param str commandName:  Command Name - Specify the name of the command.
        :param list[InputNameValue] commandInputs:  Command Inputs - Specify a matrix of input names and values
        required for executing the command.
        :param bool printOutput:  Print Output - Defines whether to print the command output
         in the Sandbox command output window.
        :rtype: CommandExecutionCompletedResultInfo
        """
        try:
            return self.api_session.ExecuteTopologyCommand(self.id,commandName,commandInputs,printOutput)

        except CloudShellAPIError as error:
            raise QualiError(self.name, error.message)

    # -----------------------------------------
    # -----------------------------------------
    def SaveSandboxAsBlueprint(self, blueprint_name,write_to_output=True):
        try:
            snapshot_exist = True
            details =self.api_session.GetTopologyDetails(blueprint_name)
        except CloudShellAPIError:
            snapshot_exist = False
        if snapshot_exist:
            err = "Blueprint " +blueprint_name + " already exist. Please select a different name."
            self.ReportError(err,writeToOutputWindow=write_to_output)
        # save the current Sandbox as a new Blueprint with the given snapshot name
        self.api_session.SaveReservationAsTopology(self.id, topologyName=blueprint_name,includeInactiveRoutes=True)


