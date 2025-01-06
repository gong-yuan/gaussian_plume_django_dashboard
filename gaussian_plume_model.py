
# https://personalpages.manchester.ac.uk/staff/paul.connolly/teaching/practicals/gaussian_plume_modelling.html
###########################################################################
# GAUSSIAN PLUME MODEL FOR TEACHING PURPOSES                              #
# PAUL CONNOLLY (UNIVERSITY OF MANCHESTER, 2017)                          #
# THIS CODE IS PROVIDED `AS IS' WITH NO GUARANTEE OF ACCURACY             #
# IT IS USED TO DEMONSTRATE THE EFFECTS OF ATMOSPHERIC STABILITY,         #
# WINDSPEED AND DIRECTION AND MULTIPLE STACKS ON THE DISPERSION OF        #
# POLLUTANTS FROM POINT SOURCES                                           #
###########################################################################

import numpy as np
import sys
from scipy.special import erfcinv as erfcinv
import tqdm as tqdm
import time
import math
from gauss_func import gauss_func

import matplotlib.pyplot as plt
from matplotlib import rc
from pdb import set_trace
import matplotlib.pyplot as plt
import io
import urllib, base64
import requests
import pandas as pd
import requests
from pdb import set_trace
np.random.seed(1234)
# rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',*x-coordinatey':'serif','serif':['Palatino']})
# rc('tx-coordinateetex=True)

def convert_point(x, y, deg):
    theta1 = math.radians(deg)
    r = math.sqrt(x*x + y*y)
    if r == 0:
        return x, y
    cos0 = x / r
    sin0 = y / r
    sin_t = math.sin(theta1)
    cos_t = math.cos(theta1)
    sin1 = sin0 * cos_t + cos0 * sin_t
    cos1 = cos0 * cos_t - sin0 * sin_t
    return r * cos1, r *sin1

def convert_points(X, Y, deg):
    newX = np.zeros_like(X)
    newY = np.zeros_like(Y)

    for row in range(newX.shape[0]):
        for col in range(newX.shape[1]):
            newX[row, col], newY[row, col] = convert_point(X[row, col], Y[row, col], deg)
    return newX, newY


def coor_convert(val1, val2, api_key, option):
    if option == '4326to3414':
        argnames = ['latitude', 'longitude']
        outputnames = ['X', 'Y']
    elif option == '3414to4326':
        argnames = ['X', 'Y']
        outputnames = ['latitude', 'longitude']
    rurl = f'https://www.onemap.gov.sg/api/common/convert/{option}?{argnames[0]}={val1}&{argnames[1]}={val2}'
    print(rurl)
    headers = {"Authorization": api_key}
    response = requests.request("GET", rurl, headers=headers)
    assert response.status_code == 200
    result = response.json()
    return result[outputnames[0]], result[outputnames[1]]


def coors_convert(stack_x, stack_y, api_key, option):
    stack_xnew = []
    stack_ynew = []
    for i in range(len(stack_x)):
        x,y = coor_convert(stack_x[i], stack_y[i], api_key, option)
        print("Converted: ", x,y)
        stack_xnew.append(x)
        stack_ynew.append(y)
    return stack_xnew, stack_ynew

def calc_center(stack_x, stack_y):
    cx = 0
    cy = 0
    for i in range(len(stack_x)):
        cx+=stack_x[i]
        cy+=stack_y[i]
    return cx / len(stack_x), cy / len(stack_y)

def center_coors(stack_x, stack_y, cx, cy):
    stack_xnew = []
    stack_ynew = []
    for i in range(len(stack_x)):
        stack_xnew.append(stack_x[i] - cx)
        stack_ynew.append(stack_y[i] - cy)
    return stack_xnew, stack_ynew
    
def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def get_onemap_token(email = "gygongyuan@gmail.com", password = "Ex9fNTX2%vbd") -> str:
    url = "https://www.onemap.gov.sg/api/auth/post/getToken"
    payload = {"email": email, "password": password}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json().get('access_token')


def run_simulation(RH, aerosol_type, dry_size, humidify, stab1, stability_used, output, x_slice, y_slice, wind, stacks, stack_x, stack_y, Q, H, days, num_contour, windspeed, wind_dir_deg):
    print("Aerosol: ", aerosol_type)
    ##########################################################################
    ##################Location Conversion#####################################
    ##########################################################################
    print("stack_x: ", stack_x, "stack_y: ", stack_y)
    stack_x_orig, stack_y_orig = stack_x.copy(), stack_y.copy()
    onemap_api_key = get_onemap_token()
    stack_xm, stack_ym = coors_convert(stack_x, stack_y, onemap_api_key, '4326to3414')
    print("converted to x, y. stack_x: ", stack_xm, "stack_y: ", stack_ym)
    cx,cy = calc_center(stack_xm, stack_ym)
    stack_x, stack_y = center_coors(stack_xm, stack_ym, cx, cy)
    print("centered x, y. in meters stack_xnew: ", stack_x, "stack_ynew: ", stack_y)

    ##########################################################################
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
    stability_str=['Very unstable', 'Moderately unstable','Slightly unstable', \
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
    print("len(x): ", len(x))
    y=x;              # x-grid is same as y-grid
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
    
    wind_speed=float(windspeed)*np.ones((days*24,1)); # m/s
    print(f"Using windspeed: {wind_speed}")
    if wind == CONSTANT_WIND:
       wind_dir=0.*np.ones((days*24,1));
       wind_dir_str='Constant wind';
    elif wind == FLUCTUATING_WIND:
       wind_dir=360.*np.random.rand(days*24,1);
       wind_dir_str='Random wind';
    elif wind == PREVAILING_WIND:
       wind_dir=-np.sqrt(2.)*erfcinv(2.*np.random.rand(24*days,1))*40.; #norminv(rand(days.*24,1),0,40);
       # note at this point you can add on the prevailing wind direction, i.e.
       wind_dir_str='Prevailing wind';
    wind_dir=wind_dir + 270 - wind_dir_deg;
    wind_dir[np.where(wind_dir>=360.)]= np.mod(wind_dir[np.where(wind_dir>=360)],360);
    # else:// there is no such option
    #    sys.exit()
    #--------------------------------------------------------------------------



    # SECTION 3: Main loop
    # For all times...
    C1=np.zeros((len(x),len(y),len(wind_dir)))
    for i in range(0,len(wind_dir)):
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
       aerosol_type_act = aerosol_type - 1
       mass=np.pi/6.*rho_s[aerosol_type_act]*dry_size**3.;
       moles=mass/Ms[aerosol_type_act];

       nw=RH*nu[aerosol_type_act]*moles/(1.-RH);
       mass2=nw*Mw+moles*Ms[aerosol_type_act];
       C1=C1*mass2/mass;
    else:
       sys.exit()


    # output the plots
    cmap = plt.get_cmap('Blues')
    widc = 0.4
    if output == PLAN_VIEW:
        # plt.figure();
       concentration = np.nanmean(C1,axis=2)*1e6
       plt.contour(x + cx, y + cy,concentration, levels = num_contour, cmap=cmap, linewidths = widc)
       # plt.pcolor(x + cx, y + cy, concentration, cmap=cmap)  # 'jet')
       plt.clim((np.min(concentration), np.max(concentration)));
       for i in range(len(stack_xm)):
           plt.plot([stack_xm[i]], [stack_ym[i]], '+', label='Stack ' + (str(i + 1)))
       plt.legend()

       plt.title(stability_str + '\n' + wind_dir_str);
       plt.xlabel('x');
       plt.ylabel('y');
       cb1=plt.colorbar();
       cb1.set_label('$\mu$ g m$^{-3}$');
       data = pd.DataFrame({'X': (x+cx).reshape(-1), 'Y': (y+cy).reshape(-1), 'Concentration_µg': concentration.reshape(-1)})
       return process_df(data), process_plot(plt)
       # plt.show()

    elif output == HEIGHT_SLICE:
        concentration = np.nanmean(C1,axis=2)*1e6
        plt.pcolor(y + cy,z,concentration, cmap=cmap)
        # plt.contour(y+cy, z,concentration, levels = num_contour, cmap=cmap, linewidths = widc)
        for i in range(len(stack_xm)):
            plt.plot([stack_ym[i]], [H[i]], '+', label='Stack ' + (str(i + 1)))
        plt.legend()

        plt.clim((np.min(concentration), np.max(concentration)));
        plt.xlabel('y');
        plt.ylabel('z (metres)');
        plt.title(stability_str + '\n' + wind_dir_str);
        cb1=plt.colorbar();
        cb1.set_label('$\mu$ g m$^{-3}$');
        # plt.show()
        data = pd.DataFrame({'y': (y + cy).reshape(-1), 'Z': z.reshape(-1), 'Concentration_µg': concentration.reshape(-1)})
        return process_df(data), process_plot(plt)

    elif output == SURFACE_TIME:
       f,(ax1, ax2) = plt.subplots(2, sharex=True, sharey=False)
       ax1.plot(times,1e6*np.squeeze(C1[y_slice,x_slice,:]));
       try:
          ax1.plot(times,smooth(1e6*np.squeeze(C1[y_slice,x_slice,:]),24),'r');
          ax1.legend(('Hourly mean','Daily mean'))
       except:
          sys.exit()

       ax1.set_xlabel('time (days)');
       ax1.set_ylabel('Mass loading ($\mu$ g m$^{-3}$)');
       ax1.set_title(stability_str +'\n' + wind_dir_str);

       ax2.plot(times,stability);
       ax2.set_xlabel('time (days)');
       ax2.set_ylabel('Stability parameter');
       data = pd.DataFrame({'Time': times, 'MassLoading ($\mu$ g m$^{-3}$)': 1e6*np.squeeze(C1[y_slice,x_slice,:])})
       # f.show()
       return process_df(data), process_plot(plt)

    elif output == NO_PLOT:
       print('don''t plot');
    else:
       sys.exit()


###########################################################################
def process_df(data):
    buf = io.BytesIO()
    data.to_csv(buf, index = False)
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri =  urllib.parse.quote(string)
    return uri

def process_plot(plt):
    fig = plt.gcf()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png', dpi = 600)
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri =  urllib.parse.quote(string)
    return uri # render(request,'home.html',{'data':uri})


if __name__=="__main__":
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
    #--------------------------------------------------------------------------
    # SECTION 1: Configuration
    # Variables can be changed by the user+++++++++++++++++++++++++++++++++++++
    RH=0.90;
    aerosol_type=SODIUM_CHLORIDE;

    dry_size=60e-9;
    humidify=DRY_AEROSOL;

    stab1=1; # set from 1-6
    stability_used=ANNUAL_CYCLE # CONSTANT_STABILITY;


    output=PLAN_VIEW;
    x_slice=26; # position (1-50) to take the slice in the x-direction
    y_slice=1;  # position (1-50) to plot concentrations vs time

    wind=PREVAILING_WIND;
    stacks=ONE_STACK;
    stack_x=[0., 1000., -200.];
    stack_y=[0., 250., -500.];

    Q=[40., 40., 40.]; # mass emitted per unit time
    H=[50., 50., 50.]; # stack height, m
    days=50;          # run the model for 365 days
    run_simulation(RH, aerosol_type, dry_size, humidify, stab1, stability_used, output, x_slice, y_slice, wind, stacks, stack_x, stack_y, Q, H, days)
