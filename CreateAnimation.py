#!/home/siddharthmaddalivivekanand/python/local/envs/analysis/bin/python

# numerics/computation
import numpy as np

# animation and rendering
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap, BoundaryNorm

# DB management
import h5py as h5

# logging 
from logzero import logger

# command-line parsing
import sys
import argparse
from argparse import Namespace


# start
parser = argparse.ArgumentParser( description='Render Matplotlib animation from simulation data. ' )

parser.add_argument( '--dump', type=str, default='BaselineWavesAzim.h5', help='This is the HDF5 file containing the simulation. Default value \'BaselinAzim.h5\'. ' )
parser.add_argument( '--animate', action='store_true', default=False, help='Set this flag to render time-domain evolution to screen. ')
parser.add_argument( '--movie', type=str, default=None, help='Provide a filename with .mp4 extension to save animation to movie file. ')
parser.add_argument( '--skip-frame', type=int, default=1, help='Skip this many time steps between frames of the movie. ' )
parser.add_argument( '--signal', action='store_true', default=False, help='Plots the measured signal alongside the wave animation' )
parser.add_argument( '--focus-regime', action='store_true', default=False, help='Plot focus region. Requires simulation dump file to have attribute focal_length. ' )
parser.add_argument( '--legend-loc', type=str, default='best', help='Legend location in plot. ' )

args = parser.parse_args()
if len( sys.argv )==1: # print help message if no command line arguments
    parser.print_help( sys.stderr )
    sys.exit( 0 )

logger.info( f'Loading simulation file {args.dump}...' )
with h5.File( args.dump, 'r' ) as fid: 
    img_backdrop = fid[ 'image' ][:]
    pressure_wave = fid[ 'pressure' ][:]
    params = dict( fid[ 'pressure' ].attrs )
    materials_dict = { key.replace( 'medium_', '' ):val for key, val in params.items() if 'medium_' in key }
    segs, orders = list( materials_dict.keys() ), list( materials_dict.values() )
    segs = [ segs[n] for n in np.argsort( orders ) ]
    orders = np.sort( orders )
    
    # specific modifications to the legend
    segs = [ st if st != 'water' else 'electrolyte' for st in segs ]
    segs = [ st if st != 'oil' else 'couplant' for st in segs ]

    params = Namespace( **params )
    
fs = args.skip_frame
if args.signal: 
    fig = plt.figure( figsize=( 14, 5 ) )
    ax = fig.subplots( 1, 2 )
    myax = ax[0]
else: 
    fig = plt.figure( figsize=( 7, 7 ) )
    ax = fig.subplots( 1, 1 )
    myax = ax

num_categories = len( segs )
colors = plt.get_cmap( 'tab10', num_categories ).colors  
cmap = ListedColormap( colors )
bounds = -0.5 + np.arange( len( segs )+1 )
norm = BoundaryNorm( bounds, cmap.N )

im = myax.pcolormesh( np.arange( params.x.size ), np.arange( params.y.size ), img_backdrop, cmap=cmap, norm=norm, alpha=0.5 )
cbar = fig.colorbar( im, ax=myax, fraction=0.046, pad=0.05, ticks=np.arange( len( segs ) ) )
cbar.ax.set_yticklabels( segs )
fld = myax.imshow( pressure_wave[0,:,:], origin='lower', cmap='seismic' )
myax.plot( params.xloc, params.yloc, '^k', markersize=2, label='Source' )

fld.set_clim( [ params.pmin/params.csf, params.pmax/params.csf ] )
myax.set_xlim( [ 0, params.x.size ] )
myax.set_yticks( np.arange( 0, params.y.size, 100 ), [ f'{st:.2f}' for st in params.y[::100] ] )
myax.set_xticks( np.arange( 0, params.x.size, 100 ), [ f'{st:.2f}' for st in params.x[::100] ] )
myax.set_xlabel( 'x (mm)' )
myax.set_ylabel( 'y (mm)' )
myax.axis( 'equal' )
myax.axis( 'square' )
titl = myax.set_title( f'Pressure wave at time step {0:.3f} us', weight='bold' )

if args.signal:
    ax[1].plot( params.t/1.e-6, pressure_wave[:,params.yloc,params.xloc].sum( axis=1 ) )
    ax[1].set_xlabel( 't ($\\mu$s)' )
    ax[1].axis( 'tight' )
    ax[1].grid()
    ax[1].set_title( 'Pulse echo signal', weight='bold' )

if args.focus_regime: 
    if hasattr( params, 'focal_length' ):
        logger.info( f'Plotting focus regime at {params.focal_length:.2f} focus...' ) 
        edge1, edge2 = params.xloc.min(), params.xloc.max() 
        # mid = np.argmin( np.abs( params.x ) )
        mid = 0.5*( edge1 + edge2 )
        if not isinstance( mid, int ):
            mid = mid.mean()
        foc = np.argmin( np.abs( params.y -params.y[params.yloc[0]] - params.focal_length ) )
        pts = np.array( 
            [ 
                [ edge1, params.yloc[0] ], 
                [ mid, foc ], 
                [ edge2, params.yloc[0] ]
            ]
        ).T
        myax.plot( pts[0,:], pts[1,:], color=[0.5]*3, linestyle=':', label='Focus regime' )
    else: 
        logger.warning( 'No focal length specified. Skipping focus regime... ' )

myax.legend( loc=args.legend_loc )
plt.tight_layout()

if args.animate: 
    def animate( n ):
        fld.set_data( pressure_wave[fs*n,:,:] )
        fld.set_clim( [ params.pmin/params.csf, params.pmax/params.csf ] )
        titl.set_text( f'Pressure wave at time {(fs*n*params.dt/1.e-6):.3f} us' )
        return fld,

    ani = animation.FuncAnimation( 
        fig, 
        animate, 
        interval=10, 
        frames=pressure_wave[::fs,:,:].shape[0], 
        # frames=10,
        blit=False, 
        repeat=False 
    )
    plt.show()

    if args.movie is not None: 
        assert isinstance( args.movie, str ), 'Should provide a string for movie file name. '
        assert args.movie[-4:]=='.mp4', 'Movie file should contain extention .mp4 '
        logger.info( f'Writing animation to {args.movie}...' )
        writervideo = animation.FFMpegWriter( fps=60 ) 
        ani.save(f'{args.movie}', writer=writervideo ) 
    else: 
        logger.info( 'Skipping movie dump...' )
else: 
    logger.info( 'Skipping animation...' )
    plt.show()
