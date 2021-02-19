import numpy as np
from path_planning import go_to_location

def test_population(population, Config, frame, send_to_location=False, 
           location_bounds=[], destinations=[], location_no=1, 
           location_odds=1.0):
    if frame % Config.min_ticks_between_tests != 0: # testing the individuals periodically
        return 0,0

    number_of_tests = 0
    positive = 0
    for idx in range(len(population)):
        if population[idx,16] == 1: # do not test people that are already known to be sick or have died or recovered
            continue

        is_sick = population[idx,6]
        severity = int(population[idx,15])
        if is_sick:
            testing_probability = Config.test_chances[severity] if severity != -1 else 0
        else:
            testing_probability = Config.test_chances_healthy
        should_test = np.random.random() < testing_probability
        if should_test:
            number_of_tests += 1
            if is_sick:
                positive += 1
                population[idx,16] = 1
            else:
                population[idx,16] = 0
        if severity == 2 and len(population[population[:,10] == 1]) <= Config.healthcare_capacity:
            population[idx,10] = 1
        if is_sick and severity != -1 and send_to_location and np.random.uniform() <= (should_test + Config.self_isolate_severity_proportion[severity]) * location_odds:
            population[idx], destinations[idx] = go_to_location(population[idx,:],
                                                                destinations[idx],
                                                                location_bounds, 
                                                                dest_no=location_no)
    if Config.verbose:
        print('testing at timestep %i: %i/%i' % (frame, positive, number_of_tests))
    return positive, number_of_tests