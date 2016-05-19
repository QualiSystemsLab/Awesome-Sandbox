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
    def ClearResourcesStatus(self):
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

# ===================================
# ===================================
class SandboxEx(SandboxBase):
    def __init__(self, reservation_id, logger):
        super(SandboxEx, self).__init__(reservation_id,logger)
        found_tftp_server = False
        for resource in self.root_resources:
            if resource.model == 'Generic TFTP server':
                tftp_server_destination_path = resource.GetAttribute("TFTP path")
                self.config_files_root = 'tftp://' + resource.address + "/" + tftp_server_destination_path
                found_tftp_server=True
                break
        if not found_tftp_server:
            self.ReportError("Failed to find a TFTP server",writeToOutputWindow=True)

    # ----------------------------------
    # LoadNetworkConfig(ResourceName,config_type, RestoreMethod=Override)
    # ResourceName - The name of the resource we would like to load the config onto
    # ConfigPath – the path to the configuration file, including the configuration file name.
    # The path should include the protocol type. This input is mandatory.
    # the configuration file name doesnt include “StartUp” or “Running”
    # Restore Method – optional, if empty the default value will be taken.
    # Possible values – Append or Override
    # Default value – Override
    # The command should fail if the configuration file name doesnt include “StartUp” or “Running”
    # config_stage - Gold, Base, Snapshot...
    # A path to a config file will look like ROOT_DIR/CONFIG_STAGE/BlueprintX/resourceY_ModelZ.cfg
    # e.g. tftp://configs/Gold/Large_Office/svl290-gg07-sw1_c3850.cfg
    # Base config is an exception. The blueprint's name is not in the path
    # e.g. tftp://configs/Base/svl290-gg07-sw1_c3850.cfg
    # ----------------------------------
    def LoadConfig(self, config_stage, config_type, restore_method="Override",write_to_output = True):
        """
        Load the configuration from config files on the Blueprint's devices
        :param str config_stage:  The stage of the config e.g Gold, Base
        :param str config_type:  Possible values - StartUp or Running
        :param str restore_method: Optional. Restore method. Can be Append or Override
        """
        self.ReloadDetails()
        root_path=''
        if config_stage.lower() == 'gold' or config_stage.lower() == 'snapshot':
            root_path =self.config_files_root + '/' + config_stage + '/' + self.Blueprint_name + '/'
        elif config_stage.lower() == 'base':
            root_path =self.config_files_root + '/' + config_stage + '/'
        for resource in self.root_resources:
            try:
                config_path = root_path + resource.name + '_' + resource.model + '.cfg'
                self.ReportInfo('Loading configuration for device: ' + resource.name +
                                                                 ' from:' + config_path,write_to_output)
                resource.LoadNetworkConfig(self.id, config_path, config_type, restore_method)
                self.api_session.SetResourceLiveStatus(resource.full_path,'Online')
            except QualiError as qe:
                err = "Failed to load configuration for device " + resource.name + ". " + qe.__str__()
                self.ReportError(err,writeToOutputWindow=write_to_output,raise_error=False)
                self.api_session.SetResourceLiveStatus(resource.full_path,'Error')
            except:
                err = "Failed to load configuration for device " + resource.name + \
                      ". Unexpected error: " + sys.exc_info()[0]
                self.ReportError(err,writeToOutputWindow=write_to_output,raise_error=False)
                self.api_session.SetResourceLiveStatus(resource.full_path,'Error')

    # ----------------------------------
    # Set alias to valid/mismatch on routes that require validation
    # ----------------------------------
    def RoutesValidation(self):
        """
        Set alias to valid/mismatch on routes that require validation
        """
        try:
            updated_routes = []
            """:type : list[UpdateRouteAliasRequest]"""
            self.ReloadDetails()
            # loop over the root resources and in case this is a device that requires route validation
            # set its Adjacent attribute with value
            for root_rsc in self.root_resources:
                # Check if this devices requires route validation
                if root_rsc.IsRunRoutesValidationOn():
                    root_rsc.GetNeighbors(self.id)
            # go over the connectors list and validate the routes
            for conn in self.details.ReservationDescription.Connectors:
                status = self._GetRouteStatus(conn.Source, conn.Target)
                if status != "":
                    updated_routes.append(UpdateRouteAliasRequest(conn.Source, conn.Target, status))

            # Update the aliases in the topology
            self.api_session.UpdateRouteAliasesInReservation(self.id, updated_routes)
        except QualiError as qe:
            err = "Failed to validate routes. " + qe.__str__()
            self.ReportError(err)
        except:
            err = "Failed to validate routes. Unexpected error: " + sys.exc_info()[0]
            self.ReportError(err)

    # ----------------------------------
    # ----------------------------------
    def _GetRouteStatus(self, resource1, resource2):
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
        if not target_resource.IsRunRoutesValidationOn() or not source_resource.IsRunRoutesValidationOn():
            return ""
        # check that the target value equals the value in the Adjacent attribute
        for portAttr in self.api_session.GetResourceDetails(resource2).ResourceAttributes:
            if portAttr.Name == "Adjacent":
                if resource1 == portAttr.Value:
                    return "Valid"
                else:
                    return "Mismatch"
        # If we got here this means those are devices that need validation, but the Adjacent attribute was not found
        return "Mismatch"


    # ----------------------------------
    # ----------------------------------
    def SaveSnapshot(self, snapshot_name,config_type,write_to_output=True):
        """
        Load the configuration from the devices to the tftp
        :param str snapshot_name:  The name of the snapshot
        :param str config_type:  StartUp or Running
        """
        self.ReloadDetails()
        config_path = self.config_files_root + '/Snapshots/' + snapshot_name

        #If the snapshot name already exist (on tftp + CS Blueprints) - raise error
        try:
            snapshot_exist = True
            details =self.api_session.GetTopologyDetails(snapshot_name)
        except CloudShellAPIError:
            snapshot_exist = False
        if snapshot_exist:
            #raise QualiError(self.id, "Snapshot " +snapshot_name + " already exist. Please select a different name.")
            err = "Snapshot " +snapshot_name + " already exist. Please select a different name."
            self.ReportError(err,write_to_output)
        # save the current Sandbox as a new Blueprint with the given snapshot name
        self.api_session.SaveReservationAsTopology(self.id, topologyName=snapshot_name,includeInactiveRoutes=True)

        # check - do I need to create the snapshot folder on the tfp server if it doesn't exist?
        for resource in self.root_resources:
            try:
                self.ReportInfo('Saving configuration for device: ' + resource.name + ' to: ' + config_path, write_to_output)
                resource.SaveNetworkConfig(self.id, config_path, config_type)

            except QualiError as qe:
                err = "Failed to save configuration for device " + resource.name + ". " + qe.__str__()
                self.ReportError(err,writeToOutputWindow=write_to_output)
            except:
                err = "Failed to save configuration for device " + resource.name + \
                      ". Unexpected error: " + sys.exc_info()[0]
                self.ReportError(err,writeToOutputWindow=write_to_output)



    # ----------------------------------
    #Is this Sandbox originates from a snapshot Blueprint?
    # ----------------------------------
    def IsSnapshot(self):
        #check if there is a directory with the Blueprint's name under the snapshots dir
        envDir = self.config_files_root + '/Snapshots/' + self.Blueprint_name
        return os.path.isdir(envDir)
