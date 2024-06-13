from django.shortcuts import render
from django.http import HttpResponse
from pdb import set_trace;
import os, sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
import gaussian_plume_model
import requests
from pdb import set_trace

# from json import dumps
# Create your views here.
def index(request):
    # return HttpResponse('<h1>Welcome</h1>')
    # name = 'Jim'
    # return render(request, 'index.html', {'name': name})
    # context = {
    #     'name': 'Jay',
    #     'age': 23,
    #     'nationality': 'US'
    # }
    # return render(request, 'index.html', context)
    # my_name = request.GET['my_name']
    return render(request, 'index.html')

# def get_input(request):
def counter(request):
    # words = request.GET['text']
    context = {}
    labels = {}
    fields = {"RH": "Relative Air Humidity",
              "dry_size": "Dry Diameter (m)",
              "x_slice": "Slice id in x-direction (0-50)",
              "y_slice": "Slice id in y-direction (0-50)",
              "days": "Model Run-time in days",
              # 'onemap_api_key': "Onemap API Key",
              "stack_x0": "latitude of stack 1",
              "stack_x1": "latitude of stack 2",
              "stack_x2": "latitude of stack 3",
              "stack_y0": "longitude of stack 1",
              "stack_y1": "longitude of stack 2",
              "stack_y2": "longitude of stack 3",
              "Q0": "Mass emitted / unit time of stack 1",
              "Q1": "Mass emitted / unit time of stack 2",
              "Q2": "Mass emitted / unit time of stack 3",
              "H0": "Height of stack 1 (m)",
              "H1": "Height of stack 2 (m)",
              "H2": "Height of stack 3 (m)",
    #           };
    # option_id_labels = {
        "aerosol_type": "Aerosol Type",
        "humidify": "Humidify Aerosol?",
        "stab1": "Vertical Stability Parameter",
        "stability_used": "Stability Variant",
        "output": "Output View Type",
        "wind": "Wind Field",
        "wind_dir": "Wind Direction (→: 0, ↑: 90, ↓: 270, ←: 180)",
        # 'cen_lat': "Center Latitude", 'cen_lon': "Center Longitude",
        "stacks": "Number of Stacks"
    }

    option_list = {
      "aerosol_type": ["SODIUM_CHLORIDE", "SULPHURIC_ACID", "ORGANIC_ACID", "AMMONIUM_NITRATE"],
      "humidify": ["DRY_AEROSOL", "HUMIDIFY"],
      "stab1": ["Very unstable", "Moderately unstable", "Slightly unstable", "Neutral", "Moderately stable", "Very stable"],
      "stability_used": ["CONSTANT_STABILITY", "ANNUAL_CYCLE"],
      "output": ["PLAN_VIEW", "HEIGHT_SLICE", "SURFACE_TIME", "NO_PLOT"],
      "wind": ["CONSTANT_WIND", "FLUCTUATING_WIND", "PREVAILING_WIND"],
      "stacks": ["ONE_STACK", "TWO_STACKS", "THREE_STACKS"]
    }
    num_stacks  = int(request.GET['stacks'])
    stack_names = ["stack_x0", "stack_x1", "stack_x2", "stack_y0", "stack_y1", "stack_y2", "Q0", "Q1", "Q2", "H0", "H1", "H2"]
    used_stack_names = [x for i in range(num_stacks) for x in ["stack_x" + str(i), "stack_y" + str(i), "Q" + str(i),  "H" + str(i)]]
    vstab = int(request.GET['stability_used'])
    print("vstab: ", vstab)
    output = int(request.GET['output'])
    option_values = {}
    # for key in sorted(fields.keys()) + sorted(option_id_labels.keys()):
    for key in fields.keys():
        curr_val = request.GET[key]
        if key in stack_names:
            if curr_val == '':
                curr_val = -1
        if key != 'onemap_api_key':
            try:
                curr_val = float(curr_val)
            except:
                set_trace()
            if curr_val % 1 == 0:
                curr_val = int(curr_val)

        if key in set(stack_names).difference(used_stack_names): continue
        if (vstab == 2) and (key == 'stab1'): continue
        if (output == 1) and (key in ['x_slice', 'y_slice']): continue
        if (output == 2) and (key in ['y_slice']): continue
        if (output == 3) and (key in ['num_contour']): continue

        context[key] = curr_val
        labels[key] = fields[key]
        if key in option_list.keys():
            option_values[key] = option_list[key][curr_val-1]
        # context[key + 'Label'] = files[key]

    RH=context['RH'];
    aerosol_type=context['aerosol_type'];
    dry_size=context['dry_size'];
    humidify=context['humidify'];
    stab1=int(request.GET['stab1']) # context['stab1']; # set from 1-6
    stability_used=context['stability_used'];
    output=context['output'];
    x_slice=int(request.GET['x_slice']) # context['x_slice'] # position (1-50) to take the slice in the x-direction
    y_slice=int(request.GET['y_slice']) # context['y_slice'];  # position (1-50) to plot concentrations vs time
    wind=context['wind'];
    stacks=context['stacks'];
    stack_x=[context['stack_x' + str(x)] for x in range(stacks)];
    stack_y=[context['stack_y' + str(x)] for x in range(stacks)];
    # convert stack_x0, stack_y0 from lat, lon to x, y
    Q=[context['Q' + str(x)] for x in range(stacks)]; # mass emitted per unit time
    H=[context['H' + str(x)] for x in range(stacks)]; # stack height, m
    days=context['days'];          # run the model for 365 days
    # onemap_api_key = context['onemap_api_key']
    wind_dir = float(context['wind_dir'])
    rotation = wind_dir - 270
    num_contour = int(request.GET['num_contour'])

    details, uri = gaussian_plume_model.run_simulation(RH, aerosol_type, dry_size, humidify, stab1, stability_used, output, x_slice, y_slice, wind, stacks, stack_x, stack_y, Q, H, days, num_contour, rotation)
    context['uri'] = uri
    context['Details'] = details
    # return render(request,'counter.html',{'data':uri})
    return render(request, 'counter.html', {'data': context, 'label': labels, 'option_values': option_values})
