
from src.handlerOfRings import COMMANDS, OperatorHandler, LoadNotebook, ShowBirthdays
#comment line below and uncomment the one above before instaling as a packege, this line needs for testing
# from handlerOfRings import * 

from sys import stdout as console


waiting = True
goodbyes = ("good bye", "close", "exit", "end", "bye")

# request-response cycle
def main_action(func):
    def inner(operator):
        try:
            func(operator)
        except AttributeError:
            print('Check twice or type the "help" to print the list of commands!')
        except Exception as e:
            message = str(e)
            print(message)
    
    return inner

@main_action
def main(operator) -> str:
    trimmed_operator = OperatorHandler().execute(operator)
    if trimmed_operator not in COMMANDS:
        raise AttributeError
    else:
        command = COMMANDS[trimmed_operator]
        command.execute(operator)

def entry_point():
    load = LoadNotebook().execute(None)
    console.write(load) if load != None else None
    try:
        birthday_message = ShowBirthdays().execute('7')
        if birthday_message != None:
            console.write(f"Someone has a birthday soon: {birthday_message}\n")
    except Exception as e:
        message = str(e)
        print(message)
    while waiting == True:
        operator = input(":")
        if operator in goodbyes:
            main('goodbye')
            break
        else: 
            main(operator)

if __name__ == '__main__':
    entry_point()
