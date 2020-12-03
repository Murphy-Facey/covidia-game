# Covidia

This is a covid based game created using the python game library, pygame

## How to run 

After install python if you have not, you need to install pygame using the command below
```
pip install pygame
```

Then run the main.py file using this command below
```
python main.py
```

## Game Information

The player can change color based on the state they are currently in.
*PURPLE*: means the player is wearing a mask
*AQUA*: means the player has a sanitizer and can kill covidia
*GREEN*: means the player is quarantined
_Please note: When player catches covidia, the player is quarantined and loses immunity towards covidia (which equates to life)_

The enemy can also change color based of the state they are currently in:
*WHITE*: means the enemy is scared
*SHADES OF GREEN*: means the enemy can roam freely
*DARK BLUE*: means enemy has been sanitized
_Please note: One of the enemy is set to chase the player and all the rest roam randomly._

## Contribution

This source code for the game is based of [a-plus-coding's pacman game](https://github.com/a-plus-coding/pacman-with-python)