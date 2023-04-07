import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import scipy.signal as signal
from functools import partial


def create_grating(sf, ori, phase, wave, imsize, colour):
    """
    :param sf: spatial frequency (in pixels)
    :param ori: wave orientation (in degrees, [0-360])
    :param phase: wave phase (in degrees, [0-360])
    :param wave: type of wave ('sqr' or 'sin')
    :param imsize: image size (integer)
    :return: numpy array of shape (imsize, imsize)
    """
    # Get x and y coordinates
    x, y = np.meshgrid(np.arange(imsize[0]), np.arange(imsize[1]))
    x = x/sf
    y = y/sf

    phase_rad = (phase * math.pi) / 180
    if orientation == 'horizontal':  # then movement is vertical
        y += phase_rad
    else:
        x += phase_rad

    # Get the appropriate gradient
    # gradient = np.sin(ori * math.pi / 180) * x - np.cos(ori * math.pi / 180) * y

    # sine wave
    ori_rad = (ori * math.pi) / 180
    sine_wave = np.sin(np.cos(ori_rad) * x + np.sin(ori_rad) * y)

    # Plug gradient into wave function
    if wave == 'sin':
        grating = sine_wave
    elif wave == 'sqr':
        grating = signal.square(sine_wave)
    elif wave == 'blk':
        grating1 = signal.square(sine_wave)

        ori_rad2 = ((ori + 90) * math.pi) / 180
        sine_wave2 = np.sin(np.cos(ori_rad2) * x + np.sin(ori_rad2) * y)
        grating2 = signal.square(sine_wave2)

        grating = grating1 + grating2
        # we only want the intermediate values
        grating[grating > 0] = -2.

    else:
        raise NotImplementedError

    # convert array to rgb values
    grating = (grating - np.min(grating)) / (np.max(grating) - np.min(grating))
    red = np.ones(grating.shape) * 255
    green = np.ones(grating.shape) * 255
    blue = np.ones(grating.shape) * 255

    red[grating > 0.5] = 0
    if colour == 'blue' or colour == 'black':
        green[grating > 0.5] = 0

    if colour == 'green' or colour == 'black':
        blue[grating > 0.5] = 0

    grating = (np.dstack((red, green, blue)).astype(np.uint8))
    return grating


# make figure
colour = 'green'  # green, blue, or black
orientation = 'horizontal'  # 90 for horizontal, 0 for vertical
direction = 'down'  # left, right, up, down
grate_type = 'sqr'  # sin, sqr, or blk
spatial_freq = 200/2
image_size = [3440/2, 1440/2]

file_name = colour + '_' + grate_type + '_' + orientation + '_' + direction

if orientation == 'horizontal':
    orient = 90
elif orientation == 'vertical':
    orient = 0

if direction == 'right' or direction == 'down':
    reverse_motion = 'y'
else:
    reverse_motion = 'n'

fig = plt.figure(frameon=False)
dpi = 96
# fig.set_size_inches(30, 12)
fig.set_size_inches(image_size[0]/dpi, image_size[1]/dpi)

ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)

# Hide X and Y axes label marks
ax.xaxis.set_tick_params(labelbottom=False)
ax.yaxis.set_tick_params(labelleft=False)
# Hide X and Y axes tick marks
ax.set_xticks([])
ax.set_yticks([])

phases = list(range(1, 361, 2))
if reverse_motion == 'y':
    phases.reverse()
ims = []


for idx, p in enumerate(phases):

    grate = create_grating(spatial_freq, orient, p, grate_type, image_size, colour=colour)
    im = ax.imshow(grate, animated=True, aspect='auto')
    ims.append([im])

ani = animation.ArtistAnimation(fig, ims, blit=True)
# plt.show()

writer_video = animation.FFMpegWriter(fps=30)
# ani.save(file_name + '.gif')
ani.save(file_name + '.mp4', writer=writer_video)
print('done!')
