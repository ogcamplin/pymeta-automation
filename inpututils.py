import re

class InputUtils():
    @staticmethod
    def get_text_input(prompt, regex_pattern):
        while True:
            print(prompt)
            print('> ', end='')
            
            try:
                inp = input()
                if re.match(regex_pattern, inp) is not None:
                    return inp
                else:
                    raise ValueError("Invalid input")
            except Exception as e:
                print(e)

    @staticmethod
    def get_number_input(prompt, upper_bound):
        while True:
            print(prompt)
            print('> ', end='')
            
            try:
                inp = int(input())
                if inp >= 0 and inp <= upper_bound:
                    return inp
                else:
                    raise ValueError("Invalid input")
            except Exception as e:
                print(e)
