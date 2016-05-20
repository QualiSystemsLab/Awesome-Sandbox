from QualiEnvironmentUtils.Networking.NetworkingSaveNRestore import *

dev.attach_to_cloudshell_as('admin', 'admin', 'Global', '6d200cf7-6448-41fe-b9ed-5e4b363ccefb',
                            server_address='localhost', cloudshell_api_port='8029')

# ----------------------------------
# save the snapshot
# ----------------------------------
reservation_id=helpers.get_reservation_context_details().id

logger = get_qs_logger(log_category='EnvironmentCommands',
                       log_group=reservation_id, log_file_prefix='SaveSnapshot')

sandbox = SandboxBase(reservation_id, logger)
saveNRestoreTool = NetworkingSaveRestore(sandbox)
sandbox.clear_all_resources_live_status()
try:
    #todo: get the snapshot's name as a parameter from the user
    sandbox.SaveSandboxAsBlueprint('test1')
    saveNRestoreTool.SaveConfig(snapshot_name='test1',config_type='Running', ignore_models=['Generic TFTP server'])
except QualiError as qe:
    logger.error("Save snapshot failed. " + str(qe))
except:
    logger.error ("Save snapshot. Unexpected error:" + sys.exc_info())


