from QualiEnvironmentUtils.Reservation import *

dev.attach_to_cloudshell_as('admin', 'admin', 'Global', 'e84d2103-36e1-404f-aa0d-45ed6d4f84ab',
                            server_address='localhost', cloudshell_api_port='8029')

# ----------------------------------
# Setup
# ----------------------------------
reservation_id=helpers.get_reservation_context_details().id
logger = get_qs_logger(log_category='EnvironmentCommands',
                       log_group=reservation_id, log_file_prefix='Setup')

tftp = ResourceBase('TFTP Server')
tftp_path =tftp.GetAttribute("TFTP path")

reservation = ReservationEx('tftp://' + tftp.address + "/" + tftp_path,reservation_id, logger)
try:
    reservation.ClearResourcesStatus()
    if reservation.IsSnapshot():
        reservation.LoadConfig('Snapshots', 'Running')
    else:
        reservation.LoadConfig('Gold', 'Running')
    # call activateRoutes
    reservation.WriteMessageToOutput("Connecting routes")
    reservation.ActivateRoutes()
    reservation.WriteMessageToOutput("Routes connected")
    # Call RoutesValidation
 #   reservation.RoutesValidation()
except QualiError as qe:
    logger.error("Setup failed. " + str(qe))
except:
    logger.error("Setup failed. Unexpected error:" + sys.exc_info()[0])


