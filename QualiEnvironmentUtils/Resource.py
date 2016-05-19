__author__ = 'ayelet.a'

import cloudshell.api.cloudshell_dev_helpers as dev
import cloudshell.api.cloudshell_scripts_helpers as helpers
from cloudshell.api.cloudshell_api import *
from cloudshell.api.common_cloudshell_api import *
import sys
from QualiUtils import *

#dev.attach_to_cloudshell_as('admin', 'admin', 'Global', '2f01bb1d-7e4c-464e-9398-39f57e914153',
#                            server_address='localhost', cloudshell_api_port='8028', command_parameters={},
#                            resource_name=None)




# ===================================
# ===================================
class ResourceBase(object):
    def __init__(self, resource_full_path):
        if resource_full_path != "":
            self.full_path = resource_full_path
            self.api_session = helpers.get_api_session()
            self.details = self.api_session.GetResourceDetails(resource_full_path)
            self.name = self.details.Name
            self.address = self.details.Address
            self.model = self.details.ResourceModelName
            self.commands = self.api_session.GetResourceCommands(resource_full_path).Commands
            self.attributes = self.details.ResourceAttributes

    # -----------------------------------------
    # -----------------------------------------
    def GetAttribute(self, attribute_name):
        for attribute in self.attributes:
            if attribute.Name == attribute_name:
                return attribute.Value
        raise QualiError(self.name, "Attribute: " + attribute_name + " not found")
    # -----------------------------------------
    # implement the command to get the neighbors and their ports
    # will return a dictionary of device's name and its port
    # -----------------------------------------
    def GetNeighbors(self, reservation_id):
        """
        Launch the GetNeighbors command on the device
        :param str reservation_id:  Reservation id.
        """
        # Run executeCommand with the getNeighbors command and its params (ConfigPath,RestoreMethod)
        try:
            self.ExecuteCommand(reservation_id, 'GetNeighbors', printOutput=True)
        except QualiError as error:
            raise QualiError(self.name, "Failed to update neighbors: " + error.message)
        except:
            raise QualiError(self.name, "Failed to update neighbors. Unexpected error:" + sys.exc_info()[0])

    # -----------------------------------------
    # -----------------------------------------
    def LoadNetworkConfig(self, reservation_id, config_path, config_type, restore_method='Override'):
        """
        Load config from a configuration file on the device
        :param str reservation_id:  Reservation id.
        :param config_path:  The path to the config file
        :param config_type:  StartUp or Running
        :param restore_method:  Optional. Restore method. Can be Append or Override.
        """
        # Run executeCommand with the restore command and its params (ConfigPath,RestoreMethod)
        try:
            self.ExecuteCommand(reservation_id, 'Restore',
                                commandInputs=[InputNameValue('source_file', str(config_path)),
                                               InputNameValue('clear_config', str(restore_method)),
                                               InputNameValue('config_type', str(config_type))],
                                printOutput=True)
        except QualiError as qerror:
            raise QualiError(self.name, "Failed to load configuration: " + qerror.message)
        except:
            raise QualiError(self.name, "Failed to load configuration. Unexpected error:" + sys.exc_info()[0])

    # -----------------------------------------
    # -----------------------------------------
    def SaveConfig(self, reservation_id, config_path, config_type):
        """
        Save config from the device
        :param str reservation_id:  Reservation id.
        :param config_path:  The path where to save the config file
        :param config_type:  StartUp or Running
        """
        # Run executeCommand with the restore command and its params (ConfigPath,RestoreMethod)
        try:
#             self.ExecuteCommand(reservation_id, 'Save',
#                                commandInputs=[InputNameValue('Configuration Type', str(config_type)),
#                                               InputNameValue('Folder Path', str(config_path))],
#                                printOutput=True)
             self.ExecuteCommand(reservation_id, 'Save',
                                commandInputs=[InputNameValue('ConfigurationType', str(config_type)),
                                               InputNameValue('Path', str(config_path))],
                                printOutput=True)
            #TODO?
            #check the output is the created file name

        except QualiError as qerror:
            raise QualiError(self.name, "Failed to load configuration: " + qerror.message)
        except:
            raise QualiError(self.name, "Failed to load configuration. Unexpected error:" + sys.exc_info()[0])

    # -----------------------------------------
    # -----------------------------------------
    # noinspection PyPep8Naming,PyDefaultArgument
    def ExecuteCommand(self, reservation_id, commandName, commandInputs=[], printOutput=False):
        """
        Executes a command
        :param str reservation_id:  Reservation id.
        :param str commandName:  Command Name - Specify the name of the command.
        :param list[InputNameValue] commandInputs:  Command Inputs - Specify a matrix of input names and values
        required for executing the command.
        :param bool printOutput:  Print Output - Defines whether to print the command output
         in the Sandbox command output window.
        :rtype: CommandExecutionCompletedResultInfo
        """
        # check the command exists on the device
        if self.commands.__sizeof__() > 0:
            # Run executeCommand with the restore command and its params (ConfigPath,RestoreMethod)
            try:
                return helpers.get_api_session().ExecuteCommand(reservation_id, self.name, 'Resource', commandName,
                                                         commandInputs, printOutput)
            except CloudShellAPIError as error:
                raise QualiError(self.name, error.message)


        else:
            raise QualiError(self.name, 'No commands were found')

    # -----------------------------------------
    # -----------------------------------------
    def IsRunRoutesValidationOn(self):
        """
        Look for the attribute indicating if this device requires route validation
        :rtype: bool
        """
        for attr in self.attributes:
            if attr.Name == 'RunRoutesValidation':
                if attr.Value == "True":
                    return True
                else:
                    return False
            return False
