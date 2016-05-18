from QualiEnvironmentUtils.Reservation import *

dev.attach_to_cloudshell_as('admin', 'admin', 'Global', 'd2463929-bd12-48e7-82f5-a736bb72ba30',
                            server_address='localhost', cloudshell_api_port='8028', command_parameters={},
                            resource_name='')

# ----------------------------------
# Teardown
# ----------------------------------
reservation_id=helpers.get_reservation_context_details().id
logger = get_qs_logger(log_category='EnvironmentCommands',
                       log_group=reservation_id, log_file_prefix='Teardown')
reservation = ReservationEx('tftp://CloudShell/configs',reservation_id, logger)
reservation.ClearResourcesStatus()
try:
    reservation.LoadConfig('Base', 'Running')

except QualiError as qe:
    print("Teardown failed: " + qe.__str__())
except:
    print ("Teardown failed. Unexpected error:", sys.exc_info()[0])
