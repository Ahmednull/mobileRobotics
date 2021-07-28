# done by Abdul Ahad

import numpy as np
import math
import random
import matplotlib.pyplot as plt

#to convert cordinates in the gridmap to world cordinates
def map2world(grid,i,j,x_0):
    origin = [grid.shape[0]/2 , grid.shape[1]/2]
    pose = [0,0,0]
    pose[0] = (i - origin[0])*0.01 + x_0[0]   #0.01 resolution
    pose[1] = (j - origin[1])*0.01 + x_0[1]
    return pose

def inverse_motion_model(u):
    del_rot1 = math.atan2((u[1][1]-u[0][1]),(u[1][0]-u[0][0])) - u[0][2]
    del_trans = math.sqrt( (u[1][0]-u[0][0])**2 + (u[1][1]-u[0][1])**2)
    del_rot2 = u[1][2]-u[0][2]-del_rot1
    return del_rot1, del_trans, del_rot2

    
def prob(query, std):
      return max(0,(1/(math.sqrt(6)*std) - (abs(query)/(6 * (std**2)))))

def motion_model_odometry(x0,xt,u_t,alpha,gridmap):
    del_rot1, del_trans, del_rot2 = inverse_motion_model(u_t)
    del_rot1_hat, del_trans_hat, del_rot2_hat = inverse_motion_model([x0,xt])
    p1 = prob((del_rot1-del_rot1_hat),(alpha[0]*abs(del_rot1)+alpha[1]*del_trans))
    p2 = prob((del_trans-del_trans_hat),(alpha[2]*del_trans+alpha[3]*abs(del_rot1+del_rot2)))
    p3 = 1
    return p1*p2*p3

def sample(b):
    return ((math.sqrt(6)/2)*(np.random.uniform(-b,b)+np.random.uniform(-b,b)))


def sample_motion_model_odometry(x0,u_t,alpha):
    
        del_rot1, del_trans, del_rot2 = inverse_motion_model(u_t)
        del_rot1_hat = del_rot1 +sample( alpha[0]*abs(del_rot1) + alpha[1]*del_trans)
        del_trans_hat = del_trans +sample( alpha[2]*del_trans + alpha[3]* (abs(del_rot1)+abs(del_rot2)) ) 
        del_rot2_hat = del_rot2 +sample( alpha[0]*abs(del_rot2)+ alpha[1]*del_trans)
        
        x = x0[0] + del_trans_hat*math.cos(x0[2]+del_rot1_hat)
        y = x0[1] + del_trans_hat*math.sin(x0[2]+del_rot1_hat)
        theta = x0[2] + del_rot1_hat + del_rot2_hat
        return [x, y, theta]

