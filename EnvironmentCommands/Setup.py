from QualiEnvironmentUtils.Sandbox import *

dev.attach_to_cloudshell_as('admin', 'admin', 'Global', '8f65ecb7-aa00-405a-9be6-a89bee3a10cc',
                            server_address='localhost', cloudshell_api_port='8029')

# ----------------------------------
# Setup
# ----------------------------------
reservation_id=helpers.get_reservation_context_details().id
logger = get_qs_logger(log_category='EnvironmentCommands',
                       log_group=reservation_id, log_file_prefix='Setup')

sandbox = SandboxEx(reservation_id, logger)
try:
    sandbox.ClearResourcesStatus()
    if sandbox.IsSnapshot():
        sandbox.LoadConfig('Snapshots', 'Running')
    else:
        sandbox.LoadConfig('Gold', 'Running')
    # call activateRoutes
    sandbox.WriteMessageToOutput("Connecting routes")
    sandbox.ActivateRoutes()
    sandbox.WriteMessageToOutput("Routes connected")
    # Call RoutesValidation
 #   sandbox.RoutesValidation()
except QualiError as qe:
    logger.error("Setup failed. " + str(qe))
except:
    logger.error("Setup failed. Unexpected error:" + sys.exc_info()[0])


