from QualiEnvironmentUtils.Sandbox import *
from QualiEnvironmentUtils.Networking.NetworkingSaveNRestore import *
from QualiEnvironmentUtils.Networking.NetworkingHealthCheck import *

import tftpy
dev.attach_to_cloudshell_as('admin', 'admin', 'Global', '7197cefc-d171-49b4-8399-ea8cf88d09dd',
                            server_address='localhost', cloudshell_api_port='8029')

# ----------------------------------
# Setup
# ----------------------------------
reservation_id = helpers.get_reservation_context_details().id
logger = get_qs_logger(log_category='EnvironmentCommands',
                       log_group=reservation_id, log_file_prefix='Setup')

sandbox = SandboxBase(reservation_id, logger)

do_save_restore = True
saveNRestoreTool = NetworkingSaveRestore(sandbox)
healthCheckTool = NetworkingHealthCheck(sandbox)

try:
    #sandbox.clear_all_resources_live_status()
    healthCheckTool.devices_health_check(write_to_output=True)

    # TODO- Get the config set name from the orchestration's params
    config_set_name = ''
    if saveNRestoreTool.is_snapshot():
        saveNRestoreTool.load_config(config_stage='Snapshots', config_type='Running',
                                     ignore_models=['Generic TFTP server'])
    else:
        saveNRestoreTool.load_config(config_stage='Gold', config_type='Running',
                                     ignore_models=['Generic TFTP server','Config Set Pool'], config_set_name=config_set_name)

    # call activate_all_routes_and_connectors
    sandbox.activate_all_routes_and_connectors()

    # Call routes_validation
    #   sandbox.routes_validation()
except QualiError as qe:
    logger.error("Setup failed. " + str(qe))
except:
    logger.error("Setup failed. Unexpected error:" + str(sys.exc_info()[0]))
