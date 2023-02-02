# A text-based Python program to convert Strings into Morse Code.
import csv
import time
import pyperclip

# opening morse alphabet file and creating dictionary
morse_alphabet = {}
with open('morse_alphabet.csv') as file:
    data = csv.reader(file, delimiter=';')
    for row in data:
        morse_alphabet.update({row[0]: row[1]})


def printing_morse_alphabet():
    print(morse_alphabet)


def coding_to_morse():
    # coding message to morse code
    # taking message from user
    message = input("Type message to convert into morse alphabet: ").upper()

    # coding process
    morse_code_message = ""
    print_warning = False
    for idx, char in enumerate(message):
        if morse_alphabet.get(char) == 'None':
            print_warning = True
        if idx != len(message)-1:
            morse_code_message = morse_code_message + f'{morse_alphabet.get(char)} '
        else:
            morse_code_message = morse_code_message + f'{morse_alphabet.get(char)}'

    # printing encoded message
    if print_warning:
        print(f'Warning: entered message contains unrecognized character.')
    print(f'\nMorse code for entered message: \n{morse_code_message}\n')
    pyperclip.copy(morse_code_message)
    return


def decoding_from_morse():
    # taking morse message from user
    morse_message = input("Type morse message to decode: ").upper()

    # decoding morse message
    try:
        decoded_message = ''
        words = morse_message.split(' / ')
        for word in words:
            morse_chars = word.split(' ')
            for morse_char in morse_chars:
                key = list(filter(lambda x: morse_alphabet[x] == morse_char, morse_alphabet))[0]
                decoded_message += key
            decoded_message += ' '
        # printing decoded message
        print(f'\nDecoded message: \n{decoded_message}\n')
        pyperclip.copy(decoded_message)
    except IndexError:
        print("Provided message error. Unrecognized character inside.")


print(".-----------------------.\n"
      "| MORSE CODER BY MO1DER |\n"
      "'-----------------------'")
action = True
while action:
    action = input('Decide what you want to do. \n'
                   '   Press "C" or "1" for coding message to morse code\n'
                   '   Press "D" or "2" for decoding message from morse code\n'
                   '   Press "A" or "3" for showing morse alphabet\n'
                   '   Press any other key for leave program\n'
                   '   (result will be copied to clipboard) ').upper()
    if action == "C" or action == "1":
        coding_to_morse()
        time.sleep(3)
    elif action == "D" or action == "2":
        decoding_from_morse()
        time.sleep(3)
    elif action == "A" or action == "3":
        printing_morse_alphabet()
        time.sleep(3)
    else:
        print("See you next time. Bye")
        action = False
        break



