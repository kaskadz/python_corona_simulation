import numpy as np
from path_planning import go_to_location

def test_population(population, Config, frame, positive, send_to_location=False, 
           location_bounds=[], destinations=[], location_no=1, 
           location_odds=1.0):
    if frame % Config.min_ticks_between_tests != 0: # testing the individuals periodically
        return None, None

    positive_rolling_avg = 0 if len(positive) == 0 else np.mean(positive[-3:])

    number_of_tests = 0
    positive = 0

    tests_pool_max = int(Config.max_tests_daily_proportion * Config.pop_size)
    tests_pool_min = int(Config.min_tests_daily_proportion * Config.pop_size)
    desired_test_count = int(1 / Config.desired_positive_proportion * positive_rolling_avg)
    tests_pool = int(np.clip(desired_test_count, tests_pool_min, tests_pool_max))

    #sev2 cases
    sev2_mask = (population[:,16] != 1) & (population[:,15] == 2)
    sev2_idxs = np.asarray(population[sev2_mask, 0], dtype=np.int32)
    sev2_count = sum(sev2_mask)
    sev2_tests_count = min(sev2_count, tests_pool_max)
    sev2_selected_idxs = np.random.choice(sev2_idxs, sev2_tests_count, replace=False)
    population[sev2_selected_idxs, 16] = 1
    number_of_tests += sev2_tests_count
    positive += sev2_tests_count

    #sev1 cases
    tests_left = tests_pool - number_of_tests
    if tests_left > 0:
        sev1_mask = (population[:,16] != 1) & (population[:,15] == 1)
        sev1_idxs = np.asarray(population[sev1_mask, 0], dtype=np.int32)
        sev1_count = sum(sev1_mask)
        sev1_tests_count = min(sev1_count, tests_left)
        sev1_selected_idxs = np.random.choice(sev1_idxs, sev1_tests_count, replace=False)
        population[sev1_selected_idxs, 16] = 1
        number_of_tests += sev1_tests_count
        positive += sev1_tests_count

    tests_left = tests_pool - number_of_tests
    if tests_left > 0:
        sev0_mask = (population[:,16] != 1) & (population[:,15] < 1)
        sev0_idxs = np.asarray(population[sev0_mask, 0], dtype=np.int32)
        sev0_count = sum(sev0_mask)
        sev0_tests_count = min(sev0_count, tests_left)
        sev0_selected_idxs = np.random.choice(sev0_idxs, sev0_tests_count, replace=False)
        population[sev0_selected_idxs, 16] = population[sev0_selected_idxs, 6] == 1
        number_of_tests += sev0_tests_count
        positive += sum(population[sev0_selected_idxs, 6] == 1)

    for idx in range(len(population)):
        is_sick = population[idx,6]
        severity = int(population[idx,15])
        if severity == 2 and len(population[population[:,10] == 1]) <= Config.healthcare_capacity:
            population[idx,10] = 1
        if is_sick and severity != -1 and send_to_location and np.random.uniform() <= max(population[idx,16] == 1 + Config.self_isolate_severity_proportion[severity], 1) * location_odds:
            population[idx], destinations[idx] = go_to_location(population[idx,:],
                                                                destinations[idx],
                                                                location_bounds, 
                                                                dest_no=location_no)
    if Config.verbose:
        print('testing at timestep %i: %i/%i' % (frame, positive, number_of_tests))
    return positive, number_of_tests