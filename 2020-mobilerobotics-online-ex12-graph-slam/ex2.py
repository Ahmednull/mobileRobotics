from math import atan2, sin, cos
from socket import fromfd
import numpy as np
from collections import namedtuple
import matplotlib.pyplot as plt


# Helper functions to get started
class Graph:
    def __init__(self, x, nodes, edges, lut):
        self.x = x
        self.nodes = nodes
        self.edges = edges
        self.lut = lut


def read_graph_g2o(filename):
    """ This function reads the g2o text file as the graph class

    Parameters
    ----------
    filename : string
        path to the g2o file

    Returns
    -------
    graph: Graph contaning information for SLAM

    """
    Edge = namedtuple(
        'Edge', ['Type', 'fromNode', 'toNode', 'measurement', 'information'])
    edges = []
    nodes = {}
    with open(filename, 'r') as file:
        for line in file:
            data = line.split()

            if data[0] == 'VERTEX_SE2':
                nodeId = int(data[1])
                pose = np.array(data[2:5], dtype=np.float32)
                nodes[nodeId] = pose

            elif data[0] == 'VERTEX_XY':
                nodeId = int(data[1])
                loc = np.array(data[2:4], dtype=np.float32)
                nodes[nodeId] = loc

            elif data[0] == 'EDGE_SE2':
                Type = 'P'
                fromNode = int(data[1])
                toNode = int(data[2])
                measurement = np.array(data[3:6], dtype=np.float32)
                uppertri = np.array(data[6:12], dtype=np.float32)
                information = np.array(
                    [[uppertri[0], uppertri[1], uppertri[2]],
                     [uppertri[1], uppertri[3], uppertri[4]],
                     [uppertri[2], uppertri[4], uppertri[5]]])
                edge = Edge(Type, fromNode, toNode, measurement, information)
                edges.append(edge)

            elif data[0] == 'EDGE_SE2_XY':
                Type = 'L'
                fromNode = int(data[1])
                toNode = int(data[2])
                measurement = np.array(data[3:5], dtype=np.float32)
                uppertri = np.array(data[5:8], dtype=np.float32)
                information = np.array([[uppertri[0], uppertri[1]],
                                        [uppertri[1], uppertri[2]]])
                edge = Edge(Type, fromNode, toNode, measurement, information)
                edges.append(edge)

            else:
                print('VERTEX/EDGE type not defined')

    # compute state vector and lookup table
    lut = {}
    x = []
    offset = 0
    for nodeId in nodes:
        lut.update({nodeId: offset})
        offset = offset + len(nodes[nodeId])
        x.append(nodes[nodeId])
    x = np.concatenate(x, axis=0)

    # collect nodes, edges and lookup in graph structure
    graph = Graph(x, nodes, edges, lut)
    print('Loaded graph with {} nodes and {} edges'.format(
        len(graph.nodes), len(graph.edges)))

    return graph


def v2t(pose):
    """This function converts SE2 pose from a vector to transformation

    Parameters
    ----------
    pose : 3x1 vector
        (x, y, theta) of the robot pose

    Returns
    -------
    T : 3x3 matrix
        Transformation matrix corresponding to the vector
    """
    c = np.cos(pose[2])
    s = np.sin(pose[2])
    T = np.array([[c, -s, pose[0]], [s, c, pose[1]], [0, 0, 1]])
    return T


def t2v(T):
    """This function converts SE2 transformation to vector for

    Parameters
    ----------
    T : 3x3 matrix
        Transformation matrix for 2D pose

    Returns
    -------
    pose : 3x1 vector
        (x, y, theta) of the robot pose
    """
    x = T[0, 2]
    y = T[1, 2]
    theta = np.arctan2(T[1, 0], T[0, 0])
    v = np.array([x, y, theta])
    return v


def plot_graph(g):

    # initialize figure
    plt.figure(1)
    plt.clf()

    # get a list of all poses and landmarks
    poses, landmarks = get_poses_landmarks(g)

    # plot robot poses
    if len(poses) > 0:
        poses = np.stack(poses, axis=0)
        plt.plot(poses[:, 0], poses[:, 1], 'bo')

    # plot landmarks
    if len(landmarks) > 0:
        landmarks = np.stack(landmarks, axis=0)
        plt.plot(landmarks[:, 0], landmarks[:, 1], 'r*')

    # plot edges/constraints
    poseEdgesP1 = []
    poseEdgesP2 = []
    landmarkEdgesP1 = []
    landmarkEdgesP2 = []

    for edge in g.edges:
        fromIdx = g.lut[edge.fromNode]
        toIdx = g.lut[edge.toNode]
        if edge.Type == 'P':
            poseEdgesP1.append(g.x[fromIdx:fromIdx + 3])
            poseEdgesP2.append(g.x[toIdx:toIdx + 3])

        elif edge.Type == 'L':
            landmarkEdgesP1.append(g.x[fromIdx:fromIdx + 2])
            landmarkEdgesP2.append(g.x[toIdx:toIdx + 2])

    poseEdgesP1 = np.stack(poseEdgesP1, axis=0)
    poseEdgesP2 = np.stack(poseEdgesP2, axis=0)
    plt.plot(np.concatenate((poseEdgesP1[:, 0], poseEdgesP2[:, 0])),
             np.concatenate((poseEdgesP1[:, 1], poseEdgesP2[:, 1])), 'r')

    plt.draw()
    plt.pause(1)

    return


def get_poses_landmarks(g):
    poses = []
    landmarks = []

    for nodeId in g.nodes:
        dimension = len(g.nodes[nodeId])
        offset = g.lut[nodeId]

        if dimension == 3:
            pose = g.x[offset:offset + 3]
            poses.append(pose)
        elif dimension == 2:
            landmark = g.x[offset:offset + 2]
            landmarks.append(landmark)

    return poses, landmarks


def run_graph_slam(g, numIterations):

    # perform optimization
    for i in range(numIterations):

        # compute the incremental update dx of the state vector

        # apply the solution to the state vector g.x

        # plot graph

        # compute and print global error

        # terminate procedure if change is less than 10e-4
        pass


def compute_global_error(g):
    """ This function computes the total error for the graph.

    Parameters
    ----------
    g : Graph class

    Returns
    -------
    Fx: scalar
        Total error for the graph
    """
    Fx = 0
    for edge in g.edges:

        # pose-pose constraint
        if edge.Type == 'P':

            # compute idx for nodes using lookup table
            fromIdx = g.lut[edge.fromNode]
            toIdx = g.lut[edge.toNode]

            # get node state for the current edge
            x1 = g.x[fromIdx:fromIdx + 3]
            x2 = g.x[toIdx:toIdx + 3]

            # get measurement and information matrix for the edge
            z12 = edge.measurement
            info12 = edge.information

            # (TODO) compute the error due to this edge
            Z = v2t(z12)
            X1_inverse = np.linalg.inv(v2t(x1))
            X2 = v2t(x2)
            Fx += np.linalg.norm(t2v(np.linalg.inv(Z) @ (X1_inverse @ X2)))

        # pose-pose constraint
        elif edge.Type == 'L':

            # compute idx for nodes using lookup table
            fromIdx = g.lut[edge.fromNode]
            toIdx = g.lut[edge.toNode]

            # get node states for the current edge
            x = g.x[fromIdx:fromIdx + 3]
            l = g.x[toIdx:toIdx + 2]

            # get measurement and information matrix for the edge
            z = edge.measurement
            info12 = edge.information

            # (TODO) compute the error due to this edge
            X = v2t(x)[:2, :2]
            Fx += np.linalg.norm((np.linalg.inv(X) @ np.expand_dims(l,
                                 axis=1)) - np.expand_dims(z, axis=1))

    return Fx


def linearize_and_solve(g):
    """ This function solves the least-squares problem for one iteration
        by linearizing the constraints

    Parameters
    ----------
    g : Graph class

    Returns
    -------
    dx : Nx1 vector
         change in the solution for the unknowns x
    """

    # initialize the sparse H and the vector b
    H = np.zeros((len(g.x), len(g.x)))
    b = np.zeros(len(g.x))
    b = np.expand_dims(b, axis=1)

    # set flag to fix gauge
    needToAddPrior = True
    Fx = 0

    # compute the addend term to H and b for each of our constraints
    print('linearize and build system')

    for edge in g.edges:

        # pose-pose constraint
        if edge.Type == 'P':

            # compute idx for nodes using lookup table
            fromIdx = g.lut[edge.fromNode]
            toIdx = g.lut[edge.toNode]

            # get node state for the current edge
            x_i = g.x[fromIdx:fromIdx + 3]
            x_j = g.x[toIdx:toIdx + 3]

            # (TODO) compute the error and the Jacobians
            e, A, B = linearize_pose_pose_constraint(
                x_i, x_j, edge.measurement)

            # (TODO) compute the terms

            b_i = (e.T @ edge.information @ A).reshape(3, 1)

            b_j = (e.T @ edge.information @ B).reshape(3, 1)

            H_ii = A.T @ edge.information @ A
            H_ij = A.T @ edge.information @ B
            H_ji = B.T @ edge.information @ A
            H_jj = B.T @ edge.information @ B

            # (TODO) add the terms to H matrix and b
            H[fromIdx:fromIdx + 3, fromIdx:fromIdx + 3] += H_ii
            H[fromIdx:fromIdx + 3, toIdx:toIdx + 3] += H_ij
            H[toIdx:toIdx + 3, fromIdx:fromIdx + 3] += H_ji
            H[toIdx:toIdx + 3, toIdx:toIdx + 3] += H_jj

            b[fromIdx:fromIdx+3] += b_i
            b[toIdx:toIdx+3] += b_j

            # Add the prior for one pose of this edge
            # This fixes one node to remain at its current location
            if needToAddPrior:
                H[fromIdx:fromIdx + 3, fromIdx:fromIdx +
                  3] = H[fromIdx:fromIdx + 3,
                         fromIdx:fromIdx + 3] + 1000 * np.eye(3)
                needToAddPrior = False

        # pose-pose constraint
        elif edge.Type == 'L':

            # compute idx for nodes using lookup table
            fromIdx = g.lut[edge.fromNode]
            toIdx = g.lut[edge.toNode]

            # get node states for the current edge
            x = g.x[fromIdx:fromIdx + 3]
            l = g.x[toIdx:toIdx + 2]

            # (TODO) compute the error and the Jacobians
            e, A, B = linearize_pose_landmark_constraint(
                x, l, edge.measurement)

            # (TODO) compute the terms
            b_i = e.T @ edge.information @ A

            b_j = e.T @ edge.information @ B

            H_ii = A.T @ edge.information @ A
            H_ij = A.T @ edge.information @ B
            H_ji = B.T @ edge.information @ A
            H_jj = B.T @ edge.information @ B

            print(np.shape(H[fromIdx:fromIdx + 3,
                  fromIdx:fromIdx + 3]), np.shape(H_ii))

            # (TODO) add the terms to H matrix and b
            H[fromIdx:fromIdx + 3, fromIdx:fromIdx + 3] += H_ii
            H[fromIdx:fromIdx + 3, toIdx:toIdx + 2] += H_ij
            H[toIdx:toIdx + 2, fromIdx:fromIdx + 3] += H_ji
            H[toIdx:toIdx + 2, toIdx:toIdx + 2] += H_jj

            b[fromIdx:fromIdx+3] += b_i
            b[toIdx:toIdx+2] += b_j

    # solve system
    dx = np.linalg.solve(H, b)

    return dx


def linearize_pose_pose_constraint(x1, x2, z):
    """Compute the error and the Jacobian for pose-pose constraint

    Parameters
    ----------
    x1 : 3x1 vector
         (x,y,theta) of the first robot pose
    x2 : 3x1 vector
         (x,y,theta) of the second robot pose
    z :  3x1 vector
         (x,y,theta) of the measurement

    Returns
    -------
    e  : 3x1
         error of the constraint
    A  : 3x3
         Jacobian wrt x1
    B  : 3x3
         Jacobian wrt x2
    """

    R_ij = v2t(z)[:2, :2]
    t_ij = v2t(z)[:2, 2].reshape(2, 1)
    theta_ij = atan2(R_ij[1, 0], R_ij[1, 1])

    R_i = v2t(x1)[:2, :2]
    theta_i = atan2(R_i[1, 0], R_i[1, 1])
    del_R_i = np.array([[-sin(theta_i), cos(theta_i)],
                       [-cos(theta_i), -sin(theta_i)]])
    t_i = v2t(x1)[:2, 2].reshape(2, 1)
    t_j = v2t(x2)[:2, 2].reshape(2, 1)
    R_j = v2t(x2)[:2, :2]
    theta_j = atan2(R_j[1, 0], R_j[1, 1])

    A_11 = -(R_ij.T @ R_i.T)
    A_12 = R_ij.T @ del_R_i @ (t_j-t_i)
    A_21_22 = np.array([0, 0, -1]).reshape(1, 3)
    A = np.vstack((np.hstack((A_11, A_12)), A_21_22))

    B_11 = R_ij.T@R_i.T
    B_12 = np.zeros([2, 1])
    B_21_22 = np.array([0, 0, 1]).reshape(1, 3)
    B = np.vstack((np.hstack((B_11, B_12)), B_21_22))

    e_11 = R_ij.T@(R_i.T @ (t_j - t_i) - t_ij)
    e_12 = np.array([theta_j-theta_i-theta_ij])
    e = np.vstack((e_11, e_12))

    return e, A, B


def linearize_pose_landmark_constraint(x, l, z):
    """Compute the error and the Jacobian for pose-landmark constraint

    Parameters
    ----------
    x : 3x1 vector
        (x,y,theta) og the robot pose
    l : 2x1 vector
        (x,y) of the landmark
    z : 2x1 vector
        (x,y) of the measurement

    Returns
    -------
    e : 2x1 vector
        error for the constraint
    A : 2x3 Jacobian wrt x
    B : 2x2 Jacobian wrt l
    """

    R_i = v2t(x)[:2, :2]
    t_i = v2t(x)[:2, 2]
    theta_i = atan2(R_i[1, 0], R_i[1, 1])

    del_R_i = np.array([[-sin(theta_i), cos(theta_i)],
                       [-cos(theta_i), -sin(theta_i)]])

    A_11 = -R_i.T
    A_12 = del_R_i@(np.expand_dims(l, axis=1) - np.expand_dims(t_i, axis=1))
    A = np.hstack((A_11, A_12))
    # print(np.shape(np.expand_dims(l, axis=1)),  np.shape(
    #     np.expand_dims(t_i, axis=1)), np.shape(A_12))

    B = R_i.T

    e = np.dot(R_i.T, l - t_i) - z

    return e, A, B
