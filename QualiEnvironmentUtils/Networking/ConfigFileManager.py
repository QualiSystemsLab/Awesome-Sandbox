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

    def create_file_from_template(self, template_path, destination_path):

        client = tftpy.TftpClient(self.tftp_server.address, 69)
     #   temp_file = file(name=destination_path,mode='rw')
        temp_file='c:\\temp\\x.cfg'
        client.download(template_path, temp_file)
        assert True