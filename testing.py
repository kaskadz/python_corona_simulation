import numpy as np
from path_planning import go_to_location

def test_population(population, Config, frame, send_to_location=False, 
           location_bounds=[], destinations=[], location_no=1, 
           location_odds=1.0):
    if len(population[population[:,6] == 1]) / Config.pop_size < Config.test_proportion_to_start:
        return 0, 0
    number_of_tests = 0
    positive = 0
    for idx, agent in enumerate(population):
        tested = agent[16]
        if tested:
            continue
        is_sick = agent[6]
        severity = int(agent[15])
        if is_sick:
            testing_probability = Config.test_chances[severity]
        else:
            testing_probability = Config.test_chances_healthy
        tested = np.random.random() < testing_probability
        if tested:
            number_of_tests += 1
            if is_sick:
                positive += 1
                agent[16] = 1
        if severity == 2 and len(population[population[:,10] == 1]) <= Config.healthcare_capacity:
            agent[10] = 1
        if is_sick and send_to_location and np.random.uniform() <= (tested + Config.self_isolate_severity_proportion[severity]) * location_odds:
            population[idx], destinations[idx] = go_to_location(agent,
                                                                destinations[idx],
                                                                location_bounds, 
                                                                dest_no=location_no)

    if Config.verbose:
        print('testing at timestep %i: %i/%i' % (frame, positive, number_of_tests))
    return positive, number_of_tests