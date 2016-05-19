from QualiEnvironmentUtils.Networking.NetworkingSaveNRestore import *

dev.attach_to_cloudshell_as('admin', 'admin', 'Global', '18e5dd1f-aa63-493c-a72c-aa1809f4cb17',
                            server_address='localhost', cloudshell_api_port='8029')

# ----------------------------------
# Teardown
# ----------------------------------
reservation_id=helpers.get_reservation_context_details().id
logger = get_qs_logger(log_category='EnvironmentCommands',
                       log_group=reservation_id, log_file_prefix='Teardown')

sandbox = SandboxBase(reservation_id, logger)
saveNRestoreTool = NetworkingSaveRestore(sandbox)

sandbox.ClearResourcesStatus()
try:
    saveNRestoreTool.LoadConfig(config_stage='Base', config_type= 'Running',ignore_models=['Generic TFTP server'])

except QualiError as qe:
    logger.error("Teardown failed. " + str(qe))
except:
    logger.error("Teardown failed. Unexpected error:" + sys.exc_info()[0])
