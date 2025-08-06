#############################################################################
# 
# sampling.py
# 
# Simple ray-tracing library for 2D and 3D simulations
# 
# Siddharth Maddali
# siddharth@liminalinsights.com
# 
#############################################################################

import numpy as np
from logzero import logger
from tqdm.contrib.concurrent import process_map

def SampleAlongLine( origin, direction, step_size, num_steps ):
    direction /= np.linalg.norm( direction ) # normalize to get unit vector
    locations = [ 
        origin + n*step_size*direction
        for n in range( num_steps )
    ]
    locations = np.concatenate( [ ar[:,np.newaxis] for ar in locations ], axis=1 )
    return locations

def IsInMapRegion( point, map_lims ):
    return all( [ pt >= ml[0] and pt <= ml[1] for pt, ml in zip( point, map_lims ) ] )

def CalculateTimeOfFlight( point_query, point_origin, speed_map, steps_per_pixel=8 ):
    assert point_query.size == point_origin.size == np.ndim( speed_map ), 'Point dimension mismatch. '
    
    # assuming input points are already in pixel units
    displacement = point_query - point_origin
    distance = np.linalg.norm( displacement )
    direction = displacement / distance 
    steps = np.linspace( 0., distance, np.round( distance*steps_per_pixel ).astype( int ) )
    dx = ( steps[1:] - steps[:-1] ).mean()
    samples = steps[np.newaxis,:] * direction[:,np.newaxis] 
    samples += point_origin[:,np.newaxis].repeat( samples.shape[1], axis=1 )
    samples = np.round( samples ).astype( int )
    speeds = speed_map[ *samples ]
    dt = np.array( [ dx / sp for sp in speeds ] )
    return dt.sum(), speeds


