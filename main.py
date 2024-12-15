import argparse
import copy
import numpy as np
import pprint
from project.utils.logging_config import logger
from project.tasks.llm.contract.agent.agent import ContractAgent, Contract_PhysicalAgent
from project.tasks.llm.negotiation.agent.agent import NegotiationAgent, Negotiation_PhysicalAgent
from project.tasks.llm.social_structure.agent.agent import PhysicalAgent
from project.tasks.llm.llm_env_wrapper import LLMEnvWrapper

OUTPUT_DIR = "project/tasks/llm/outputs/"


def parse_args():
    """Parse command-line arguments for running an LLM environment task."""
    parser = argparse.ArgumentParser(description="Run LLM environment tasks with specified configurations.")

    parser.add_argument(
        '--task_name',
        type=str,
        choices=[
            "easy_contract", "hard_contract",
            "easy_negotiation", "hard_negotiation",
            "social_structure_unconnected", "social_structure_connected",
            "social_structure_ind_group", "social_structure_ovlp_group",
            "social_structure_hierarchical", "social_structure_dynamic"
        ],
        default="easy_contract",
        help="Name of the task scenario to run."
    )

    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4o-mini',
        help="Model name or ID to use for the agents."
    )

    parser.add_argument(
        '--max_episodes',
        type=int,
        default=1,
        help="Maximum number of episodes (complete runs) to simulate."
    )

    return parser.parse_args()


def initialize_agents(task_name, model, info, task_info, agent_name_list, env_agent_name_list, player2name):
    """
    Initialize agents based on the task scenario.

    Returns:
        agents (list): Primary agents (e.g., for negotiation/contract phase).
        physical_agents (list): Agents used in the physical execution phase, if applicable.
        phase1_length (int): Length of the initial (negotiation/contract) phase before switching to physical phase.
    """
    agent_num = len(env_agent_name_list)

    if "contract" in task_name:
        phase1_length = 5 * info[env_agent_name_list[0]]["group_num"]
        logger.info("Initializing contract agents | Phase1 length: %d", phase1_length)

        # Negotiation/contract agents
        agents = [
            ContractAgent(
                info=info[env_agent_name_list[agent_id]],
                task_info=task_info,
                agent_id=agent_id,
                agent_name=env_agent_name_list[agent_id],
                agent_name_list=agent_name_list,
                env_agent_name_list=env_agent_name_list,
                player2name=player2name,
                task=task_name,
                model=model
            ) for agent_id in range(agent_num)
        ]
        for agent in agents:
            agent.reset()

        # Physical agents
        physical_agents = [
            Contract_PhysicalAgent(
                info=info[env_agent_name_list[agent_id]],
                task_info=task_info,
                agent_id=agent_id,
                agent_name=env_agent_name_list[agent_id],
                agent_name_list=agent_name_list,
                env_agent_name_list=env_agent_name_list,
                player2name=player2name,
                task=task_name,
                model=model
            ) for agent_id in range(agent_num)
        ]
        for p_agent in physical_agents:
            p_agent.reset()

    elif "negotiation" in task_name:
        phase1_length = info[env_agent_name_list[0]]["negotiation_steps"]
        logger.info("Initializing negotiation agents | Phase1 length: %d", phase1_length)

        # Negotiation/contract agents
        agents = [
            NegotiationAgent(
                info=info[env_agent_name_list[agent_id]],
                task_info=task_info,
                agent_id=agent_id,
                agent_name=env_agent_name_list[agent_id],
                agent_name_list=agent_name_list,
                env_agent_name_list=env_agent_name_list,
                player2name=player2name,
                task=task_name,
                model=model
            ) for agent_id in range(agent_num)
        ]
        for agent in agents:
            agent.reset()

        # Physical agents
        physical_agents = [
            Negotiation_PhysicalAgent(
                info=info[env_agent_name_list[agent_id]],
                task_info=task_info,
                agent_id=agent_id,
                agent_name=env_agent_name_list[agent_id],
                agent_name_list=agent_name_list,
                env_agent_name_list=env_agent_name_list,
                player2name=player2name,
                task=task_name,
                model=model
            ) for agent_id in range(agent_num)
        ]
        for p_agent in physical_agents:
            p_agent.reset()

    elif "social_structure" in task_name:
        phase1_length = 0
        logger.info("Initializing social structure agents | No pre-physical negotiation phase.")

        # No negotiation phase, directly use physical agents
        agents = []
        physical_agents = [
            PhysicalAgent(
                info=info[env_agent_name_list[agent_id]],
                task_info=task_info,
                agent_id=agent_id,
                agent_name=env_agent_name_list[agent_id],
                agent_name_list=agent_name_list,
                env_agent_name_list=env_agent_name_list,
                player2name=player2name,
                task=task_name,
                model=model
            ) for agent_id in range(agent_num)
        ]
        for p_agent in physical_agents:
            p_agent.reset()

    else:
        # If we get here, it's an unsupported or unexpected task name
        logger.error("Unsupported task name encountered: %s", task_name)
        raise ValueError(f"Unsupported task name: {task_name}")

    return agents, physical_agents, phase1_length


def map_player_to_agent_roles(agent_num):
    """Return agent name lists and player-to-name mapping depending on agent_num."""
    if agent_num == 4:
        agent_name_list = ['carpenter_0', 'carpenter_1', 'miner_0', 'miner_1']
        player2name = {
            'player_0': 'carpenter_0',
            'player_1': 'carpenter_1',
            'player_2': 'miner_0',
            'player_3': 'miner_1'
        }
    elif agent_num == 8:
        agent_name_list = [
            'carpenter_0', 'carpenter_1', 'carpenter_2', 'carpenter_3',
            'miner_0', 'miner_1', 'miner_2', 'miner_3'
        ]
        player2name = {
            'player_0': 'carpenter_0',
            'player_1': 'carpenter_1',
            'player_2': 'carpenter_2',
            'player_3': 'carpenter_3',
            'player_4': 'miner_0',
            'player_5': 'miner_1',
            'player_6': 'miner_2',
            'player_7': 'miner_3'
        }
    else:
        logger.error("Unexpected number of agents: %d. Supported: 4 or 8.", agent_num)
        raise ValueError(f"Unsupported number of agents: {agent_num}")

    return agent_name_list, player2name


def main():
    """Main entry point for executing the LLM environment simulation."""
    args = parse_args()

    # Log initial configuration
    logger.info("==========================================")
    logger.info("Starting LLM environment run.")
    logger.info("Configuration | Task: %s | Model: %s | Max Episodes: %d", args.task_name, args.model, args.max_episodes)
    logger.info("==========================================")
    
    env = LLMEnvWrapper()
    task_info = env.env_handler.config_loader.config.task

    # Log task configuration details (if available)
    logger.info("Task Info Loaded: %s", pprint.pformat(task_info))

    for episode in range(args.max_episodes):
        obs, info = env.reset()
        agent_num = len(info)
        env_agent_name_list = list(info.keys())

        logger.info("---------------------------------------------------")
        logger.info("Starting Episode %d | Task: %s | Model: %s | Agents: %d",
                    episode, args.task_name, args.model, agent_num)
        logger.info("---------------------------------------------------")

        # Map player_# to agent roles
        try:
            agent_name_list, player2name = map_player_to_agent_roles(agent_num)
        except ValueError:
            logger.error("Unable to proceed with this configuration.")
            break

        max_length = info[env_agent_name_list[0]]["max_length"]
        logger.info("Episode %d | Task: %s | Model: %s | Max Steps: %d", 
                    episode, args.task_name, args.model, max_length)

        # Initialize agents
        try:
            agents, physical_agents, phase1_length = initialize_agents(
                task_name=args.task_name,
                model=args.model,
                info=info,
                task_info=task_info,
                agent_name_list=agent_name_list,
                env_agent_name_list=env_agent_name_list,
                player2name=player2name
            )
        except ValueError as e:
            logger.error("Error during agent initialization: %s", e)
            break

        pre_action = [0] * agent_num
        pre_position = [0] * agent_num
        reward_total = [0] * agent_num

        # Start simulation steps
        for step in range(max_length):
            # Switch to physical agents after negotiation/contract phase ends
            if step == phase1_length and physical_agents:
                logger.info("Episode %d | Switching to physical agents at step %d", episode, step)
                agents = physical_agents

            current_phase = "PHYSICAL" if step >= phase1_length else "NEGOTIATION/CONTRACT"
            logger.info("%s PHASE | Episode: %d | Task: %s | Model: %s | Step: %d/%d",
                        current_phase, episode, args.task_name, args.model, step, max_length)

            # Compute actions for each agent
            actions = {}
            for agent_id, agent in enumerate(agents):
                agent_name = agent.agent_name
                llm_obs = agent.update_obs(obs[agent_name], pre_position, pre_action)
                agent.update_policy(llm_obs)
                action = agent.Action.action
                agent.Action.new()

                pre_action[agent_id] = copy.deepcopy(action)
                pre_position[agent_id] = copy.deepcopy(llm_obs['current_pos'])
                actions[agent_name] = action

                current_plan = agent.current_plan
                logger.info(
                    "%s PHASE | Episode: %d | Step: %d | Agent: %s | Current Plan: %s | Action: %s",
                    current_phase, episode, step,
                    agent.agent_name_list[agent.env_agent_name_list.index(agent_name)],
                    current_plan, action
                )

            # Execute actions in the environment
            next_obs, reward, terminated, truncated, info = env.step(actions)
            obs = next_obs

            # Update cumulative rewards
            for agent_id in range(agent_num):
                reward_total[agent_id] += reward[env_agent_name_list[agent_id]]

            logger.info(
                "%s PHASE | Episode: %d | Step: %d | Immediate Reward: %s | Cumulative Reward: %s",
                current_phase, episode, step, reward, reward_total
            )

            # If terminated or truncated flags are present and indicate early stopping, break early
            if any(terminated.values()) or any(truncated.values()):
                logger.info("Episode %d ended early due to termination or truncation at step %d.", episode, step)
                break

        # Episode completion log
        logger.info("Episode %d completed. Final cumulative rewards: %s", episode, reward_total)
        logger.info("=======================================================")


if __name__ == "__main__":
    main()
