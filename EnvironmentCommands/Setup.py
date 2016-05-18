from QualiEnvironmentUtils.Reservation import *

dev.attach_to_cloudshell_as('admin', 'admin', 'Global', '6d200cf7-6448-41fe-b9ed-5e4b363ccefb',
                            server_address='localhost', cloudshell_api_port='8028', command_parameters={},
                            resource_name='')

# ----------------------------------
# Setup
# ----------------------------------
reservation_id=helpers.get_reservation_context_details().id
logger = get_qs_logger(log_category='EnvironmentCommands',
                       log_group=reservation_id, log_file_prefix='Setup')
#Todo in future - implement our looger e.g DBlogger


reservation = ReservationEx('tftp://CloudShell/configs',reservation_id, logger)
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
    print("Setup failed. " + qe.__str__())
except:
    print ("Setup failed. Unexpected error:", sys.exc_info()[0])


