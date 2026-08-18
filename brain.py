from commands import execute_command


def process_message(message):
    message = message.strip()
    if not message :
        return ""

    #attempt to exectue command

    command_response = execute_command(message)


    if command_response:
        return command_response


    #since /no ai brain yet il reply this only

    return "message received, currently not coonected to ai, cant perform task"

