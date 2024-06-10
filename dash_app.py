###########################################################################
# GAUSSIAN PLUME MODEL FOR TEACHING PURPOSES                              #
# PAUL CONNOLLY (UNIVERSITY OF MANCHESTER, 2017)                          #
# THIS CODE IS PROVIDED `AS IS' WITH NO GUARANTEE OF ACCURACY             #
# IT IS USED TO DEMONSTRATE THE EFFECTS OF ATMOSPHERIC STABILITY,         #
# WINDSPEED AND DIRECTION AND MULTIPLE STACKS ON THE DISPERSION OF        #
# POLLUTANTS FROM POINT SOURCES                                           #
###########################################################################
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

import numpy as np
import sys
from scipy.special import erfcinv as erfcinv
import tqdm as tqdm
from gauss_func import gauss_func
app = dash.Dash(__name__, suppress_callback_exceptions=True)

###########################################################################
# Do not change these variables                                           #
###########################################################################


# SECTION 0: Definitions (normally don't modify this section)
# view
PLAN_VIEW=1;
HEIGHT_SLICE=2;
SURFACE_TIME=3;
NO_PLOT=4;

# wind field
CONSTANT_WIND=1;
FLUCTUATING_WIND=2;
PREVAILING_WIND=3;

# number of stacks
ONE_STACK=1;
TWO_STACKS=2;
THREE_STACKS=3;

# stability of the atmosphere
CONSTANT_STABILITY=1;
ANNUAL_CYCLE=2;
stability_str=['Very unstable','Moderately unstable','Slightly unstable', \
    'Neutral','Moderately stable','Very stable'];
# Aerosol properties
HUMIDIFY=2;
DRY_AEROSOL=1;

SODIUM_CHLORIDE=1;
SULPHURIC_ACID=2;
ORGANIC_ACID=3;
AMMONIUM_NITRATE=4;
nu=[2., 2.5, 1., 2.];
rho_s=[2160., 1840., 1500., 1725.];
Ms=[58.44e-3, 98e-3, 200e-3, 80e-3];
Mw=18e-3;


dxy=100;          # resolution of the model in both x and y directions
dz=10;
x=np.mgrid[-2500:2500+dxy:dxy]; # solve on a 5 km domain
y=x;              # x-grid is same as y-grid
###########################################################################



# SECTION 1: Configuration
# Variables can be changed by the user+++++++++++++++++++++++++++++++++++++
RH=0.90;
aerosol_type=SODIUM_CHLORIDE;

dry_size=60e-9;
humidify=HUMIDIFY;

stab1=1; # set from 1-6
stability_used=CONSTANT_STABILITY;


output=PLAN_VIEW; #PLAN_VIEW, HEIGHT_SLICE, SURFACE_TIME
x_slice=26; # position (1-50) to take the slice in the x-direction
y_slice=1;  # position (1-50) to plot concentrations vs time

wind=PREVAILING_WIND;
stacks=ONE_STACK;
stack_x=[0., 1000., -200.];
stack_y=[0., 250., -500.];

Q=[40., 40., 40.]; # mass emitted per unit time
H=[50., 50., 50.]; # stack height, m
days=50;          # run the model for 365 days
#--------------------------------------------------------------------------
times=np.mgrid[1:(days)*24+1:1]/24.;

Dy=10.;
Dz=10.;

# SECTION 2: Act on the configuration information

# Decide which stability profile to use
if stability_used == CONSTANT_STABILITY:

   stability=stab1*np.ones((days*24,1));
   stability_str=stability_str[stab1-1];
elif stability_used == ANNUAL_CYCLE:

   stability=np.round(2.5*np.cos(times*2.*np.pi/(365.))+3.5);
   stability_str='Annual cycle';
else:
   sys.exit()


# decide what kind of run to do, plan view or y-z slice, or time series
if output == PLAN_VIEW or output == SURFACE_TIME or output == NO_PLOT:

   C1=np.zeros((len(x),len(y),days*24)); # array to store data, initialised to be zero

   [x,y]=np.meshgrid(x,y); # x and y defined at all positions on the grid
   z=np.zeros(np.shape(x));    # z is defined to be at ground level.
elif output == HEIGHT_SLICE:
   z=np.mgrid[0:500+dz:dz];       # z-grid

   C1=np.zeros((len(y),len(z),days*24)); # array to store data, initialised to be zero

   [y,z]=np.meshgrid(y,z); # y and z defined at all positions on the grid
   x=x[x_slice]*np.ones(np.shape(y));    # x is defined to be x at x_slice
else:
   sys.exit()

# Set the wind based on input flags++++++++++++++++++++++++++++++++++++++++
wind_speed=5.*np.ones((days*24,1)); # m/s
if wind == CONSTANT_WIND:
   wind_dir=0.*np.ones((days*24,1));
   wind_dir_str='Constant wind';
elif wind == FLUCTUATING_WIND:
   wind_dir=360.*np.random.rand(days*24,1);
   wind_dir_str='Random wind';
elif wind == PREVAILING_WIND:
   wind_dir=-np.sqrt(2.)*erfcinv(2.*np.random.rand(24*days,1))*40.; #norminv(rand(days.*24,1),0,40);
   # note at this point you can add on the prevailing wind direction, i.e.
   # wind_dir=wind_dir+200;
   wind_dir[np.where(wind_dir>=360.)]= \
        np.mod(wind_dir[np.where(wind_dir>=360)],360);
   wind_dir_str='Prevailing wind';
else:
   sys.exit()
#--------------------------------------------------------------------------
# SECTION 3: Main loop
# For all times...
C1=np.zeros((len(x),len(y),len(wind_dir)))
for i in tqdm.tqdm(range(0,len(wind_dir))):
   for j in range(0,stacks):
        C=np.ones((len(x),len(y)))
        C=gauss_func(Q[j],wind_speed[i],wind_dir[i],x,y,z,
            stack_x[j],stack_y[j],H[j],Dy,Dz,stability[i]);
        C1[:,:,i]=C1[:,:,i]+C;


# SECTION 4: Post process / output

# decide whether to humidify the aerosol and hence increase the mass
if humidify == DRY_AEROSOL:
   print('do not humidify');
elif humidify == HUMIDIFY:
   mass=np.pi/6.*rho_s[aerosol_type]*dry_size**3.;
   moles=mass/Ms[aerosol_type];

   nw=RH*nu[aerosol_type]*moles/(1.-RH);
   mass2=nw*Mw+moles*Ms[aerosol_type];
   C1=C1*mass2/mass;
else:
   sys.exit()


def smooth(y, box_pts):
   box = np.ones(box_pts) / box_pts
   y_smooth = np.convolve(y, box, mode='same')
   return y_smooth

app.layout = html.Div([
   dcc.Graph(id='plot_1'),
])

@app.callback(
   Output('plot_1', 'figure'),
   [Input('plot_1', 'clickData')]
)
def heatmap(_):
   #
   if output == PLAN_VIEW:
      data = np.mean(C1, axis=2) * 1e6

      fig = go.Figure(data=go.Heatmap(z=data, colorscale='Jet'))

      fig.update_layout(
         # title='Pseudocolor Plot',
         xaxis=dict(title='x (metres)', titlefont=dict(size=12, color='black')),
         yaxis=dict(title='y (metres)')
      )
   ##
   elif output == HEIGHT_SLICE:

      data = np.mean(C1, axis=2) * 1e6

      fig = go.Figure(data=go.Heatmap(z=data, colorscale='Jet'))

      fig.update_layout(
         title=stability_str + '\n' + wind_dir_str,
         xaxis=dict(title='y (metres)'),
         yaxis=dict(title='z (metres)'),
         coloraxis_colorbar=dict(title='$\mu$ g m$^{-3}$'),
         coloraxis=dict(cmin=0, cmax=1e2)
      )
   else:
      fig = go.Figure()
      fig.add_trace(go.Scatter(x=times, y=1e6 * np.squeeze(C1[y_slice, x_slice, :]), mode='lines', name='Hourly mean'))
      try:
         smoothed_data = smooth(1e6 * np.squeeze(C1[y_slice, x_slice, :]), 24)
         fig.add_trace(go.Scatter(x=times, y=smoothed_data, mode='lines', name='Daily mean', line=dict(color='red')))
         fig.update_layout(legend=dict(x=0, y=1, traceorder="normal"))
      except Exception as e:
         print("Exception occurred:", e)

      fig.add_trace(go.Scatter(x=times, y=stability, mode='lines'))

      fig.update_layout(
         title=stability_str + '\n' + wind_dir_str,
         xaxis=dict(title='time (days)'),
         yaxis=dict(title='Mass loading ($\mu$ g m$^{-3}$)', domain=[0.55, 1]),
         yaxis2=dict(title='Stability parameter', domain=[0, 0.45])
      )
   return fig

if __name__ == '__main__':
    app.run_server(debug=True)
