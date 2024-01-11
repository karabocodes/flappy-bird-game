import random
import sys
import pygame
from pygame.locals import *

# Global variables for the game
fps = 32
screen_width = 289
screen_height = 511
screen = pygame.display.set_mode((screen_width, screen_height))
ground_y = screen_height * 0.8
game_sprites = {}
game_sounds = {}
player_image = 'gallery/sprites/bird.png'
background_image = 'gallery/sprites/background.png'
pipe_image = 'gallery/sprites/pipe.png'

def welcome_screen():
    """
    Shows welcome images on the screen
    """

    player_x = int(screen_width / 5)
    player_y = int((screen_height - game_sprites['player'].get_height()) / 2)
    message_x = int((screen_width - game_sprites['message'].get_width()) / 2)
    message_y = int(screen_height * 0.13)
    base_x = 0

    while True:
        for event in pygame.event.get():
            # if the user clicks on the cross button, close the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            # If the user presses space or up key, start the game for them
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            else:
                screen.blit(game_sprites['background'], (0, 0))
                screen.blit(game_sprites['player'], (player_x, player_y))
                screen.blit(game_sprites['message'], (message_x, message_y))
                screen.blit(game_sprites['base'], (base_x, ground_y))
                pygame.display.update()
                pygame.time.Clock().tick(fps)

def main_game():
    """
    Main game loop
    """
    score = 0
    player_x = int(screen_width / 5)
    player_y = int(screen_width / 2)
    base_x = 0

    # Create 2 pipes for blitting on the screen
    new_pipe1 = get_random_pipe()
    new_pipe2 = get_random_pipe()

    # List of upper pipes
    upper_pipes = [
        {'x': screen_width + 200, 'y': new_pipe1[0]['y']},
        {'x': screen_width + 200 + (screen_width / 2), 'y': new_pipe2[0]['y']},
    ]
    # List of lower pipes
    lower_pipes = [
        {'x': screen_width + 200, 'y': new_pipe1[1]['y']},
        {'x': screen_width + 200 + (screen_width / 2), 'y': new_pipe2[1]['y']},
    ]

    pipe_vel_x = -4

    player_vel_y = -9
    player_max_vel_y = 10
    player_min_vel_y = -8
    player_acc_y = 1

    player_flap_acc_v = -8  # velocity while flapping
    player_flapped = False  # It is true only when the bird is flapping

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player_y > 0:
                    player_vel_y = player_flap_acc_v
                    player_flapped = True
                    game_sounds['wing'].play()

        crash_test = is_collide(player_x, player_y, upper_pipes, lower_pipes)  # This function will return true if the player is crashed
        if crash_test:
            return

        # check for score
        player_mid_pos = player_x + game_sprites['player'].get_width() / 2
        for pipe in upper_pipes:
            pipe_mid_pos = pipe['x'] + game_sprites['pipe'][0].get_width() / 2
            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                score += 1
                print(f"Your score is {score}")
                game_sounds['point'].play()

        if player_vel_y < player_max_vel_y and not player_flapped:
            player_vel_y += player_acc_y

        if player_flapped:
            player_flapped = False
        player_height = game_sprites['player'].get_height()
        player_y = player_y + min(player_vel_y, ground_y - player_y - player_height)

        # move pipes to the left
        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            upper_pipe['x'] += pipe_vel_x
            lower_pipe['x'] += pipe_vel_x

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0 < upper_pipes[0]['x'] < 5:
            new_pipe = get_random_pipe()
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        # if the pipe is out of the screen, remove it
        if upper_pipes[0]['x'] < -game_sprites['pipe'][0].get_width():
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        # Lets blit our sprites now
        screen.blit(game_sprites['background'], (0, 0))
        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            screen.blit(game_sprites['pipe'][0], (upper_pipe['x'], upper_pipe['y']))
            screen.blit(game_sprites['pipe'][1], (lower_pipe['x'], lower_pipe['y']))

        screen.blit(game_sprites['base'], (base_x, ground_y))
        screen.blit(game_sprites['player'], (player_x, player_y))
        my_digits = [int(x) for x in list(str(score))]
        width = 0
        for digit in my_digits:
            width += game_sprites['numbers'][digit].get_width()
        x_offset = (screen_width - width) / 2

        for digit in my_digits:
            screen.blit(game_sprites['numbers'][digit], (x_offset, screen_height * 0.12))
            x_offset += game_sprites['numbers'][digit].get_width()
        pygame.display.update()
        pygame.time.Clock().tick(fps)

def is_collide(player_x, player_y, upper_pipes, lower_pipes):
    """
    Check for collision between the bird and pipes or ground
    """
    if player_y > ground_y - 25 or player_y < 0:
        game_sounds['hit'].play()
        return True

    for pipe in upper_pipes:
        pipe_height = game_sprites['pipe'][0].get_height()
        if player_y < pipe_height + pipe['y'] and abs(player_x - pipe['x']) < game_sprites['pipe'][0].get_width():
            game_sounds['hit'].play()
            return True

    for pipe in lower_pipes:
        if (player_y + game_sprites['player'].get_height() > pipe['y']) and abs(player_x - pipe['x']) < game_sprites['pipe'][0].get_width():
            game_sounds['hit'].play()
            return True

    return False

def get_random_pipe():
    """
    Generate positions of two pipes (one bottom straight and one top rotated) for blitting on the screen
    """
    pipe_height = game_sprites['pipe'][0].get_height()
    offset = screen_height / 3
    y2 = offset + random.randrange(0, int(screen_height - game_sprites['base'].get_height() - 1.2 * offset))
    pipe_x = screen_width + 10
    y1 = pipe_height - y2 + offset
    pipe = [
        {'x': pipe_x, 'y': -y1},  # upper Pipe
        {'x': pipe_x, 'y': y2}    # lower Pipe
    ]
    return pipe

if __name__ == "__main__":
    # This will be the main point from where our game will start
    pygame.init()  # Initialize all pygame's modules
    pygame_time_clock = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird')
    game_sprites['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha(),
    )

    game_sprites['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
    game_sprites['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()
    game_sprites['pipe'] = (
        pygame.transform.rotate(pygame.image.load(pipe_image).convert_alpha(), 180),
        pygame.image.load(pipe_image).convert_alpha()
    )

    # Game sounds
    game_sounds['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    game_sounds['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    game_sounds['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    game_sounds['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    game_sounds['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    game_sprites['background'] = pygame.image.load(background_image).convert()
    game_sprites['player'] = pygame.image.load(player_image).convert_alpha()

    while True:
        welcome_screen()  # Shows welcome screen to the user until he presses a button
        main_game()  # This is the main game function
