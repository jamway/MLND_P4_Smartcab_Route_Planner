from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import random
import itertools
class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.qlearner={}
        self.alpha=None
        self.gamma=None
        self.epsilon=None
        # TODO: Initialize any additional variables here
        # Add qlearner as storage of knowledge
        # Add Parameters for q-learner : Alpha, Gamma, Epsilon

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
 
    def set_learner_parameter(self,alpha,gamma,epsilon):
        #Used to control parameters for action selection and learning process
        self.alpha=alpha
        self.gamma=gamma
        self.epsilon = epsilon
        
    def update(self, t):
        alpha=self.alpha
        gamma=self.gamma
        epsilon=self.epsilon

        if alpha == None:
            alpha = 0.5
        if gamma == None:
            gamma = 0.8
        if epsilon == None:
            epsilon = 0.1
        # Avoid error
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        light = inputs['light']
    
        state=(self.next_waypoint,light)
        # Choose information to memorize : next waypoint, light, check if there is car coming and from which direction.
        self.state = state
        # TODO: Update state
        state_1=state
     
        #Make a copy of state for learning
        # TODO: Select action according to your policy
        action = self.action_selector(state_1,epsilon)
        #Search through memory to find the best action
        # Execute action and get reward
        reward = self.env.act(self, action)
        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
        n_inputs=self.env.sense(self)
        #Gather inputs again for learniing purpose
        #Make a copy of new state for learning
        self.next_waypoint = self.planner.next_waypoint()
        state_2=(self.planner.next_waypoint(),n_inputs['light'])
        #Create next state (or new current state), for learning purpose.
        self.learner(alpha,gamma,state_1,action,state_2,reward)
        # Learn by first state, action executed, following state, and reward
        # TODO: Learn policy based on state, action, reward

    def action_selector(self, state, epsilon):
        actions = self.env.valid_actions
        qlearner=self.qlearner
        if random.random() < epsilon:
            action = random.choice(actions)
            #Exploration rate, to increase the chance of discovering new state
        else:
            q_list=[qlearner.get((state,a),0.0) for a in actions]
            # Find all possible action and corresponding Q values
            # Ensure the action with the best Q is choosen
            count = q_list.count(max(q_list))
            if count > 1:
                action = actions[random.choice([i for i in range(len(actions)) if q_list[i] == max(q_list)])]
                #Avoid confusion made by multiple values that matches maximum value
            else:
                action = actions[q_list.index(max(q_list))]
        return action

            
    def learner(self, alpha, gamma, state, action,n_state,reward):
        qlearner = self.qlearner
        old_value = qlearner.get((state,action), None)
        #Check if state_1 exists in memory, if so retrive value.
 
        max_q_2 = max([qlearner.get((n_state,a),0.0) for a in self.env.valid_actions])
        # Use best value at state_2 as expected maximum future outcome
        value = reward + gamma*max_q_2
        # Discount future value with Gamma and adjust the importance of future reward
        # Plus reward gained to be the value for state_1
        # If state_2 hasn't been visited, this value equals to reward
        
        if old_value is None:
            qlearner[(state,action)]=reward
            # Set initial value to state, action combination
        else:
            qlearner[(state,action)]= old_value + alpha*(value-old_value)
        # Use difference between old value and new value to add experience gradually
        # Further use alpha to adjust how relevant recent experience is.
        # When alpha is high recent experience override old value easily
        self.qlearner = qlearner
        #Store memory to global variable
   
 
def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials
 
    # Now simulate it
    sim = Simulator(e, update_delay=0.08, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False
    # alpha, gamma, epsilon in itertools.product([0.77],[0.23],[0.06]):
    for alpha, gamma, epsilon in itertools.product([0.77],[0.23],[0.06]):
        print alpha, gamma, epsilon
        a.set_learner_parameter(alpha, gamma, epsilon)
        sim.run(n_trials=100) 
    # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__': 
    run()
    
