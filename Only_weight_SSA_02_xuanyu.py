import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm


'''
参考论文：An Improved Chaos Sparrow Search Optimization Algorithm Using Adaptive Weight Modification 
        and Hybrid Strategies
'''


def icssa_sparrow_search_optimization(population, max_iterations, search_num_l, search_num_u, dim, fitness_function, flag_p):
    ST = 0.8
    propotion_alerter = 0.1
    # The propotion of producer
    propotion_producer = 0.2
    producer_num = round(population * propotion_producer)
    low_bundary = search_num_l * np.ones((1, dim))
    up_bundary  = search_num_u * np.ones((1, dim))

    # 代表麻雀位置
    position = np.zeros((population, dim))
    # 适应度初始化
    fitness = np.zeros(population)

    for i in range(population):
        position[i, :] = low_bundary + (up_bundary - low_bundary) * np.random.rand(1, dim)
        fitness[i] = fitness_function(position[i, :])

    # 初始化收敛曲线
    convergence_curve = np.zeros(max_iterations)
    t0 = 125
    w0 = 1.5
    # for t in tqdm(range(max_iterations), desc="ICSSOA", miniters=max_iterations/5):
    for t in range(max_iterations):
        # 对麻雀的适应度值进行排序，并取出下标
        fitness_sorted_index = np.argsort(fitness.T)
        best_finess = np.min(fitness)
        best_finess_index = np.argmin(fitness)
        best_position = position[best_finess_index, :]

        worst_fitness = np.max(fitness)
        worst_fitness_index = np.argmax(fitness)
        worst_positon = position[worst_fitness_index, :]

        # 1) 发现者（探索者、生产者）位置更新策略
        R2 = np.random.rand(1)
        inertia_weight = 0
        if t <= t0:
            inertia_weight = w0
        elif t > t0:
            inertia_weight = (1 / t)**0.9

        for i in range(producer_num):
            p_i = fitness_sorted_index[i]
            if R2 < ST:
                alaph = np.random.rand()
                position[p_i, :] = inertia_weight * position[p_i, :] * np.exp(-i / (alaph * max_iterations))
            elif R2 >= ST:
                q = np.random.normal(0, 1 , 1)
                l_dim = np.ones((1, dim))
                position[p_i, :] = inertia_weight * position[p_i, :] + q * l_dim

            # 越界处理
            position[p_i, :] = np.clip(position[p_i, :], search_num_l, search_num_u)
            fitness[p_i] = fitness_function(position[p_i, :])

        # 找出最优的”探索者“
        next_best_position_index = np.argmin(fitness[:])
        next_best_position = position[next_best_position_index, :]

        # 2) 追随者(scrounger)位置更新策略
        for i in range(0, population - producer_num):
            s_i = fitness_sorted_index[i + producer_num]
            o_i = i + producer_num
            if o_i > (population / 2):
                q = np.random.normal(0, 1, 1)
                position[s_i, :] = q * np.exp((worst_positon - position[s_i, :])/(o_i**2))
            else:
                l_dim = np.ones((1, dim))
                a = np.floor(np.random.rand(1, dim) * 2) * 2 - 1
                a_plus = 1 / (a.T * np.dot(a, a.T))
                position[s_i, :] = next_best_position + l_dim * np.dot(np.abs(position[s_i, :] - next_best_position),
                                                                       a_plus)

            # 越界处理
            position[s_i, :] = np.clip(position[s_i, :], search_num_l, search_num_u)
            fitness[s_i] = fitness_function(position[s_i, :])

        # 3) 意识到危险的麻雀的位置更新
        arrc = np.arange(len(fitness_sorted_index[:]))
        # 随机排列序列
        random_arrc = np.random.permutation(arrc)
        # 随机选取警戒者
        num_alerter = round(propotion_alerter * population)
        alerter_index = fitness_sorted_index[random_arrc[0:num_alerter]]

        for i in range(num_alerter):
            a_i = alerter_index[i]
            f_i = fitness[a_i]
            f_g = best_finess
            f_w = worst_fitness
            if f_i > f_g:
                beta = np.random.normal(0, 1 , 1)
                position[a_i, :] = best_position + beta * np.abs(position[a_i, :] - best_position)
            elif f_i == f_g:
                e = 1e-20
                k = np.random.uniform(-1, 1, 1)
                position[a_i, :] = position[a_i, :] + k * ((np.abs(position[a_i, :] - worst_positon)) /
                                                           (f_i - f_w + e))
            # 越界处理
            position[a_i, :] = np.clip(position[a_i, :], search_num_l, search_num_u)
            fitness[a_i] = fitness_function(position[a_i, :])
        if t == 0:
            convergence_curve[t] = np.min(fitness)
        else:
            convergence_curve[t] = min(np.min(fitness), convergence_curve[t-1])
        if flag_p == 1:
            print("ICSSA", t + 1, " / ", max_iterations)
    return convergence_curve









# convergence_fit   = sparrow_search_optimization(population_size,
#                                                 max_iterations,
#                                                 -search_range,
#                                                 search_range,
#                                                 Dn,
#                                                 fitness_function)
# print(convergence_fit[488:])
# plt.yscale('log')
# plt.xlabel('iterations')
# plt.ylabel('fitness')
# plt.title('sparrow search algorithm')
# plt.plot(convergence_fit)
# plt.show()



