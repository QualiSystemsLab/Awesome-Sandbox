# coding=utf-8
from Sandbox import *
import tftpy

# ===================================
# ===================================
class ConfigFileManager(object):
    def __init__(self, sandbox):
        """
        :param SandboxBase sandbox:  The sandbox the config file mgr will work with
        """
        self.sandbox = sandbox
        self.tftp_server = self.sandbox.get_tftp_resource()

    #        self.is_there_ip_pool = False
    #        root_resources = self.sandbox.get_root_resources()
    #        for resource in root_resources:
    #                if resource.model == 'Generic IP Pool Device':
    #                    self.is_there_ip_pool = True
    #                    self.ip_pool = resource
    #                    break

    # TODO-For future implementation the manager might need info from resources in the sandbox
    # This will be represented in the template file as {sandbox.<Resource_Role>.<Attribute_value>}
    # currently only data from the pool is replaced in the template. Data from the pool is represented as
    # {configSetPool.<Resource_Role>.<value>} e.g. {configSetPool.CA1.IP}
    # ----------------------------------
    # Replace parameters in the template file with concrete values
    # Parameters in the template file are marked with {}
    # ----------------------------------
    def create_concrete_config_from_template(self, template_io_data, concrete_config_io_data, config_set_data):
        #template_data= template_io_data.readlines()
        #concrete_config_io_data.write(str(template_data))
        #set=str(config_set_data)
        #concrete_config_io_data.write(set)
        #concrete_config_io_data.flush()
        assert(True)

