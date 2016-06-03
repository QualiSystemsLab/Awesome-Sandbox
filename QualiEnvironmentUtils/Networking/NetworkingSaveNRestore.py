# coding=utf-8
from Sandbox import *
from Networking.ConfigFileManager import *
from Networking.PoolManager import *

class NetworkingSaveRestore():
    def __init__(self, sandbox):
        """
        Get the root directory for the config files on the tftp server
        :param SandboxBase sandbox:  The sandbox save & restore will be done in
        """
        self.sandbox = sandbox
        tftp_resource = self.sandbox.get_tftp_resource()
        if tftp_resource is not None:
            tftp_server_destination_path = tftp_resource.get_attribute("TFTP Network configs path")
            if tftp_server_destination_path != "":
                self.config_files_root = 'tftp://' + tftp_resource.address + "/" + tftp_server_destination_path
            else:
                self.sandbox.report_error("Failed to find the network's tftp path", raise_error=True,
                                          write_to_output_window=False)
        else:
            self.sandbox.report_error("Failed to find a tftp resource in the sandbox", raise_error=True,
                                      write_to_output_window=False)

        pool_resource = self.sandbox.get_pool_resource()
        #update all the resources' attributes with the data from the pool
        if pool_resource is not None:
            pool_manager = PoolManager(sandbox = self.sandbox, pool_resource = pool_resource)
            pool_manager.push_data_from_pool_to_sandbox()
    # ----------------------------------
    # load_network_config(ResourceName,config_type, RestoreMethod=Override)
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
    def load_config(self, config_stage, config_type, restore_method="Override", config_set_name='', ignore_models=[],
                    write_to_output=True):
        """
        Load the configuration from config files on the Blueprint's devices
        :param str config_stage:  The stage of the config e.g Gold, Base
        :param str config_type:  Possible values - StartUp or Running
        :param str restore_method: Optional. Restore method. Can be Append or Override
        :param str config_set_name: Optional. If we have multiple configuration sets for the same blueprint.
        the nam of the set selected by the user
        :param list[str] ignore_models: Optional. Models that should be ignored and not load config on the device
        """

        config_file_mgr = ConfigFileManager(self.sandbox)
        root_path = ''
        loaded_ip_address = ''
        if config_stage.lower() == 'gold' or config_stage.lower() == 'snapshot':
            root_path = self.config_files_root + '/' + config_stage + '/' + self.sandbox.Blueprint_name + '/'
            if config_set_name != '':
                root_path = root_path + config_set_name + '/'
        elif config_stage.lower() == 'base':
            root_path = self.config_files_root + '/' + config_stage + '/'
        root_resources = self.sandbox.get_root_resources()
        """:type : list[ResourceBase]"""
        for resource in root_resources:

            load_config_to_device = True
            # check if the device is marked for not loading config during
            try:
                disable_load_config = resource.get_attribute("Disable Load Config")
                if disable_load_config:
                    load_config_to_device = False
            except QualiError:  # if attribute not found then assume load config in enabled
                pass
            for ignore_model in ignore_models:
                if resource.model.lower() == ignore_model.lower():
                    load_config_to_device = False
                    break
            if load_config_to_device == True:
                try:
                    config_path = root_path + resource.alias + '_' + resource.model + '.cfg'
                    #if originated from an abstract resource - create a concrete config file from the template
                    #it will be saved under /temp/<SandboxId>/<Resource name>_<model>.cfg
                    #tftp://configs/Gold/Large_Office/Set1/temp/477f8eb2-213b-4065-81c8-a78e1306274b/svl290-gg07-sw1_c3850.cfg
                    is_resource_abstract = self.sandbox.is_abstract(resource.alias)
                    if is_resource_abstract:
                        concrete_file_path = root_path + 'temp/' + self.sandbox.id +'/'+ resource.name + '_' + \
                                             resource.model + '.cfg'
                        config_file_mgr.create_file_from_template(template_path = config_path,
                                                                  destination_path = concrete_file_path)
                        config_path = concrete_file_path
                        check_if_need_to_update_address=True
                    self.sandbox.report_info(
                        'Loading configuration for device: ' + resource.name + ' from:' + config_path, write_to_output)
                    resource.load_network_config(self.sandbox.id, config_path, config_type, restore_method)
                    # If we changed the management ip address during the load of the config-
                    # Update the resource's address in CloudShell by calling set_address()
                    if config_stage.lower() == 'gold' or config_stage.lower() == 'snapshot':
                        loaded_ip_address = resource.get_attribute("Gold management ip")
                    elif config_stage.lower() == 'base':
                        loaded_ip_address = resource.get_attribute("Base management ip")
                    if is_resource_abstract and resource.address != loaded_ip_address:
                        resource.set_address(loaded_ip_address)
                        #TODO - Reset the driver/session to work with the new ip address

                    self.sandbox.api_session.SetResourceLiveStatus(resource.name, 'Online')
                except QualiError as qe:
                    err = "Failed to load configuration for device " + resource.name + ". " + str(qe)
                    self.sandbox.report_error(err, write_to_output_window=write_to_output, raise_error=False)
                    self.sandbox.api_session.SetResourceLiveStatus(resource.name, 'Error')
                except:
                    err = "Failed to load configuration for device " + resource.name + \
                          ". Unexpected error: " + str(sys.exc_info()[0])
                    self.sandbox.report_error(err, write_to_output_window=write_to_output, raise_error=False)
                    self.sandbox.api_session.SetResourceLiveStatus(resource.name, 'Error')

    # ----------------------------------
    # ----------------------------------
    def save_config(self, snapshot_name, config_type, ignore_models=[], write_to_output=True):
        """
        Load the configuration from the devices to the tftp
        :param str snapshot_name:  The name of the snapshot
        :param str config_type:  StartUp or Running
        """
        root_resources = self.sandbox.get_root_resources()

        config_path = self.config_files_root + '/Snapshots/' + snapshot_name

        # TODO: check - do I need to create the snapshot folder on the tfp server if it doesn't exist?
        for resource in root_resources:
            save_config_from_device = True
            for ignore_model in ignore_models:
                if resource.model.lower() == ignore_model.lower():
                    save_config_from_device = False
                    break
            if save_config_from_device == True:
                try:
                    self.sandbox.report_info(
                        'Saving configuration for device: ' + resource.name + ' to: ' + config_path, write_to_output)
                    resource.SaveNetworkConfig(self.sandbox.id, config_path, config_type)

                except QualiError as qe:
                    err = "Failed to save configuration for device " + resource.name + ". " + str(qe)
                    self.sandbox.report_error(err, write_to_output_window=write_to_output)
                except:
                    err = "Failed to save configuration for device " + resource.name + \
                          ". Unexpected error: " + str(sys.exc_info()[0])
                    self.sandbox.report_error(err, write_to_output_window=write_to_output)

    # ----------------------------------
    # Is this Sandbox originates from a snapshot Blueprint?
    # ----------------------------------
    def is_snapshot(self):
        # check if there is a directory with the Blueprint's name under the snapshots dir
        envDir = self.config_files_root + '/Snapshots/' + self.sandbox.Blueprint_name
        return os.path.isdir(envDir)
