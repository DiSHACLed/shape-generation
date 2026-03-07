def prompt_y_n(prompt : str, default : bool = True):
    while True:
        # Show the prompt with default choice
        default_str = f"[{'Y' if default is True else 'y'}/{'N' if default is False else 'n'}]"
        response = input(f"{prompt} {default_str}: ").strip().lower()

        if response == '':
            return default

        if response in ('y', 'yes'):
            return True
        elif response in ('n', 'no'):
            return False
        else:
            print("Please respond with 'y' or 'n'.")

