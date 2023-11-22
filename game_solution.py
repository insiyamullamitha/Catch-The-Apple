"""Catch The Apple Game (1280 x 720 window dimensions).

This module uses the Tkinter library. Apples fall from the top and player must catch them using an arrow-controlled basket.

Default left and right arrow keys control movement. Players are able to change the keys.

The game tracks the player's number of lives (lost when they do not catch an apple, or catch a rotten one) and score.

The game ends when the player loses all their lives or quits. Players have options to pause or save game for later.

Leaderboard records top 5 player's names and scores.

Author: Insiya Mullamitha
Date: November 2023
"""


from tkinter import Tk, Canvas, PhotoImage, Button, messagebox, simpledialog
import random

window = Tk()

# Constant game values
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
APPLE_SPEED_MIN = 8
APPLE_SPEED_MAX = 20
APPLE_VALUE = 5
BASKET_WIDTH = 230
BASKET_HEIGHT = 212
BASKET_SPEED = 50

# Game images files loaded using PhotoImage
BACKGROUND_IMAGE = PhotoImage(file="images/game_background.png")
BOSS_KEY_IMAGE = PhotoImage(file="images/boss_key_background.png")
BASKET_IMAGE = PhotoImage(file="images/basket.png")
APPLE_IMAGE = PhotoImage(file="images/apple.png")
ROTTEN_APPLE_IMAGE = PhotoImage(file="images/rotten_apple.png")

# Direction keys containing arrow button text and corresponding keyboard events
DIRECTION_KEYS = {"LEFT/RIGHT": ["<Left>", "<Right>"],
                  "A/D": ["a", "d"],
                  "J/L": ["j", "l"],
                  "-/+": ["<minus>", "<equal>"]}

# Global variables used throughout program
left_arrow_key = "<Left>"
right_arrow_key = "<Right>"
arrow_key_text = "LEFT/RIGHT"
state = None
lives = 3
current_score = 0
player_name = ""
basket_x = 530
apple_speed = APPLE_SPEED_MIN
number_of_apples = 1
apple_objects = []


# Canvas object set to window size and turquoise colour
canvas = Canvas(window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, background="#287484")
canvas.pack()
canvas.focus_set()


def set_window_dimensions(w, h):
    """Create Tk window with given dimensions and position in the centre of the screen

    Parameters:
    w (int): window width
    h (int): window height

    Returns:
    window: window object with coordinates, dimensions and title
    """
    window.resizable(False, False)
    window.title("Apple Catcher Game")
    # Compare window and screen size to position window in the centre
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_coordinate = int((screen_width/2) - (w/2))
    y_coordinate = int((screen_height/2) - (h/2))
    window.geometry(str(w) + "x" + str(h) + "+" + str(x_coordinate) + "+" + str(y_coordinate))
    return window


def bind_keyboard_inputs():
    """Bind user-inputted keys that player will use during game

    Allow user to pause, cheat, use boss key and move basket
    """
    # Left and right arrow keys for basket, can be changed by accessing global function IDs
    global left_key_bind, right_key_bind
    left_key_bind = canvas.bind(left_arrow_key, move_basket)
    right_key_bind = canvas.bind(right_arrow_key, move_basket)
    # Pause key
    canvas.bind("p", lambda event: pause_game())
    # Boss key
    canvas.bind("b", lambda event: start_boss_key())
    # Cheat code keys
    canvas.bind("s", lambda event: cheat_slow_apple())
    canvas.bind("i", lambda event: cheat_maximise_lives())


def start_menu():
    """Display initial menu buttons and game instructions"""
    global instruction_text
    # Menu buttons including leaderboard, play and change arrow key
    create_change_arrow_keys_button()
    create_leaderboard_button()
    create_play_button()
    # Game instructions displayed above and below menu screen buttons
    canvas.create_text(640, 280, text="PRESS PLAY TO START AND 'P' TO PAUSE OR QUIT DURING THE GAME...",
                       fill="black", font=("Arial", 15, "bold"))
    instruction_text = canvas.create_text(640, 430, text="USE YOUR CHOSEN ARROW KEYS TO MOVE THE BASKET LEFT AND RIGHT AND COLLECT AS MANY APPLES AS YOU CAN (BUT AVOID THE ROTTEN ONES!).",
                       fill="black", font=("Arial", 15, "bold"))
    display_image(APPLE_IMAGE, 600, 130)


def create_change_arrow_keys_button():
    """Create button which changes left and right arrow key binding when clicked"""
    global change_arrow_key_button
    change_arrow_key_button = Button(window, highlightbackground="lightblue", fg="red", text=arrow_key_text, height=3, width=8, command=handle_change_arrow_keys_button, state="normal")
    # Place on the right of play button
    change_arrow_key_button.place(x=702, y=320)


def handle_change_arrow_keys_button():
    """Change text on arrow key button to represent the new key binding"""
    global change_arrow_key_button
    global arrow_key_text
    try:
        # Find position of new arrow key text in DIRECTIONS_KEYS dictionary
        current_keys = change_arrow_key_button.cget("text")
        arrow_key_text_index = list(DIRECTION_KEYS).index(current_keys) + 1
        # Assign new arrow key text
        arrow_key_text = list(DIRECTION_KEYS)[arrow_key_text_index]
    except:
        # If index is out of range, assign first key text in dictionary
        arrow_key_text = list(DIRECTION_KEYS)[0]
    # Change button text with determined value
    change_arrow_key_button["text"] = arrow_key_text
    # Change actual key binding
    bind_new_arrow_keys(change_arrow_key_button["text"])


def bind_new_arrow_keys(new_arrow_keys):
    """Unbind existing left and right arrow key and bind new user-selected ones

    Parameters:
    new_arrow_keys (str): text on arrow_key_button representing the new key binding
    """
    global left_arrow_key, right_arrow_key, left_key_bind, right_key_bind
    # Unbind previously selected left and right arrow keys
    canvas.unbind(left_arrow_key, left_key_bind)
    canvas.unbind(right_arrow_key, right_key_bind)
    # Determine new left and arrow keys using new text on arrow_key_button
    left_arrow_key = DIRECTION_KEYS[new_arrow_keys][0]
    right_arrow_key = DIRECTION_KEYS[new_arrow_keys][1]
    # Bind new keys to move_basket function
    left_key_bind = canvas.bind(left_arrow_key, move_basket)
    right_key_bind = canvas.bind(right_arrow_key, move_basket)


def create_leaderboard_button():
    """Create leaderboard button which shows the leaderboard page when clicked"""
    global leaderboard_button
    leaderboard_button = Button(window, highlightbackground="lightblue", fg="blue", text="LEADERBOARD",
                                height=3, width=8, command=handle_leaderboard_button, state="normal")
    # Place on left side of play button
    leaderboard_button.place(x=472, y=320)


def handle_leaderboard_button():
    """Change button positions and text before calling function to display leaderboard table in the centre of the screen"""
    global instruction_text
    # Remove game instructions
    canvas.itemconfig(instruction_text, text="")
    # Remove irrelevant buttons and reposition others
    leaderboard_button.place_forget()
    change_arrow_key_button.place(x=534, y=600)
    play_button.place(x=664, y=600)
    display_leaderboard()


def update_leaderboard():
    """Check new player score against existing leaderboard scores in file

    Update text file if the new score is higher and lists in descending order
    """
    # Assign player_high_scores to 2D list containing top 5 player names and scores
    player_high_scores = get_leaderboard_scores()
    # Check if current_score is higher than any in the list, return index if True
    for x in range(4, -1, -1):
        if current_score <= player_high_scores[x][1]:
            if x == 4:
                return
        else:
            change_index = x
    # Insert new score and name into list and remove the last element so there are only 5
    player_high_scores.insert(change_index, [player_name.upper(), current_score])
    player_high_scores.pop()
    lines = ""
    # Update leaderboard text file with new leaderboard information
    for score in player_high_scores:
        lines += score[0] + "," + str(score[1]) + "\n"
    with open("leaderboard.txt", "w") as file:
        file.write(lines)


def get_leaderboard_scores():
    """Return leaderboard leaders and corresponding scores in 2D list

    Returns:
    player_high_scores (2D list): List of 5 elements containing player name and score
    """
    player_high_scores = []
    # Open leaderboard text file for reading and storing each line in list
    with open("leaderboard.txt", "r") as file:
        lines = file.readlines()
    # Clean data and split each list element into player and score
    for line in lines:
        line = line.strip("\n").split(",")
        line[1] = int(line[1])
        player_high_scores.append(line)
    # Sort list using score (2nd item in each element)
    player_high_scores.sort(key=lambda x: x[1], reverse=True)
    return player_high_scores


def display_leaderboard():
    """Draw leaderboard table using canvas shapes

    Display 5 leaderboard player names and scores
    """
    # Use coloured rectangles to highlight sections of the table
    canvas.create_rectangle(265, 100, 515, 550, fill="#56909c")
    canvas.create_rectangle(515, 100, 1015, 175, fill="#56909c")
    canvas.create_rectangle(515, 175, 1015, 550, fill="#80acb5")
    # Draw horizontal and vertical lines to create a table with 3 columns and 6 rows
    for x in range(7):
        canvas.create_line(265, 75*(x+1)+25, 1015, 75*(x+1)+25, fill="black", width=5)
    for y in range(4):
        canvas.create_line((y+1)*250+15, 100, (y+1)*250+15, 550, fill="black", width=5)
    # Headers for table
    canvas.create_text(639, 145, text="PLAYER", fill="black", font=("Arial", 40))
    canvas.create_text(885, 145, text="SCORE", fill="black", font=("Arial", 40))
    # Iterate through leaderboard list and display information (Rank, Player, Score) in table
    player_high_scores = get_leaderboard_scores()
    for p, player in enumerate(player_high_scores):
        canvas.create_text(390, 145+((p+1)*75), text=str(p+1)+".", fill="black", font=("Arial", 40))
        canvas.create_text(639, 145+((p+1)*75), text=player[0], fill="black", font=("Arial", 40))
        canvas.create_text(885, 145+((p+1)*75), text=player[1], fill="black", font=("Arial", 40))


def create_play_button():
    """Create play button object which starts game process when clicked"""
    global play_button
    play_button = Button(window, highlightbackground="lightblue", fg="#32CD32", text="PLAY", height=3, width=5, command=check_recontinue, state="normal")
    # Place button in centre of the menu screen
    play_button.place(x=602, y=320)


def check_recontinue():
    """Check whether player has a stored previous game in file

    Give player the choice to restore these values

    Ask player to enter their name
    """
    # Check if previous_games_values text file is empty
    with open("previous_game_values.txt", "r") as file:
        if not file.read(1):
            recontinuing = False
        # Only give player option to reload if file is not empty
        else:
            recontinuing = messagebox.askyesno("Previous game",
                                               "Would you like to recontinue the previous game?  Your progress will be lost otherwise...")
    # Restores game values if possible and player agrees
    if recontinuing:
        get_previous_game_values()
    enter_player_name()


def get_previous_game_values():
    """Restore previous game values from text file and loads into current game values"""
    global current_score, lives, apple_speed, number_of_apples
    # Reads and cleans information from previous_game_values text file into array
    with open("previous_game_values.txt", "r") as file:
        values = [line.strip() for line in file]
    # Each line in file corresponds to game value
    current_score = int(values[0])
    lives = int(values[1])
    apple_speed = int(values[2])
    number_of_apples = int(values[3])


def enter_player_name():
    """Use popup box to ask player for their name

    Continuously ask until their name is within 3-10 characters or they press cancel

    Start game once name is acceptable
    """
    global player_name
    player_name = ""
    while len(player_name) < 3 or len(player_name) > 10:
        player_name = simpledialog.askstring("Name", "What is your name?")
        # If player presses cancel, return to existing screen
        if player_name is None:
            return
    start_game_objects()


def start_game_objects():
    """Delete previous game values

    Delete menu screen buttons

    Create game objects and enters apple falling loop
    """
    global state
    state = "play"
    # Discard previous_game_values text file contents as player has chosen to use or delete
    open("previous_game_values.txt", "w").close()
    # Clear menu or leaderboard screen of buttons and other text
    canvas.delete("all")
    play_button.destroy()
    leaderboard_button.destroy()
    change_arrow_key_button.destroy()
    # Display game screen background and objects
    display_image(BACKGROUND_IMAGE, 0, 0)
    create_basket()
    create_score()
    create_lives()
    window.after(30000, increase_number_of_apples)
    for _ in range(number_of_apples):
        apple_objects.append(create_apple())
    move_apples()


def display_image(image_file, coord_x, coord_y):
    """Display given image on screen at given coordinates

    Parameters:
    image_file (PhotoImage object)
    coord_x: desired x-coordinate of image
    coord_y: desired y-coordinate of image

    Returns:
    canvas image object
    """
    return canvas.create_image(coord_x,coord_y, anchor="nw", image=image_file)


def create_basket():
    """Create basket object in the bottom centre of the game screen"""
    global basket_object
    basket_object = display_image(BASKET_IMAGE, basket_x, 500)


def create_score():
    """Display current_score within blue rectangle text box in top left corner"""
    global score_object, score_rectangle
    score_rectangle = canvas.create_rectangle(22, 30, 158, 70, fill="lightblue")
    # Expand size of blue text box according to size of score
    if len(str(current_score)) > 1:
        for _ in range(len(str(current_score))-1):
            update_textbox_length()
    score_object = canvas.create_text(87, 50, text="Score: " + str(current_score),
                                      fill="black", font=("Helvetica", "30", "bold"))


def update_score(value):
    """Update current_score with given value and update score_object text

    Check whether size of current_score has increased and consequently changed textbox length

    Increase speed of apple every 15 points

    Parameters:
    value (int): used to increment/decrement current_score
    """
    global current_score, apple_speed
    # Adjust text box size if size of score has increased
    if len(str(current_score + value)) > len(str(current_score)):
        update_textbox_length()
    # Ensure that current_score cannot be negative
    current_score = max(current_score+value, 0)
    # Update score text on screen
    canvas.itemconfig(score_object, text="Score: " + str(current_score))
    # Increase apple_speed every 15 points
    if current_score % 15 == 0:
        apple_speed += 1


def update_textbox_length():
    """Increase length of score object rectangle"""
    x0, y0, x1, y1 = canvas.coords(score_rectangle)
    x0 -= 8
    x1 += 8
    canvas.coords(score_rectangle, x0, y0, x1, y1)


def create_lives():
    """Display number of lives in red rectangle text box below current_score"""
    global lives_object
    canvas.create_rectangle(22, 80, 158, 120, fill="#FF6961")
    lives_object = canvas.create_text(87, 100, text="Lives: " + str(lives),
                                      fill="black", font=("Helvetica", "30", "bold"))


def update_lives(decrease=True):
    """Update number of lives and updates lives_object text

    Number of lives can be decremented (rotten/missed apple) or incremented (boss key) using decrease value

    Parameters:
    decrease (Boolean): default True decrements number of lives, False increments
    """
    global lives_object, lives
    # Decreases or increases number of lives depending on decrease
    if decrease:
        lives -= 1
    else:
        if lives < 3:
            lives += 1
    # Updates lives_object text on screen
    canvas.itemconfig(lives_object, text="Lives: " + str(lives))


def create_apple():
    """Create apple object at the top of the screen in a random x position

    Randomly assign rotten or normal apple image and corresponding tag

    Returns:
    apple_object: canvas apple_object with calculated coordinates
    """
    # Random x position within window
    apple_x = random.randint(BASKET_SPEED-10, WINDOW_WIDTH-BASKET_WIDTH+150)
    # Random y position placed randomly above screen to space out apples
    apple_y = random.randint(-1500, 0)
    # Randomly generate normal (90% weight) or rotten (10% weight) apple_object
    apple_object = canvas.create_image(apple_x, apple_y, anchor="nw", image=APPLE_IMAGE, tags="normal")
    random_apple = random.choice([ROTTEN_APPLE_IMAGE,
                                  APPLE_IMAGE, APPLE_IMAGE, APPLE_IMAGE,
                                  APPLE_IMAGE, APPLE_IMAGE, APPLE_IMAGE,
                                  APPLE_IMAGE, APPLE_IMAGE, APPLE_IMAGE])
    tag = "normal"
    if random_apple == ROTTEN_APPLE_IMAGE:
        tag = "rotten"
    # Assign new apple_object with rotten/normal image and tag
    canvas.itemconfig(apple_object, image=random_apple, tags=tag)
    return apple_object


def move_apples():
    """Move apple by its current speed every 10ms

    Check that the apple has not reached the floor or collided with basket before moving

    Create more apples if there is 1 or less apples on screen

    Stop moving when player has paused/quit game or there are no more lives left

    Returns:
    end_game (function): End of game when lives are all lost
    """
    global state, apple_objects
    # Only moves apple when game is in play
    if state == "paused":
        return "Paused"
    state = "play"
    # Checks if there is one or less apple_objects and potentially creates one more if so
    if len(apple_objects) <= 1:
        for _ in range(random.randint(0, number_of_apples)):
            window.after(random.randint(1, 5), lambda : apple_objects.append(create_apple()))
    # Moves every existing apple and checks for collisions
    for apple_object in apple_objects:
        canvas.move(apple_object, 0, apple_speed)
        # If apple is at the bottom of the screen check if collision has occurred
        if canvas.coords(apple_object)[1] > WINDOW_HEIGHT - BASKET_HEIGHT + 35:
            check_apple_caught(apple_object)
            # Ends game if no more lives
            if lives <= 0:
                canvas.update()
                return end_game()
    # Function repeats every 10ms as long as game in play
    window.after(10, move_apples)


def delete_apple(apple_object):
    """Remove apple_object that have reached the bottom from the apple_objects list and screen

    Parameters:
    apple_object: canvas apple_object to be removed
    """
    global apple_objects
    apple_objects.remove(apple_object)
    canvas.delete(apple_object)


def increase_number_of_apples():
    """Increase number of falling apples

    Repeat every 30 seconds as long as there is a maximum of 4

    Stop increasing when player is no longer in game
    """
    global number_of_apples
    # Verify that user is in one of the game states
    if state is not None:
        if number_of_apples <= 3:
            number_of_apples += 1
            window.after(30000, increase_number_of_apples)
        else:
            return


def check_apple_caught(apple_object):
    """Check if apple and basket have collided using boundary boxes

    Use apple tag to determine whether apple is rotten or normal

    Update score and number of lives depending on tag
    """
    global apple_objects
    # Basket and apple boundary boxes
    basket_bbox = canvas.bbox(basket_object)
    apple_bbox = canvas.bbox(apple_object)
    # Check for collision between apple bottom and basket top
    if basket_bbox[0] < apple_bbox[0] < basket_bbox[2]:
        # Increase score if apple is normal
        if apple_object in canvas.find_withtag("normal"):
            update_score(APPLE_VALUE)
        # Decrease score and number of lives if apple is rotten
        else:
            update_score(-APPLE_VALUE)
            update_lives()
    # Decrease number of lives as normal apple has reached the bottom and not been collected
    elif apple_object in canvas.find_withtag("normal"):
        update_lives()
    # Removes apple as it has reached bottom
    delete_apple(apple_object)


def pause_game():
    """Check that player is in the middle of the game and pauses if they press "p"

    Create buttons to allow player to quit with and without saving their progress

    Bind "p" key so they can unpause by pressing it again
    """
    # Check that game is currently being played before pausing
    global state
    if state == "play":
        state = "paused"
        # Display option buttons that allow player to quit with and without saving
        global quit_button, save_button
        quit_button = Button(window, highlightbackground="lightblue", fg="red", text="QUIT",
                             height=3, width=5, command=quit_game, state="normal")
        quit_button.place(x=602, y=280)
        save_button = Button(window, highlightbackground="lightblue", fg="#32CD32", text="QUIT AND SAVE PROGRESS",
                             height=3, width=18, command=save_game, state="normal")
        save_button.place(x=545, y=370)
        # Bind "p" key so player can unpause
        canvas.bind("p", lambda event: unpause_game())


def quit_game():
    """End game and resets all game values

    Return to menu screen
    """
    # Delete pause state menu options and clear screen
    global state, quit_button, save_button
    quit_button.destroy()
    save_button.destroy()
    canvas.delete("all")
    # Bind "p" so player can pause in future game
    canvas.bind("p", lambda event: pause_game())
    state = None
    # Reset all game values and return to menu screen
    reset_values()
    start_menu()


def save_game():
    """Save player's current_score, lives and apple_speed to text file"""
    with open("previous_game_values.txt", "w") as file:
        file.write(str(current_score) + "\n" +
                   str(lives) + "\n" +
                   str(apple_speed) + "\n" +
                   str(number_of_apples))
    # Reset game values and return to menu screen
    quit_game()


def unpause_game():
    """Unpause game when player presses "p"

    Destroy mid-game menu options

    Bind "p" so that player can pause again when they press it
    """
    # Exit pause state and remove pause menu option
    global state, quit_button, save_button
    state = None
    quit_button.destroy()
    save_button.destroy()
    # Bind "p" to allow player to pause again
    canvas.bind("p", lambda event: pause_game())
    # Continue apple falling movement
    move_apples()


def start_boss_key():
    """Check that player is in the middle of the game and show boss key background if they press "b"

    Display image of GitLab repo and change window title to reflect

    Pause game and binds key so player can resume when they press "b"
    """
    # Check that player is playing game before performing boss key
    global state
    if state == "play":
        global boss_key_background
        # Pause game so player can continue progress
        state = "paused"
        # Bind "b" so player can exit boss key action
        canvas.bind("b", lambda event: end_boss_key())
        # Display image of GitLab and retitle window
        boss_key_background = display_image(BOSS_KEY_IMAGE, 0, 0)
        window.title("gitlab.cs.man.ac.uk")


def end_boss_key():
    """Stop displaying boss key background and resumes game

    Bind "b" so player can use boss key again
    """
    # Clear screen of boss key background and retitle original game name
    global state, boss_key_background
    state = None
    canvas.delete(boss_key_background)
    window.title("Apple Catcher Game")
    # Continue game play as before
    canvas.bind("b", lambda event: start_boss_key())
    move_apples()


def end_game():
    """End game when player loses all lives

    Update leaderboard with new game values

    Return to menu and displays game over messagebox
    """
    # Exit game state
    global state
    state = None
    canvas.delete("all")
    # Update leaderboard table and clear game values
    update_leaderboard()
    reset_values()
    # Return to menu screen with messagebox Game Over information
    start_menu()
    messagebox.showinfo("showinfo",
                         "Game over! Click play to start again or check the leaderboard to see if you beat a high score :)")


def reset_values():
    """Reset lives, current_score, apple_speed, basket_x and player_name and apple_objects ready for next game"""
    global lives, current_score, apple_speed, basket_x, player_name, apple_objects, number_of_apples
    lives = 3
    current_score = 0
    apple_speed = APPLE_SPEED_MIN
    basket_x = 530
    player_name = ""
    apple_objects = []
    number_of_apples = 1


def move_basket(event):
    """Move basket left or right depending on arrow key movement and wall collisions

    Parameters:
    event: triggered by left_arrow_key and right_arrow_key keypress
    """
    # Checks that player is in game before moving basket
    global state, basket_x
    if state == "paused":
        return
    direction = event.keysym
    # Verifies which direction key relates to (left/right)
    if direction in DIRECTION_KEYS[arrow_key_text][0]:
        if basket_x > 30:  # Moving left, basket should not collide with wall
            basket_x -= BASKET_SPEED
    # Moving right, basket should not collide with right wall
    else:
        if basket_x + BASKET_SPEED < WINDOW_WIDTH-BASKET_WIDTH:
            basket_x += BASKET_SPEED
    # Update new basket position on screen
    canvas.moveto(basket_object, basket_x, 500)


def cheat_slow_apple():
    """Cheat key "s" resets apple_speed to original base value during game"""
    # Checks that player is in game play before performing cheat action
    if state != "paused":
        global apple_speed
        apple_speed = APPLE_SPEED_MIN


def cheat_maximise_lives():
    """Cheat key "i" increments number of lives by 1 during game"""
    # Checks that player is in game play before performing cheat action
    if state != "paused":
        update_lives(False)


# Initialise window
window = set_window_dimensions(WINDOW_WIDTH, WINDOW_HEIGHT)

# Bind keyboard inputs and begin program

bind_keyboard_inputs()
start_menu()

window.mainloop()
