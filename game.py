import random
from project.env.environment import Environment

def main():
    # Initialize the environment
    env = Environment(config_name='./config/main.json')

    # Reset the environment to start a new episode
    obs, infos = env.reset()

    # Run a simple game loop
    done = False
    while not done:
        # Generate random actions for each player
        action_dict = {player_name: random.choice(['move_up', 'move_down', 'move_left', 'move_right'])
                       for player_name in obs.keys()}

        # Step the environment with the random actions
        next_obs, rewards, terminateds, truncateds, infos = env.step(action_dict)

        # Check if the episode is done
        done = terminateds['__all__']

        # Print observations and rewards for debugging
        print(f"Observations: {next_obs}")
        print(f"Rewards: {rewards}")

    # Close the environment
    env.close()

if __name__ == "__main__":
    main() 