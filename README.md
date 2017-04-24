# Pygame Platformer

## About
<img src="/nog2k17.png" width="360">

## Ideas for student projects

### Easy

- Change the dimensions of the game window.
- Name your game.
- Find your own custom artwork for blocks.
- Find your own custom artwork for the hero.
- Find your own custom artwork for enemies.
- Find your own fonts.
- Find your own sound effects and music.
- Customize the background layer for a level.
- Customize the scenery layer for a level.
- Create a custom splash screen.
- Change point value for coins.
- Make power-ups give points to the player.
- Make health display hearts/max.
- Update the display_stats function so that it shows the name of the current level.

### Medium

- Let the 'S' key toggle sound on and off. Show a little speaker/mute icon to indicate the current state of sound.
- Let the 'M' key toggle music on and off. Show a little note icon (crossed out or uncrossed) to indicate the current state of music.
- Create your own custom artwork. http://www.piskelapp.com/ is a good site for this.
- Give points for completing a level.
- Create invincibility (star) power-up.
- Create a power-up which increases the max hearts a player can have.
- Add prizes other than coins and give them a point value.
- Track coins separately from the score. (They can still be worth points.) Give an extra live when a number of coins is earned. Reset the coin count after a life is given.
- Invent your own power-up.
- Invent a "power-up" which has a negative consequence on a player other than reducing hearts or lives.
- Display lives with a character icon x number of lives.
- Make a player die when they fall through the bottom of the world. You'll need to make sure enemies that fall through are also removed from the game. Pygame's sprite.kill() function will be useful for this.
- Make a credits screen for when the player wins the game.
- Add a 'Pause' stage to the game which is activated when the player presses 'P' (or a button on the joystick). All movement and time should stop during a pause stage. Pressing 'P' again should resume. Be sure to show a message indicating the game is paused.
- Add a victory sound that plays when the game is won.

### Hard

- Design a standard level.
- Incorporate different kinds of levels (normal, space level, underwater, etc.) into the game.
- Change the game so that it uses the XBox controller instead of the keyboard. (https://github.com/joncoop/pygame-xbox360controller)
- Kill enemies when you land on them. You'll need to check which direction you hit the enemy from in process enemies. Award different point values for different enemy types.
- Make the game save high scores to a text file in a data folder.

### How clever are you?

- Add a moving element such as clouds or flickering torches to the background or scenery layer.
- Create Bullet enemy.
- Create some other kind of custom enemy with unique behavior.
- Display actual hearts to show health. Show empty hearts when health not full.
- Show time on the stats layer. Give a time bonus for completing a level. Have the hero die if the level is not completed in a set amount of time.
- Add secret parts of the level that utilize vertical scrolling.
- Add ladders to the game. If a player is on a ladder, don't apply gravity. Assign vy by player input instead.
- Put warp pipes or doors in the game.
- Put switches in the game that open areas of a level.
- Put mystery blocks in the game.

### More!

- Create a text/image advertisement for your game.
- Create a video advertisement for your game.
- Write a review of a classmate's game.
- Create a website for your game.


## Grading

Each small phase of the game we've built in class will count as a minor assessment. (You'll get a 100% for each unless I suspect that you're not keeping up. In that case, I'll check up on you individually.)

One major assessment will be to create a single level of a game with custom artwork, complex level design, and a couple selected easy/medium features.

The second major assessment will be customizing the game by adding a variety of easy, medium, hard features, each of which has different point values.
