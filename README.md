# Chrome Dino Game AI

Welcome to my Chrome Dino Game AI project! 🎮 This is a recreation of the classic Chrome Dino game built in Pygame, where I’ve trained an AI using NEAT (NeuroEvolution of Augmenting Topologies) to jump, duck, and dodge its way to a high score of 5000+. Check out the video on my LinkedIn to see it in action: Phase 1 with clueless dinos, Phase 2 of the brain evolving, and Phase 3 hitting that sweet high score! 🌟

## Requirements

To run this project on your machine, you’ll need:

- **Python 3.7+** 🐍
- **Pygame**: For the game itself (`pip install pygame`)
- **NEAT-Python**: For the AI training (`pip install neat-python`)
- A virtual environment is optional but recommended:  
  - Create: `python -m venv .venv`  
  - Activate (Windows): `.venv\Scripts\activate`  
  - Activate (Mac/Linux): `source .venv/bin/activate`

## How to Run

1. Clone this repo:  
   `git clone https://github.com/mhs3n/Google_Dino_neat.git`  
2. Navigate to the folder:  
   `cd dino-game-ai`  
3. Install the requirements:  
  
4. Run the game:  
   `python dino_neat.py`  
5. Watch the dinos evolve! The AI starts from scratch and learns to play over generations. 🧠

## Project Structure

- `dino_neat.py`: The main script with the game and NEAT AI logic.  
- `config-feedforward.txt`: NEAT configuration file for training the AI.  
- `Assets/`: Images for the dino, cacti, birds, and background.  

## Notes

- The AI might take a few dozen generations to get good—patience is key! ⏳  
- Want to tweak it? Play with the `config-feedforward.txt` settings like `pop_size` or `node_add_prob`.  

Enjoy, and let me know what you think! What game should the AI learn next? 🚀