import ast
import numpy as np
import time, os
import matplotlib.pyplot as plt
from epics import caget

## Test frame grab from beamline PV

from p4p.client.thread import Context
ctx = Context('pva')

# TO=DO: use bsui and tiled
# pass-318826 test_det [3]: image = db.v2[-1]['primary']['data']['OAV_writing_image'].read()
# pass-318826 test_det [4]: plt.imshow(image[0][0])


# print("hexx = {}".format(hexx))
# print("hexy = {}".format(hexy))
# print("hexz = {}".format(hexz))
# print("prs = {}".format(prs))

# Get the current camera image
folder = 'ManualAlign260128'
os.makedirs(folder, exist_ok=True)


count = 0
t0 = time.time()
for ii in np.arange(99999999):
    # Get the current HEX stage positions
    samx = caget('XF:12ID2C-ES{MCS:2-Ax:3}Mtr.RBV')
    samy = caget('XF:12ID2C-ES{MCS:2-Ax:5}Mtr.RBV')
    samz = caget('XF:12ID2C-ES{MCS:2-Ax:4}Mtr.RBV')
    samth = caget('XF:12ID2C-ES{MCS:2-Ax:6}Mtr.RBV')
    samch = caget('XF:12ID2C-ES{MCS:2-Ax:2}Mtr.RBV')
    hexx = caget('XF:12IDC-OP:2{HEX:Stg-Ax:X}Mtr.RBV')
    hexy = caget('XF:12IDC-OP:2{HEX:Stg-Ax:Y}Mtr.RBV')
    hexz = caget('XF:12IDC-OP:2{HEX:Stg-Ax:Z}Mtr.RBV')
    prs = caget('XF:12IDC-OP:2{HEX:PRS-Ax:Rot}Mtr.RBV')
    t = time.time() - t0
    frame = ctx.get('XF:12IDC-BI{Cam:HEX}Pva1:Image')
    filename = f"./{folder}/frame_top_{count}_{t:.2f}s_prs{prs:.2f}_samx{samx:.2f}_y{samy:.2f}_z{samz:.2f}_th{samth:.2f}_ch{samch:.2f}_hexx{hexx:.2f}_y{hexy:.2f}_z{hexz:.2f}"
    #np.save(filename+'.npy', frame)
    np.savez_compressed(filename+'.npz', frame=frame)
    # plt.imshow(frame)
    # plt.savefig(filename+'.png')

    frame = ctx.get('XF:12IDC-BI{Cam:SAM}Pva1:Image')   # 2024-2.3-py311-tiled
    filename = f"./{folder}/frame_on_{count}_{t:.2f}s_prs{prs:.2f}_samx{samx:.2f}_y{samy:.2f}_z{samz:.2f}_th{samth:.2f}_ch{samch:.2f}_hexx{hexx:.2f}_y{hexy:.2f}_z{hexz:.2f}"
    #  filename = f"./{folder}/frame_on_{count}_{t:.2f}s_prs{prs}_samx{samx}_y{samy}_z{samz}_th{samth}_ch{samch}_hexx{hexx}_y{hexy}_z{hexz}"
    #np.save(filename+'.npy', frame)
    np.savez_compressed(filename+'.npz', frame=frame)
    # plt.imshow(frame)
    # plt.savefig(filename+'.png')

    count = count + 1

    time.sleep(1)

    # frame = ctx.get('XF:12ID2-ES{Pilatus:Det-2M}Pva1:Image')
    # filename = "./frame_saxs_{}_hexx{}_hexy{}_hexz{}".format(count, hexx, hexy, hexz)
    # np.save(filename+'.npy', frame)
    # plt.imshow(frame)
    # plt.savefig(filename+'.png')

