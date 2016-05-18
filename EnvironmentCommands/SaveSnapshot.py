from QualiEnvironmentUtils.Reservation import *

dev.attach_to_cloudshell_as('admin', 'admin', 'Global', '6d200cf7-6448-41fe-b9ed-5e4b363ccefb',
                            server_address='localhost', cloudshell_api_port='8029')

# ----------------------------------
# save the snapshot
# ----------------------------------
reservation_id=helpers.get_reservation_context_details().id

logger = get_qs_logger(log_category='EnvironmentCommands',
                       log_group=reservation_id, log_file_prefix='SaveSnapshot')
tftp = ResourceBase('TFTP Server')
tftp_path =tftp.GetAttribute("TFTP path")

reservation = ReservationEx('tftp://' + tftp.address + "/" + tftp_path,reservation_id, logger)
reservation.ClearResourcesStatus()
try:
    #todo: get the snapshot's name as a parameter from the user
    reservation.SaveSnapshot('test1','Running')
except QualiError as qe:
    print("Setup failed. " + qe.__str__())
except:
    print ("Setup failed. Unexpected error:", sys.exc_info())


