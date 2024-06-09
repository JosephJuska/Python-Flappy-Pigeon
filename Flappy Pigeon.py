import os
import time
import random
import json

try:
    import keyboard

except ImportError:
    print('Module \'keyboard\' will be installed in order to make sure the game works properly.')
    time.sleep(1.5)
    input('Press \'enter\' to continue...')
    os.system("pip install keyboard")
    import keyboard


# CONSTANTS
DEFAULT_SETTINGS = {
    'bird': '>',
    'height': 20,
    'width': 80,
    'difficulties': {
        0: ('Baby', 0.05, 30),
        500: ('Easy', 0.045, 25),
        1000: ('Medium', 0.035, 20),
        3000: ('Hard', 0.025, 15),
        6666: ('HELL', 0.015, 10)
    },
    'gravity': 0.7,
    'boost': 3,
    'pipe_gap': 5,
    'keyboard': {
        'jump': 'space',
        'exit': 'escape'
    }
}

SCRIPT_PATH = os.path.abspath(__file__)

SETTINGS_PATH = os.path.join(os.path.dirname(SCRIPT_PATH), 'settings.json')
# CONSTANTS

# SETTINGS CONFIG
def read_settings():
    if not os.path.exists(SETTINGS_PATH):
        create_settings()

    if os.path.getsize(SETTINGS_PATH) == 0:
        create_settings()

    with open(SETTINGS_PATH, 'r') as f:
        settings = json.load(f)
    
    return settings

def create_settings():
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(DEFAULT_SETTINGS, f, indent=2)

def update_settings(settings):
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(settings, f, indent=2)

SETTINGS = read_settings() 
# SETTINGS CONFIG

# UTILS
def show_screen(screen):
    clear_screen()
    print(screen)

def clear_screen():
    os.system('cls') if os.name == 'nt' else os.system('clear')

def show_error_wrong_type(variable_name, type):
    show_error(f'{variable_name} must be a {type}')

def show_error_invalid_choice(variable_name, choices):
    choice_string = ','.join(str(choice) for choice in choices)
    show_error(f'{variable_name} can only be {choice_string}')

def show_error(message):
    print(message)
    time.sleep(1.5)
    input('Press \'enter\' to continue...')

def is_float(value):
    try:
        if value.lower() in ['inf', '-inf', 'nan']:
            return False
        
        value = float(value)
        return True
    except ValueError:
        return False

def generate_validation_result(success, data):
    return (success, data)

def generate_validation_success(data):
    return generate_validation_result(True, data)

def generate_validation_error_wrong_type(field_name, type):
    return generate_validation_result(False, f'{field_name.title()} must be a {type}')

def generate_validation_result_wrong_range(field_name, min, max=False):
    error_message = f'{field_name.title()} must be bigger than {min}' if not max else f'{field_name.title()} must be between {min} and {max}'
    return generate_validation_result(False, error_message) 
# UTILS

# PAGES UTILS
def generate_screen(page_name, choices):
    choices_text = ''
    for i in range(len(choices)):
        choices_text += f'\n\t{i + 1}. {choices[i][0].title()}'

    choices_text += f'\n\t{len(choices) + 1}. Exit'
    screen = f'''
-----------------------------
        Flappy Pigeon
        
        {page_name.capitalize()}
{choices_text}
-----------------------------
'''
    
    return screen

def create_page(page_name, choices_func):
    def wrapper():
        while True:
            choices = choices_func()
            screen = generate_screen(page_name, choices)
            show_screen(screen)
            choice = input(': ')
            if not choice.isnumeric():
                show_error_wrong_type('Choice', 'number')
                continue

            if int(choice) > len(choices) + 1 or int(choice) < 0:
                show_error_invalid_choice('Choice', ''.join(str(i) for i in range(1, len(choices) + 2)))
                continue

            if int(choice) == len(choices) + 1:
                break

            else:
                callback = choices[int(choice) - 1][1]
                callback()

    return wrapper

def create_settings_field_update_key_page(page_name, choices_func, field_name, callback):
    def wrapper():
        while True:
            choices = choices_func()
            screen = generate_screen(page_name, choices)
            show_screen(screen)
            print(f'Press a key to update {field_name}: ', end='', flush=True)

            while True:
                event = keyboard.read_event(suppress=True)
                if event.event_type == keyboard.KEY_DOWN:
                    new_key = event.name
                    break

            callback(new_key)
            print(f'{field_name} has been updated to \'{new_key}\'')
            time.sleep(1.5)
            print('Press \'enter\' to continue...')
            break
    
    return wrapper

def create_settings_field_update_page(page_name, choices_func, field_name, validator, callback):
    def wrapper():
        while True:
            choices = choices_func()
            screen = generate_screen(page_name, choices)
            show_screen(screen)
            choice = input(f'{field_name.title()}(\'exit\' to exit): ')
            if choice == 'exit':
                break

            result = validator(choice)
            if not result[0]:
                show_error(result[1])
                continue

            callback(result[1])
            break
    
    return wrapper

def generate_board(width, height):
    board = ''
    board += '+' + '-' * width + '+\n'
    for _ in range(height):
        board += '|' + ' ' * width + '|\n'

    board += '+' + '-' * width + '+\n'
    return board
# PAGES UTILS

# GAME UTILS
def calculate_speeds(gravity, boost):
    initial_speed = 0

    speed = initial_speed
    max_speed = speed
    for _ in range(100): 
        speed = min(1.2, speed + boost)
        max_speed = max(max_speed, speed)

    speed = initial_speed
    min_speed = speed
    for _ in range(100):
        speed = max(-1, speed - gravity)
        min_speed = min(min_speed, speed)

    return min_speed, max_speed

def physics_test_refresh_screen(bird, bird_x, bird_y, difficulty, boost, gravity, width, height, exit_key, jump_key):
    clear_screen()
    print(f'Press \'{jump_key}\' to jump')
    print('+' + '-' * width + '+')
    for y in range(height):
        line = '|'
        for x in range(width):
            if y == bird_y and x == bird_x:
                line += bird
            else:
                line += " "

        line += '|'
        print(line)

    print('+' + '-' * width + '+')

    print('Difficulty: ' + difficulty)
    print('Boost:' + str(boost))
    print('Gravity:' + str(gravity))
    print(f'Press \'{exit_key}\' to exit')

def refresh_screen(bird, bird_x, bird_y, pipes, difficulty, score, pipe_gap, width, height):
    clear_screen()

    print('+' + '-' * width + '+')
    for y in range(height):
        line = '|'
        for x in range(width):
            if y == bird_y and x == bird_x:
                line += bird
            elif any(pipe_x <= x < pipe_x + 2 and (y < pipe_y or y > pipe_y + pipe_gap) for pipe_x, pipe_y in pipes):
                line += "*"
            else:
                line += " "

        line += '|'
        print(line)

    print('+' + '-' * width + '+')

    print('Level: ' + difficulty)
    print("Score: " + str(score))

def generate_start_bird_pos(width, height):
    bird_x = round(width // 10 * 2)
    bird_y = round(height // 10 * 2)
    return bird_x, bird_y

def generate_pipe(width, height, pipe_gap):
    return (width, random.randint(0, height - pipe_gap + 1))

def bird_touched_pipe(pipes, pipe_gap, bird_x, bird_y):
    return any(pipe_x <= bird_x < pipe_x + 2 and (bird_y < pipe_y or bird_y > pipe_y + pipe_gap) for pipe_x, pipe_y in pipes)

def game_loop():
    flag = False

    score = 0
    speed = 0

    jump_key = SETTINGS['keyboard']['jump']
    exit_key = SETTINGS['keyboard']['exit']

    width = SETTINGS['width']
    height = SETTINGS['height']

    bird = SETTINGS['bird']
    bird_x, bird_y = generate_start_bird_pos(width, height)

    gravity = SETTINGS['gravity']
    boost = SETTINGS['boost']

    difficulties = SETTINGS['difficulties']
    difficulty = difficulties.get('0')
    difficulty_level = difficulty[0]
    refresh_rate = difficulty[1]

    pipe_gap = SETTINGS['pipe_gap']
    pipe_distance = difficulty[2]
    pipes = [generate_pipe(width, height, pipe_gap)]

    refresh_screen(bird, bird_x, bird_y, pipes, difficulty_level, score, pipe_gap, width, height)
    print(f'Press \'{jump_key}\' to jump')
    print(f'Press \'{exit_key}\' to exit')
    print('Have FUN!')
    while True:
        if keyboard.is_pressed(jump_key):
            flag = True
            break
    
        if keyboard.is_pressed(exit_key):
            return
        
    if flag:
        while True:
            speed = max(-1, speed - gravity)
            if keyboard.is_pressed(jump_key):
                speed = min(1.2, speed + boost)

            bird_y = min(height, bird_y - round(speed))

            if bird_touched_pipe(pipes, pipe_gap, bird_x, bird_y):
                print("Game Over!")
                time.sleep(1.5)
                input('Press \'enter\' to continue...')
                break

            if bird_y > height:
                print("Game Over!")
                time.sleep(1.5)
                input('Press \'enter\' to continue...')
                break

            pipes = [(x - 1, y) for x, y in pipes if x > -2]
            if pipes[-1][0] < width - pipe_distance:
                pipes.append(generate_pipe(width, height, pipe_gap))

            if pipes[0][1] < 0:
                pipes.pop(0)

            score += 1
            difficulty = difficulties.get(str(score), difficulty)
            difficulty_level = difficulty[0]
            refresh_rate = difficulty[1]
            pipe_distance = difficulty[2]

            refresh_screen(bird, bird_x, bird_y, pipes, difficulty_level, score, pipe_gap, width, height)

            time.sleep(refresh_rate)
# GAME UTILS

# VALIDATORS
def validate_width(width):
    if not width.isnumeric():
        return generate_validation_error_wrong_type('width', 'number')
    
    width = int(width)
    if width < 40:
        return generate_validation_result_wrong_range('width', 40)
    
    return generate_validation_success(width)

def validate_height(height):
    if not height.isnumeric():
        return generate_validation_error_wrong_type('height', 'number')
    
    height = int(height)
    if height < 6:
        return generate_validation_result_wrong_range('height', 6)
    
    return generate_validation_success(height)

def validate_gravity(gravity):
    if not is_float(gravity):
        return generate_validation_error_wrong_type('gravity', 'number')
    
    gravity = float(gravity)
    if gravity < 0.1:
        return generate_validation_result_wrong_range('gravity', 0.1)
    
    return generate_validation_success(gravity)

def validate_boost(boost):
    if not is_float(boost):
        return generate_validation_error_wrong_type('boost', 'number')
    
    boost = float(boost)
    if boost < 0.1:
        return generate_validation_result_wrong_range('boost', 0.1)
    
    return generate_validation_success(boost)
# VALIDATORS

# UPDATE FUNCTIONS
def update_value(field_name, value):
    SETTINGS[field_name] = value
    update_settings(SETTINGS)

def update_height(height):
    SETTINGS['height'] = height
    pipe_gap = max(3, min(6, height // 2))
    SETTINGS['pipe_gap'] = pipe_gap
    update_settings(SETTINGS)

def update_keyboard_key(field_name, value):
    SETTINGS['keyboard'][field_name] = value
    update_settings(SETTINGS)
# UPDATE FUNCTIONS

# PAGES
def screen_settings_test():
    screen = generate_board(SETTINGS['width'], SETTINGS['height'])
    exit_key = SETTINGS['keyboard']['exit']
    show_screen(screen)
    print(f'Press \'{exit_key}\' to exit')
    while True:
        if keyboard.is_pressed(exit_key):
            break

def screen_settings_choices():
    return (
        (f'width: {SETTINGS["width"]}', screen_settings_width),
        (f'height: {SETTINGS["height"]}', screen_settings_height),
        (f'test screen', screen_settings_test),
    )

screen_settings_height = create_settings_field_update_page('screen settings', screen_settings_choices, 'height', validate_height, update_height)

screen_settings_width = create_settings_field_update_page('screen settings', screen_settings_choices, 'width', validate_width, lambda value: update_value('width', value))

screen_settings = create_page('screen settings', screen_settings_choices)



def physics_test(difficulty):
    def wrapper():
        difficulty_text = difficulty[0]
        refresh_rate = difficulty[1]

        width = SETTINGS['width']
        height = SETTINGS['height']

        gravity = SETTINGS['gravity']
        boost = SETTINGS['boost']

        bird = SETTINGS['bird']
        bird_x, bird_y = generate_start_bird_pos(width, height)
        jump_key = SETTINGS['keyboard']['jump']
        exit_key = SETTINGS['keyboard']['exit']

        speed = 0
        min_speed, max_speed = calculate_speeds(gravity, boost)

        while True:
            speed = max(min_speed, speed - gravity)
            if keyboard.is_pressed(jump_key):
                speed = min(max_speed, speed + boost)

            if keyboard.is_pressed(exit_key):
                break

            bird_y = max(0, min(height - 1, bird_y - round(speed)))

            physics_test_refresh_screen(bird, bird_x, bird_y, difficulty_text, boost, gravity, width, height, exit_key, jump_key)

            time.sleep(refresh_rate)

    return wrapper

def physics_settings_choices():
    return (
        (f'gravity: {SETTINGS["gravity"]}', physics_settings_gravity),
        (f'boost: {SETTINGS["boost"]}', physics_settings_boost),
        (f'test physics', game_play_test_page),
    )

def game_play_test_choices():
    return tuple((choice[0], physics_test(choice)) for choice in SETTINGS['difficulties'].values())

game_play_test_page = create_page('game play test difficulties', game_play_test_choices)

physics_settings_boost = create_settings_field_update_page('physics settings', physics_settings_choices, 'boost', validate_boost, lambda value: update_value('boost', value))

physics_settings_gravity = create_settings_field_update_page('physics settings', physics_settings_choices, 'gravity', validate_gravity, lambda value: update_value('gravity', value))

physics_settings = create_page('physics settings', physics_settings_choices)



def controls_settings_choices():
    jump_key = SETTINGS['keyboard']['jump']
    exit_key = SETTINGS['keyboard']['exit']
    return (
        (f'jump: {jump_key}', controls_settings_jump),
        (f'exit: {exit_key}', controls_settings_exit),
        ('test keys', game_play_test_page)
    )

controls_settings_exit = create_settings_field_update_key_page('controls settings', controls_settings_choices, 'exit', lambda value: update_keyboard_key('exit', value))

controls_settings_jump = create_settings_field_update_key_page('control settings', controls_settings_choices, 'jump', lambda value: update_keyboard_key('jump', value))

controls_settings = create_page('controls settings', controls_settings_choices)



def reset_settings_page():
    clear_screen()
    SETTINGS = DEFAULT_SETTINGS
    update_settings(SETTINGS)
    print('Settings has been reset to the default settings')
    time.sleep(1.5)
    input('Press \'enter\' to continue...')

def settings_choices():
    return (
        ('screen size', screen_settings), 
        ('physics', physics_settings), 
        ('controls', controls_settings),
        ('reset settings', reset_settings_page)
    )

settings = create_page('settings', settings_choices)



def menu_choices():
    return (
        ('play', game_loop), 
        ('settings', settings)
    )

menu = create_page('menu', menu_choices)
# PAGES

def main():
    menu()

if __name__ == '__main__':
    main()