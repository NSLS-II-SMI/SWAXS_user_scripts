
from bluesky.run_engine import WaitForTimeoutError, FailedStatus

def alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th, align_th):
    try:
        yield from bps.mv(thorlabs_su, measurement_pos,timeout=10)
    except:
        pass
    try:
        yield from bps.mv(thorlabs_su, measurement_pos,timeout=10)
    except:
        pass
    try:
        yield from bps.mv(thorlabs_su, measurement_pos,timeout=10)
    except:
        pass
    yield from alignement_gisaxs_hex(angle=align_th)

    yield from bps.mvr(stage.th, th)
    yield from bps.mvr(stage.y, 0.05)

    yield from bps.mv(thorlabs_su, coating_start_pos)




def blade_coating_2025_1(sample_name='bladecoating', coating_start_pos=10, measurement_pos=87, align_th=0.12,th=0.12, dets = [pil2M, pil900KW]):
    #yield from shopen()
    #yield from bps.sleep(1)
    #yield from shopen()
    #yield from bps.sleep(1)
    #yield from shopen()
    #yield from bps.sleep(2)
    
    # yield from bps.mv(thorlabs_su, thorlabs_su.position)
    yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th, align_th)

    det_exposure_time(1, 200)
    # det_exposure_time(0.5,300)
    #det_exposure_time(2, 600)
    sample_id(user_name='ML', sample_name=sample_name)
    yield from bps.mv(syringe_pu.dir, 0) # set pump to infuse (push rather than withdraw)
    yield from bps.mv(syringe_pu.go, 1) # start pump 
    yield from bps.sleep(2.5)
    yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump
    
    yield from bps.mv(thorlabs_su, measurement_pos)
    dets.append(xbpm3.sumX, xbpm2.sumX)
    yield from bp.count(dets)

    # yield from shclose()





def blade_coating_2025_1_slowexp_withoutmotion(sample_name='bladecoating', coating_start_pos=10, measurement_pos=87,align_th=0.12, th=0.12, dets = [pil2M, pil900KW]):   
    
    yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th, align_th)

    det_exposure_time(0.5, 0.5)
    # det_exposure_time(0.5,300)
    #det_exposure_time(2, 600)
    sample_id(user_name='SG', sample_name=sample_name)

    yield from bps.mv(syringe_pu.dir, 0) # set pump to infuse (push rather than withdraw)
    yield from bps.mv(syringe_pu.go, 1) # start pump 
    yield from bps.sleep(15)
    yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump

    yield from bps.mv(thorlabs_su, measurement_pos)

    yield from bp.count(dets, num=120, delay=2.5)

def hydration_scan(sample_name='bladecoating', coating_start_pos=0, measurement_pos=60, th=0.12, dets = [pil2M, pil900KW]):   
    
    # yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th)

    det_exposure_time(0.5, 0.5)
    # det_exposure_time(0.5,300)
    #det_exposure_time(2, 600)
    sample_id(user_name='SG', sample_name=sample_name)

    yield from bps.mv(syringe_pu.dir, 0) # set pump to infuse (push rather than withdraw)
    yield from bps.mv(syringe_pu.go, 1) # start pump 
    yield from bps.sleep(15)
    yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump

    yield from bps.mv(thorlabs_su, measurement_pos)

    yield from bp.count(dets, num=120, delay=2.5)


def blade_coating_2025_1_slowexp_withmotion(sample_name='bladecoating', coating_start_pos=10, measurement_pos=87,align_th=0.12, th=0.12, dets = [pil2M, pil900KW]):
    
    yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th, align_th)

    det_exposure_time(0.5, 0.5)
    # det_exposure_time(0.5,300)
    #det_exposure_time(2, 600)
    sample_id(user_name='JC', sample_name=sample_name)
    yield from bps.mv(syringe_pu.dir, 0) # set pump to infuse (push rather than withdraw)
    yield from bps.mv(syringe_pu.go, 1) # start pump 
    yield from bps.sleep(2.5)
    yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump
    
    yield from bps.mv(thorlabs_su, measurement_pos)
    yield from bp.scan([pil2M, pil900KW], thorlabs_su, measurement_pos, measurement_pos-15, num=480, per_step=one_1d_step_withwait)



def blade_coating_2025_1_slowexp_withmotion_Kelvin(sample_name='bladecoating', coating_start_pos=10, measurement_pos=87,align_th=0.12, th=0.16, dets = [pil2M, pil900KW]):
    
    yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th, align_th)

    det_exposure_time(0.5, 0.5)
    # det_exposure_time(0.5,300)
    #det_exposure_time(2, 600)
    sample_id(user_name='ML', sample_name=sample_name)
    yield from bps.mv(syringe_pu.dir, 0) # set pump to infuse (push rather than withdraw)
    yield from bps.mv(syringe_pu.go, 1) # start pump 
    yield from bps.sleep(2.5)
    yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump
    
    yield from bps.mv(thorlabs_su, measurement_pos)
    yield from bp.scan([pil2M, pil900KW], thorlabs_su, measurement_pos, measurement_pos-10, num=600, per_step=one_1d_step_withwait)


def exsitu_2025_01(sample_name='bladecoating', th=0.12, dets = [pil2M, pil900KW]):
    
    #yield from alignement_gisaxs_hex(0.1)
    det_exposure_time(0.5,0.5)
    sample_id(user_name='AR', sample_name=sample_name)
    
    yield from bps.mvr(stage.th, th)
    yield from bp.count([pil2M, pil900KW])
    yield from bps.mvr(stage.th, -th)


def one_1d_step_withwait(detectors, motor, step, take_reading=None):
    """
    Inner loop of a 1D step scan

    This is the default function for ``per_step`` param in 1D plans.

    Parameters
    ----------
    detectors : iterable
        devices to read
    motor : Settable
        The motor to move
    step : Any
        Where to move the motor to
    take_reading : plan, optional
        function to do the actual acquisition ::

           def take_reading(dets, name='primary'):
                yield from ...

        Callable[List[OphydObj], Optional[str]] -> Generator[Msg], optional

        Defaults to `trigger_and_read`
    """
    take_reading = bps.trigger_and_read if take_reading is None else take_reading

    def move():
        grp = bps._short_uid("set")
        yield bps.Msg("checkpoint")
        yield bps.Msg("set", motor, step, group=grp)
        yield bps.Msg("wait", None, group=grp)

    yield from move()
    yield from bps.sleep(1)
    return (yield from take_reading(list(detectors) + [motor]))



def su_y_center_align():
    """
    hexapod height scan, finding the center of a hole between y=0 and y=5 and moving there

    """
    # Activate the automated derivative calculation
    bec._calc_derivative_and_stats = True

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)

    yield from smi.modeAlignment(technique="gisaxs")

    # Set direct beam ROI
    yield from smi.setDirectBeamROI()

    # Scan height on the DB only
    yield from bp.scan([pil2M], stage.y, 0, 4, 25)
    ps(der=False, plot=True)
    yield from bps.mv(stage.y, ps.cen)

    # Close all the matplotlib windows
    #plt.close("all")

    # Return angle
    yield from smi.modeMeasurement()

    # Deactivate the automated derivative calculation
    bec._calc_derivative_and_stats = False

def exsitu_2025_01(sample_name='bladecoating', dets = [pil2M, pil900KW]):
    
    #yield from alignement_gisaxs_hex(0.1)
    det_exposure_time(0.2,0.2)
    sample_id(user_name='AR', sample_name=sample_name)
    
    #dets.append(xbpm3.sumX, xbpm2.sumX)
    yield from bp.count([pil2M, pil900KW])




'''error:
Transient Scan ID: 972273     Time: 2025-07-28 00:39:38
Persistent Unique Scan ID: 'cd75a6c3-9eef-49f4-89de-177da9e3f2f3'
New stream: 'baseline'
WARNING:stamina:Scheduled retry in 0.77 seconds due to ReadTimeout('The read operation timed out') (attempt 1)
An exception has occurred, use '%tb verbose' to see the full traceback.
ReadTimeout: The read operation timed out
'''


'''Transient Scan ID: 972353     Time: 2025-07-28 08:52:44
Persistent Unique Scan ID: '8d147c26-7ce8-42ea-8eef-434deb67ae23'
New stream: 'baseline'
/nsls2/data1/smi/shared/config/bluesky/profile_collection/startup/smiclasses/pilatus.py:265: UserWarning: .dispatch is deprecated, use .generate_datum instead
  self.dispatch(self._image_name, ttime.time())
New stream: 'primary'                                                                                                                                          
+-----------+------------+----------------------+--------------------+-----------------------+                                                                 
|   seq_num |       time | thorlabs_su_readback | pil2M_stats1_total | pil900KW_stats1_total |
+-----------+------------+----------------------+--------------------+-----------------------+
|         1 | 08:52:48.9 |               87.000 |              71611 |               4716647 |
|         2 | 08:52:52.1 |               86.984 |              69657 |               3867875 |                                                                 
|         3 | 08:52:54.7 |               86.967 |              72141 |               4730328 |                                                                 
|         4 | 08:52:57.2 |               86.950 |              70618 |               4850188 |                                                                 
|         5 | 08:52:59.9 |               86.933 |              67691 |               4822302 |                                                                 
|         6 | 08:53:02.5 |               86.917 |              69381 |               4928953 |                                                                 
|         7 | 08:53:05.0 |               86.900 |              71107 |               4703155 |                                                                 
|         8 | 08:53:07.6 |               86.883 |              68334 |               4740905 |                                                                 
|         9 | 08:53:10.3 |               86.867 |              63615 |               4555301 |                                                                 
|        10 | 08:53:12.9 |               86.850 |              70707 |               4709888 |                                                                 
|        11 | 08:53:15.5 |               86.833 |              67305 |               4715088 |                                                                 
|        12 | 08:53:18.2 |               86.817 |              67676 |               4803240 |                                                                 
|        13 | 08:53:20.9 |               86.800 |              72729 |               4876618 |                                                                 
|        14 | 08:53:23.7 |               86.783 |              64131 |               4532137 |                                                                 
|        15 | 08:53:26.3 |               86.767 |              68947 |               4644725 |                                                                 
|        16 | 08:53:28.9 |               86.750 |              68615 |               4733281 |                                                                 
|        17 | 08:53:31.5 |               86.733 |              72412 |               4822479 |                                                                 
|        18 | 08:53:34.2 |               86.716 |              75028 |               4789179 |                                                                 
|        19 | 08:53:36.8 |               86.700 |              66254 |               4429471 |                                                                 
|        20 | 08:53:39.4 |               86.683 |              65923 |               4502989 |                                                                 
|        21 | 08:53:42.1 |               86.666 |              58681 |               4071125 |                                                                 
|        22 | 08:53:44.9 |               86.650 |              63730 |               4333738 |                                                                 
|        23 | 08:53:47.6 |               86.633 |              61922 |               4277245 |                                                                 
|        24 | 08:53:50.2 |               86.616 |              62746 |               4284464 |                                                                 
|        25 | 08:53:53.9 |               86.600 |              59424 |               4203000 |                                                                 
|        26 | 08:53:56.8 |               86.583 |              56072 |               4148017 |                                                                 
|        27 | 08:53:59.6 |               86.566 |              62984 |               4453063 |                                                                 
|        28 | 08:54:02.5 |               86.549 |              61727 |               4465809 |                                                                 
|        29 | 08:54:05.7 |               86.533 |              58055 |               4115791 |                                                                 
|        30 | 08:54:08.4 |               86.516 |              58562 |               4313100 |                                                                 
|        31 | 08:54:11.3 |               86.499 |              59072 |               4268279 |                                                                 
|        32 | 08:54:14.1 |               86.483 |              61648 |               4363118 |                                                                 
|        33 | 08:54:16.9 |               86.466 |              56818 |               4147914 |                                                                 
|        34 | 08:54:19.7 |               86.449 |              60957 |               4330479 |                                                                 
|        35 | 08:54:22.4 |               86.433 |              61962 |               4299927 |                                                                 
|        36 | 08:54:25.1 |               86.416 |              68778 |               4673617 |                                                                 
|        37 | 08:54:27.7 |               86.399 |              61225 |               4240940 |                                                                 
|        38 | 08:54:30.5 |               86.383 |              58035 |               4109063 |                                                                 
|        39 | 08:54:33.5 |               86.366 |              55337 |               4075212 |                                                                 
|        40 | 08:54:36.3 |               86.349 |              54599 |               4074949 |                                                                 
|        41 | 08:54:39.1 |               86.332 |              56641 |               4073941 |                                                                 
|        42 | 08:54:42.0 |               86.316 |              59555 |               4317192 |                                                                 
|        43 | 08:54:44.8 |               86.299 |              60748 |               4353472 |                                                                 
|        44 | 08:54:48.1 |               86.282 |              54332 |               3979607 |                                                                 
|        45 | 08:54:50.8 |               86.266 |              52927 |               3970430 |                                                                 
|        46 | 08:54:53.7 |               86.249 |              56634 |               4125173 |                                                                 
|        47 | 08:54:56.5 |               86.232 |              52875 |               4032935 |                                                                 
|        48 | 08:54:59.3 |               86.216 |              55120 |               4139302 |                                                                 
|        49 | 08:55:02.0 |               86.199 |              57140 |               4235525 |                                                                 
+-----------+------------+----------------------+--------------------+-----------------------+                                                                 
|   seq_num |       time | thorlabs_su_readback | pil2M_stats1_total | pil900KW_stats1_total |                                                                 
+-----------+------------+----------------------+--------------------+-----------------------+
|        50 | 08:55:04.8 |               86.182 |              55941 |               4264008 |
|        51 | 08:55:07.7 |               86.166 |              57547 |               4277227 |                                                                 
|        52 | 08:55:12.0 |               86.149 |              55385 |               4089077 |                                                                 
|        53 | 08:55:14.8 |               86.132 |              51074 |               3963023 |                                                                 
|        54 | 08:55:17.6 |               86.115 |              55084 |               4162673 |                                                                 
|        55 | 08:55:20.4 |               86.099 |              51719 |               4031837 |                                                                 
|        56 | 08:55:23.4 |               86.082 |              49697 |               3855228 |                                                                 
|        57 | 08:55:26.3 |               86.065 |              50551 |               3909370 |                                                                 
|        58 | 08:55:29.1 |               86.049 |              45617 |               3683240 |                                                                 
|        59 | 08:55:31.9 |               86.032 |              52175 |               4118379 |                                                                 
|        60 | 08:55:34.9 |               86.015 |              50442 |               3848560 |                                                                 
|        61 | 08:55:37.7 |               85.999 |              48705 |               3774341 |                                                                 
|        62 | 08:55:40.5 |               85.982 |              51067 |               3904501 |                                                                 
|        63 | 08:55:43.6 |               85.965 |              49308 |               3803922 |                                                                 
|        64 | 08:55:46.4 |               85.948 |              52068 |               3936908 |                                                                 
|        65 | 08:55:49.1 |               85.932 |              52355 |               3949369 |                                                                 
|        66 | 08:55:52.0 |               85.915 |              50995 |               3947668 |                                                                 
|        67 | 08:55:54.9 |               85.898 |              51536 |               3935781 |                                                                 
|        68 | 08:55:57.9 |               85.882 |              51474 |               3937022 |                                                                 
|        69 | 08:56:00.7 |               85.865 |              46223 |               3763205 |                                                                 
|        70 | 08:56:03.6 |               85.848 |              46357 |               3744181 |                                                                 
|        71 | 08:56:06.6 |               85.832 |              47014 |               3770972 |                                                                 
|        72 | 08:56:09.4 |               85.815 |              48090 |               3794316 |                                                                 
|        73 | 08:56:12.5 |               85.798 |              44725 |               3717559 |                                                                 
|        74 | 08:56:15.3 |               85.782 |              46132 |               3780181 |                                                                 
|        75 | 08:56:18.2 |               85.765 |              46992 |               3789737 |                                                                 
|        76 | 08:56:22.8 |               85.748 |              42347 |               3601366 |                                                                 
WARNING:stamina:Scheduled retry in 0.67 seconds due to ReadTimeout('The read operation timed out') (attempt 1)                                                 
+-----------+------------+----------------------+--------------------+-----------------------+
generator scan ['8d147c26'] (scan num: 972353)
An exception has occurred, use '%tb verbose' to see the full traceback.
ReadTimeout: The read operation timed out

See /home/xf12id/.cache/bluesky/log/bluesky.log for the full traceback.

pass-317903 Nafion_SiO2_30_10per_run_1 [71]: %tb verbose
---------------------------------------------------------------------------
ReadTimeout                               Traceback (most recent call last)
File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpx/_transports/default.py:101, in map_httpcore_exceptions()
    100 try:
--> 101     yield
    102 except Exception as exc:

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpx/_transports/default.py:250, in HTTPTransport.handle_request(self=<httpx.HTTPTransport object>, request=<Request('PATCH', 'https://tiled-dev.nsls2.bnl.g...deb67ae23/streams/primary/internal?partition=0')>)
    249 with map_httpcore_exceptions():
--> 250     resp = self._pool.handle_request(req)
        req = <Request [b'PATCH']>
        self._pool = <ConnectionPool [Requests: 0 active, 0 queued | Connections: 0 active, 1 idle]>
        self = <httpx.HTTPTransport object at 0x7f2daef036d0>
    252 assert isinstance(resp.stream, typing.Iterable)

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpcore/_sync/connection_pool.py:256, in ConnectionPool.handle_request(self=<ConnectionPool [Requests: 0 active, 0 queued | Connections: 0 active, 1 idle]>, request=<Request [b'PATCH']>)
    255     self._close_connections(closing)
--> 256     raise exc from None
    258 # Return the response. Note that in this case we still have to manage
    259 # the point at which the response is closed.

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpcore/_sync/connection_pool.py:236, in ConnectionPool.handle_request(self=<ConnectionPool [Requests: 0 active, 0 queued | Connections: 0 active, 1 idle]>, request=<Request [b'PATCH']>)
    234 try:
    235     # Send the request on the assigned connection.
--> 236     response = connection.handle_request(
        connection = <HTTPConnection ['https://tiled-dev.nsls2.bnl.gov:443', HTTP/1.1, CLOSED, Request Count: 1]>
        pool_request = <httpcore._sync.connection_pool.PoolRequest object at 0x7f2c41b01240>
        pool_request.request = <Request [b'PATCH']>
    237         pool_request.request
    238     )
    239 except ConnectionNotAvailable:
    240     # In some cases a connection may initially be available to
    241     # handle a request, but then become unavailable.
    242     #
    243     # In this case we clear the connection and try again.

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpcore/_sync/connection.py:103, in HTTPConnection.handle_request(self=<HTTPConnection ['https://tiled-dev.nsls2.bnl.gov:443', HTTP/1.1, CLOSED, Request Count: 1]>, request=<Request [b'PATCH']>)
    101     raise exc
--> 103 return self._connection.handle_request(request)
        request = <Request [b'PATCH']>
        self._connection = <HTTP11Connection ['https://tiled-dev.nsls2.bnl.gov:443', CLOSED, Request Count: 1]>
        self = <HTTPConnection ['https://tiled-dev.nsls2.bnl.gov:443', HTTP/1.1, CLOSED, Request Count: 1]>

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpcore/_sync/http11.py:136, in HTTP11Connection.handle_request(self=<HTTP11Connection ['https://tiled-dev.nsls2.bnl.gov:443', CLOSED, Request Count: 1]>, request=<Request [b'PATCH']>)
    135         self._response_closed()
--> 136 raise exc

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpcore/_sync/http11.py:106, in HTTP11Connection.handle_request(self=<HTTP11Connection ['https://tiled-dev.nsls2.bnl.gov:443', CLOSED, Request Count: 1]>, request=<Request [b'PATCH']>)
     97 with Trace(
     98     "receive_response_headers", logger, request, kwargs
     99 ) as trace:
    100     (
    101         http_version,
    102         status,
    103         reason_phrase,
    104         headers,
    105         trailing_data,
--> 106     ) = self._receive_response_headers(**kwargs)
        kwargs = {'request': <Request [b'PATCH']>}
        self = <HTTP11Connection ['https://tiled-dev.nsls2.bnl.gov:443', CLOSED, Request Count: 1]>
    107     trace.return_value = (
    108         http_version,
    109         status,
    110         reason_phrase,
    111         headers,
    112     )

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpcore/_sync/http11.py:177, in HTTP11Connection._receive_response_headers(self=<HTTP11Connection ['https://tiled-dev.nsls2.bnl.gov:443', CLOSED, Request Count: 1]>, request=<Request [b'PATCH']>)
    176 while True:
--> 177     event = self._receive_event(timeout=timeout)
        timeout = 30.0
        self = <HTTP11Connection ['https://tiled-dev.nsls2.bnl.gov:443', CLOSED, Request Count: 1]>
    178     if isinstance(event, h11.Response):

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpcore/_sync/http11.py:217, in HTTP11Connection._receive_event(self=<HTTP11Connection ['https://tiled-dev.nsls2.bnl.gov:443', CLOSED, Request Count: 1]>, timeout=30.0)
    216 if event is h11.NEED_DATA:
--> 217     data = self._network_stream.read(
        self._network_stream = <httpcore._backends.sync.SyncStream object at 0x7f2c41b020e0>
        self = <HTTP11Connection ['https://tiled-dev.nsls2.bnl.gov:443', CLOSED, Request Count: 1]>
        self.READ_NUM_BYTES = 65536
        timeout = 30.0
    218         self.READ_NUM_BYTES, timeout=timeout
    219     )
    221     # If we feed this case through h11 we'll raise an exception like:
    222     #
    223     #     httpcore.RemoteProtocolError: can't handle event type
   (...)
    227     # perspective. Instead we handle this case distinctly and treat
    228     # it as a ConnectError.

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpcore/_backends/sync.py:126, in SyncStream.read(self=<httpcore._backends.sync.SyncStream object>, max_bytes=65536, timeout=30.0)
    125 exc_map: ExceptionMapping = {socket.timeout: ReadTimeout, OSError: ReadError}
--> 126 with map_exceptions(exc_map):
        exc_map = {<class 'TimeoutError'>: <class 'httpcore.ReadTimeout'>, <class 'OSError'>: <class 'httpcore.ReadError'>}
    127     self._sock.settimeout(timeout)

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/contextlib.py:153, in _GeneratorContextManager.__exit__(self=<contextlib._GeneratorContextManager object>, typ=<class 'TimeoutError'>, value=TimeoutError('The read operation timed out'), traceback=<traceback object>)
    152 try:
--> 153     self.gen.throw(typ, value, traceback)
        typ = <class 'TimeoutError'>
        value = TimeoutError('The read operation timed out')
        self.gen = <generator object map_exceptions at 0x7f2ce0635a10>
        traceback = <traceback object at 0x7f2c50129100>
        self = <contextlib._GeneratorContextManager object at 0x7f2c41b03880>
    154 except StopIteration as exc:
    155     # Suppress StopIteration *unless* it's the same exception that
    156     # was passed to throw().  This prevents a StopIteration
    157     # raised inside the "with" statement from being suppressed.

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpcore/_exceptions.py:14, in map_exceptions(map={<class 'TimeoutError'>: <class 'httpcore.ReadTimeout'>, <class 'OSError'>: <class 'httpcore.ReadError'>})
     13     if isinstance(exc, from_exc):
---> 14         raise to_exc(exc) from exc
        to_exc = <class 'httpcore.ReadTimeout'>
     15 raise

ReadTimeout: The read operation timed out

The above exception was the direct cause of the following exception:

ReadTimeout                               Traceback (most recent call last)
Cell In[70], line 1
----> 1 RE(blade_coating_2025_1_slowexp_withmotion_Kelvin(sample_name='Nafion_SiO2_30_10per_run_1',align_th=0.12, th=0.16, dets = [pil2M, pil900KW]))
        RE = <bluesky.run_engine.RunEngine object at 0x7f2e18723310>
        [pil2M, pil900KW] = [SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}', name='pil900KW', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
        pil2M = SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])
        pil900KW = WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}', name='pil900KW', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])

File ~/src/bluesky/src/bluesky/run_engine.py:976, in RunEngine.__call__(self=<bluesky.run_engine.RunEngine object>, plan=<generator object blade_coating_2025_1_slowexp_withmotion_Kelvin>, subs=None, **metadata_kw={})
    972         self._blocking_event.set()
    974     self._task_fut.add_done_callback(set_blocking_event)
--> 976 plan_return = self._resume_task(init_func=_build_task)
        self = <bluesky.run_engine.RunEngine object at 0x7f2e18723310>
    978 if self._interrupted:
    979     raise RunEngineInterrupted(self.pause_msg) from None

File ~/src/bluesky/src/bluesky/run_engine.py:1121, in RunEngine._resume_task(self=<bluesky.run_engine.RunEngine object>, init_func=<function RunEngine.__call__.<locals>._build_task>)
   1118             plan_return = self.NO_PLAN_RETURN
   1119         # otherwise re-raise it
   1120         else:
-> 1121             raise exc
        exc = ReadTimeout('The read operation timed out')
   1122 else:
   1123     plan_return = None

File ~/src/bluesky/src/bluesky/run_engine.py:1756, in RunEngine._run(self=<bluesky.run_engine.RunEngine object>)
   1754     exit_reason = str(err)
   1755     self.log.exception("Run aborted")
-> 1756     raise err
   1757 finally:
   1758     if not exit_reason:

File ~/src/bluesky/src/bluesky/run_engine.py:1610, in RunEngine._run(self=<bluesky.run_engine.RunEngine object>)
   1607 # The normal case of clean operation
   1608 else:
   1609     try:
-> 1610         msg = self._plan_stack[-1].send(resp)
        self = <bluesky.run_engine.RunEngine object at 0x7f2e18723310>
        self._plan_stack = deque([])
        resp = <object object at 0x7f2c88e72c60>
        msg = Msg('unstage', obj=SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), args=(), kwargs={}, run=None)
   1611     # We have exhausted the top generator
   1612     except StopIteration:
   1613         # pop the dead generator go back to the top

File ~/src/bluesky/src/bluesky/preprocessors.py:1399, in SupplementalData.__call__(self=SupplementalData(baseline=[sample_chamber_pressu...configuration_attrs=[])], monitors=[], flyers=[]), plan=<generator object baseline_wrapper>)
   1397 plan = monitor_during_wrapper(plan, self.monitors)
   1398 plan = baseline_wrapper(plan, self.baseline)
-> 1399 return (yield from plan)
        plan = <generator object baseline_wrapper at 0x7f2cfc183370>

File ~/src/bluesky/src/bluesky/preprocessors.py:1252, in baseline_wrapper(plan=<generator object monitor_during_wrapper>, devices=[sample_chamber_pressure(prefix='XF:12IDC-VA:2', ...d_attrs=['waxs', 'maxs'], configuration_attrs=[]), Energy(prefix='', name='energy', settle_time=1, ...abledcmgap', 'target_harmonic'], concurrent=True), DCMInternals(prefix='', name='dcm_config', read_...ocity', 'theta.acceleration', 'theta.motor_egu']), InsertionDevice(prefix='SR:C12-ID:G1{IVU:1-Ax:Ga..._attrs=['user_readback'], configuration_attrs=[]), EpicsMotor(prefix='XF:12ID:m65', name='energy_br...t_dir', 'velocity', 'acceleration', 'motor_egu']), TwoButtonShutter(prefix='XF:12IDC-VA:2{Det:1M-GV...', read_attrs=['status'], configuration_attrs=[]), TwoButtonShutter(prefix='XF:12IDA-PPS:2{PSh}', n...', read_attrs=['status'], configuration_attrs=[]), SAXSBeamStops(prefix='XF:12IDC-ES:2{BS:SAXS-Ax:'...ocity', 'y_pin.acceleration', 'y_pin.motor_egu']), EpicsSignalRO(read_pv='SR:C03-BI{DCCT:1}I:Real-I...753707616.6464, auto_monitor=False, string=False), Attenuator(prefix='XF:12IDC-OP:2{Fltr:1-1}', nam...', read_attrs=['status'], configuration_attrs=[]), Attenuator(prefix='XF:12IDC-OP:2{Fltr:1-2}', nam...', read_attrs=['status'], configuration_attrs=[]), Attenuator(prefix='XF:12IDC-OP:2{Fltr:1-3}', nam...', read_attrs=['status'], configuration_attrs=[]), Attenuator(prefix='XF:12IDC-OP:2{Fltr:1-4}', nam...', read_attrs=['status'], configuration_attrs=[]), Attenuator(prefix='XF:12IDC-OP:2{Fltr:1-5}', nam...', read_attrs=['status'], configuration_attrs=[]), Attenuator(prefix='XF:12IDC-OP:2{Fltr:1-6}', nam...', read_attrs=['status'], configuration_attrs=[]), Attenuator(prefix='XF:12IDC-OP:2{Fltr:1-7}', nam...', read_attrs=['status'], configuration_attrs=[]), Attenuator(prefix='XF:12IDC-OP:2{Fltr:1-8}', nam...', read_attrs=['status'], configuration_attrs=[]), Attenuator(prefix='XF:12IDC-OP:2{Fltr:1-9}', nam...', read_attrs=['status'], configuration_attrs=[]), Attenuator(prefix='XF:12IDC-OP:2{Fltr:1-10}', na...', read_attrs=['status'], configuration_attrs=[]), Attenuator(prefix='XF:12IDC-OP:2{Fltr:1-11}', na...', read_attrs=['status'], configuration_attrs=[]), ...], name='baseline')
   1250     return (yield from plan)
   1251 else:
-> 1252     return (yield from plan_mutator(plan, insert_baseline))
        plan = <generator object monitor_during_wrapper at 0x7f2cfc183f40>

File ~/src/bluesky/src/bluesky/preprocessors.py:188, in plan_mutator(plan=<generator object monitor_during_wrapper>, msg_proc=<function baseline_wrapper.<locals>.insert_baseline>)
    186             continue
    187         else:
--> 188             raise ex
    189 # if inserting / mutating, put new generator on the stack
    190 # and replace the current msg with the first element from the
    191 # new generator
    192 if id(msg) not in msgs_seen:
    193     # Use the id as a hash, and hold a reference to the msg so that
    194     # it cannot be garbage collected until the plan is complete.

File ~/src/bluesky/src/bluesky/preprocessors.py:141, in plan_mutator(plan=<generator object monitor_during_wrapper>, msg_proc=<function baseline_wrapper.<locals>.insert_baseline>)
    139 ret = result_stack.pop()
    140 try:
--> 141     msg = plan_stack[-1].send(ret)
        plan_stack = deque([])
        ret = [SAXSBeamStops(prefix='XF:12IDC-ES:2{BS:SAXS-Ax:', name='pil2M_beamstop', parent='pil2M', read_attrs=['x_rod', 'x_rod.user_readback', 'x_rod.user_setpoint', 'y_rod', 'y_rod.user_readback', 'y_rod.user_setpoint', 'x_pin', 'x_pin.user_readback', 'x_pin.user_setpoint', 'y_pin', 'y_pin.user_readback', 'y_pin.user_setpoint'], configuration_attrs=['x_rod', 'x_rod.user_offset', 'x_rod.user_offset_dir', 'x_rod.velocity', 'x_rod.acceleration', 'x_rod.motor_egu', 'y_rod', 'y_rod.user_offset', 'y_rod.user_offset_dir', 'y_rod.velocity', 'y_rod.acceleration', 'y_rod.motor_egu', 'x_pin', 'x_pin.user_offset', 'x_pin.user_offset_dir', 'x_pin.velocity', 'x_pin.acceleration', 'x_pin.motor_egu', 'y_pin', 'y_pin.user_offset', 'y_pin.user_offset_dir', 'y_pin.velocity', 'y_pin.acceleration', 'y_pin.motor_egu']), DetMotor(prefix='XF:12IDC-ES:2{Det:1M-Ax:', name='pil2M_motor', parent='pil2M', read_attrs=['x', 'x.user_readback', 'x.user_setpoint', 'y', 'y.user_readback', 'y.user_setpoint', 'z', 'z.user_readback', 'z.user_setpoint'], configuration_attrs=['x', 'x.user_offset', 'x.user_offset_dir', 'x.velocity', 'x.acceleration', 'x.motor_egu', 'y', 'y.user_offset', 'y.user_offset_dir', 'y.velocity', 'y.acceleration', 'y.motor_egu', 'z', 'z.user_offset', 'z.user_offset_dir', 'z.velocity', 'z.acceleration', 'z.motor_egu']), TransformPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Trans1:', name='pil2M_trans1', parent='pil2M', read_attrs=[], configuration_attrs=[]), OverlayPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Over1:', name='pil2M_over1', parent='pil2M', read_attrs=[], configuration_attrs=[]), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats5:', name='pil2M_stats5', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats4:', name='pil2M_stats4', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats3:', name='pil2M_stats3', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats2:', name='pil2M_stats2', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats1:', name='pil2M_stats1', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI4:', name='pil2M_roi4', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI3:', name='pil2M_roi3', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI2:', name='pil2M_roi2', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI1:', name='pil2M_roi1', parent='pil2M', read_attrs=[], configuration_attrs=[]), TIFFPluginWithFileStore(prefix='XF:12ID2-ES{Pilatus:Det-2M}TIFF1:', name='pil2M_tiff', parent='pil2M', read_attrs=[], configuration_attrs=[]), PilatusDetectorCamV33(prefix='XF:12ID2-ES{Pilatus:Det-2M}cam1:', name='pil2M_cam', parent='pil2M', read_attrs=['file_number'], configuration_attrs=['acquire_period', 'acquire_time', 'image_mode', 'manufacturer', 'model', 'num_exposures', 'num_images', 'trigger_mode']), SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
        msg = Msg('unstage', obj=SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), args=(), kwargs={}, run=None)
    142 except StopIteration as e:
    143     # discard the exhausted generator
    144     exhausted_gen = plan_stack.pop()

File ~/src/bluesky/src/bluesky/preprocessors.py:863, in monitor_during_wrapper(plan=<generator object fly_during_wrapper>, signals=[])
    861 plan1 = plan_mutator(plan, insert_after_open)
    862 plan2 = plan_mutator(plan1, insert_before_close)
--> 863 return (yield from plan2)
        plan2 = <generator object plan_mutator at 0x7f2ce33f76f0>

File ~/src/bluesky/src/bluesky/preprocessors.py:188, in plan_mutator(plan=<generator object plan_mutator>, msg_proc=<function monitor_during_wrapper.<locals>.insert_before_close>)
    186             continue
    187         else:
--> 188             raise ex
    189 # if inserting / mutating, put new generator on the stack
    190 # and replace the current msg with the first element from the
    191 # new generator
    192 if id(msg) not in msgs_seen:
    193     # Use the id as a hash, and hold a reference to the msg so that
    194     # it cannot be garbage collected until the plan is complete.

File ~/src/bluesky/src/bluesky/preprocessors.py:141, in plan_mutator(plan=<generator object plan_mutator>, msg_proc=<function monitor_during_wrapper.<locals>.insert_before_close>)
    139 ret = result_stack.pop()
    140 try:
--> 141     msg = plan_stack[-1].send(ret)
        plan_stack = deque([])
        ret = [SAXSBeamStops(prefix='XF:12IDC-ES:2{BS:SAXS-Ax:', name='pil2M_beamstop', parent='pil2M', read_attrs=['x_rod', 'x_rod.user_readback', 'x_rod.user_setpoint', 'y_rod', 'y_rod.user_readback', 'y_rod.user_setpoint', 'x_pin', 'x_pin.user_readback', 'x_pin.user_setpoint', 'y_pin', 'y_pin.user_readback', 'y_pin.user_setpoint'], configuration_attrs=['x_rod', 'x_rod.user_offset', 'x_rod.user_offset_dir', 'x_rod.velocity', 'x_rod.acceleration', 'x_rod.motor_egu', 'y_rod', 'y_rod.user_offset', 'y_rod.user_offset_dir', 'y_rod.velocity', 'y_rod.acceleration', 'y_rod.motor_egu', 'x_pin', 'x_pin.user_offset', 'x_pin.user_offset_dir', 'x_pin.velocity', 'x_pin.acceleration', 'x_pin.motor_egu', 'y_pin', 'y_pin.user_offset', 'y_pin.user_offset_dir', 'y_pin.velocity', 'y_pin.acceleration', 'y_pin.motor_egu']), DetMotor(prefix='XF:12IDC-ES:2{Det:1M-Ax:', name='pil2M_motor', parent='pil2M', read_attrs=['x', 'x.user_readback', 'x.user_setpoint', 'y', 'y.user_readback', 'y.user_setpoint', 'z', 'z.user_readback', 'z.user_setpoint'], configuration_attrs=['x', 'x.user_offset', 'x.user_offset_dir', 'x.velocity', 'x.acceleration', 'x.motor_egu', 'y', 'y.user_offset', 'y.user_offset_dir', 'y.velocity', 'y.acceleration', 'y.motor_egu', 'z', 'z.user_offset', 'z.user_offset_dir', 'z.velocity', 'z.acceleration', 'z.motor_egu']), TransformPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Trans1:', name='pil2M_trans1', parent='pil2M', read_attrs=[], configuration_attrs=[]), OverlayPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Over1:', name='pil2M_over1', parent='pil2M', read_attrs=[], configuration_attrs=[]), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats5:', name='pil2M_stats5', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats4:', name='pil2M_stats4', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats3:', name='pil2M_stats3', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats2:', name='pil2M_stats2', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats1:', name='pil2M_stats1', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI4:', name='pil2M_roi4', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI3:', name='pil2M_roi3', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI2:', name='pil2M_roi2', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI1:', name='pil2M_roi1', parent='pil2M', read_attrs=[], configuration_attrs=[]), TIFFPluginWithFileStore(prefix='XF:12ID2-ES{Pilatus:Det-2M}TIFF1:', name='pil2M_tiff', parent='pil2M', read_attrs=[], configuration_attrs=[]), PilatusDetectorCamV33(prefix='XF:12ID2-ES{Pilatus:Det-2M}cam1:', name='pil2M_cam', parent='pil2M', read_attrs=['file_number'], configuration_attrs=['acquire_period', 'acquire_time', 'image_mode', 'manufacturer', 'model', 'num_exposures', 'num_images', 'trigger_mode']), SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
        msg = Msg('unstage', obj=SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), args=(), kwargs={}, run=None)
    142 except StopIteration as e:
    143     # discard the exhausted generator
    144     exhausted_gen = plan_stack.pop()

File ~/src/bluesky/src/bluesky/preprocessors.py:188, in plan_mutator(plan=<generator object fly_during_wrapper>, msg_proc=<function monitor_during_wrapper.<locals>.insert_after_open>)
    186             continue
    187         else:
--> 188             raise ex
    189 # if inserting / mutating, put new generator on the stack
    190 # and replace the current msg with the first element from the
    191 # new generator
    192 if id(msg) not in msgs_seen:
    193     # Use the id as a hash, and hold a reference to the msg so that
    194     # it cannot be garbage collected until the plan is complete.

File ~/src/bluesky/src/bluesky/preprocessors.py:141, in plan_mutator(plan=<generator object fly_during_wrapper>, msg_proc=<function monitor_during_wrapper.<locals>.insert_after_open>)
    139 ret = result_stack.pop()
    140 try:
--> 141     msg = plan_stack[-1].send(ret)
        plan_stack = deque([])
        ret = [SAXSBeamStops(prefix='XF:12IDC-ES:2{BS:SAXS-Ax:', name='pil2M_beamstop', parent='pil2M', read_attrs=['x_rod', 'x_rod.user_readback', 'x_rod.user_setpoint', 'y_rod', 'y_rod.user_readback', 'y_rod.user_setpoint', 'x_pin', 'x_pin.user_readback', 'x_pin.user_setpoint', 'y_pin', 'y_pin.user_readback', 'y_pin.user_setpoint'], configuration_attrs=['x_rod', 'x_rod.user_offset', 'x_rod.user_offset_dir', 'x_rod.velocity', 'x_rod.acceleration', 'x_rod.motor_egu', 'y_rod', 'y_rod.user_offset', 'y_rod.user_offset_dir', 'y_rod.velocity', 'y_rod.acceleration', 'y_rod.motor_egu', 'x_pin', 'x_pin.user_offset', 'x_pin.user_offset_dir', 'x_pin.velocity', 'x_pin.acceleration', 'x_pin.motor_egu', 'y_pin', 'y_pin.user_offset', 'y_pin.user_offset_dir', 'y_pin.velocity', 'y_pin.acceleration', 'y_pin.motor_egu']), DetMotor(prefix='XF:12IDC-ES:2{Det:1M-Ax:', name='pil2M_motor', parent='pil2M', read_attrs=['x', 'x.user_readback', 'x.user_setpoint', 'y', 'y.user_readback', 'y.user_setpoint', 'z', 'z.user_readback', 'z.user_setpoint'], configuration_attrs=['x', 'x.user_offset', 'x.user_offset_dir', 'x.velocity', 'x.acceleration', 'x.motor_egu', 'y', 'y.user_offset', 'y.user_offset_dir', 'y.velocity', 'y.acceleration', 'y.motor_egu', 'z', 'z.user_offset', 'z.user_offset_dir', 'z.velocity', 'z.acceleration', 'z.motor_egu']), TransformPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Trans1:', name='pil2M_trans1', parent='pil2M', read_attrs=[], configuration_attrs=[]), OverlayPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Over1:', name='pil2M_over1', parent='pil2M', read_attrs=[], configuration_attrs=[]), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats5:', name='pil2M_stats5', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats4:', name='pil2M_stats4', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats3:', name='pil2M_stats3', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats2:', name='pil2M_stats2', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats1:', name='pil2M_stats1', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI4:', name='pil2M_roi4', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI3:', name='pil2M_roi3', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI2:', name='pil2M_roi2', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI1:', name='pil2M_roi1', parent='pil2M', read_attrs=[], configuration_attrs=[]), TIFFPluginWithFileStore(prefix='XF:12ID2-ES{Pilatus:Det-2M}TIFF1:', name='pil2M_tiff', parent='pil2M', read_attrs=[], configuration_attrs=[]), PilatusDetectorCamV33(prefix='XF:12ID2-ES{Pilatus:Det-2M}cam1:', name='pil2M_cam', parent='pil2M', read_attrs=['file_number'], configuration_attrs=['acquire_period', 'acquire_time', 'image_mode', 'manufacturer', 'model', 'num_exposures', 'num_images', 'trigger_mode']), SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
        msg = Msg('unstage', obj=SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), args=(), kwargs={}, run=None)
    142 except StopIteration as e:
    143     # discard the exhausted generator
    144     exhausted_gen = plan_stack.pop()

File ~/src/bluesky/src/bluesky/preprocessors.py:925, in fly_during_wrapper(plan=<generator object blade_coating_2025_1_slowexp_withmotion_Kelvin>, flyers=[])
    923 plan1 = plan_mutator(plan, insert_after_open)
    924 plan2 = plan_mutator(plan1, insert_before_close)
--> 925 return (yield from plan2)
        plan2 = <generator object plan_mutator at 0x7f2ce33f49e0>

File ~/src/bluesky/src/bluesky/preprocessors.py:188, in plan_mutator(plan=<generator object plan_mutator>, msg_proc=<function fly_during_wrapper.<locals>.insert_before_close>)
    186             continue
    187         else:
--> 188             raise ex
    189 # if inserting / mutating, put new generator on the stack
    190 # and replace the current msg with the first element from the
    191 # new generator
    192 if id(msg) not in msgs_seen:
    193     # Use the id as a hash, and hold a reference to the msg so that
    194     # it cannot be garbage collected until the plan is complete.

File ~/src/bluesky/src/bluesky/preprocessors.py:141, in plan_mutator(plan=<generator object plan_mutator>, msg_proc=<function fly_during_wrapper.<locals>.insert_before_close>)
    139 ret = result_stack.pop()
    140 try:
--> 141     msg = plan_stack[-1].send(ret)
        plan_stack = deque([])
        ret = [SAXSBeamStops(prefix='XF:12IDC-ES:2{BS:SAXS-Ax:', name='pil2M_beamstop', parent='pil2M', read_attrs=['x_rod', 'x_rod.user_readback', 'x_rod.user_setpoint', 'y_rod', 'y_rod.user_readback', 'y_rod.user_setpoint', 'x_pin', 'x_pin.user_readback', 'x_pin.user_setpoint', 'y_pin', 'y_pin.user_readback', 'y_pin.user_setpoint'], configuration_attrs=['x_rod', 'x_rod.user_offset', 'x_rod.user_offset_dir', 'x_rod.velocity', 'x_rod.acceleration', 'x_rod.motor_egu', 'y_rod', 'y_rod.user_offset', 'y_rod.user_offset_dir', 'y_rod.velocity', 'y_rod.acceleration', 'y_rod.motor_egu', 'x_pin', 'x_pin.user_offset', 'x_pin.user_offset_dir', 'x_pin.velocity', 'x_pin.acceleration', 'x_pin.motor_egu', 'y_pin', 'y_pin.user_offset', 'y_pin.user_offset_dir', 'y_pin.velocity', 'y_pin.acceleration', 'y_pin.motor_egu']), DetMotor(prefix='XF:12IDC-ES:2{Det:1M-Ax:', name='pil2M_motor', parent='pil2M', read_attrs=['x', 'x.user_readback', 'x.user_setpoint', 'y', 'y.user_readback', 'y.user_setpoint', 'z', 'z.user_readback', 'z.user_setpoint'], configuration_attrs=['x', 'x.user_offset', 'x.user_offset_dir', 'x.velocity', 'x.acceleration', 'x.motor_egu', 'y', 'y.user_offset', 'y.user_offset_dir', 'y.velocity', 'y.acceleration', 'y.motor_egu', 'z', 'z.user_offset', 'z.user_offset_dir', 'z.velocity', 'z.acceleration', 'z.motor_egu']), TransformPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Trans1:', name='pil2M_trans1', parent='pil2M', read_attrs=[], configuration_attrs=[]), OverlayPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Over1:', name='pil2M_over1', parent='pil2M', read_attrs=[], configuration_attrs=[]), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats5:', name='pil2M_stats5', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats4:', name='pil2M_stats4', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats3:', name='pil2M_stats3', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats2:', name='pil2M_stats2', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats1:', name='pil2M_stats1', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI4:', name='pil2M_roi4', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI3:', name='pil2M_roi3', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI2:', name='pil2M_roi2', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI1:', name='pil2M_roi1', parent='pil2M', read_attrs=[], configuration_attrs=[]), TIFFPluginWithFileStore(prefix='XF:12ID2-ES{Pilatus:Det-2M}TIFF1:', name='pil2M_tiff', parent='pil2M', read_attrs=[], configuration_attrs=[]), PilatusDetectorCamV33(prefix='XF:12ID2-ES{Pilatus:Det-2M}cam1:', name='pil2M_cam', parent='pil2M', read_attrs=['file_number'], configuration_attrs=['acquire_period', 'acquire_time', 'image_mode', 'manufacturer', 'model', 'num_exposures', 'num_images', 'trigger_mode']), SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
        msg = Msg('unstage', obj=SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), args=(), kwargs={}, run=None)
    142 except StopIteration as e:
    143     # discard the exhausted generator
    144     exhausted_gen = plan_stack.pop()

File ~/src/bluesky/src/bluesky/preprocessors.py:188, in plan_mutator(plan=<generator object blade_coating_2025_1_slowexp_withmotion_Kelvin>, msg_proc=<function fly_during_wrapper.<locals>.insert_after_open>)
    186             continue
    187         else:
--> 188             raise ex
    189 # if inserting / mutating, put new generator on the stack
    190 # and replace the current msg with the first element from the
    191 # new generator
    192 if id(msg) not in msgs_seen:
    193     # Use the id as a hash, and hold a reference to the msg so that
    194     # it cannot be garbage collected until the plan is complete.

File ~/src/bluesky/src/bluesky/preprocessors.py:141, in plan_mutator(plan=<generator object blade_coating_2025_1_slowexp_withmotion_Kelvin>, msg_proc=<function fly_during_wrapper.<locals>.insert_after_open>)
    139 ret = result_stack.pop()
    140 try:
--> 141     msg = plan_stack[-1].send(ret)
        plan_stack = deque([])
        ret = [SAXSBeamStops(prefix='XF:12IDC-ES:2{BS:SAXS-Ax:', name='pil2M_beamstop', parent='pil2M', read_attrs=['x_rod', 'x_rod.user_readback', 'x_rod.user_setpoint', 'y_rod', 'y_rod.user_readback', 'y_rod.user_setpoint', 'x_pin', 'x_pin.user_readback', 'x_pin.user_setpoint', 'y_pin', 'y_pin.user_readback', 'y_pin.user_setpoint'], configuration_attrs=['x_rod', 'x_rod.user_offset', 'x_rod.user_offset_dir', 'x_rod.velocity', 'x_rod.acceleration', 'x_rod.motor_egu', 'y_rod', 'y_rod.user_offset', 'y_rod.user_offset_dir', 'y_rod.velocity', 'y_rod.acceleration', 'y_rod.motor_egu', 'x_pin', 'x_pin.user_offset', 'x_pin.user_offset_dir', 'x_pin.velocity', 'x_pin.acceleration', 'x_pin.motor_egu', 'y_pin', 'y_pin.user_offset', 'y_pin.user_offset_dir', 'y_pin.velocity', 'y_pin.acceleration', 'y_pin.motor_egu']), DetMotor(prefix='XF:12IDC-ES:2{Det:1M-Ax:', name='pil2M_motor', parent='pil2M', read_attrs=['x', 'x.user_readback', 'x.user_setpoint', 'y', 'y.user_readback', 'y.user_setpoint', 'z', 'z.user_readback', 'z.user_setpoint'], configuration_attrs=['x', 'x.user_offset', 'x.user_offset_dir', 'x.velocity', 'x.acceleration', 'x.motor_egu', 'y', 'y.user_offset', 'y.user_offset_dir', 'y.velocity', 'y.acceleration', 'y.motor_egu', 'z', 'z.user_offset', 'z.user_offset_dir', 'z.velocity', 'z.acceleration', 'z.motor_egu']), TransformPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Trans1:', name='pil2M_trans1', parent='pil2M', read_attrs=[], configuration_attrs=[]), OverlayPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Over1:', name='pil2M_over1', parent='pil2M', read_attrs=[], configuration_attrs=[]), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats5:', name='pil2M_stats5', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats4:', name='pil2M_stats4', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats3:', name='pil2M_stats3', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats2:', name='pil2M_stats2', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats1:', name='pil2M_stats1', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI4:', name='pil2M_roi4', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI3:', name='pil2M_roi3', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI2:', name='pil2M_roi2', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI1:', name='pil2M_roi1', parent='pil2M', read_attrs=[], configuration_attrs=[]), TIFFPluginWithFileStore(prefix='XF:12ID2-ES{Pilatus:Det-2M}TIFF1:', name='pil2M_tiff', parent='pil2M', read_attrs=[], configuration_attrs=[]), PilatusDetectorCamV33(prefix='XF:12ID2-ES{Pilatus:Det-2M}cam1:', name='pil2M_cam', parent='pil2M', read_attrs=['file_number'], configuration_attrs=['acquire_period', 'acquire_time', 'image_mode', 'manufacturer', 'model', 'num_exposures', 'num_images', 'trigger_mode']), SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
        msg = Msg('unstage', obj=SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), args=(), kwargs={}, run=None)
    142 except StopIteration as e:
    143     # discard the exhausted generator
    144     exhausted_gen = plan_stack.pop()

File ~/SWAXS_user_scripts/LBL/bladecoating.py:126, in blade_coating_2025_1_slowexp_withmotion_Kelvin(sample_name='Nafion_SiO2_30_10per_run_1', coating_start_pos=10, measurement_pos=87, align_th=0.12, th=0.16, dets=[SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M..., 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}',..., 'stats1.profile_size', 'stats1.ts_num_points'])])
    123 yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump
    125 yield from bps.mv(thorlabs_su, measurement_pos)
--> 126 yield from bp.scan([pil2M, pil900KW], thorlabs_su, measurement_pos, measurement_pos-10, num=600, per_step=one_1d_step_withwait)
        [pil2M, pil900KW] = [SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}', name='pil900KW', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
        pil2M = SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])
        pil900KW = WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}', name='pil900KW', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])
        measurement_pos = 87
        thorlabs_su = ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}Mtr', name='thorlabs_su', settle_time=0.0, timeout=None, read_attrs=['readback', 'setpoint', 'done'], configuration_attrs=[], limits=None, egu='')
        measurement_pos-10 = 77
        bp = <module 'bluesky.plans' from '/home/xf12id/src/bluesky/src/bluesky/plans.py'>

File ~/src/bluesky/src/bluesky/plans.py:1291, in scan(detectors=[SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M..., 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}',..., 'stats1.profile_size', 'stats1.ts_num_points'])], num=600, per_step=<function one_1d_step_withwait>, md={}, *args=(ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}...e'], configuration_attrs=[], limits=None, egu=''), 87, 77))
   1287 _md["hints"].update(md.get("hints", {}) or {})  # type: ignore
   1289 full_cycler = plan_patterns.inner_product(num=num, args=args)
-> 1291 return (yield from scan_nd(detectors, full_cycler, per_step=per_step, md=_md))
        _md = {'plan_args': {'detectors': ["SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])", "WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}', name='pil900KW', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])"], 'num': 600, 'args': ["ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}Mtr', name='thorlabs_su', settle_time=0.0, timeout=None, read_attrs=['readback', 'setpoint', 'done'], configuration_attrs=[], limits=None, egu='')", 87, 77], 'per_step': '<function one_1d_step_withwait at 0x7f2cc0a76320>'}, 'plan_name': 'scan', 'plan_pattern': 'inner_product', 'plan_pattern_module': 'bluesky.plan_patterns', 'plan_pattern_args': {'num': 600, 'args': ["ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}Mtr', name='thorlabs_su', settle_time=0.0, timeout=None, read_attrs=['readback', 'setpoint', 'done'], configuration_attrs=[], limits=None, egu='')", 87, 77]}, 'motors': ('thorlabs_su',), 'hints': {'dimensions': [(['thorlabs_su_readback'], 'primary')]}}
        full_cycler = cycler(ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}Mtr', name='thorlabs_su', settle_time=0.0, timeout=None, read_attrs=['readback', 'setpoint', 'done'], configuration_attrs=[], limits=None, egu=''), [87.0, 86.98330550918197, 86.96661101836393, 86.94991652754591, 86.93322203672788, 86.91652754590984, 86.89983305509182, 86.88313856427379, 86.86644407345575, 86.84974958263773, 86.8330550918197, 86.81636060100168, 86.79966611018364, 86.78297161936561, 86.76627712854759, 86.74958263772955, 86.73288814691152, 86.7161936560935, 86.69949916527545, 86.68280467445743, 86.6661101836394, 86.64941569282136, 86.63272120200334, 86.61602671118531, 86.59933222036727, 86.58263772954925, 86.56594323873122, 86.54924874791318, 86.53255425709516, 86.51585976627713, 86.49916527545909, 86.48247078464107, 86.46577629382304, 86.44908180300501, 86.43238731218698, 86.41569282136895, 86.39899833055092, 86.38230383973288, 86.36560934891486, 86.34891485809683, 86.3322203672788, 86.31552587646077, 86.29883138564274, 86.2821368948247, 86.26544240400668, 86.24874791318865, 86.23205342237061, 86.21535893155259, 86.19866444073456, 86.18196994991652, 86.1652754590985, 86.14858096828047, 86.13188647746244, 86.1151919866444, 86.09849749582638, 86.08180300500835, 86.06510851419031, 86.04841402337229, 86.03171953255426, 86.01502504173622, 85.9983305509182, 85.98163606010017, 85.96494156928213, 85.9482470784641, 85.93155258764608, 85.91485809682804, 85.89816360601002, 85.88146911519199, 85.86477462437395, 85.84808013355592, 85.8313856427379, 85.81469115191986, 85.79799666110183, 85.78130217028381, 85.76460767946578, 85.74791318864774, 85.73121869782972, 85.71452420701169, 85.69782971619365, 85.68113522537563, 85.6644407345576, 85.64774624373956, 85.63105175292154, 85.61435726210351, 85.59766277128547, 85.58096828046745, 85.56427378964942, 85.54757929883138, 85.53088480801335, 85.51419031719533, 85.49749582637729, 85.48080133555926, 85.46410684474124, 85.4474123539232, 85.43071786310517, 85.41402337228715, 85.39732888146912, 85.38063439065108, 85.36393989983306, 85.34724540901503, 85.33055091819699, 85.31385642737897, 85.29716193656094, 85.2804674457429, 85.26377295492487, 85.24707846410685, 85.23038397328881, 85.21368948247078, 85.19699499165276, 85.18030050083472, 85.1636060100167, 85.14691151919867, 85.13021702838063, 85.1135225375626, 85.09682804674458, 85.08013355592655, 85.06343906510851, 85.04674457429049, 85.03005008347246, 85.01335559265442, 84.9966611018364, 84.97996661101837, 84.96327212020033, 84.9465776293823, 84.92988313856428, 84.91318864774624, 84.89649415692821, 84.87979966611019, 84.86310517529215, 84.84641068447412, 84.8297161936561, 84.81302170283806, 84.79632721202003, 84.779632721202, 84.76293823038398, 84.74624373956594, 84.72954924874792, 84.71285475792989, 84.69616026711185, 84.67946577629382, 84.6627712854758, 84.64607679465776, 84.62938230383973, 84.61268781302171, 84.59599332220367, 84.57929883138564, 84.56260434056762, 84.54590984974958, 84.52921535893155, 84.51252086811353, 84.49582637729549, 84.47913188647746, 84.46243739565944, 84.4457429048414, 84.42904841402337, 84.41235392320534, 84.39565943238732, 84.37896494156928, 84.36227045075125, 84.34557595993323, 84.32888146911519, 84.31218697829716, 84.29549248747914, 84.2787979966611, 84.26210350584307, 84.24540901502505, 84.228714524207, 84.21202003338898, 84.19532554257096, 84.17863105175292, 84.16193656093489, 84.14524207011686, 84.12854757929883, 84.1118530884808, 84.09515859766277, 84.07846410684473, 84.06176961602671, 84.04507512520868, 84.02838063439066, 84.01168614357262, 83.99499165275459, 83.97829716193657, 83.96160267111853, 83.9449081803005, 83.92821368948248, 83.91151919866444, 83.89482470784641, 83.87813021702839, 83.86143572621035, 83.84474123539232, 83.8280467445743, 83.81135225375625, 83.79465776293823, 83.7779632721202, 83.76126878130216, 83.74457429048414, 83.72787979966611, 83.71118530884809, 83.69449081803005, 83.67779632721202, 83.661101836394, 83.64440734557596, 83.62771285475793, 83.6110183639399, 83.59432387312187, 83.57762938230384, 83.56093489148581, 83.54424040066777, 83.52754590984975, 83.51085141903172, 83.49415692821368, 83.47746243739566, 83.46076794657763, 83.4440734557596, 83.42737896494157, 83.41068447412354, 83.39398998330552, 83.37729549248748, 83.36060100166945, 83.34390651085143, 83.32721202003339, 83.31051752921536, 83.29382303839733, 83.2771285475793, 83.26043405676127, 83.24373956594324, 83.2270450751252, 83.21035058430718, 83.19365609348915, 83.17696160267111, 83.16026711185309, 83.14357262103506, 83.12687813021702, 83.110183639399, 83.09348914858097, 83.07679465776293, 83.0601001669449, 83.04340567612688, 83.02671118530886, 83.01001669449082, 82.99332220367279, 82.97662771285476, 82.95993322203672, 82.9432387312187, 82.92654424040067, 82.90984974958263, 82.89315525876461, 82.87646076794658, 82.85976627712854, 82.84307178631052, 82.82637729549249, 82.80968280467445, 82.79298831385643, 82.7762938230384, 82.75959933222036, 82.74290484140234, 82.72621035058431, 82.70951585976627, 82.69282136894824, 82.67612687813022, 82.6594323873122, 82.64273789649415, 82.62604340567613, 82.6093489148581, 82.59265442404006, 82.57595993322204, 82.55926544240401, 82.54257095158597, 82.52587646076795, 82.50918196994992, 82.49248747913188, 82.47579298831386, 82.45909849749583, 82.44240400667779, 82.42570951585977, 82.40901502504174, 82.3923205342237, 82.37562604340567, 82.35893155258765, 82.34223706176962, 82.32554257095158, 82.30884808013356, 82.29215358931553, 82.27545909849749, 82.25876460767947, 82.24207011686144, 82.2253756260434, 82.20868113522538, 82.19198664440735, 82.17529215358931, 82.15859766277129, 82.14190317195326, 82.12520868113522, 82.1085141903172, 82.09181969949917, 82.07512520868113, 82.0584307178631, 82.04173622704508, 82.02504173622705, 82.00834724540901, 81.99165275459099, 81.97495826377296, 81.95826377295492, 81.9415692821369, 81.92487479131887, 81.90818030050083, 81.8914858096828, 81.87479131886478, 81.85809682804674, 81.84140233722871, 81.82470784641069, 81.80801335559265, 81.79131886477462, 81.7746243739566, 81.75792988313856, 81.74123539232053, 81.72454090150251, 81.70784641068447, 81.69115191986644, 81.67445742904842, 81.65776293823038, 81.64106844741235, 81.62437395659433, 81.6076794657763, 81.59098497495826, 81.57429048414023, 81.55759599332221, 81.54090150250417, 81.52420701168614, 81.50751252086812, 81.49081803005008, 81.47412353923205, 81.45742904841403, 81.44073455759599, 81.42404006677796, 81.40734557595994, 81.3906510851419, 81.37395659432387, 81.35726210350585, 81.3405676126878, 81.32387312186978, 81.30717863105176, 81.29048414023373, 81.27378964941569, 81.25709515859766, 81.24040066777964, 81.2237061769616, 81.20701168614357, 81.19031719532555, 81.17362270450751, 81.15692821368948, 81.14023372287146, 81.12353923205342, 81.10684474123539, 81.09015025041737, 81.07345575959933, 81.0567612687813, 81.04006677796328, 81.02337228714524, 81.00667779632721, 80.98998330550918, 80.97328881469116, 80.95659432387312, 80.9398998330551, 80.92320534223707, 80.90651085141903, 80.889816360601, 80.87312186978298, 80.85642737896494, 80.83973288814691, 80.82303839732889, 80.80634390651085, 80.78964941569282, 80.7729549248748, 80.75626043405676, 80.73956594323873, 80.7228714524207, 80.70617696160267, 80.68948247078464, 80.67278797996661, 80.65609348914859, 80.63939899833055, 80.62270450751252, 80.6060100166945, 80.58931552587646, 80.57262103505843, 80.5559265442404, 80.53923205342237, 80.52253756260434, 80.50584307178632, 80.48914858096828, 80.47245409015025, 80.45575959933223, 80.43906510851419, 80.42237061769616, 80.40567612687813, 80.3889816360601, 80.37228714524207, 80.35559265442404, 80.338898163606, 80.32220367278798, 80.30550918196995, 80.28881469115191, 80.27212020033389, 80.25542570951586, 80.23873121869784, 80.2220367278798, 80.20534223706177, 80.18864774624375, 80.1719532554257, 80.15525876460768, 80.13856427378965, 80.12186978297161, 80.10517529215359, 80.08848080133556, 80.07178631051752, 80.0550918196995, 80.03839732888147, 80.02170283806343, 80.00500834724541, 79.98831385642738, 79.97161936560934, 79.95492487479132, 79.93823038397329, 79.92153589315527, 79.90484140233723, 79.8881469115192, 79.87145242070117, 79.85475792988314, 79.83806343906511, 79.82136894824708, 79.80467445742904, 79.78797996661102, 79.771285475793, 79.75459098497495, 79.73789649415693, 79.7212020033389, 79.70450751252086, 79.68781302170284, 79.67111853088481, 79.65442404006677, 79.63772954924875, 79.62103505843072, 79.6043405676127, 79.58764607679466, 79.57095158597663, 79.5542570951586, 79.53756260434056, 79.52086811352254, 79.50417362270451, 79.48747913188647, 79.47078464106845, 79.45409015025042, 79.43739565943238, 79.42070116861436, 79.40400667779633, 79.38731218697829, 79.37061769616027, 79.35392320534224, 79.3372287145242, 79.32053422370618, 79.30383973288815, 79.28714524207012, 79.27045075125208, 79.25375626043406, 79.23706176961602, 79.220367278798, 79.20367278797997, 79.18697829716194, 79.1702838063439, 79.15358931552588, 79.13689482470785, 79.12020033388981, 79.10350584307179, 79.08681135225376, 79.07011686143572, 79.0534223706177, 79.03672787979967, 79.02003338898163, 79.0033388981636, 78.98664440734558, 78.96994991652755, 78.95325542570951, 78.93656093489149, 78.91986644407345, 78.90317195325542, 78.8864774624374, 78.86978297161937, 78.85308848080133, 78.8363939899833, 78.81969949916528, 78.80300500834724, 78.78631051752922, 78.76961602671119, 78.75292153589315, 78.73622704507513, 78.7195325542571, 78.70283806343906, 78.68614357262103, 78.66944908180301, 78.65275459098497, 78.63606010016694, 78.61936560934892, 78.60267111853088, 78.58597662771285, 78.56928213689483, 78.5525876460768, 78.53589315525876, 78.51919866444074, 78.50250417362271, 78.48580968280467, 78.46911519198665, 78.45242070116862, 78.43572621035058, 78.41903171953255, 78.40233722871453, 78.38564273789649, 78.36894824707846, 78.35225375626044, 78.3355592654424, 78.31886477462437, 78.30217028380635, 78.28547579298831, 78.26878130217028, 78.25208681135226, 78.23539232053423, 78.21869782971619, 78.20200333889817, 78.18530884808013, 78.1686143572621, 78.15191986644408, 78.13522537562605, 78.11853088480801, 78.10183639398998, 78.08514190317196, 78.06844741235392, 78.0517529215359, 78.03505843071787, 78.01836393989983, 78.0016694490818, 77.98497495826378, 77.96828046744574, 77.95158597662771, 77.93489148580969, 77.91819699499166, 77.90150250417362, 77.8848080133556, 77.86811352253756, 77.85141903171953, 77.8347245409015, 77.81803005008348, 77.80133555926544, 77.78464106844741, 77.76794657762939, 77.75125208681135, 77.73455759599332, 77.7178631051753, 77.70116861435726, 77.68447412353923, 77.6677796327212, 77.65108514190317, 77.63439065108514, 77.61769616026712, 77.60100166944909, 77.58430717863105, 77.56761268781302, 77.55091819699499, 77.53422370617696, 77.51752921535893, 77.50083472454091, 77.48414023372287, 77.46744574290484, 77.45075125208682, 77.43405676126878, 77.41736227045075, 77.40066777963273, 77.38397328881469, 77.36727879799666, 77.35058430717864, 77.3338898163606, 77.31719532554257, 77.30050083472455, 77.2838063439065, 77.26711185308848, 77.25041736227045, 77.23372287145241, 77.21702838063439, 77.20033388981636, 77.18363939899834, 77.1669449081803, 77.15025041736227, 77.13355592654425, 77.11686143572621, 77.10016694490818, 77.08347245409016, 77.06677796327212, 77.05008347245409, 77.03338898163607, 77.01669449081803, 77.0])
        detectors = [SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}', name='pil900KW', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
        per_step = <function one_1d_step_withwait at 0x7f2cc0a76320>

File ~/src/bluesky/src/bluesky/plans.py:1168, in scan_nd(detectors=[SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M..., 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}',..., 'stats1.profile_size', 'stats1.ts_num_points'])], cycler=cycler(ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100...409, 77.03338898163607, 77.01669449081803, 77.0]), per_step=<function scan_nd.<locals>.adapter>, md={'hints': {'dimensions': [(['thorlabs_su_readback'], 'primary')]}, 'motors': ('thorlabs_su',), 'plan_args': {'args': ["ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}...e'], configuration_attrs=[], limits=None, egu='')", 87, 77], 'detectors': ["SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M..., 'stats1.profile_size', 'stats1.ts_num_points'])", "WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}',..., 'stats1.profile_size', 'stats1.ts_num_points'])"], 'num': 600, 'per_step': '<function one_1d_step_withwait at 0x7f2cc0a76320>'}, 'plan_name': 'scan', 'plan_pattern': 'inner_product', 'plan_pattern_args': {'args': ["ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}...e'], configuration_attrs=[], limits=None, egu='')", 87, 77], 'num': 600}, 'plan_pattern_module': 'bluesky.plan_patterns'})
   1165     for step in list(cycler):
   1166         yield from per_step(detectors, step, pos_cache)
-> 1168 return (yield from inner_scan_nd())

File ~/src/bluesky/src/bluesky/utils/__init__.py:1279, in make_decorator.<locals>.dec_outer.<locals>.dec.<locals>.dec_inner(*inner_args=(), **inner_kwargs={})
   1277 plan = gen_func(*inner_args, **inner_kwargs)
   1278 plan = wrapper(plan, *args, **kwargs)
-> 1279 return (yield from plan)
        plan = <generator object stage_wrapper at 0x7f2c88ea6960>

File ~/src/bluesky/src/bluesky/preprocessors.py:1013, in stage_wrapper(plan=<generator object scan_nd.<locals>.inner_scan_nd>, devices=[SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M..., 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}',..., 'stats1.profile_size', 'stats1.ts_num_points']), ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}...e'], configuration_attrs=[], limits=None, egu='')])
   1010     yield from stage_devices()
   1011     return (yield from plan)
-> 1013 return (yield from finalize_wrapper(inner(), unstage_devices()))

File ~/src/bluesky/src/bluesky/preprocessors.py:548, in finalize_wrapper(plan=<generator object stage_wrapper.<locals>.inner>, final_plan=<generator object stage_wrapper.<locals>.unstage_devices>, pause_for_debug=False)
    546 cleanup = True
    547 try:
--> 548     ret = yield from plan
        plan = <generator object stage_wrapper.<locals>.inner at 0x7f2ce33f4a50>
    549 except GeneratorExit:
    550     cleanup = False

File ~/src/bluesky/src/bluesky/preprocessors.py:1011, in stage_wrapper.<locals>.inner()
   1009 def inner():
   1010     yield from stage_devices()
-> 1011     return (yield from plan)
        plan = <generator object scan_nd.<locals>.inner_scan_nd at 0x7f2ca8265f50>

File ~/src/bluesky/src/bluesky/utils/__init__.py:1279, in make_decorator.<locals>.dec_outer.<locals>.dec.<locals>.dec_inner(*inner_args=(), **inner_kwargs={})
   1277 plan = gen_func(*inner_args, **inner_kwargs)
   1278 plan = wrapper(plan, *args, **kwargs)
-> 1279 return (yield from plan)
        plan = <generator object run_wrapper at 0x7f2ce05382e0>

File ~/src/bluesky/src/bluesky/preprocessors.py:370, in run_wrapper(plan=<generator object scan_nd.<locals>.inner_scan_nd>, md={'detectors': ['pil2M', 'pil900KW'], 'hints': {'dimensions': [(['thorlabs_su_readback'], 'primary')]}, 'motors': ('thorlabs_su',), 'num_intervals': 599, 'num_points': 600, 'plan_args': {'args': ["ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}...e'], configuration_attrs=[], limits=None, egu='')", 87, 77], 'detectors': ["SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M..., 'stats1.profile_size', 'stats1.ts_num_points'])", "WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}',..., 'stats1.profile_size', 'stats1.ts_num_points'])"], 'num': 600, 'per_step': '<function one_1d_step_withwait at 0x7f2cc0a76320>'}, 'plan_name': 'scan', 'plan_pattern': 'inner_product', 'plan_pattern_args': {'args': ["ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}...e'], configuration_attrs=[], limits=None, egu='')", 87, 77], 'num': 600}, 'plan_pattern_module': 'bluesky.plan_patterns'})
    367     else:
    368         yield from close_run(exit_status="fail", reason=str(e))
--> 370 yield from contingency_wrapper(plan, except_plan=except_plan, else_plan=close_run)
        plan = <generator object scan_nd.<locals>.inner_scan_nd at 0x7f2ce05384a0>
    371 return rs_uid

File ~/src/bluesky/src/bluesky/preprocessors.py:622, in contingency_wrapper(plan=<generator object scan_nd.<locals>.inner_scan_nd>, except_plan=<function run_wrapper.<locals>.except_plan>, else_plan=<function close_run>, final_plan=None, pause_for_debug=False, auto_raise=True)
    620 cleanup = True
    621 try:
--> 622     ret = yield from plan
        ret = None
        plan = <generator object scan_nd.<locals>.inner_scan_nd at 0x7f2ce05384a0>
    623 except GeneratorExit:
    624     cleanup = False

File ~/src/bluesky/src/bluesky/plans.py:1166, in scan_nd.<locals>.inner_scan_nd()
   1164     yield from bps.declare_stream(*motors, *detectors, name="primary")
   1165 for step in list(cycler):
-> 1166     yield from per_step(detectors, step, pos_cache)
        step = {ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}Mtr', name='thorlabs_su', settle_time=0.0, timeout=None, read_attrs=['readback', 'setpoint', 'done'], configuration_attrs=[], limits=None, egu=''): 85.74791318864774}
        detectors = [SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}', name='pil900KW', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
        per_step = <function scan_nd.<locals>.adapter at 0x7f2c71063490>
        pos_cache = defaultdict(<function scan_nd.<locals>.<lambda> at 0x7f2c71060040>, {})

File ~/src/bluesky/src/bluesky/plans.py:1146, in scan_nd.<locals>.adapter(detectors=[SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M..., 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}',..., 'stats1.profile_size', 'stats1.ts_num_points'])], step=85.74791318864774, pos_cache=defaultdict(<function scan_nd.<locals>.<lambda> at 0x7f2c71060040>, {}))
   1142 def adapter(detectors, step, pos_cache):
   1143     # one_nd_step 'step' parameter is a dict; one_id_step 'step'
   1144     # parameter is a value
   1145     (step,) = step.values()
-> 1146     return (yield from user_per_step(detectors, motor, step))
        step = 85.74791318864774
        user_per_step = <function one_1d_step_withwait at 0x7f2cc0a76320>
        detectors = [SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}', name='pil900KW', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
        motor = ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}Mtr', name='thorlabs_su', settle_time=0.0, timeout=None, read_attrs=['readback', 'setpoint', 'done'], configuration_attrs=[], limits=None, egu='')

File ~/SWAXS_user_scripts/LBL/bladecoating.py:174, in one_1d_step_withwait(detectors=[SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M..., 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}',..., 'stats1.profile_size', 'stats1.ts_num_points'])], motor=ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}...e'], configuration_attrs=[], limits=None, egu=''), step=85.74791318864774, take_reading=<function trigger_and_read>)
    172 yield from move()
    173 yield from bps.sleep(1)
--> 174 return (yield from take_reading(list(detectors) + [motor]))
        take_reading = <function trigger_and_read at 0x7f2e18a8ff40>
        list(detectors) + [motor] = [SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}', name='pil900KW', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}Mtr', name='thorlabs_su', settle_time=0.0, timeout=None, read_attrs=['readback', 'setpoint', 'done'], configuration_attrs=[], limits=None, egu='')]
        motor = ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}Mtr', name='thorlabs_su', settle_time=0.0, timeout=None, read_attrs=['readback', 'setpoint', 'done'], configuration_attrs=[], limits=None, egu='')
        list(detectors) = [SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}', name='pil900KW', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
        [motor] = [ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}Mtr', name='thorlabs_su', settle_time=0.0, timeout=None, read_attrs=['readback', 'setpoint', 'done'], configuration_attrs=[], limits=None, egu='')]
        detectors = [SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}', name='pil900KW', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]

File ~/src/bluesky/src/bluesky/utils/__init__.py:1975, in Plan.__iter__(self=<bluesky.utils.Plan object>)
   1973 def __iter__(self):
   1974     self._stack = None
-> 1975     return (yield from self._iter)
        self = <bluesky.utils.Plan object at 0x7f2c41b60be0>
        self._iter = <generator object trigger_and_read at 0x7f2ce04b2ab0>

File ~/src/bluesky/src/bluesky/plan_stubs.py:1476, in trigger_and_read(devices=[SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M..., 'stats1.profile_size', 'stats1.ts_num_points']), WAXS_Detector(prefix='XF:12IDC-ES:2{Det:900KW}',..., 'stats1.profile_size', 'stats1.ts_num_points']), ThorlabsMotor(prefix='XF:12ID2-ES{DDSM100-Ax:X1}...e'], configuration_attrs=[], limits=None, egu='')], name='primary')
   1472     return ret
   1474 from .preprocessors import rewindable_wrapper
-> 1476 return (yield from rewindable_wrapper(inner_trigger_and_read(), rewindable))
        rewindable = True

File ~/src/bluesky/src/bluesky/preprocessors.py:749, in rewindable_wrapper(plan=<generator object trigger_and_read.<locals>.inner_trigger_and_read>, rewindable=True)
    747     return (yield from finalize_wrapper(plan, restore_rewindable()))
    748 else:
--> 749     return (yield from plan)
        plan = <generator object trigger_and_read.<locals>.inner_trigger_and_read at 0x7f2cc091db60>

File ~/src/bluesky/src/bluesky/plan_stubs.py:1471, in trigger_and_read.<locals>.inner_trigger_and_read()
   1468     yield from drop()
   1469     raise exp
-> 1471 ret = yield from contingency_wrapper(read_plan(), except_plan=exception_path, else_plan=standard_path)
   1472 return ret

File ~/src/bluesky/src/bluesky/preprocessors.py:641, in contingency_wrapper(plan=<generator object trigger_and_read.<locals>.inner_trigger_and_read.<locals>.read_plan>, except_plan=<function trigger_and_read.<locals>.inner_trigger_and_read.<locals>.exception_path>, else_plan=<function trigger_and_read.<locals>.inner_trigger_and_read.<locals>.standard_path>, final_plan=None, pause_for_debug=False, auto_raise=True)
    639 else:
    640     if else_plan:
--> 641         yield from else_plan()
        else_plan = <function trigger_and_read.<locals>.inner_trigger_and_read.<locals>.standard_path at 0x7f2c41a74a60>
    642 finally:
    643     # if the exception raised in `GeneratorExit` that means
    644     # someone called `gen.close()` on this generator.  In those
   (...)
    650 
    651     # https://docs.python.org/3/reference/expressions.html?#generator.close
    652     if cleanup and final_plan:

File ~/src/bluesky/src/bluesky/plan_stubs.py:1465, in trigger_and_read.<locals>.inner_trigger_and_read.<locals>.standard_path()
   1464 def standard_path():
-> 1465     yield from save()

File ~/src/bluesky/src/bluesky/utils/__init__.py:1975, in Plan.__iter__(self=<bluesky.utils.Plan object>)
   1973 def __iter__(self):
   1974     self._stack = None
-> 1975     return (yield from self._iter)
        self = <bluesky.utils.Plan object at 0x7f2ca97c94e0>
        self._iter = <generator object save at 0x7f2ce0635620>

File ~/src/bluesky/src/bluesky/plan_stubs.py:128, in save()
    114 @plan
    115 def save() -> MsgGenerator:
    116     """
    117     Close a bundle of readings and emit a completed Event document.
    118 
   (...)
    126     :func:`bluesky.plan_stubs.create`
    127     """
--> 128     return (yield Msg("save"))

File ~/src/bluesky/src/bluesky/preprocessors.py:213, in plan_mutator(plan=<generator object blade_coating_2025_1_slowexp_withmotion_Kelvin>, msg_proc=<function fly_during_wrapper.<locals>.insert_after_open>)
    209         continue
    211 try:
    212     # yield out the 'current message' and collect the return
--> 213     inner_ret = yield msg
        msg = Msg('unstage', obj=SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), args=(), kwargs={}, run=None)
        inner_ret = [SAXSBeamStops(prefix='XF:12IDC-ES:2{BS:SAXS-Ax:', name='pil2M_beamstop', parent='pil2M', read_attrs=['x_rod', 'x_rod.user_readback', 'x_rod.user_setpoint', 'y_rod', 'y_rod.user_readback', 'y_rod.user_setpoint', 'x_pin', 'x_pin.user_readback', 'x_pin.user_setpoint', 'y_pin', 'y_pin.user_readback', 'y_pin.user_setpoint'], configuration_attrs=['x_rod', 'x_rod.user_offset', 'x_rod.user_offset_dir', 'x_rod.velocity', 'x_rod.acceleration', 'x_rod.motor_egu', 'y_rod', 'y_rod.user_offset', 'y_rod.user_offset_dir', 'y_rod.velocity', 'y_rod.acceleration', 'y_rod.motor_egu', 'x_pin', 'x_pin.user_offset', 'x_pin.user_offset_dir', 'x_pin.velocity', 'x_pin.acceleration', 'x_pin.motor_egu', 'y_pin', 'y_pin.user_offset', 'y_pin.user_offset_dir', 'y_pin.velocity', 'y_pin.acceleration', 'y_pin.motor_egu']), DetMotor(prefix='XF:12IDC-ES:2{Det:1M-Ax:', name='pil2M_motor', parent='pil2M', read_attrs=['x', 'x.user_readback', 'x.user_setpoint', 'y', 'y.user_readback', 'y.user_setpoint', 'z', 'z.user_readback', 'z.user_setpoint'], configuration_attrs=['x', 'x.user_offset', 'x.user_offset_dir', 'x.velocity', 'x.acceleration', 'x.motor_egu', 'y', 'y.user_offset', 'y.user_offset_dir', 'y.velocity', 'y.acceleration', 'y.motor_egu', 'z', 'z.user_offset', 'z.user_offset_dir', 'z.velocity', 'z.acceleration', 'z.motor_egu']), TransformPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Trans1:', name='pil2M_trans1', parent='pil2M', read_attrs=[], configuration_attrs=[]), OverlayPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Over1:', name='pil2M_over1', parent='pil2M', read_attrs=[], configuration_attrs=[]), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats5:', name='pil2M_stats5', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats4:', name='pil2M_stats4', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats3:', name='pil2M_stats3', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats2:', name='pil2M_stats2', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats1:', name='pil2M_stats1', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI4:', name='pil2M_roi4', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI3:', name='pil2M_roi3', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI2:', name='pil2M_roi2', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI1:', name='pil2M_roi1', parent='pil2M', read_attrs=[], configuration_attrs=[]), TIFFPluginWithFileStore(prefix='XF:12ID2-ES{Pilatus:Det-2M}TIFF1:', name='pil2M_tiff', parent='pil2M', read_attrs=[], configuration_attrs=[]), PilatusDetectorCamV33(prefix='XF:12ID2-ES{Pilatus:Det-2M}cam1:', name='pil2M_cam', parent='pil2M', read_attrs=['file_number'], configuration_attrs=['acquire_period', 'acquire_time', 'image_mode', 'manufacturer', 'model', 'num_exposures', 'num_images', 'trigger_mode']), SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
    214 except GeneratorExit:
    215     # special case GeneratorExit.  We must clean up all of our plans
    216     # and exit with out yielding anything else.
    217     for p in plan_stack:

File ~/src/bluesky/src/bluesky/preprocessors.py:213, in plan_mutator(plan=<generator object plan_mutator>, msg_proc=<function fly_during_wrapper.<locals>.insert_before_close>)
    209         continue
    211 try:
    212     # yield out the 'current message' and collect the return
--> 213     inner_ret = yield msg
        msg = Msg('unstage', obj=SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), args=(), kwargs={}, run=None)
        inner_ret = [SAXSBeamStops(prefix='XF:12IDC-ES:2{BS:SAXS-Ax:', name='pil2M_beamstop', parent='pil2M', read_attrs=['x_rod', 'x_rod.user_readback', 'x_rod.user_setpoint', 'y_rod', 'y_rod.user_readback', 'y_rod.user_setpoint', 'x_pin', 'x_pin.user_readback', 'x_pin.user_setpoint', 'y_pin', 'y_pin.user_readback', 'y_pin.user_setpoint'], configuration_attrs=['x_rod', 'x_rod.user_offset', 'x_rod.user_offset_dir', 'x_rod.velocity', 'x_rod.acceleration', 'x_rod.motor_egu', 'y_rod', 'y_rod.user_offset', 'y_rod.user_offset_dir', 'y_rod.velocity', 'y_rod.acceleration', 'y_rod.motor_egu', 'x_pin', 'x_pin.user_offset', 'x_pin.user_offset_dir', 'x_pin.velocity', 'x_pin.acceleration', 'x_pin.motor_egu', 'y_pin', 'y_pin.user_offset', 'y_pin.user_offset_dir', 'y_pin.velocity', 'y_pin.acceleration', 'y_pin.motor_egu']), DetMotor(prefix='XF:12IDC-ES:2{Det:1M-Ax:', name='pil2M_motor', parent='pil2M', read_attrs=['x', 'x.user_readback', 'x.user_setpoint', 'y', 'y.user_readback', 'y.user_setpoint', 'z', 'z.user_readback', 'z.user_setpoint'], configuration_attrs=['x', 'x.user_offset', 'x.user_offset_dir', 'x.velocity', 'x.acceleration', 'x.motor_egu', 'y', 'y.user_offset', 'y.user_offset_dir', 'y.velocity', 'y.acceleration', 'y.motor_egu', 'z', 'z.user_offset', 'z.user_offset_dir', 'z.velocity', 'z.acceleration', 'z.motor_egu']), TransformPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Trans1:', name='pil2M_trans1', parent='pil2M', read_attrs=[], configuration_attrs=[]), OverlayPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Over1:', name='pil2M_over1', parent='pil2M', read_attrs=[], configuration_attrs=[]), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats5:', name='pil2M_stats5', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats4:', name='pil2M_stats4', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats3:', name='pil2M_stats3', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats2:', name='pil2M_stats2', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats1:', name='pil2M_stats1', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI4:', name='pil2M_roi4', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI3:', name='pil2M_roi3', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI2:', name='pil2M_roi2', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI1:', name='pil2M_roi1', parent='pil2M', read_attrs=[], configuration_attrs=[]), TIFFPluginWithFileStore(prefix='XF:12ID2-ES{Pilatus:Det-2M}TIFF1:', name='pil2M_tiff', parent='pil2M', read_attrs=[], configuration_attrs=[]), PilatusDetectorCamV33(prefix='XF:12ID2-ES{Pilatus:Det-2M}cam1:', name='pil2M_cam', parent='pil2M', read_attrs=['file_number'], configuration_attrs=['acquire_period', 'acquire_time', 'image_mode', 'manufacturer', 'model', 'num_exposures', 'num_images', 'trigger_mode']), SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
    214 except GeneratorExit:
    215     # special case GeneratorExit.  We must clean up all of our plans
    216     # and exit with out yielding anything else.
    217     for p in plan_stack:

    [... skipping similar frames: plan_mutator at line 213 (2 times)]

File ~/src/bluesky/src/bluesky/preprocessors.py:213, in plan_mutator(plan=<generator object monitor_during_wrapper>, msg_proc=<function baseline_wrapper.<locals>.insert_baseline>)
    209         continue
    211 try:
    212     # yield out the 'current message' and collect the return
--> 213     inner_ret = yield msg
        msg = Msg('unstage', obj=SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), args=(), kwargs={}, run=None)
        inner_ret = [SAXSBeamStops(prefix='XF:12IDC-ES:2{BS:SAXS-Ax:', name='pil2M_beamstop', parent='pil2M', read_attrs=['x_rod', 'x_rod.user_readback', 'x_rod.user_setpoint', 'y_rod', 'y_rod.user_readback', 'y_rod.user_setpoint', 'x_pin', 'x_pin.user_readback', 'x_pin.user_setpoint', 'y_pin', 'y_pin.user_readback', 'y_pin.user_setpoint'], configuration_attrs=['x_rod', 'x_rod.user_offset', 'x_rod.user_offset_dir', 'x_rod.velocity', 'x_rod.acceleration', 'x_rod.motor_egu', 'y_rod', 'y_rod.user_offset', 'y_rod.user_offset_dir', 'y_rod.velocity', 'y_rod.acceleration', 'y_rod.motor_egu', 'x_pin', 'x_pin.user_offset', 'x_pin.user_offset_dir', 'x_pin.velocity', 'x_pin.acceleration', 'x_pin.motor_egu', 'y_pin', 'y_pin.user_offset', 'y_pin.user_offset_dir', 'y_pin.velocity', 'y_pin.acceleration', 'y_pin.motor_egu']), DetMotor(prefix='XF:12IDC-ES:2{Det:1M-Ax:', name='pil2M_motor', parent='pil2M', read_attrs=['x', 'x.user_readback', 'x.user_setpoint', 'y', 'y.user_readback', 'y.user_setpoint', 'z', 'z.user_readback', 'z.user_setpoint'], configuration_attrs=['x', 'x.user_offset', 'x.user_offset_dir', 'x.velocity', 'x.acceleration', 'x.motor_egu', 'y', 'y.user_offset', 'y.user_offset_dir', 'y.velocity', 'y.acceleration', 'y.motor_egu', 'z', 'z.user_offset', 'z.user_offset_dir', 'z.velocity', 'z.acceleration', 'z.motor_egu']), TransformPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Trans1:', name='pil2M_trans1', parent='pil2M', read_attrs=[], configuration_attrs=[]), OverlayPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}Over1:', name='pil2M_over1', parent='pil2M', read_attrs=[], configuration_attrs=[]), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats5:', name='pil2M_stats5', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats4:', name='pil2M_stats4', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats3:', name='pil2M_stats3', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats2:', name='pil2M_stats2', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), StatsWCentroid(prefix='XF:12ID2-ES{Pilatus:Det-2M}Stats1:', name='pil2M_stats1', parent='pil2M', read_attrs=['total'], configuration_attrs=['bgd_width', 'centroid_threshold', 'compute_centroid', 'compute_histogram', 'compute_profiles', 'compute_statistics', 'hist_max', 'hist_min', 'hist_size', 'profile_cursor', 'profile_size', 'ts_num_points']), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI4:', name='pil2M_roi4', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI3:', name='pil2M_roi3', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI2:', name='pil2M_roi2', parent='pil2M', read_attrs=[], configuration_attrs=[]), ROIPlugin(prefix='XF:12ID2-ES{Pilatus:Det-2M}ROI1:', name='pil2M_roi1', parent='pil2M', read_attrs=[], configuration_attrs=[]), TIFFPluginWithFileStore(prefix='XF:12ID2-ES{Pilatus:Det-2M}TIFF1:', name='pil2M_tiff', parent='pil2M', read_attrs=[], configuration_attrs=[]), PilatusDetectorCamV33(prefix='XF:12ID2-ES{Pilatus:Det-2M}cam1:', name='pil2M_cam', parent='pil2M', read_attrs=['file_number'], configuration_attrs=['acquire_period', 'acquire_time', 'image_mode', 'manufacturer', 'model', 'num_exposures', 'num_images', 'trigger_mode']), SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points'])]
    214 except GeneratorExit:
    215     # special case GeneratorExit.  We must clean up all of our plans
    216     # and exit with out yielding anything else.
    217     for p in plan_stack:

File ~/src/bluesky/src/bluesky/run_engine.py:1677, in RunEngine._run(self=<bluesky.run_engine.RunEngine object>)
   1672 # try to finally run the command the user asked for
   1673 try:
   1674     # this is one of two places that 'async'
   1675     # exceptions (coming in via throw) can be
   1676     # raised
-> 1677     new_response = await coro(msg)
        new_response = None
        msg = Msg('unstage', obj=SAXS_Detector(prefix='XF:12ID2-ES{Pilatus:Det-2M}', name='pil2M', read_attrs=['cam', 'cam.file_number', 'tiff', 'stats1', 'stats1.total'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'tiff', 'stats1', 'stats1.bgd_width', 'stats1.centroid_threshold', 'stats1.compute_centroid', 'stats1.compute_histogram', 'stats1.compute_profiles', 'stats1.compute_statistics', 'stats1.hist_max', 'stats1.hist_min', 'stats1.hist_size', 'stats1.profile_cursor', 'stats1.profile_size', 'stats1.ts_num_points']), args=(), kwargs={}, run=None)
        coro = <bound method RunEngine._unstage of <bluesky.run_engine.RunEngine object at 0x7f2e18723310>>
   1679 # special case `CancelledError` and let the outer
   1680 # exception block deal with it.
   1681 except asyncio.CancelledError:

File ~/src/bluesky/src/bluesky/run_engine.py:2077, in RunEngine._save(self=<bluesky.run_engine.RunEngine object>, msg=Msg('save', obj=None, args=(), kwargs={}, run=None))
   2075     raise IllegalMessageSequence(ims_msg)
   2076 else:
-> 2077     await current_run.save(msg)
        msg = Msg('save', obj=None, args=(), kwargs={}, run=None)
        current_run = <bluesky.bundlers.RunBundler object at 0x7f2ca9796d70>

File ~/src/bluesky/src/bluesky/bundlers.py:598, in RunBundler.save(self=<bluesky.bundlers.RunBundler object>, msg=Msg('save', obj=None, args=(), kwargs={}, run=None))
    588 filled = {
    589     k: False
    590     for k, v in self._descriptors[desc_key].descriptor_doc["data_keys"].items()
    591     if "external" in v and v["external"] != "STREAM:"
    592 }
    593 event_doc = compose_event(
    594     data=data,
    595     timestamps=timestamps,
    596     filled=filled,
    597 )
--> 598 await self.emit(DocumentNames.event, event_doc)
        event_doc = {'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}, 'seq_num': 76, 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db'}
        self = <bluesky.bundlers.RunBundler object at 0x7f2ca9796d70>
        DocumentNames.event = <DocumentNames.event: 'event'>
    599 doc_logger.debug(
    600     "[event] document emitted with data keys %r (run_uid=%r)",
    601     data.keys(),
    602     self._run_start_uid,
    603     extra={"doc_name": "event", "run_uid": self._run_start_uid, "data_keys": data.keys()},
    604 )

File ~/src/bluesky/src/bluesky/run_engine.py:2680, in RunEngine.emit(self=<bluesky.run_engine.RunEngine object>, name=<DocumentNames.event: 'event'>, doc={'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'})
   2679 async def emit(self, name, doc):
-> 2680     self.emit_sync(name, doc)
        name = <DocumentNames.event: 'event'>
        doc = {'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}, 'seq_num': 76, 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db'}
        self = <bluesky.run_engine.RunEngine object at 0x7f2e18723310>

File ~/src/bluesky/src/bluesky/run_engine.py:2677, in RunEngine.emit_sync(self=<bluesky.run_engine.RunEngine object>, name=<DocumentNames.event: 'event'>, doc={'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'})
   2674 "Process blocking callbacks and schedule non-blocking callbacks."
   2676 # Process the doc, already validated against the schema in event-model
-> 2677 self.dispatcher.process(name, doc)
        name = <DocumentNames.event: 'event'>
        doc = {'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}, 'seq_num': 76, 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db'}
        self.dispatcher = <bluesky.run_engine.Dispatcher object at 0x7f2dfd437d00>
        self = <bluesky.run_engine.RunEngine object at 0x7f2e18723310>

File ~/src/bluesky/src/bluesky/run_engine.py:2700, in Dispatcher.process(self=<bluesky.run_engine.Dispatcher object>, name=<DocumentNames.event: 'event'>, doc={'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'})
   2691 def process(self, name, doc):
   2692     """
   2693     Dispatch document ``doc`` of type ``name`` to the callback registry.
   2694 
   (...)
   2698     doc : dict
   2699     """
-> 2700     exceptions = self.cb_registry.process(name, name.name, doc)
        name = <DocumentNames.event: 'event'>
        doc = {'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}, 'seq_num': 76, 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db'}
        self.cb_registry = <bluesky.utils.CallbackRegistry object at 0x7f2dfd0b7c40>
        self = <bluesky.run_engine.Dispatcher object at 0x7f2dfd437d00>
   2701     for exc, traceback in exceptions:  # noqa: B007
   2702         warn(  # noqa: B028
   2703             "A %r was raised during the processing of a %s "  # noqa: UP031
   2704             "Document. The error will be ignored to avoid "
   (...)
   2707             "and run again." % (exc, name.name)
   2708         )

File ~/src/bluesky/src/bluesky/utils/__init__.py:443, in CallbackRegistry.process(self=<bluesky.utils.CallbackRegistry object>, sig=<DocumentNames.event: 'event'>, *args=('event', {'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'}), **kwargs={})
    441 for cid, func in list(self.callbacks[sig].items()):  # noqa: B007
    442     try:
--> 443         func(*args, **kwargs)
        func = <bluesky.utils._BoundMethodProxy object at 0x7f2daef698a0>
        args = ('event', {'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}, 'seq_num': 76, 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db'})
        kwargs = {}
    444     except ReferenceError:
    445         self._remove_proxy(func)

File ~/src/bluesky/src/bluesky/utils/__init__.py:533, in _BoundMethodProxy.__call__(self=<bluesky.utils._BoundMethodProxy object>, *args=('event', {'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'}), **kwargs={})
    531     mtd = self.func
    532 # invoke the callable and return the result
--> 533 return mtd(*args, **kwargs)
        mtd = <bluesky.callbacks.tiled_writer.TiledWriter object at 0x7f2daef68940>
        args = ('event', {'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}, 'seq_num': 76, 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db'})
        kwargs = {}

File ~/src/bluesky/src/bluesky/callbacks/tiled_writer.py:844, in TiledWriter.__call__(self=<bluesky.callbacks.tiled_writer.TiledWriter object>, name='event', doc={'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'})
    843 def __call__(self, name, doc):
--> 844     self._run_router(name, doc)
        self._run_router = RunRouter([
    <bound method TiledWriter._factory of <bluesky.callbacks.tiled_writer.TiledWriter object at 0x7f2daef68940>>])
        name = 'event'
        doc = {'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}, 'seq_num': 76, 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db'}
        self = <bluesky.callbacks.tiled_writer.TiledWriter object at 0x7f2daef68940>

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/event_model/__init__.py:191, in DocumentRouter.__call__(self=RunRouter([
    <bound method TiledWriter._facto...d_writer.TiledWriter object at 0x7f2daef68940>>]), name='event', doc={'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'}, validate=False)
    171 def __call__(
    172     self, name: str, doc: dict, validate: bool = False
    173 ) -> Tuple[str, dict]:
    174     """
    175     Process a document.
    176 
   (...)
    189         instance as doc, a copy of doc, or a different dict altogether.
    190     """
--> 191     return self._dispatch(name, doc, validate)
        name = 'event'
        doc = {'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}, 'seq_num': 76, 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db'}
        validate = False
        self = RunRouter([
    <bound method TiledWriter._factory of <bluesky.callbacks.tiled_writer.TiledWriter object at 0x7f2daef68940>>])

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/event_model/__init__.py:208, in DocumentRouter._dispatch(self=RunRouter([
    <bound method TiledWriter._facto...d_writer.TiledWriter object at 0x7f2daef68940>>]), name='event', doc={'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': False, 'pil900KW_image': False}, 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'}, validate=False)
    205 event_page = pack_event_page(cast(Event, doc))
    206 # Subclass' implementation of event_page may return a valid
    207 # EventPage or None or NotImplemented.
--> 208 output_event_page = self.event_page(event_page)
        self = RunRouter([
    <bound method TiledWriter._factory of <bluesky.callbacks.tiled_writer.TiledWriter object at 0x7f2daef68940>>])
        event_page = {'time': [1753707382.8083541], 'uid': ['01147161-5529-4a45-bf6f-732ee86f9fd1'], 'seq_num': [76], 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': [False], 'pil900KW_image': [False]}, 'data': {'pil2M_cam_file_number': [76], 'pil2M_image': ['17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75'], 'pil2M_stats1_total': [42347.0], 'pil900KW_cam_file_number': [76], 'pil900KW_image': ['cfa921ac-3de2-464c-a3df-6b4cbb086353/75'], 'pil900KW_stats1_total': [3601366.0], 'thorlabs_su_readback': [85.748], 'thorlabs_su_setpoint': [85.74791318864774], 'thorlabs_su_done': [1]}, 'timestamps': {'pil2M_cam_file_number': [1753707381.738371], 'pil2M_image': [1753707381.6910598], 'pil2M_stats1_total': [1753707382.404384], 'pil900KW_cam_file_number': [1753707381.739924], 'pil900KW_image': [1753707381.6923807], 'pil900KW_stats1_total': [1753707382.649849], 'thorlabs_su_readback': [1753707380.83863], 'thorlabs_su_setpoint': [1753707380.83863], 'thorlabs_su_done': [1753707380.687973]}}
    209 output_event_page = (
    210     output_event_page if output_event_page is not None else event_page
    211 )
    212 if output_event_page is not NotImplemented:

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/event_model/__init__.py:1644, in RunRouter.event_page(self=RunRouter([
    <bound method TiledWriter._facto...d_writer.TiledWriter object at 0x7f2daef68940>>]), doc={'data': {'pil2M_cam_file_number': [76], 'pil2M_image': ['17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75'], 'pil2M_stats1_total': [42347.0], 'pil900KW_cam_file_number': [76], 'pil900KW_image': ['cfa921ac-3de2-464c-a3df-6b4cbb086353/75'], 'pil900KW_stats1_total': [3601366.0], 'thorlabs_su_done': [1], 'thorlabs_su_readback': [85.748], 'thorlabs_su_setpoint': [85.74791318864774]}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': [False], 'pil900KW_image': [False]}, 'seq_num': [76], 'time': [1753707382.8083541], 'timestamps': {'pil2M_cam_file_number': [1753707381.738371], 'pil2M_image': [1753707381.6910598], 'pil2M_stats1_total': [1753707382.404384], 'pil900KW_cam_file_number': [1753707381.739924], 'pil900KW_image': [1753707381.6923807], 'pil900KW_stats1_total': [1753707382.649849], 'thorlabs_su_done': [1753707380.687973], 'thorlabs_su_readback': [1753707380.83863], 'thorlabs_su_setpoint': [1753707380.83863]}, 'uid': ['01147161-5529-4a45-bf6f-732ee86f9fd1']})
   1642         raise
   1643 for callback in self._factory_cbs_by_descriptor[descriptor_uid]:
-> 1644     callback("event_page", doc)
        callback = <bluesky.callbacks.tiled_writer.RunNormalizer object at 0x7f2c41b62260>
        doc = {'time': [1753707382.8083541], 'uid': ['01147161-5529-4a45-bf6f-732ee86f9fd1'], 'seq_num': [76], 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': [False], 'pil900KW_image': [False]}, 'data': {'pil2M_cam_file_number': [76], 'pil2M_image': ['17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75'], 'pil2M_stats1_total': [42347.0], 'pil900KW_cam_file_number': [76], 'pil900KW_image': ['cfa921ac-3de2-464c-a3df-6b4cbb086353/75'], 'pil900KW_stats1_total': [3601366.0], 'thorlabs_su_readback': [85.748], 'thorlabs_su_setpoint': [85.74791318864774], 'thorlabs_su_done': [1]}, 'timestamps': {'pil2M_cam_file_number': [1753707381.738371], 'pil2M_image': [1753707381.6910598], 'pil2M_stats1_total': [1753707382.404384], 'pil900KW_cam_file_number': [1753707381.739924], 'pil900KW_image': [1753707381.6923807], 'pil900KW_stats1_total': [1753707382.649849], 'thorlabs_su_readback': [1753707380.83863], 'thorlabs_su_setpoint': [1753707380.83863], 'thorlabs_su_done': [1753707380.687973]}}
   1645 for callback in self._subfactory_cbs_by_descriptor[descriptor_uid]:
   1646     callback("event_page", doc)

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/event_model/__init__.py:191, in DocumentRouter.__call__(self=<bluesky.callbacks.tiled_writer.RunNormalizer object>, name='event_page', doc={'data': {'pil2M_cam_file_number': [76], 'pil2M_image': ['17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75'], 'pil2M_stats1_total': [42347.0], 'pil900KW_cam_file_number': [76], 'pil900KW_image': ['cfa921ac-3de2-464c-a3df-6b4cbb086353/75'], 'pil900KW_stats1_total': [3601366.0], 'thorlabs_su_done': [1], 'thorlabs_su_readback': [85.748], 'thorlabs_su_setpoint': [85.74791318864774]}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': [False], 'pil900KW_image': [False]}, 'seq_num': [76], 'time': [1753707382.8083541], 'timestamps': {'pil2M_cam_file_number': [1753707381.738371], 'pil2M_image': [1753707381.6910598], 'pil2M_stats1_total': [1753707382.404384], 'pil900KW_cam_file_number': [1753707381.739924], 'pil900KW_image': [1753707381.6923807], 'pil900KW_stats1_total': [1753707382.649849], 'thorlabs_su_done': [1753707380.687973], 'thorlabs_su_readback': [1753707380.83863], 'thorlabs_su_setpoint': [1753707380.83863]}, 'uid': ['01147161-5529-4a45-bf6f-732ee86f9fd1']}, validate=False)
    171 def __call__(
    172     self, name: str, doc: dict, validate: bool = False
    173 ) -> Tuple[str, dict]:
    174     """
    175     Process a document.
    176 
   (...)
    189         instance as doc, a copy of doc, or a different dict altogether.
    190     """
--> 191     return self._dispatch(name, doc, validate)
        name = 'event_page'
        doc = {'time': [1753707382.8083541], 'uid': ['01147161-5529-4a45-bf6f-732ee86f9fd1'], 'seq_num': [76], 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': [False], 'pil900KW_image': [False]}, 'data': {'pil2M_cam_file_number': [76], 'pil2M_image': ['17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75'], 'pil2M_stats1_total': [42347.0], 'pil900KW_cam_file_number': [76], 'pil900KW_image': ['cfa921ac-3de2-464c-a3df-6b4cbb086353/75'], 'pil900KW_stats1_total': [3601366.0], 'thorlabs_su_readback': [85.748], 'thorlabs_su_setpoint': [85.74791318864774], 'thorlabs_su_done': [1]}, 'timestamps': {'pil2M_cam_file_number': [1753707381.738371], 'pil2M_image': [1753707381.6910598], 'pil2M_stats1_total': [1753707382.404384], 'pil900KW_cam_file_number': [1753707381.739924], 'pil900KW_image': [1753707381.6923807], 'pil900KW_stats1_total': [1753707382.649849], 'thorlabs_su_readback': [1753707380.83863], 'thorlabs_su_setpoint': [1753707380.83863], 'thorlabs_su_done': [1753707380.687973]}}
        validate = False
        self = <bluesky.callbacks.tiled_writer.RunNormalizer object at 0x7f2c41b62260>

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/event_model/__init__.py:199, in DocumentRouter._dispatch(self=<bluesky.callbacks.tiled_writer.RunNormalizer object>, name='event_page', doc={'data': {'pil2M_cam_file_number': [76], 'pil2M_image': ['17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75'], 'pil2M_stats1_total': [42347.0], 'pil900KW_cam_file_number': [76], 'pil900KW_image': ['cfa921ac-3de2-464c-a3df-6b4cbb086353/75'], 'pil900KW_stats1_total': [3601366.0], 'thorlabs_su_done': [1], 'thorlabs_su_readback': [85.748], 'thorlabs_su_setpoint': [85.74791318864774]}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': [False], 'pil900KW_image': [False]}, 'seq_num': [76], 'time': [1753707382.8083541], 'timestamps': {'pil2M_cam_file_number': [1753707381.738371], 'pil2M_image': [1753707381.6910598], 'pil2M_stats1_total': [1753707382.404384], 'pil900KW_cam_file_number': [1753707381.739924], 'pil900KW_image': [1753707381.6923807], 'pil900KW_stats1_total': [1753707382.649849], 'thorlabs_su_done': [1753707380.687973], 'thorlabs_su_readback': [1753707380.83863], 'thorlabs_su_setpoint': [1753707380.83863]}, 'uid': ['01147161-5529-4a45-bf6f-732ee86f9fd1']}, validate=False)
    193 def _dispatch(self, name: str, doc: dict, validate: bool) -> Tuple[str, dict]:
    194     """
    195     Dispatch to the method corresponding to the `name`.
    196 
    197     Optionally validate that the result is still a valid document.
    198     """
--> 199     output_doc = getattr(self, name)(doc)
        doc = {'time': [1753707382.8083541], 'uid': ['01147161-5529-4a45-bf6f-732ee86f9fd1'], 'seq_num': [76], 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': [False], 'pil900KW_image': [False]}, 'data': {'pil2M_cam_file_number': [76], 'pil2M_image': ['17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75'], 'pil2M_stats1_total': [42347.0], 'pil900KW_cam_file_number': [76], 'pil900KW_image': ['cfa921ac-3de2-464c-a3df-6b4cbb086353/75'], 'pil900KW_stats1_total': [3601366.0], 'thorlabs_su_readback': [85.748], 'thorlabs_su_setpoint': [85.74791318864774], 'thorlabs_su_done': [1]}, 'timestamps': {'pil2M_cam_file_number': [1753707381.738371], 'pil2M_image': [1753707381.6910598], 'pil2M_stats1_total': [1753707382.404384], 'pil900KW_cam_file_number': [1753707381.739924], 'pil900KW_image': [1753707381.6923807], 'pil900KW_stats1_total': [1753707382.649849], 'thorlabs_su_readback': [1753707380.83863], 'thorlabs_su_setpoint': [1753707380.83863], 'thorlabs_su_done': [1753707380.687973]}}
        name = 'event_page'
        self = <bluesky.callbacks.tiled_writer.RunNormalizer object at 0x7f2c41b62260>
    201     # If 'event' is not defined by the subclass but 'event_page' is, or
    202     # vice versa, use that. And the same for 'datum_page' / 'datum.
    203     if output_doc is NotImplemented:

File ~/src/bluesky/src/bluesky/callbacks/tiled_writer.py:477, in RunNormalizer.event_page(self=<bluesky.callbacks.tiled_writer.RunNormalizer object>, doc={'data': {'pil2M_cam_file_number': [76], 'pil2M_image': ['17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75'], 'pil2M_stats1_total': [42347.0], 'pil900KW_cam_file_number': [76], 'pil900KW_image': ['cfa921ac-3de2-464c-a3df-6b4cbb086353/75'], 'pil900KW_stats1_total': [3601366.0], 'thorlabs_su_done': [1], 'thorlabs_su_readback': [85.748], 'thorlabs_su_setpoint': [85.74791318864774]}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'filled': {'pil2M_image': [False], 'pil900KW_image': [False]}, 'seq_num': [76], 'time': [1753707382.8083541], 'timestamps': {'pil2M_cam_file_number': [1753707381.738371], 'pil2M_image': [1753707381.6910598], 'pil2M_stats1_total': [1753707382.404384], 'pil900KW_cam_file_number': [1753707381.739924], 'pil900KW_image': [1753707381.6923807], 'pil900KW_stats1_total': [1753707382.649849], 'thorlabs_su_done': [1753707380.687973], 'thorlabs_su_readback': [1753707380.83863], 'thorlabs_su_setpoint': [1753707380.83863]}, 'uid': ['01147161-5529-4a45-bf6f-732ee86f9fd1']})
    475 def event_page(self, doc: EventPage):
    476     for _doc in unpack_event_page(doc):
--> 477         self.event(_doc)
        _doc = {'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'seq_num': 76, 'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}, 'filled': {'pil2M_image': False, 'pil900KW_image': False}}
        self = <bluesky.callbacks.tiled_writer.RunNormalizer object at 0x7f2c41b62260>

File ~/src/bluesky/src/bluesky/callbacks/tiled_writer.py:421, in RunNormalizer.event(self=<bluesky.callbacks.tiled_writer.RunNormalizer object>, doc={'data': {'pil2M_cam_file_number': 76, 'pil2M_image': '17ff6507-705c-4ac3-b9b2-eb7a4dd2e582/75', 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_image': 'cfa921ac-3de2-464c-a3df-6b4cbb086353/75', 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_image': 1753707381.6910598, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_image': 1753707381.6923807, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'})
    419 event_doc["data"] = {k: v for k, v in doc["data"].items() if k in event_keys}
    420 event_doc["timestamps"] = {k: v for k, v in doc["timestamps"].items() if k in event_keys}
--> 421 self.emit(DocumentNames.event, event_doc)
        event_doc = {'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'seq_num': 76, 'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}}
        DocumentNames.event = <DocumentNames.event: 'event'>
        self = <bluesky.callbacks.tiled_writer.RunNormalizer object at 0x7f2c41b62260>
    423 # Part 2. ----- External Data -----
    424 # Process _external_ data: Loop over all referenced Datums and all external data keys that are not filled
    425 for data_key, datum_id in doc["data"].items():

File ~/src/bluesky/src/bluesky/callbacks/tiled_writer.py:482, in RunNormalizer.emit(self=<bluesky.callbacks.tiled_writer.RunNormalizer object>, name=<DocumentNames.event: 'event'>, doc={'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'})
    480 """Check the document schema and send to the dispatcher"""
    481 schema_validators[name].validate(doc)
--> 482 self.dispatcher.process(name, doc)
        doc = {'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'seq_num': 76, 'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}}
        name = <DocumentNames.event: 'event'>
        self.dispatcher = <bluesky.run_engine.Dispatcher object at 0x7f2ca97a04f0>
        self = <bluesky.callbacks.tiled_writer.RunNormalizer object at 0x7f2c41b62260>

File ~/src/bluesky/src/bluesky/run_engine.py:2700, in Dispatcher.process(self=<bluesky.run_engine.Dispatcher object>, name=<DocumentNames.event: 'event'>, doc={'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'})
   2691 def process(self, name, doc):
   2692     """
   2693     Dispatch document ``doc`` of type ``name`` to the callback registry.
   2694 
   (...)
   2698     doc : dict
   2699     """
-> 2700     exceptions = self.cb_registry.process(name, name.name, doc)
        name = <DocumentNames.event: 'event'>
        doc = {'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'seq_num': 76, 'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}}
        self.cb_registry = <bluesky.utils.CallbackRegistry object at 0x7f2ca97a1270>
        self = <bluesky.run_engine.Dispatcher object at 0x7f2ca97a04f0>
   2701     for exc, traceback in exceptions:  # noqa: B007
   2702         warn(  # noqa: B028
   2703             "A %r was raised during the processing of a %s "  # noqa: UP031
   2704             "Document. The error will be ignored to avoid "
   (...)
   2707             "and run again." % (exc, name.name)
   2708         )

File ~/src/bluesky/src/bluesky/utils/__init__.py:443, in CallbackRegistry.process(self=<bluesky.utils.CallbackRegistry object>, sig=<DocumentNames.event: 'event'>, *args=('event', {'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'}), **kwargs={})
    441 for cid, func in list(self.callbacks[sig].items()):  # noqa: B007
    442     try:
--> 443         func(*args, **kwargs)
        func = <bluesky.utils._BoundMethodProxy object at 0x7f2ca97a1330>
        args = ('event', {'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'seq_num': 76, 'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}})
        kwargs = {}
    444     except ReferenceError:
    445         self._remove_proxy(func)

File ~/src/bluesky/src/bluesky/utils/__init__.py:533, in _BoundMethodProxy.__call__(self=<bluesky.utils._BoundMethodProxy object>, *args=('event', {'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'}), **kwargs={})
    531     mtd = self.func
    532 # invoke the callable and return the result
--> 533 return mtd(*args, **kwargs)
        mtd = <bluesky.callbacks.tiled_writer._RunWriter object at 0x7f2c41b10100>
        args = ('event', {'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'seq_num': 76, 'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}})
        kwargs = {}

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/event_model/__init__.py:191, in DocumentRouter.__call__(self=<bluesky.callbacks.tiled_writer._RunWriter object>, name='event', doc={'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'}, validate=False)
    171 def __call__(
    172     self, name: str, doc: dict, validate: bool = False
    173 ) -> Tuple[str, dict]:
    174     """
    175     Process a document.
    176 
   (...)
    189         instance as doc, a copy of doc, or a different dict altogether.
    190     """
--> 191     return self._dispatch(name, doc, validate)
        name = 'event'
        doc = {'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'seq_num': 76, 'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}}
        validate = False
        self = <bluesky.callbacks.tiled_writer._RunWriter object at 0x7f2c41b10100>

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/event_model/__init__.py:199, in DocumentRouter._dispatch(self=<bluesky.callbacks.tiled_writer._RunWriter object>, name='event', doc={'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'}, validate=False)
    193 def _dispatch(self, name: str, doc: dict, validate: bool) -> Tuple[str, dict]:
    194     """
    195     Dispatch to the method corresponding to the `name`.
    196 
    197     Optionally validate that the result is still a valid document.
    198     """
--> 199     output_doc = getattr(self, name)(doc)
        doc = {'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1', 'time': 1753707382.8083541, 'seq_num': 76, 'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774, 'thorlabs_su_done': 1}, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863, 'thorlabs_su_done': 1753707380.687973}}
        name = 'event'
        self = <bluesky.callbacks.tiled_writer._RunWriter object at 0x7f2c41b10100>
    201     # If 'event' is not defined by the subclass but 'event_page' is, or
    202     # vice versa, use that. And the same for 'datum_page' / 'datum.
    203     if output_doc is NotImplemented:

File ~/src/bluesky/src/bluesky/callbacks/tiled_writer.py:646, in _RunWriter.event(self=<bluesky.callbacks.tiled_writer._RunWriter object>, doc={'data': {'pil2M_cam_file_number': 76, 'pil2M_stats1_total': 42347.0, 'pil900KW_cam_file_number': 76, 'pil900KW_stats1_total': 3601366.0, 'thorlabs_su_done': 1, 'thorlabs_su_readback': 85.748, 'thorlabs_su_setpoint': 85.74791318864774}, 'descriptor': '997dfcdc-55db-4284-8ff0-6a069d2429db', 'seq_num': 76, 'time': 1753707382.8083541, 'timestamps': {'pil2M_cam_file_number': 1753707381.738371, 'pil2M_stats1_total': 1753707382.404384, 'pil900KW_cam_file_number': 1753707381.739924, 'pil900KW_stats1_total': 1753707382.649849, 'thorlabs_su_done': 1753707380.687973, 'thorlabs_su_readback': 1753707380.83863, 'thorlabs_su_setpoint': 1753707380.83863}, 'uid': '01147161-5529-4a45-bf6f-732ee86f9fd1'})
    643 data_cache.append(row)
    645 if len(data_cache) >= self._batch_size:
--> 646     self._write_internal_data(data_cache, desc_node=self._desc_nodes[desc_uid])
        desc_uid = '997dfcdc-55db-4284-8ff0-6a069d2429db'
        data_cache = []
        self._desc_nodes[desc_uid] = <BlueskyEventStream {'time', 'pil900KW_image', 'thorlabs_su_done', 'pil2M_image', 'pil900KW_cam_file_number', 'thorlabs_su_setpoint', 'thorlabs_su_readback', 'pil2M_stats1_total', 'pil2M_cam_file_number', 'pil900KW_stats1_total'} stream_name='primary'>
        self = <bluesky.callbacks.tiled_writer._RunWriter object at 0x7f2c41b10100>
        self._desc_nodes = {'b4654852-67cd-4666-87e8-89fc0559666a': <BlueskyEventStream {'hfm_y_user_setpoint', 'piezo_ch_user_setpoint', 'hfm_voltage_ch10_trg', 'vfm_voltage_ch15_trg', 'hfm_voltage_ch15_trg', 'SBS_pad', 'crl_lens9', 'MDrive_m8', 'hfm_voltage_ch0_trg', 'att2_12_status', 'stage_z_user_setpoint', 'crl_lens2', 'hfm_x_user_setpoint', 'crl_lens2_user_setpoint', 'time', 'crl_ph', 'hfm_voltage_ch3_trg', 'xbpm3_pos_x', 'hfm_voltage_ch11', 'hfm_voltage_ch6_trg', 'hfm_voltage_ch9', 'Pilatus2M_bs_kind', 'MDrive_m5', 'crl_ph_user_setpoint', 'hfm_voltage_set_tar', 'eslit_vg_user_setpoint', 'hfm_voltage_ch11_trg', 'ssa_hg', 'crl_lens7_user_setpoint', 'piezo_z', 'crl_lens12_user_setpoint', 'MDrive_m7_user_setpoint', 'crl_lens8_user_setpoint', 'att2_1_status', 'vdm_th_user_setpoint', 'ssa_vg_user_setpoint', 'vdm_y_user_setpoint', 'xbpm2_posX', 'crl_lens3_user_setpoint', 'vfm_voltage_ch0', 'ring_current', 'dsa_y_user_setpoint', 'ls_input_B', 'xbpm2_posY', 'prs', 'dsa_x', 'energy_energy', 'SBS_y_user_setpoint', 'hfm_voltage_ch4', 'saxs_beamstop_y_rod', 'thorlabs_su_done', 'vdm_x', 'Pilatus900kw_sdd', 'stage_ch', 'energy_energy_setpoint', 'vfm_voltage_ch12', 'hfm_voltage_ch9_trg', 'detector_saxs_pos_z', 'hfm_voltage_ch7_trg', 'wbs_h', 'detector_saxs_pos_x_user_setpoint', 'hfm_voltage_ch12', 'att1_10_status', 'vfm_voltage_ch13', 'dcm_config_roll', 'SBS_pad_user_setpoint', 'dcm_config_theta', 'SAXS_y', 'cslit_v', 'wbs_h_user_setpoint', 'ssa_hg_user_setpoint', 'cslit_vg', 'piezo_th', 'saxs_beamstop_x_pin', 'MDrive_m4_user_setpoint', 'ls_input_C', 'att2_4_status', 'ssa_vg', 'dcm_config_pitch', 'att2_11_status', 'vdm_x_user_setpoint', 'hfm_voltage_ch14_trg', 'hfm_voltage_ch7', 'att2_2_status', 'ls_input_A', 'crl_lens12', 'MDrive_m3', 'crl_lens10', 'crl_lens11', 'dcm_config_roll_user_setpoint', 'vfm_voltage_ch11', 'MDrive_m2', 'stage_ch_user_setpoint', 'cslit_vg_user_setpoint', 'thorlabs_su_setpoint', 'energy_harmonic', 'vfm_voltage_ch2', 'xbpm2_ch1', 'vfm_voltage_ch10_trg', 'cslit_hg_user_setpoint', 'eslit_v_user_setpoint', 'dsa_x_user_setpoint', 'detector_saxs_pos_y_user_setpoint', 'vfm_voltage_ch8', 'att2_7_status', 'stage_x_user_setpoint', 'crl_lens10_user_setpoint', 'vfm_voltage_ch11_trg', 'vfm_voltage_ch13_trg', 'crl_lens5', 'piezo_th_user_setpoint', 'cslit_hg', 'piezo_y_user_setpoint', 'SAXS_y_user_setpoint', 'hfm_voltage_ch8_trg', 'dsa_y', 'stage_y', 'hfm_voltage_ch1_trg', 'xbpm3_posX', 'MDrive_m1', 'crl_lens1_user_setpoint', 'hfm_voltage_ch10', 'wbs_v_user_setpoint', 'ls_input_D', 'xbpm2_ch3', 'crl_lens8', 'hfm_voltage_ch6', 'crl_lens4_user_setpoint', 'MDrive_m1_user_setpoint', 'Pilatus2M_xbs_mask', 'vfm_voltage_ch9_trg', 'att2_8_status', 'hfm_voltage_ch2_trg', 'energy_ivugap', 'MDrive_m8_user_setpoint', 'wbs_hg_user_setpoint', 'crl_lens11_user_setpoint', 'vfm_voltage_ch6_trg', 'SAXS_z', 'eslit_v', 'dcm_config_height_user_setpoint', 'xbpm2_pos_y_user_setpoint', 'detector_saxs_pos_z_user_setpoint', 'hfm_voltage_ch15', 'vfm_y_user_setpoint', 'saxs_beamstop_y_pin', 'vfm_voltage_ch10', 'MDrive_m4', 'hfm_th_user_setpoint', 'att1_2_status', 'xbpm2_pos_x_user_setpoint', 'eslit_hg', 'vfm_voltage_ch7_trg', 'stage_z', 'crl_lens1', 'vfm_voltage_ch14_trg', 'vfm_voltage_ch5', 'xbpm3_ch2', 'att1_7_status', 'piezo_x', 'xbpm2_ch2', 'hfm_voltage_ch2', 'Pilatus2M_y0_pix', 'crl_lens7', 'xbpm2_sumX', 'xbpm3_pos_y_user_setpoint', 'crl_lens3', 'SBS_x', 'crl_lens4', 'hfm_voltage_ch3', 'vfm_voltage_ch15', 'crl_z', 'att1_9_status', 'crl_y_user_setpoint', 'vfm_voltage_shift_rel', 'ssa_h', 'MDrive_m7', 'att2_6_status', 'hfm_voltage_ch1', 'Pilatus2M_x0_pix', 'eslit_h', 'att1_11_status', 'xbpm3_posY', 'xbpm3_pos_y', 'stage_x', 'stage_th', 'vfm_x', 'Pilatus2M_sdd', 'chamber_pressure_maxs', 'thorlabs_su_readback', 'xbpm3_ch1', 'hfm_voltage_ch0', 'hfm_voltage_ch13_trg', 'hfm_x', 'cslit_v_user_setpoint', 'cslit_h', 'stage_ph', 'hfm_voltage_ch14', 'xbpm3_sumY', 'SBS_y', 'ph_shutter_status', 'hfm_th', 'saxs_beamstop_y_pin_user_setpoint', 'xbpm2_pos_x', 'xbpm2_pos_y', 'stage_y_user_setpoint', 'saxs_beamstop_x_pin_user_setpoint', 'vfm_voltage_ch14', 'energy_bragg', 'xbpm3_ch3', 'SAXS_x', 'prs_user_setpoint', 'xbpm2_sumY', 'dcm_config_pitch_user_setpoint', 'piezo_x_user_setpoint', 'MDrive_m6', 'Pilatus900kw_y0_pix', 'xbpm1_pos_x', 'crl_lens5_user_setpoint', 'hfm_voltage_ch8', 'att1_6_status', 'xbpm3_pos_x_user_setpoint', 'ssa_h_user_setpoint', 'piezo_y', 'xbpm2_ch4', 'stage_th_user_setpoint', 'vdm_th', 'cslit_h_user_setpoint', 'saxs_beamstop_x_rod_user_setpoint', 'piezo_ch', 'vfm_voltage_ch8_trg', 'att2_3_status', 'wbs_vg_user_setpoint', 'xbpm1_pos_y_user_setpoint', 'MDrive_m5_user_setpoint', 'ssa_v_user_setpoint', 'vfm_voltage_ch4_trg', 'ls_input_A_celsius', 'hfm_voltage_ch5_trg', 'hfm_voltage_shift_rel', 'vfm_voltage_ch4', 'detector_saxs_pos_y', 'saxs_beamstop_y_rod_user_setpoint', 'vfm_voltage_ch0_trg', 'detector_saxs_pos_x', 'att1_1_status', 'crl_x_user_setpoint', 'att1_12_status', 'vfm_x_user_setpoint', 'vfm_voltage_ch2_trg', 'eslit_hg_user_setpoint', 'att1_8_status', 'crl_lens6', 'Pilatus2M_ybs_mask', 'dcm_config_theta_user_setpoint', 'vfm_voltage_set_tar', 'wbs_v', 'vfm_voltage_ch1', 'vfm_voltage_ch3_trg', 'MDrive_m3_user_setpoint', 'hfm_voltage_ch13', 'hfm_voltage_ch12_trg', 'eslit_vg', 'xbpm1_pos_x_user_setpoint', 'vfm_voltage_ch9', 'dcm_config_height', 'att1_3_status', 'SAXS_z_user_setpoint', 'xbpm1_pos_y', 'att1_4_status', 'att1_5_status', 'eslit_h_user_setpoint', 'SBS_x_user_setpoint', 'wbs_hg', 'saxs_beamstop_x_rod', 'ssa_v', 'hfm_y', 'vfm_th', 'crl_x', 'att2_9_status', 'vdm_y', 'wbs_vg', 'Pilatus900kw_pixel_size', 'vfm_voltage_ch7', 'hfm_voltage_ch4_trg', 'att2_5_status', 'vfm_voltage_ch3', 'vfm_voltage_ch1_trg', 'crl_lens9_user_setpoint', 'hfm_voltage_ch5', 'xbpm3_sumX', 'vfm_y', 'SAXS_x_user_setpoint', 'MDrive_m2_user_setpoint', 'piezo_z_user_setpoint', 'chamber_pressure_waxs', 'Pilatus2M_pixel_size', 'xbpm3_ch4', 'att2_10_status', 'vfm_voltage_ch12_trg', 'crl_y', 'crl_z_user_setpoint', 'crl_th', 'crl_lens6_user_setpoint', 'MDrive_m6_user_setpoint', 'Pilatus900kw_x0_pix', 'vfm_voltage_ch6', 'vfm_th_user_setpoint', 'crl_th_user_setpoint', 'vfm_voltage_ch5_trg', 'GV7_status', 'stage_ph_user_setpoint'} stream_name='baseline'>, 'baseline': <BlueskyEventStream {'hfm_y_user_setpoint', 'piezo_ch_user_setpoint', 'hfm_voltage_ch10_trg', 'vfm_voltage_ch15_trg', 'hfm_voltage_ch15_trg', 'SBS_pad', 'crl_lens9', 'MDrive_m8', 'hfm_voltage_ch0_trg', 'att2_12_status', 'stage_z_user_setpoint', 'crl_lens2', 'hfm_x_user_setpoint', 'crl_lens2_user_setpoint', 'time', 'crl_ph', 'hfm_voltage_ch3_trg', 'xbpm3_pos_x', 'hfm_voltage_ch11', 'hfm_voltage_ch6_trg', 'hfm_voltage_ch9', 'Pilatus2M_bs_kind', 'MDrive_m5', 'crl_ph_user_setpoint', 'hfm_voltage_set_tar', 'eslit_vg_user_setpoint', 'hfm_voltage_ch11_trg', 'ssa_hg', 'crl_lens7_user_setpoint', 'piezo_z', 'crl_lens12_user_setpoint', 'MDrive_m7_user_setpoint', 'crl_lens8_user_setpoint', 'att2_1_status', 'vdm_th_user_setpoint', 'ssa_vg_user_setpoint', 'vdm_y_user_setpoint', 'xbpm2_posX', 'crl_lens3_user_setpoint', 'vfm_voltage_ch0', 'ring_current', 'dsa_y_user_setpoint', 'ls_input_B', 'xbpm2_posY', 'prs', 'dsa_x', 'energy_energy', 'SBS_y_user_setpoint', 'hfm_voltage_ch4', 'saxs_beamstop_y_rod', 'thorlabs_su_done', 'vdm_x', 'Pilatus900kw_sdd', 'stage_ch', 'energy_energy_setpoint', 'vfm_voltage_ch12', 'hfm_voltage_ch9_trg', 'detector_saxs_pos_z', 'hfm_voltage_ch7_trg', 'wbs_h', 'detector_saxs_pos_x_user_setpoint', 'hfm_voltage_ch12', 'att1_10_status', 'vfm_voltage_ch13', 'dcm_config_roll', 'SBS_pad_user_setpoint', 'dcm_config_theta', 'SAXS_y', 'cslit_v', 'wbs_h_user_setpoint', 'ssa_hg_user_setpoint', 'cslit_vg', 'piezo_th', 'saxs_beamstop_x_pin', 'MDrive_m4_user_setpoint', 'ls_input_C', 'att2_4_status', 'ssa_vg', 'dcm_config_pitch', 'att2_11_status', 'vdm_x_user_setpoint', 'hfm_voltage_ch14_trg', 'hfm_voltage_ch7', 'att2_2_status', 'ls_input_A', 'crl_lens12', 'MDrive_m3', 'crl_lens10', 'crl_lens11', 'dcm_config_roll_user_setpoint', 'vfm_voltage_ch11', 'MDrive_m2', 'stage_ch_user_setpoint', 'cslit_vg_user_setpoint', 'thorlabs_su_setpoint', 'energy_harmonic', 'vfm_voltage_ch2', 'xbpm2_ch1', 'vfm_voltage_ch10_trg', 'cslit_hg_user_setpoint', 'eslit_v_user_setpoint', 'dsa_x_user_setpoint', 'detector_saxs_pos_y_user_setpoint', 'vfm_voltage_ch8', 'att2_7_status', 'stage_x_user_setpoint', 'crl_lens10_user_setpoint', 'vfm_voltage_ch11_trg', 'vfm_voltage_ch13_trg', 'crl_lens5', 'piezo_th_user_setpoint', 'cslit_hg', 'piezo_y_user_setpoint', 'SAXS_y_user_setpoint', 'hfm_voltage_ch8_trg', 'dsa_y', 'stage_y', 'hfm_voltage_ch1_trg', 'xbpm3_posX', 'MDrive_m1', 'crl_lens1_user_setpoint', 'hfm_voltage_ch10', 'wbs_v_user_setpoint', 'ls_input_D', 'xbpm2_ch3', 'crl_lens8', 'hfm_voltage_ch6', 'crl_lens4_user_setpoint', 'MDrive_m1_user_setpoint', 'Pilatus2M_xbs_mask', 'vfm_voltage_ch9_trg', 'att2_8_status', 'hfm_voltage_ch2_trg', 'energy_ivugap', 'MDrive_m8_user_setpoint', 'wbs_hg_user_setpoint', 'crl_lens11_user_setpoint', 'vfm_voltage_ch6_trg', 'SAXS_z', 'eslit_v', 'dcm_config_height_user_setpoint', 'xbpm2_pos_y_user_setpoint', 'detector_saxs_pos_z_user_setpoint', 'hfm_voltage_ch15', 'vfm_y_user_setpoint', 'saxs_beamstop_y_pin', 'vfm_voltage_ch10', 'MDrive_m4', 'hfm_th_user_setpoint', 'att1_2_status', 'xbpm2_pos_x_user_setpoint', 'eslit_hg', 'vfm_voltage_ch7_trg', 'stage_z', 'crl_lens1', 'vfm_voltage_ch14_trg', 'vfm_voltage_ch5', 'xbpm3_ch2', 'att1_7_status', 'piezo_x', 'xbpm2_ch2', 'hfm_voltage_ch2', 'Pilatus2M_y0_pix', 'crl_lens7', 'xbpm2_sumX', 'xbpm3_pos_y_user_setpoint', 'crl_lens3', 'SBS_x', 'crl_lens4', 'hfm_voltage_ch3', 'vfm_voltage_ch15', 'crl_z', 'att1_9_status', 'crl_y_user_setpoint', 'vfm_voltage_shift_rel', 'ssa_h', 'MDrive_m7', 'att2_6_status', 'hfm_voltage_ch1', 'Pilatus2M_x0_pix', 'eslit_h', 'att1_11_status', 'xbpm3_posY', 'xbpm3_pos_y', 'stage_x', 'stage_th', 'vfm_x', 'Pilatus2M_sdd', 'chamber_pressure_maxs', 'thorlabs_su_readback', 'xbpm3_ch1', 'hfm_voltage_ch0', 'hfm_voltage_ch13_trg', 'hfm_x', 'cslit_v_user_setpoint', 'cslit_h', 'stage_ph', 'hfm_voltage_ch14', 'xbpm3_sumY', 'SBS_y', 'ph_shutter_status', 'hfm_th', 'saxs_beamstop_y_pin_user_setpoint', 'xbpm2_pos_x', 'xbpm2_pos_y', 'stage_y_user_setpoint', 'saxs_beamstop_x_pin_user_setpoint', 'vfm_voltage_ch14', 'energy_bragg', 'xbpm3_ch3', 'SAXS_x', 'prs_user_setpoint', 'xbpm2_sumY', 'dcm_config_pitch_user_setpoint', 'piezo_x_user_setpoint', 'MDrive_m6', 'Pilatus900kw_y0_pix', 'xbpm1_pos_x', 'crl_lens5_user_setpoint', 'hfm_voltage_ch8', 'att1_6_status', 'xbpm3_pos_x_user_setpoint', 'ssa_h_user_setpoint', 'piezo_y', 'xbpm2_ch4', 'stage_th_user_setpoint', 'vdm_th', 'cslit_h_user_setpoint', 'saxs_beamstop_x_rod_user_setpoint', 'piezo_ch', 'vfm_voltage_ch8_trg', 'att2_3_status', 'wbs_vg_user_setpoint', 'xbpm1_pos_y_user_setpoint', 'MDrive_m5_user_setpoint', 'ssa_v_user_setpoint', 'vfm_voltage_ch4_trg', 'ls_input_A_celsius', 'hfm_voltage_ch5_trg', 'hfm_voltage_shift_rel', 'vfm_voltage_ch4', 'detector_saxs_pos_y', 'saxs_beamstop_y_rod_user_setpoint', 'vfm_voltage_ch0_trg', 'detector_saxs_pos_x', 'att1_1_status', 'crl_x_user_setpoint', 'att1_12_status', 'vfm_x_user_setpoint', 'vfm_voltage_ch2_trg', 'eslit_hg_user_setpoint', 'att1_8_status', 'crl_lens6', 'Pilatus2M_ybs_mask', 'dcm_config_theta_user_setpoint', 'vfm_voltage_set_tar', 'wbs_v', 'vfm_voltage_ch1', 'vfm_voltage_ch3_trg', 'MDrive_m3_user_setpoint', 'hfm_voltage_ch13', 'hfm_voltage_ch12_trg', 'eslit_vg', 'xbpm1_pos_x_user_setpoint', 'vfm_voltage_ch9', 'dcm_config_height', 'att1_3_status', 'SAXS_z_user_setpoint', 'xbpm1_pos_y', 'att1_4_status', 'att1_5_status', 'eslit_h_user_setpoint', 'SBS_x_user_setpoint', 'wbs_hg', 'saxs_beamstop_x_rod', 'ssa_v', 'hfm_y', 'vfm_th', 'crl_x', 'att2_9_status', 'vdm_y', 'wbs_vg', 'Pilatus900kw_pixel_size', 'vfm_voltage_ch7', 'hfm_voltage_ch4_trg', 'att2_5_status', 'vfm_voltage_ch3', 'vfm_voltage_ch1_trg', 'crl_lens9_user_setpoint', 'hfm_voltage_ch5', 'xbpm3_sumX', 'vfm_y', 'SAXS_x_user_setpoint', 'MDrive_m2_user_setpoint', 'piezo_z_user_setpoint', 'chamber_pressure_waxs', 'Pilatus2M_pixel_size', 'xbpm3_ch4', 'att2_10_status', 'vfm_voltage_ch12_trg', 'crl_y', 'crl_z_user_setpoint', 'crl_th', 'crl_lens6_user_setpoint', 'MDrive_m6_user_setpoint', 'Pilatus900kw_x0_pix', 'vfm_voltage_ch6', 'vfm_th_user_setpoint', 'crl_th_user_setpoint', 'vfm_voltage_ch5_trg', 'GV7_status', 'stage_ph_user_setpoint'} stream_name='baseline'>, '997dfcdc-55db-4284-8ff0-6a069d2429db': <BlueskyEventStream {'time', 'pil900KW_image', 'thorlabs_su_done', 'pil2M_image', 'pil900KW_cam_file_number', 'thorlabs_su_setpoint', 'thorlabs_su_readback', 'pil2M_stats1_total', 'pil2M_cam_file_number', 'pil900KW_stats1_total'} stream_name='primary'>, 'primary': <BlueskyEventStream {'time', 'pil900KW_image', 'thorlabs_su_done', 'pil2M_image', 'pil900KW_cam_file_number', 'thorlabs_su_setpoint', 'thorlabs_su_readback', 'pil2M_stats1_total', 'pil2M_cam_file_number', 'pil900KW_stats1_total'} stream_name='primary'>}
    647     data_cache.clear()

File ~/src/bluesky/src/bluesky/callbacks/tiled_writer.py:549, in _RunWriter._write_internal_data(self=<bluesky.callbacks.tiled_writer._RunWriter object>, data_cache=[], desc_node=<BlueskyEventStream {'time', 'pil900KW_image', '..., 'pil900KW_stats1_total'} stream_name='primary'>)
    544     df_client = desc_node.create_appendable_table(
    545         schema=schema, key="internal", metadata=metadata, access_tags=self.access_tags
    546     )
    547     self._internal_tables[desc_name] = df_client
--> 549 df_client.append_partition(table, 0)
        table = pyarrow.Table
seq_num: int64
time: double
pil2M_cam_file_number: int64
pil2M_stats1_total: double
pil900KW_cam_file_number: int64
pil900KW_stats1_total: double
thorlabs_su_readback: double
thorlabs_su_setpoint: double
thorlabs_su_done: int64
ts_pil2M_cam_file_number: double
ts_pil2M_stats1_total: double
ts_pil900KW_cam_file_number: double
ts_pil900KW_stats1_total: double
ts_thorlabs_su_readback: double
ts_thorlabs_su_setpoint: double
ts_thorlabs_su_done: double
----
seq_num: [[76]]
time: [[1753707382.8083541]]
pil2M_cam_file_number: [[76]]
pil2M_stats1_total: [[42347]]
pil900KW_cam_file_number: [[76]]
pil900KW_stats1_total: [[3601366]]
thorlabs_su_readback: [[85.748]]
thorlabs_su_setpoint: [[85.74791318864774]]
thorlabs_su_done: [[1]]
ts_pil2M_cam_file_number: [[1753707381.738371]]
...
        df_client = <DataFrameClient>

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/tiled/client/dataframe.py:244, in _DaskDataFrameClient.append_partition(self=<DataFrameClient>, dataframe=pyarrow.Table
seq_num: int64
time: double
pil2M_..._pil2M_cam_file_number: [[1753707381.738371]]
..., partition=0)
    242 if partition > self.structure().npartitions:
    243     raise ValueError(f"Table has {self.structure().npartitions} partitions")
--> 244 for attempt in retry_context():
        attempt = <Attempt num=2, next_wait=0.4>
    245     with attempt:
    246         handle_error(
    247             self.context.http_client.patch(
    248                 self.item["links"]["partition"].format(index=partition),
   (...)
    251             )
    252         )

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/stamina/_core.py:525, in _RetryContextIterator.__iter__(self=_RetryContextIterator(_t_kw={'retry': <tenacity....ait_max=5.0, _wait_exp_base=2.0, _cms_to_exit=[]))
    519     return
    521 before_sleep = _make_before_sleep(
    522     self._name, CONFIG, self._args, self._kw, self._cms_to_exit
    523 )
--> 525 for r in _t.Retrying(
        r = <tenacity.AttemptManager object at 0x7f2ca9773df0>
        _t.Retrying = <class 'tenacity.Retrying'>
        _t = <module 'tenacity' from '/nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/tenacity/__init__.py'>
        self = _RetryContextIterator(_t_kw={'retry': <tenacity.retry.retry_if_exception object at 0x7f2c41b02c20>, 'stop': <tenacity.stop.stop_any object at 0x7f2c41b03640>, 'reraise': True, 'wait': <bound method _RetryContextIterator._jittered_backoff_for_rcs of ...>}, _t_a_retrying=<stamina._core._LazyNoAsyncRetry object at 0x7f2e40858f80>, _name='<context block>', _args=(), _kw={}, _attempts=10, _wait_jitter=1.0, _wait_initial=0.1, _wait_max=5.0, _wait_exp_base=2.0, _cms_to_exit=[])
        CONFIG = <stamina._config._Config object at 0x7f2e40a09530>
    526     before=self._exit_cms,
    527     before_sleep=before_sleep,
    528     **self._apply_maybe_test_mode_to_tenacity_kw(CONFIG.testing),
    529 ):
    530     yield Attempt(r, self._backoff_for_attempt_number)

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/tenacity/__init__.py:445, in BaseRetrying.__iter__(self=<Retrying object at 0x7f2c41b038b0 (stop=<tenaci...fter=<function after_nothing at 0x7f2e4080a950>)>)
    443 retry_state = RetryCallState(self, fn=None, args=(), kwargs={})
    444 while True:
--> 445     do = self.iter(retry_state=retry_state)
        retry_state = <RetryCallState 139828057354304: attempt #2; slept for 0.67; last result: failed (ReadTimeout The read operation timed out)>
        self = <Retrying object at 0x7f2c41b038b0 (stop=<tenacity.stop.stop_any object at 0x7f2c41b03640>, wait=<bound method _RetryContextIterator._jittered_backoff_for_rcs of _RetryContextIterator(_t_kw={'retry': <tenacity.retry.retry_if_exception object at 0x7f2c41b02c20>, 'stop': <tenacity.stop.stop_any object at 0x7f2c41b03640>, 'reraise': True, 'wait': <bound method _RetryContextIterator._jittered_backoff_for_rcs of ...>}, _t_a_retrying=<stamina._core._LazyNoAsyncRetry object at 0x7f2e40858f80>, _name='<context block>', _args=(), _kw={}, _attempts=10, _wait_jitter=1.0, _wait_initial=0.1, _wait_max=5.0, _wait_exp_base=2.0, _cms_to_exit=[])>, sleep=<function sleep at 0x7f2e40808160>, retry=<tenacity.retry.retry_if_exception object at 0x7f2c41b02c20>, before=<bound method _RetryContextIterator._exit_cms of _RetryContextIterator(_t_kw={'retry': <tenacity.retry.retry_if_exception object at 0x7f2c41b02c20>, 'stop': <tenacity.stop.stop_any object at 0x7f2c41b03640>, 'reraise': True, 'wait': <bound method _RetryContextIterator._jittered_backoff_for_rcs of ...>}, _t_a_retrying=<stamina._core._LazyNoAsyncRetry object at 0x7f2e40858f80>, _name='<context block>', _args=(), _kw={}, _attempts=10, _wait_jitter=1.0, _wait_initial=0.1, _wait_max=5.0, _wait_exp_base=2.0, _cms_to_exit=[])>, after=<function after_nothing at 0x7f2e4080a950>)>
        do = <tenacity.DoAttempt object at 0x7f2ca9771a50>
    446     if isinstance(do, DoAttempt):
    447         yield AttemptManager(retry_state=retry_state)

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/tenacity/__init__.py:378, in BaseRetrying.iter(self=<Retrying object at 0x7f2c41b038b0 (stop=<tenaci...fter=<function after_nothing at 0x7f2e4080a950>)>, retry_state=<RetryCallState 139828057354304: attempt #2; sle...ailed (ReadTimeout The read operation timed out)>)
    376 result = None
    377 for action in self.iter_state.actions:
--> 378     result = action(retry_state)
        result = None
        action = <function BaseRetrying._post_stop_check_actions.<locals>.exc_check at 0x7f2c71680550>
        retry_state = <RetryCallState 139828057354304: attempt #2; slept for 0.67; last result: failed (ReadTimeout The read operation timed out)>
    379 return result

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/tenacity/__init__.py:420, in BaseRetrying._post_stop_check_actions.<locals>.exc_check(rs=<RetryCallState 139828057354304: attempt #2; sle...ailed (ReadTimeout The read operation timed out)>)
    418 retry_exc = self.retry_error_cls(fut)
    419 if self.reraise:
--> 420     raise retry_exc.reraise()
        retry_exc = RetryError(<Future at 0x7f2ca9795120 state=finished raised ReadTimeout>)
    421 raise retry_exc from fut.exception()

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/tenacity/__init__.py:187, in RetryError.reraise(self=RetryError(<Future at 0x7f2ca9795120 state=finished raised ReadTimeout>))
    185 def reraise(self) -> t.NoReturn:
    186     if self.last_attempt.failed:
--> 187         raise self.last_attempt.result()
        self = RetryError(<Future at 0x7f2ca9795120 state=finished raised ReadTimeout>)
        self.last_attempt = <Future at 0x7f2ca9795120 state=finished raised ReadTimeout>
    188     raise self

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/concurrent/futures/_base.py:451, in Future.result(self=None, timeout=None)
    449     raise CancelledError()
    450 elif self._state == FINISHED:
--> 451     return self.__get_result()
        self = None
    453 self._condition.wait(timeout)
    455 if self._state in [CANCELLED, CANCELLED_AND_NOTIFIED]:

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/concurrent/futures/_base.py:403, in Future.__get_result(self=None)
    401 if self._exception:
    402     try:
--> 403         raise self._exception
        self = None
    404     finally:
    405         # Break a reference cycle with the exception in self._exception
    406         self = None

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/tiled/client/dataframe.py:247, in _DaskDataFrameClient.append_partition(self=<DataFrameClient>, dataframe=pyarrow.Table
seq_num: int64
time: double
pil2M_..._pil2M_cam_file_number: [[1753707381.738371]]
..., partition=0)
    244 for attempt in retry_context():
    245     with attempt:
    246         handle_error(
--> 247             self.context.http_client.patch(
        self = <DataFrameClient>
        partition = 0
        dataframe = pyarrow.Table
seq_num: int64
time: double
pil2M_cam_file_number: int64
pil2M_stats1_total: double
pil900KW_cam_file_number: int64
pil900KW_stats1_total: double
thorlabs_su_readback: double
thorlabs_su_setpoint: double
thorlabs_su_done: int64
ts_pil2M_cam_file_number: double
ts_pil2M_stats1_total: double
ts_pil900KW_cam_file_number: double
ts_pil900KW_stats1_total: double
ts_thorlabs_su_readback: double
ts_thorlabs_su_setpoint: double
ts_thorlabs_su_done: double
----
seq_num: [[76]]
time: [[1753707382.8083541]]
pil2M_cam_file_number: [[76]]
pil2M_stats1_total: [[42347]]
pil900KW_cam_file_number: [[76]]
pil900KW_stats1_total: [[3601366]]
thorlabs_su_readback: [[85.748]]
thorlabs_su_setpoint: [[85.74791318864774]]
thorlabs_su_done: [[1]]
ts_pil2M_cam_file_number: [[1753707381.738371]]
...
        {"Content-Type": APACHE_ARROW_FILE_MIME_TYPE} = {'Content-Type': 'application/vnd.apache.arrow.file'}
        APACHE_ARROW_FILE_MIME_TYPE = 'application/vnd.apache.arrow.file'
    248                 self.item["links"]["partition"].format(index=partition),
    249                 content=bytes(serialize_arrow(dataframe, {})),
    250                 headers={"Content-Type": APACHE_ARROW_FILE_MIME_TYPE},
    251             )
    252         )

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpx/_client.py:1218, in Client.patch(self=<httpx.Client object>, url='https://tiled-dev.nsls2.bnl.gov/api/v1/table/par...434deb67ae23/streams/primary/internal?partition=0', content=b'ARROW1\x00\x00\xff\xff\xff\xff@\x04\x00\x00\x1...\x00\x00\x00\x01@\x00\x00\x00h\x04\x00\x00ARROW1', data=None, files=None, json=None, params=None, headers={'Content-Type': 'application/vnd.apache.arrow.file'}, cookies=None, auth=<httpx._client.UseClientDefault object>, follow_redirects=<httpx._client.UseClientDefault object>, timeout=<httpx._client.UseClientDefault object>, extensions=None)
   1197 def patch(
   1198     self,
   1199     url: URL | str,
   (...)
   1211     extensions: RequestExtensions | None = None,
   1212 ) -> Response:
   1213     """
   1214     Send a `PATCH` request.
   1215 
   1216     **Parameters**: See `httpx.request`.
   1217     """
-> 1218     return self.request(
        self = <httpx.Client object at 0x7f2daef01450>
        url = 'https://tiled-dev.nsls2.bnl.gov/api/v1/table/partition//8d147c26-7ce8-42ea-8eef-434deb67ae23/streams/primary/internal?partition=0'
        content = b'ARROW1\x00\x00\xff\xff\xff\xff@\x04\x00\x00\x10\x00\x00\x00\x00\x00\n\x00\x0c\x00\x06\x00\x05\x00\x08\x00\n\x00\x00\x00\x00\x01\x04\x00\x0c\x00\x00\x00\x08\x00\x08\x00\x00\x00\x04\x00\x08\x00\x00\x00\x04\x00\x00\x00\x10\x00\x00\x00\xd8\x03\x00\x00\x94\x03\x00\x00P\x03\x00\x00\x14\x03\x00\x00\xcc\x02\x00\x00\x8c\x02\x00\x00L\x02\x00\x00\x0c\x02\x00\x00\xcc\x01\x00\x00\x88\x01\x00\x00H\x01\x00\x00\x04\x01\x00\x00\xc0\x00\x00\x00\x80\x00\x00\x00@\x00\x00\x00\x04\x00\x00\x00x\xfc\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00$\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00ts_thorlabs_su_done\x00\xb6\xfc\xff\xff\x00\x00\x02\x00\xb0\xfc\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00ts_thorlabs_su_setpoint\x00\xf2\xfc\xff\xff\x00\x00\x02\x00\xec\xfc\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00ts_thorlabs_su_readback\x00.\xfd\xff\xff\x00\x00\x02\x00(\xfd\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00,\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00ts_pil900KW_stats1_total\x00\x00\x00\x00n\xfd\xff\xff\x00\x00\x02\x00h\xfd\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00,\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x1b\x00\x00\x00ts_pil900KW_cam_file_number\x00\xae\xfd\xff\xff\x00\x00\x02\x00\xa8\xfd\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x15\x00\x00\x00ts_pil2M_stats1_total\x00\x00\x00\xea\xfd\xff\xff\x00\x00\x02\x00\xe4\xfd\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00,\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00ts_pil2M_cam_file_number\x00\x00\x00\x00*\xfe\xff\xff\x00\x00\x02\x00$\xfe\xff\xff\x00\x00\x01\x02\x10\x00\x00\x00$\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00thorlabs_su_done\x00\x00\x00\x00 \xfe\xff\xff\x00\x00\x00\x01@\x00\x00\x00`\xfe\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00thorlabs_su_setpoint\x00\x00\x00\x00\xa2\xfe\xff\xff\x00\x00\x02\x00\x9c\xfe\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00thorlabs_su_readback\x00\x00\x00\x00\xde\xfe\xff\xff\x00\x00\x02\x00\xd8\xfe\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x15\x00\x00\x00pil900KW_stats1_total\x00\x00\x00\x1a\xff\xff\xff\x00\x00\x02\x00\x14\xff\xff\xff\x00\x00\x01\x02\x10\x00\x00\x00,\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00pil900KW_cam_file_number\x00\x00\x00\x00\x18\xff\xff\xff\x00\x00\x00\x01@\x00\x00\x00X\xff\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00$\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x00pil2M_stats1_total\x00\x00\x96\xff\xff\xff\x00\x00\x02\x00\x90\xff\xff\xff\x00\x00\x01\x02\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x15\x00\x00\x00pil2M_cam_file_number\x00\x00\x00\x90\xff\xff\xff\x00\x00\x00\x01@\x00\x00\x00\xd0\xff\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00\x1c\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00time\x00\x00\x06\x00\x08\x00\x06\x00\x06\x00\x00\x00\x00\x00\x02\x00\x10\x00\x14\x00\x08\x00\x06\x00\x07\x00\x0c\x00\x00\x00\x10\x00\x10\x00\x00\x00\x00\x00\x01\x02\x10\x00\x00\x00 \x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00seq_num\x00\x08\x00\x0c\x00\x08\x00\x07\x00\x08\x00\x00\x00\x00\x00\x00\x01@\x00\x00\x00\xff\xff\xff\xffX\x03\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x16\x00\x06\x00\x05\x00\x08\x00\x0c\x00\x0c\x00\x00\x00\x00\x03\x04\x00\x18\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x18\x00\x0c\x00\x04\x00\x08\x00\n\x00\x00\x00\x1c\x02\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00(\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x000\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x008\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x008\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00H\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00H\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00P\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00P\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00X\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00X\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00h\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00h\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00p\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00p\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00x\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00x\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x13\xbc\xb3\xdd\xdc!\xdaAL\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`\xad\xe4@L\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xebyKA\x1dZd;\xdfoU@N_G\xcf\xddoU@\x01\x00\x00\x00\x00\x00\x00\x00xAo\xdd\xdc!\xdaAm\xe1\x99\xdd\xdc!\xdaA\xeaZo\xdd\xdc!\xdaA \x97\xa9\xdd\xdc!\xdaA\x1d\xac5\xdd\xdc!\xdaA\x1d\xac5\xdd\xdc!\xdaA\xc0\x07,\xdd\xdc!\xdaA\xff\xff\xff\xff\x00\x00\x00\x00\x10\x00\x00\x00\x0c\x00\x14\x00\x06\x00\x08\x00\x0c\x00\x10\x00\x0c\x00\x00\x00\x00\x00\x04\x004\x00\x00\x00$\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00P\x04\x00\x00\x00\x00\x00\x00`\x03\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x08\x00\x00\x00\x04\x00\x08\x00\x00\x00\x04\x00\x00\x00\x10\x00\x00\x00\xd8\x03\x00\x00\x94\x03\x00\x00P\x03\x00\x00\x14\x03\x00\x00\xcc\x02\x00\x00\x8c\x02\x00\x00L\x02\x00\x00\x0c\x02\x00\x00\xcc\x01\x00\x00\x88\x01\x00\x00H\x01\x00\x00\x04\x01\x00\x00\xc0\x00\x00\x00\x80\x00\x00\x00@\x00\x00\x00\x04\x00\x00\x00x\xfc\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00$\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00ts_thorlabs_su_done\x00\xb6\xfc\xff\xff\x00\x00\x02\x00\xb0\xfc\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00ts_thorlabs_su_setpoint\x00\xf2\xfc\xff\xff\x00\x00\x02\x00\xec\xfc\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00ts_thorlabs_su_readback\x00.\xfd\xff\xff\x00\x00\x02\x00(\xfd\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00,\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00ts_pil900KW_stats1_total\x00\x00\x00\x00n\xfd\xff\xff\x00\x00\x02\x00h\xfd\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00,\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x1b\x00\x00\x00ts_pil900KW_cam_file_number\x00\xae\xfd\xff\xff\x00\x00\x02\x00\xa8\xfd\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x15\x00\x00\x00ts_pil2M_stats1_total\x00\x00\x00\xea\xfd\xff\xff\x00\x00\x02\x00\xe4\xfd\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00,\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00ts_pil2M_cam_file_number\x00\x00\x00\x00*\xfe\xff\xff\x00\x00\x02\x00$\xfe\xff\xff\x00\x00\x01\x02\x10\x00\x00\x00$\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00thorlabs_su_done\x00\x00\x00\x00 \xfe\xff\xff\x00\x00\x00\x01@\x00\x00\x00`\xfe\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00thorlabs_su_setpoint\x00\x00\x00\x00\xa2\xfe\xff\xff\x00\x00\x02\x00\x9c\xfe\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00thorlabs_su_readback\x00\x00\x00\x00\xde\xfe\xff\xff\x00\x00\x02\x00\xd8\xfe\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x15\x00\x00\x00pil900KW_stats1_total\x00\x00\x00\x1a\xff\xff\xff\x00\x00\x02\x00\x14\xff\xff\xff\x00\x00\x01\x02\x10\x00\x00\x00,\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00pil900KW_cam_file_number\x00\x00\x00\x00\x18\xff\xff\xff\x00\x00\x00\x01@\x00\x00\x00X\xff\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00$\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x00pil2M_stats1_total\x00\x00\x96\xff\xff\xff\x00\x00\x02\x00\x90\xff\xff\xff\x00\x00\x01\x02\x10\x00\x00\x00(\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x15\x00\x00\x00pil2M_cam_file_number\x00\x00\x00\x90\xff\xff\xff\x00\x00\x00\x01@\x00\x00\x00\xd0\xff\xff\xff\x00\x00\x01\x03\x10\x00\x00\x00\x1c\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00time\x00\x00\x06\x00\x08\x00\x06\x00\x06\x00\x00\x00\x00\x00\x02\x00\x10\x00\x14\x00\x08\x00\x06\x00\x07\x00\x0c\x00\x00\x00\x10\x00\x10\x00\x00\x00\x00\x00\x01\x02\x10\x00\x00\x00 \x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00seq_num\x00\x08\x00\x0c\x00\x08\x00\x07\x00\x08\x00\x00\x00\x00\x00\x00\x01@\x00\x00\x00h\x04\x00\x00ARROW1'
        data = None
        files = None
        json = None
        params = None
        headers = {'Content-Type': 'application/vnd.apache.arrow.file'}
        cookies = None
        auth = <httpx._client.UseClientDefault object at 0x7f2e41820250>
        follow_redirects = <httpx._client.UseClientDefault object at 0x7f2e41820250>
        timeout = <httpx._client.UseClientDefault object at 0x7f2e41820250>
        extensions = None
   1219         "PATCH",
   1220         url,
   1221         content=content,
   1222         data=data,
   1223         files=files,
   1224         json=json,
   1225         params=params,
   1226         headers=headers,
   1227         cookies=cookies,
   1228         auth=auth,
   1229         follow_redirects=follow_redirects,
   1230         timeout=timeout,
   1231         extensions=extensions,
   1232     )

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpx/_client.py:825, in Client.request(self=<httpx.Client object>, method='PATCH', url='https://tiled-dev.nsls2.bnl.gov/api/v1/table/par...434deb67ae23/streams/primary/internal?partition=0', content=b'ARROW1\x00\x00\xff\xff\xff\xff@\x04\x00\x00\x1...\x00\x00\x00\x01@\x00\x00\x00h\x04\x00\x00ARROW1', data=None, files=None, json=None, params=None, headers={'Content-Type': 'application/vnd.apache.arrow.file'}, cookies=None, auth=<httpx._client.UseClientDefault object>, follow_redirects=<httpx._client.UseClientDefault object>, timeout=<httpx._client.UseClientDefault object>, extensions=None)
    810     warnings.warn(message, DeprecationWarning, stacklevel=2)
    812 request = self.build_request(
    813     method=method,
    814     url=url,
   (...)
    823     extensions=extensions,
    824 )
--> 825 return self.send(request, auth=auth, follow_redirects=follow_redirects)
        request = <Request('PATCH', 'https://tiled-dev.nsls2.bnl.gov/api/v1/table/partition//8d147c26-7ce8-42ea-8eef-434deb67ae23/streams/primary/internal?partition=0')>
        self = <httpx.Client object at 0x7f2daef01450>
        auth = <httpx._client.UseClientDefault object at 0x7f2e41820250>
        follow_redirects = <httpx._client.UseClientDefault object at 0x7f2e41820250>

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpx/_client.py:914, in Client.send(self=<httpx.Client object>, request=<Request('PATCH', 'https://tiled-dev.nsls2.bnl.g...deb67ae23/streams/primary/internal?partition=0')>, stream=False, auth=<httpx.Auth object>, follow_redirects=True)
    910 self._set_timeout(request)
    912 auth = self._build_request_auth(request, auth)
--> 914 response = self._send_handling_auth(
        self = <httpx.Client object at 0x7f2daef01450>
        request = <Request('PATCH', 'https://tiled-dev.nsls2.bnl.gov/api/v1/table/partition//8d147c26-7ce8-42ea-8eef-434deb67ae23/streams/primary/internal?partition=0')>
        auth = <httpx.Auth object at 0x7f2ca97cbaf0>
        follow_redirects = True
    915     request,
    916     auth=auth,
    917     follow_redirects=follow_redirects,
    918     history=[],
    919 )
    920 try:
    921     if not stream:

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpx/_client.py:942, in Client._send_handling_auth(self=<httpx.Client object>, request=<Request('PATCH', 'https://tiled-dev.nsls2.bnl.g...deb67ae23/streams/primary/internal?partition=0')>, auth=<httpx.Auth object>, follow_redirects=True, history=[])
    939 request = next(auth_flow)
    941 while True:
--> 942     response = self._send_handling_redirects(
        self = <httpx.Client object at 0x7f2daef01450>
        request = <Request('PATCH', 'https://tiled-dev.nsls2.bnl.gov/api/v1/table/partition//8d147c26-7ce8-42ea-8eef-434deb67ae23/streams/primary/internal?partition=0')>
        follow_redirects = True
        history = []
    943         request,
    944         follow_redirects=follow_redirects,
    945         history=history,
    946     )
    947     try:
    948         try:

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpx/_client.py:979, in Client._send_handling_redirects(self=<httpx.Client object>, request=<Request('PATCH', 'https://tiled-dev.nsls2.bnl.g...deb67ae23/streams/primary/internal?partition=0')>, follow_redirects=True, history=[])
    976 for hook in self._event_hooks["request"]:
    977     hook(request)
--> 979 response = self._send_single_request(request)
        request = <Request('PATCH', 'https://tiled-dev.nsls2.bnl.gov/api/v1/table/partition//8d147c26-7ce8-42ea-8eef-434deb67ae23/streams/primary/internal?partition=0')>
        self = <httpx.Client object at 0x7f2daef01450>
    980 try:
    981     for hook in self._event_hooks["response"]:

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpx/_client.py:1014, in Client._send_single_request(self=<httpx.Client object>, request=<Request('PATCH', 'https://tiled-dev.nsls2.bnl.g...deb67ae23/streams/primary/internal?partition=0')>)
   1009     raise RuntimeError(
   1010         "Attempted to send an async request with a sync Client instance."
   1011     )
   1013 with request_context(request=request):
-> 1014     response = transport.handle_request(request)
        transport = <tiled.client.transport.Transport object at 0x7f2daef014e0>
        request = <Request('PATCH', 'https://tiled-dev.nsls2.bnl.gov/api/v1/table/partition//8d147c26-7ce8-42ea-8eef-434deb67ae23/streams/primary/internal?partition=0')>
   1016 assert isinstance(response.stream, SyncByteStream)
   1018 response.request = request

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/tiled/client/transport.py:91, in Transport.handle_request(self=<tiled.client.transport.Transport object>, request=<Request('PATCH', 'https://tiled-dev.nsls2.bnl.g...deb67ae23/streams/primary/internal?partition=0')>)
     89     log_request(request)
     90     collect_request(request)
---> 91 response = self.transport.handle_request(request)
        request = <Request('PATCH', 'https://tiled-dev.nsls2.bnl.gov/api/v1/table/partition//8d147c26-7ce8-42ea-8eef-434deb67ae23/streams/primary/internal?partition=0')>
        self.transport = <httpx.HTTPTransport object at 0x7f2daef036d0>
        self = <tiled.client.transport.Transport object at 0x7f2daef014e0>
     92 response.__class__ = TiledResponse
     93 response.request = request

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpx/_transports/default.py:249, in HTTPTransport.handle_request(self=<httpx.HTTPTransport object>, request=<Request('PATCH', 'https://tiled-dev.nsls2.bnl.g...deb67ae23/streams/primary/internal?partition=0')>)
    235 import httpcore
    237 req = httpcore.Request(
    238     method=request.method,
    239     url=httpcore.URL(
   (...)
    247     extensions=request.extensions,
    248 )
--> 249 with map_httpcore_exceptions():
    250     resp = self._pool.handle_request(req)
    252 assert isinstance(resp.stream, typing.Iterable)

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/contextlib.py:153, in _GeneratorContextManager.__exit__(self=<contextlib._GeneratorContextManager object>, typ=<class 'httpcore.ReadTimeout'>, value=ReadTimeout(TimeoutError('The read operation timed out')), traceback=<traceback object>)
    151     value = typ()
    152 try:
--> 153     self.gen.throw(typ, value, traceback)
        typ = <class 'httpcore.ReadTimeout'>
        value = ReadTimeout(TimeoutError('The read operation timed out'))
        self.gen = <generator object map_httpcore_exceptions at 0x7f2ce0634190>
        traceback = <traceback object at 0x7f2c41c1c680>
        self = <contextlib._GeneratorContextManager object at 0x7f2c41b00d30>
    154 except StopIteration as exc:
    155     # Suppress StopIteration *unless* it's the same exception that
    156     # was passed to throw().  This prevents a StopIteration
    157     # raised inside the "with" statement from being suppressed.
    158     return exc is not value

File /nsls2/conda/envs/2025-2.2-py310-tiled/lib/python3.10/site-packages/httpx/_transports/default.py:118, in map_httpcore_exceptions()
    115     raise
    117 message = str(exc)
--> 118 raise mapped_exc(message) from exc
        mapped_exc = <class 'httpx.ReadTimeout'>
        message = 'The read operation timed out'

ReadTimeout: The read operation timed out
'''