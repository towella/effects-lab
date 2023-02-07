import pygame

version = "1.0.0"
release = "08/02/2023"

tile_size = 16  # keep to prevent errors, even if game doesnt need tiles
screen_width = 480  #31 * tile_size  # arbitrary
screen_height = 282  #20 * tile_size  # arbitrary
# 2560 x 1600
scaling_factor = 3  # how much the screen is scaled up before bliting on display

controls = {"Move Orb": "Move Mouse", "Radial Blast": "Right Click Mouse", "Toggle Tail Bloom": pygame.K_b,
            "Toggle Gravity": pygame.K_g, "Toggle Flame": pygame.K_f,  "Toggle Repeat Blast": pygame.K_h,
            "Toggle Screen Shake": pygame.K_j,
            "+/- Tail Length/Bloom Speed": pygame.K_t,
            "+/- Flame Volume": pygame.K_v, "+/- Flame Amplitude": pygame.K_a, "+/- Flame Rate": pygame.K_r,
            "+/- Blast Width": pygame.K_w, "+/- Blast Speed": pygame.K_s, "+/- Blast Duration": pygame.K_d,
            "+/- Shake Duration": pygame.K_z, "+/- Shake Intensity": pygame.K_x,
            "Controls": pygame.K_i, "Settings": pygame.K_o, "Pause": pygame.K_p,
            "Toggle Fullscreen": "Tab", "Quit": "Esc"}

controller_map = {'square': 0, 'X': 1, 'circle': 2, 'triangle': 3, 'L1': 4, 'R1': 5, 'L2': 6, 'R2': 7, 'share': 8,
                  'options': 9, 'left_analog_press': 10, 'right_analog_press': 11, 'PS': 12, 'touchpad': 13,
                  'left_analog_x': 0,  'left_analog_y': 1, 'right_analog_x': 2,  'right_analog_y': 5}

fonts = {'small_font': '../assets/fonts/small_font.png',
         'large_font': '../assets/fonts/large_font.png'}
