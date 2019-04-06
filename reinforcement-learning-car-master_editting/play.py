from flat_game import carmunk
import numpy as np
import random
import csv
from nn import neural_net, LossHistory
import os.path
import timeit

NUM_INPUT = 5
GAMMA = 0.9  # Forgetting.
TUNING = False  # If False, just use arbitrary, pre-selected params.



def train_net(model, params):

    filename = params_to_filename(params)

    observe = 100  # Number of frames to observe before training.
    epsilon = 1
    train_frames = 100000  # Number of frames to play.
    batchSize = params['batchSize']
    buffer = params['buffer']

    # Just stuff used below.
    max_car_distance = 0
    car_distance = 0
    min_distance = 10000
    t = 0
    data_collect = []
    replay = []  # stores tuples of (S, A, R, S').

    loss_log = []

    # Create a new game instance.
    game_state = carmunk.GameState()

    # Get initial state by doing nothing and getting the state.
    _, state,_= game_state.frame_step((2))

    # Let's time it.
    start_time = timeit.default_timer()

    # Run the frames.
    while t < train_frames:

        t += 1
        car_distance += 1

        # Choose an action.
        # if random.random() < epsilon or t < observe:
        #     action = np.random.randint(0, 3)  # random
        # else:
            # Get Q values for each action.
        qval = model.predict(state, batch_size=1)
        action = (np.argmax(qval))  # best

        # Take action, observe new state and get our treat.
        reward, new_state, distance = game_state.frame_step(action)

        # Experience replay storage.
        replay.append((state, action, reward, new_state))

        # If we're done observing, start training.
        # if t > observe:

        #     # If we've stored enough in our buffer, pop the oldest.
        #     if len(replay) > buffer:
        #         replay.pop(0)

        #     # Randomly sample our experience replay memory
        #     minibatch = random.sample(replay, batchSize)   # mot liss gom 64 tuble, moi tuble gom 4 phan tu (S, A, R, S')

            # Get training values.
            # X_train, y_train = process_minibatch2(minibatch, model)

            # Train the model on this batch.
            # history = LossHistory()
            # model.fit(
            #     X_train, y_train, batch_size=batchSize,
            #     nb_epoch=1, verbose=0, callbacks=[history]
            # )
            # loss_log.append(history.losses)

        # Update the starting state with S'.
        state = new_state

        # Decrement epsilon over time.
        if epsilon > 0.1 and t > observe:
            epsilon -= (1.0/train_frames)

        if distance < min_distance:
            min_distance = distance

        # We died, so update stuff.
        if reward == -500:
            # Log the car's distance at this T.
            data_collect.append([t, car_distance])

            # Update max.
            if car_distance > max_car_distance:
                max_car_distance = car_distance

            # Time it.
            # tot_time = timeit.default_timer() - start_time
            # fps = car_distance / tot_time

            # Output some stuff so we can watch.
            # print("Max_car_distance: %d at %d\tepsilon %f\t(%d)\tdistance %d\t%f fps" %
            #       (max_car_distance, t, epsilon, car_distance, distance, fps))

            # Reset.
            car_distance = 0
            start_time = timeit.default_timer()
        if t % 10 == 0:
            print("Max_car_distance: %d at %d\tepsilon %f\t(%d)\tdistance %d \tmin_distance %d" %
                 (max_car_distance, t, epsilon, car_distance, distance, min_distance))

        # Save the model every 25,000 frames.
        # if t % 10000 == 0:
        #     model.save_weights('saved-models/' + filename + '-' +
        #                        str(t) + '.h5',
        #                        overwrite=True)
        #     print("Saving model %s - %d" % (filename, t))
        
    # Log results after we're done all frames.
    log_results(filename, data_collect, loss_log)


def log_results(filename, data_collect, loss_log):
    # Save the results to a file so we can graph it later.
    with open('results/sonar-frames/learn_data-' + filename + '.csv', 'w') as data_dump:
        wr = csv.writer(data_dump)
        wr.writerows(data_collect)

    with open('results/sonar-frames/loss_data-' + filename + '.csv', 'w') as lf:
        wr = csv.writer(lf)
        for loss_item in loss_log:
            wr.writerow(loss_item)

def process_minibatch2(minibatch, model):
    # by Microos, improve this batch processing function 
    #   and gain 50~60x faster speed (tested on GTX 1080)
    #   significantly increase the training FPS
    
    # instead of feeding data to the model one by one, 
    #   feed the whole batch is much more efficient

    mb_len = len(minibatch)
                                               # []: liss, (): tuble 
    old_states = np.zeros(shape=(mb_len, 5))   #tao ra 1 tuble gom 64 liss, moi liss gom 3 phan tu 0
    actions = np.zeros(shape=(mb_len,))
    rewards = np.zeros(shape=(mb_len,))
    new_states = np.zeros(shape=(mb_len, 5))

    for i, m in enumerate(minibatch):
        old_state_m, action_m, reward_m, new_state_m = m
        old_states[i, :] = old_state_m[...]
        actions[i] = action_m
        rewards[i] = reward_m
        new_states[i, :] = new_state_m[...]

    old_qvals = model.predict(old_states, batch_size=mb_len)
    new_qvals = model.predict(new_states, batch_size=mb_len)

    maxQs = np.max(new_qvals, axis=1)
    y = old_qvals
    non_term_inds = np.where((rewards != -500) & (rewards != 500))[0]
    term_inds = np.where((rewards == -500) & (rewards == 500))[0]

    y[non_term_inds, actions[non_term_inds].astype(int)] = rewards[non_term_inds] + (GAMMA * maxQs[non_term_inds])
    y[term_inds, actions[term_inds].astype(int)] = rewards[term_inds]
    X_train = old_states
    y_train = y
    return X_train, y_train

def params_to_filename(params):
    return str(params['nn'][0]) + '-' + str(params['nn'][1]) + '-' + \
            str(params['batchSize']) + '-' + str(params['buffer'])

if __name__ == "__main__":
    nn_param = [128, 128]
    params = {
        "batchSize": 64,
        "buffer": 50000,
        "nn": nn_param
    }
    saved_model = 'saved-models/128-128-64-50000-200000.h5'
    model = neural_net(NUM_INPUT, [128, 128], saved_model)
#        model = neural_net(NUM_INPUT, nn_param)
    train_net(model, params)
