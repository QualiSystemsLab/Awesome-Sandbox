from QualiEnvironmentUtils.Sandbox import *

dev.attach_to_cloudshell_as('admin', 'admin', 'Global', 'd2463929-bd12-48e7-82f5-a736bb72ba30',
                            server_address='localhost', cloudshell_api_port='8029')

# ----------------------------------
# Teardown
# ----------------------------------
reservation_id=helpers.get_reservation_context_details().id
logger = get_qs_logger(log_category='EnvironmentCommands',
                       log_group=reservation_id, log_file_prefix='Teardown')
tftp_server_resource = ResourceBase('TFTP Server')
tftp_server_destination_path =tftp_server_resource.GetAttribute("TFTP path")

reservation = ReservationEx('tftp_server_resource://' + tftp_server_resource.address + "/" + tftp_server_destination_path, reservation_id, logger)
reservation.ClearResourcesStatus()
try:
    reservation.LoadConfig('Base', 'Running')

except QualiError as qe:
    logger.error("Teardown failed. " + str(qe))
except:
    logger.error("Teardown failed. Unexpected error:" + sys.exc_info()[0])
