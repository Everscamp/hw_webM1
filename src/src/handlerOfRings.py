# from classes import AddressBook, Record, Notes, BodyOfNote, TegNote
# from cleaner import sorting
#comment the lines above and uncomment the one with src. below before instaling as a packege, this line needs for testing
from src.classes import AddressBook, Record, Notes, BodyOfNote, TegNote
from src.cleaner import sorting

from abc import ABC, abstractmethod
from sys import stdout as console
from pathlib import Path
import pickle
import re


NOTEBOOK = AddressBook()
FILE_NAME = 'data.bin'
FILE_NAME_NOTES = 'data2.bin'
main_folder_path = None
contacts = {}
phone_pattern = r'\d+'
name_pattern = r'[a-zA-Z_]+'
operator_pattern = r'(edit note)|(add note)|(delete note)|(delete phone)|(show all)|(good bye)|[a-zA-Z_]+\s?'
phone_operator_pattern = r'(add)|(change)|(delete phone)'

class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

# Simple welcome function
class Hello(Command):
    def execute(self, operator = None):
        console.write("How can I help you?\n")

# Remove spaces at the beginning and at the end of the string and lower case the string
class OperatorHandler(Command):
    def execute(self, operator = None):
        parced_operator = re.search(operator_pattern, operator)
        return parced_operator.group().lower().strip()

# Defines name and telephone number
class OperandMaker(Command):
    def execute(self, operator = None):
        operands = []
        trimmedContact = re.sub(phone_operator_pattern, '', operator)
        
        phoneName = re.search(name_pattern, trimmedContact)
        phoneNums = re.findall(phone_pattern, trimmedContact)
        
        if not phoneName:
            raise Exception('No name? Enter the contact in the format: "Name" "Phone Number"\n')
        else:
            operands.append(phoneName.group().capitalize())
        
        if not phoneNums:
            raise Exception('No number? Enter the contact in the format: "Name" "Phone Number"\n')
        else:
            operands.append(phoneNums)

        return operands

# function to trim operator and name for email, adddress, birthday
class OperatorTrimmer(Command):
    def execute(self, pattern: str, operator):
        trimmed = re.sub(pattern, '', operator)
        phoneName = re.search(name_pattern, trimmed).group().capitalize()
        userData = re.sub(phoneName, '', trimmed).strip() if re.search(phoneName, trimmed) \
            else re.sub(phoneName.casefold(), '', trimmed).strip()
        
        return [phoneName, userData]

# Adds a phone number to the contacts list
class AddContact(Command):
    def execute(self, operator = None):
        phoneName = OperandMaker().execute(operator)[0]
        phoneNum = OperandMaker().execute(operator)[1]

        record = NOTEBOOK.find(phoneName)
        try:
            if record != None:
                record.add_phone(phoneNum[0])

                console.write(f'Phone to contact {phoneName} has been added!\n')   
            else:
                new_record = Record(phoneName)
                new_record.add_phone(phoneNum[0])

                NOTEBOOK.add_record(new_record)

                console.write(f'Contact {phoneName} has been added!\n')    
        except ValueError:
            console.write("Wrong phone number format!\n"+ \
                "Try using format of 0993456789 - 10 digits, no symbols.\n")

# Adds a birthday to the contacts
class AddBirthday(Command):
    def execute(self, operator = None):
        contactData = OperatorTrimmer().execute('birthday', operator)

        record = NOTEBOOK.find(contactData[0])
        if record != None:
            try:
                record.add_birthday(contactData[1])

                console.write(f'Contact {contactData[0]} has a birthday now!\n')
            except ValueError:
                console.write('Wrong date format! Enter the date in format year-month-day!\n')
        else:
            console.write(f'Woopsie no contact with {contactData[0]} name!\n')

# Adds the address to the contacts
class AddAddress(Command):
    def execute(self, operator = None):
        contactData = OperatorTrimmer().execute('address', operator)

        record = NOTEBOOK.find(contactData[0])
        if record != None:
            record.add_address(contactData[1])
 
            console.write(f'Contact {contactData[0]} has a address {contactData[1]} now!\n') 
        else:
            console.write(f'Woopsie no contact with {contactData[0]} name!\n')

# Adds the email to the contacts
class AddEmail(Command):
    def execute(self, operator = None):
        contactData = OperatorTrimmer().execute('email', operator)

        record = NOTEBOOK.find(contactData[0])
        if record != None:
            record.email = contactData[1]

            console.write(f'Contact {contactData[0]} has a address {contactData[1]} now!\n')
        else:
            console.write(f'Woopsie no contact with {contactData[0]} name!\n')

# Adds note
class AddNote(Command):
    def execute(self, operator = None):
        trimmed = re.sub('add note', '', operator).strip()

        if len(trimmed) >= 1:
            NOTEBOOK.write_note(trimmed)

            console.write('Note added!\n')

        else:
            console.write("You should've write something!\n")


# Adds tag to the note with specified ID
class AddTag(Command):
    def execute(self, operator = None):
        trimmed = re.sub('tag', '', operator).strip()
        index = re.search(r'[0-9]+', trimmed).group()
        tag = re.sub(index, '', trimmed).strip()

        try:
            NOTEBOOK.search_of_note(index)
            if len(tag) >=1:
                NOTEBOOK.add_teg_to_note(index, tag)

                console.write(f'Note {index} has teg: {tag}.\n')

            else:
                console.write("Woopsie! You should've written something.\n")

        except ValueError:
            console.write('ID is incorrect or the note doesnt exist!\n')


# Finds note with specified ID/Tag/Word
class FindNote(Command):
    def execute(self, operator = None):
        trimmed = re.sub('note', '', operator).strip()
        try:
            note = NOTEBOOK.search_of_note(trimmed)
            if note is None:
                console.write("Whoopsie-daisy! Seems like there's no such note."+ \
                    "Or is it a typo?\n")
            else:
                console.write(f'{note}\n')
        except ValueError:
            console.write('ID is incorrect or the note doesnt exist!\n')

# Edits note with specified ID
class EditNote(Command):
    def execute(self, operator = None):
        trimmed = re.sub('edit note', '', operator).strip()
        index = re.search(r'[0-9]+', trimmed).group()
        new_text = re.sub(index, '', trimmed).strip()
        
        try:
            NOTEBOOK.search_of_note(index)
            if len(new_text) >=1:
                NOTEBOOK.change_note(index, new_text)

                console.write(f'Note {index} was updated!\n')
            else:
                console.write("Woopsie! You should've written something.\n")
        except ValueError:
            console.write('ID is incorrect or the note doesnt exist!\n')

# Deletes note with specified ID
class DeleteNote(Command):
    def execute(self, operator = None):
        trimmed = re.sub('delete note', '', operator).strip()
        
        try:
            NOTEBOOK.delete_the_note(trimmed)
            console.write(f'Note {trimmed} was deleted!\n')
        except KeyError:
            console.write("No note with that key!\n")

# Shows all notes
class ShowNotes(Command):
    def execute(self, operator = None):
        notes = NOTEBOOK.show_all_notes()
        if len(notes) < 1:
            console.write("Whoopsie-daisy! Seems like there's no notes. Wanna add one?\n")
        else:
            console.write(f'{notes}\n')

# Shows birthdays within certain time range
class ShowBirthdays(Command):
    def execute(self, operator = None):
        trimmed = re.sub('birthdays', '', operator).strip()
        if trimmed == '':
            trimmed = "7"

        result = NOTEBOOK.list_with_birthdays(int(trimmed))

        if len(result) < 1:
            console.write(f"Oh wow! It seenms like there's no birthdays within {trimmed} days!\n")
            return(None)
        else:
            console.write(f'{result}\n')
            return result


# Update the contact number
class ChangeNumber(Command):
    def execute(self, operator = None):
        phoneName = OperandMaker().execute(operator)[0]
        phoneNums = OperandMaker().execute(operator)[1]

        contact = NOTEBOOK.find(phoneName)
        try:
            contact.edit_phone(phoneNums[0], phoneNums[1])

            console.write(f'Contact {phoneName} has been updated!\n')
        except ValueError:
            console.write("Wrong phone number format or no such number!\n"+ \
                "Try using format of 0993456789 - 10 digits, no symbols."+ \
                    "Or make sure that contact is exist.\n")
            

# Delete the contact number for a certain contact
class DeletePhone(Command):
    def execute(operator):
        phoneName = OperandMaker().execute(operator)[0]
        phoneNums = OperandMaker().execute(operator)[1]

        contact = NOTEBOOK.find(phoneName)
        try:
            contact.remove_phone(phoneNums[0])

            console.write(f'Phone {phoneNums[0]} was deleted fron contact {phoneName}!\n')
        except ValueError:
            console.write("No such phone or there's a typo. "+\
                "Check phone format maybe, it sholuld be 10 digits no symbols.\n")

# Delete the contact
class DeleteContact(Command):
    def execute(self, operator = None):
        phoneName = re.search(name_pattern, operator.replace("delete", ""))

        if not phoneName:
            raise Exception('No name? Enter the contact in the format: "Name" "Phone Number"')
        
        capitalized_name = phoneName.group().capitalize()
        finded = NOTEBOOK.find(capitalized_name)
        if finded != None:
            NOTEBOOK.delete(capitalized_name)

            console.write(f'Contact {capitalized_name} was deleted!\n')

        else:
            console.write('Typo or no such contact!\n')


# Displays the phone number of the requested contact
class ShowContact(Command):
    def execute(self, operator = None):
        phoneName = re.search(name_pattern, operator.replace("contact", ""))

        if not phoneName:
            raise Exception('No name? Enter the contact Name')
        
        capitalized_name = phoneName.group().capitalize()
        record = NOTEBOOK.find(capitalized_name)

        return record

# Shows contact list
class ShowAll(Command):
    def execute(self, operator = None):
        book_view = NOTEBOOK.custom_iterator(len(NOTEBOOK))
        console.write(f'{next(book_view)}\n')

# Launch cleaner
class LaunchCleaner(Command):
    def execute(self, operator = None):
        global main_folder_path
        main_folder_path = Path(input('Enter the path for sorting and cleaning: '))
        console.write(sorting())

# Simple farewell function
class Goodbye(Command):
    def execute(self, operator = None):
        SaveNotebook().execute(operator)
        console.write('Your data is saved! Good bye!\n')


# Saving a notebook
class SaveNotebook(Command):
    def execute(self, operator = None):
        try:
            with open (FILE_NAME, "wb") as file:
                pickle.dump(NOTEBOOK.data, file)

            with open (FILE_NAME_NOTES, "wb") as file2:
                pickle.dump(NOTEBOOK.notes.data, file2)
            
            console.write('Data was saved to file!\n')

        except IOError as E:
            return E

# Loadind a notebook
class LoadNotebook(Command):
    def execute(self, operator = None):
        try:
            with open (FILE_NAME, "rb") as file:
                NOTEBOOK.data = pickle.load(file)
            with open (FILE_NAME_NOTES, "rb") as file2:
                NOTEBOOK.notes.data = pickle.load(file2)

            console.write('Data was loaded from file!\n')
        except FileNotFoundError:
            return "There's no data yet! \n"
        except IOError as e:
            return e

# Shows commad list
class Help(Command):
    def execute(self, operator = None):
        console.write('The list of commands: \n \
            Type "contact [name of the contact]" to see its phone num.\n \
            Type "phone [phone of the contact'+ \
                'in the format of 0993456789 - 10 digits, no symbols]" to see if its exist.\n \
            Type "add [name] [phone number in the format of 0993456789 - 10 digits,'+ \
                'no symbols]" to add new contact.\n \
            Type "change [name] [old phone number] [new phone number]" to change phone number.\n \
            Type "birthday [name] [birthday date in date format]" to add bDay to the contact.\n \
            Type "email [name] [email]" to add email to the contact.\n \
            Type "delete phone [name] [phone number]" to delete phone from the contact.\n \
            Type "delete [name]" to delte the contact.\n \
            Type "birthdays [period of time in days]" to show the contacts with birthdays within this periond.\n \
            Type "show all" to see all contacts. \n \
                <-------------------------------->\n \
            To save data as file or work with saved book use next commands: \n \
                \n \
            Type "save" to save the address book (rewrite old book!!!) \n \
            Type "load" to open saved file. \n \
                <-------------------------------->\n \
            To work with notes use next commands: \n \
                \n \
            Type "add note [text]" to add new note.\n \
            Type "change [name] [old phone number] [new phone number]" to add new contact.\n \
            Type "note [id/tag/word] find note.\n \
            Type "tag [id] to add tag.\n \
            Type "delete note [id] to delete note.\n \
            Type "notes" to see all notes.\n \
                <-------------------------------->\n \
            To launch cleaner type "clean" \n \
                <-------------------------------->\n \
            And the ultimate command: \n \
                \n \
            Type "end" to exit.\n')

COMMANDS = {'hello': Hello(),
    'add': AddContact(),
    'change': ChangeNumber(),
    'delete phone': DeletePhone(),
    'delete': DeleteContact(),
    'contact': ShowContact(),
    'show all': ShowAll(),
    'add note': AddNote(),
    'note': FindNote(),
    'delete note': DeleteNote(),
    'edit note': EditNote(),
    'notes': ShowNotes(),
    'tag': AddTag(),
    'goodbye': Goodbye(),
    'birthday': AddBirthday(),
    'birthdays': ShowBirthdays(),
    'address': AddAddress(),
    'save': SaveNotebook(),
    'email': AddEmail(),
    'load': LoadNotebook(),
    'clean': LaunchCleaner(),
    'help': Help()
}
	