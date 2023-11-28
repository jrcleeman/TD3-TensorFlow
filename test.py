import gym
import pybullet_envs
import os
from model import TD3
from replaybuffer import ReplayBuffer
import datetime as dt
import tensorflow as tf
from printerEnv import FDM

if __name__ == '__main__':
    # initialise the environment
    env = FDM()
    action_dim = env.action_space#.shape[0]
    state_dim = env.observation_space#.shape[0]
    max_action = 1.0 #float(env.action_space.high[0])


    # initialise the replay buffer
    memory = ReplayBuffer()
    # initialise the policy
    policy = TD3(state_dim, action_dim, max_action, current_time=None, summaries=True)

    total_timesteps = 0
    episode_num = 0
    episode_reward = 0
    done = True
    #Number of Test Games
    testGames = 30
    #Load Saved Policy
    policy.load_models()

    for i in range(testGames - 1):
        state = env.reset()
        done = False
        episode_reward = 0
        episode_timesteps = 0
        episode_num += 1

        while not done:
            # select an action from the actor network with noise
            action = policy.select_action(state, noise=False)

            # the agent plays the action
            next_state, reward, done = env.step(action)

            # add to the total episode reward
            episode_reward += reward
            # update the state, episode timestep and total timestep
            state = next_state
            episode_timesteps += 1
            total_timesteps += 1
        
        #Print Ep Reward
        #print('Episode: {}, Episode Reward: {:.2f}'.format(episode_num, total_timesteps, episode_reward))
