from QualiEnvironmentUtils.Sandbox import *
from QualiEnvironmentUtils.Networking.NetworkingSaveNRestore import *

dev.attach_to_cloudshell_as('admin', 'admin', 'Global', '2385544d-12c5-4667-9a1c-2d213b59fe03',
                            server_address='localhost', cloudshell_api_port='8029')

# ----------------------------------
# Setup
# ----------------------------------
reservation_id = helpers.get_reservation_context_details().id
logger = get_qs_logger(log_category='EnvironmentCommands',
                       log_group=reservation_id, log_file_prefix='Setup')

sandbox = SandboxBase(reservation_id, logger)
do_save_restore = True
try:
    saveNRestoreTool = NetworkingSaveRestore(sandbox)
except QualiError:
    do_save_restore = False
try:
    sandbox.clear_all_resources_live_status()
    if do_save_restore:
        # TODO- Get the config set name from the orchestration's params
        config_set_name = ''
        if saveNRestoreTool.is_snapshot():
            saveNRestoreTool.load_config(config_stage='Snapshots', config_type='Running',
                                         ignore_models=['Generic TFTP server'])
        else:
            saveNRestoreTool.load_config(config_stage='Gold', config_type='Running',
                                         ignore_models=['Generic TFTP server'], config_set_name=config_set_name)

    # call activate_all_routes_and_connectors
    sandbox.activate_all_routes_and_connectors()

    # Call routes_validation
    #   sandbox.routes_validation()
except QualiError as qe:
    logger.error("Setup failed. " + str(qe))
except:
    logger.error("Setup failed. Unexpected error:" + str(sys.exc_info()[0]))
