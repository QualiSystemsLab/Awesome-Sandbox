from QualiEnvironmentUtils.Sandbox import *
from QualiEnvironmentUtils.Networking.NetworkingSaveNRestore import *

dev.attach_to_cloudshell_as('admin', 'admin', 'Global', '18e5dd1f-aa63-493c-a72c-aa1809f4cb17',
                            server_address='localhost', cloudshell_api_port='8029')

# ----------------------------------
# Setup
# ----------------------------------
reservation_id=helpers.get_reservation_context_details().id
logger = get_qs_logger(log_category='EnvironmentCommands',
                       log_group=reservation_id, log_file_prefix='Setup')

sandbox = SandboxBase(reservation_id, logger)
saveNRestoreTool = NetworkingSaveRestore(sandbox)
try:
    sandbox.ClearResourcesStatus()
    if saveNRestoreTool.IsSnapshot():
        saveNRestoreTool.LoadConfig(config_stage='Snapshots',config_type= 'Running',ignore_models=['Generic TFTP server'])
    else:
        saveNRestoreTool.LoadConfig(config_stage='Gold', config_type= 'Running',ignore_models=['Generic TFTP server'])
    # call activateRoutes
    sandbox.ActivateRoutes()

    # Call RoutesValidation
 #   sandbox.RoutesValidation()
except QualiError as qe:
    logger.error("Setup failed. " + str(qe))
except:
    logger.error("Setup failed. Unexpected error:" + sys.exc_info()[0])


