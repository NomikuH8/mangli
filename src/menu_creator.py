'''
data has these parameters:
    title - title of the menu, what will appear on the top
    prompt - prompt text
    cancel_text - will show this instead of 'Return' in the last choice

options is a list of tuples, the name comes first, the function comes later
e.g.:
    options = [
        ('option1', my_func1),
        ('option2', my_func2)
    ]

if has_custom_answer is true, options can be turned into custom questions,
where you write first the prompt and then its function, the function should
have the first argument reserved to the answer, people can write 'cancel' to
cancel the operation
e.g.:
    options = [
        ('your name: ', set_name),
        ('your age: ', set_age)
    ]

operations is a dict of the program's operations, the available operations are:
    cancel_operation
'''

import os

class text_menu():
    def __init__(self, data: dict, options: list, cancel_operation, has_custom_answer: bool):
        self.data = data
        self.options = options
        self.cancel_operation = cancel_operation
        self.has_custom_answer = has_custom_answer

    def print_menu(self):
        print(self.data['title'])

        separator = ''
        for char in range(len(self.data['title'])):
            separator += '-'
        print(separator)

        for option in self.options:
            print(str(self.options.index(option) + 1) + '. ' + option[0])

        if not self.has_custom_answer: print('\n')

    def choose_option(self):
        choice = ''
        if self.data['prompt'] != None:
            choice = input(self.data['prompt'])
        else:
            choice = input('Choice: ')

        try:
            choice = int(choice)
        except:
            self.main()

        if choice == 0:
            self.cancel_operation()

        for option in self.options:
            if choice == self.options.index(option) + 1:
                option[1]()


    def custom_answer(self):
        answers = []
        for question in self.options:
            answer = input(question[0])
            question[1](answer)


    def main(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_menu()
        if self.has_custom_answer:
            self.custom_answer()
        else:
            self.choose_option()
