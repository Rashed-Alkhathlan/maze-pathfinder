# Pseudocode of A_star search algorithm
"""
ALGORITHM A_star(start, goal):
    to_visit = priorityQueue({start}) //set of nodes to visit. initially has the start node
    came_from = {} //empty map to store path

    g_score = {start: 0} //map of node cost from start to that node. initially 0 for start
    f_score = {start: heuristic(start, goal)} //map of total cost from current node to goal.

    while to_visit is not empty:
        current = to_visit.pop() //get node with lowest f_score
        if current == goal:
            return reconstruct_path(came_from, current) //reconstruct path from start to goal

        for neighbor in get_neighbors(current):
            tentative_g_score = g_score[current] + distance(current, neighbor) #cost from start to neighbor through current

            if tentative_g_score < g_score.get(neighbor, infinite): //if this path to neighbor is better than any previous one
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                if neighbor not in to_visit:
                    to_visit.add(neighbor)
    return None
"""

def a_star(start, goal):
    pass