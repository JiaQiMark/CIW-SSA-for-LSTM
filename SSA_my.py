import math
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm



def initialization_chaotic_map(population, dim):
    x = np.zeros((population, dim))
    x[0] = np.random.rand(dim)
    for i in range(1, population):
        a = np.random.rand()
        temp_x = np.zeros(dim)
        for j in range(dim):
            temp_x[j] = math.sin((a * math.pi) / x[i - 1][j])
        x[i] = temp_x
    return x


def my_sparrow_search_optimization(population, max_iterations, search_num_l, search_num_u, dim, fitness_function, flag_p):
    weight_min = 0
    weight_max = 2

    ST = 0.8
    propotion_alerter = 0.1
    # The propotion of producer
    propotion_producer = 0.2
    producer_num = round(population * propotion_producer)
    low_bundary = search_num_l * np.ones((1, dim))
    up_bundary  = search_num_u * np.ones((1, dim))

    # 初始化麻雀位置和适应度值
    position = np.zeros((population, dim))
    fitness = np.zeros(population)
    R2_new = np.zeros(population)
    chaotic_value = initialization_chaotic_map(population, dim)
    for i in range(population):
        position[i, :] = low_bundary + (up_bundary - low_bundary) * np.abs(chaotic_value[i])
        fitness[i] = fitness_function(position[i, :])


    # 初始化收敛曲线
    convergence_curve = np.zeros(max_iterations)

    # for t in tqdm(range(max_iterations), desc="SSA_my", miniters=max_iterations/5):
    for t in range(max_iterations):
        # 对麻雀的适应度值进行排序，并取出下标
        fitness_sorted_index = np.argsort(fitness.T)
        best_finess = np.min(fitness)
        best_finess_index = np.argmin(fitness)
        best_position = position[best_finess_index, :]

        worst_fitness = np.max(fitness)
        worst_fitness_index = np.argmax(fitness)
        worst_positon = position[worst_fitness_index, :]

        # 计算每个个体的惯性权重
        # ———————————反向惯性权重
        temp_x = (fitness - best_finess) / (worst_fitness - best_finess)
        inertia_weight = weight_min + (weight_max - weight_min) * (np.sin(np.pi * temp_x + np.pi/2) + 1) / 2
        inverted_weight = (weight_min + weight_max) - inertia_weight

        # 1) 发现者（探索者、生产者）位置更新策略
        for i in range(producer_num):
            R2 = np.random.rand(1)
            p_i = fitness_sorted_index[i]
            if R2 < ST:
                alaph = np.random.rand()
                position[p_i, :] = inertia_weight[p_i] * position[p_i, :] * np.exp(-i / (alaph * max_iterations))
            elif R2 >= ST:
                q = np.random.normal(0, 1, 1)
                cauchy_gauss = 1 + R2 * np.random.standard_cauchy() + (1 - R2) * np.random.normal(0, 1)
                position[p_i, :] = inertia_weight[p_i] * position[p_i, :] + q * cauchy_gauss

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
                q = np.random.normal(0, 1 , 1)
                position[s_i, :] = q * np.exp((worst_positon - position[s_i, :])/(o_i**2))
            else:
                l_dim = np.ones(dim)
                a = np.floor(np.random.rand(1, dim) * 2) * 2 - 1
                a_plus = 1 / (a.T * np.dot(a, a.T))
                position[s_i, :] = (next_best_position + inertia_weight[s_i] *
                                    np.dot(np.abs(position[s_i, :] - next_best_position), a_plus) * l_dim)

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
                position[a_i, :] = (best_position +
                                    beta * inertia_weight[a_i] * np.abs(position[a_i, :] - best_position))
            elif f_i == f_g:
                e = 1e-20
                k = np.random.uniform(-1, 1, 1)
                position[a_i, :] = (inertia_weight[a_i] * position[a_i, :] + inverted_weight[a_i] *
                                    k * ((np.abs(position[a_i, :] - worst_positon)) / (f_i - f_w + e)))
            # 越界处理
            position[a_i, :] = np.clip(position[a_i, :], search_num_l, search_num_u)
            fitness[a_i] = fitness_function(position[a_i, :])

        if t == 0:
            convergence_curve[t] = np.min(fitness)
        else:
            convergence_curve[t] = min(np.min(fitness), convergence_curve[t-1])
            # convergence_curve[t] = np.min(fitness)
        if flag_p == 1:
            print(t + 1, " / ", max_iterations)
    return convergence_curve


# my_convergence_fit =   my_sparrow_search_optimization(population_size,
#                                                       max_iterations,
#                                                       -search_range,
#                                                       search_range,
#                                                       Dn,
#                                                       fitness_function)
#
# iterations = np.linspace(0, max_iterations-1, len(my_convergence_fit), dtype=int)
# plt.yscale('log')
# plt.xlabel('iterations')
# plt.ylabel('fitness')
# plt.title('sparrow search algorithm')
# plt.plot(my_convergence_fit)
# plt.show()


