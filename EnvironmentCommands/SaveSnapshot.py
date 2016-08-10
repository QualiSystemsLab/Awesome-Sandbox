from QualiEnvironmentUtils.Networking.NetworkingSaveNRestore import *

dev.attach_to_cloudshell_as('admin', 'admin', 'Global', '949d1769-5875-4aa3-955d-ba261386a285',
                            server_address='localhost', cloudshell_api_port='8029',command_parameters={'name':'Snap13'})

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

    snapshot_name = os.environ['name']

    sandbox.save_sandbox_as_blueprint(snapshot_name)
    # replace spaces with _ in the snapshot's name

    snapshot_name = snapshot_name.replace(' ','_')

    saveNRestoreTool.save_config(snapshot_name=snapshot_name, config_type='running', ignore_models=['Generic TFTP server'])
except QualiError as qe:
    logger.error("Save snapshot failed. " + str(qe))
except:
    logger.error ("Save snapshot. Unexpected error:" + str(sys.exc_info()))


