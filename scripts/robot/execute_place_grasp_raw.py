#!/usr/bin/env python3
"""
execute_place_grasp_raw.py -- navigate-then-grasp on HSR via TOPIC-PUBLISHED goals.
CAPTURE-FUNNEL revision (15 Jul 2026), patched against the 12 Jul backup.

Funnel layers (active when close_params.csv from grasp_close_params.py is
present and the selected grasp row is ok=1; otherwise LEGACY behavior):
  L1 cage pre-close : gripper opens to cage_motor (part_width + clearance)
                      instead of 1.2 -- <=1 cm free travel, self-centering.
  L2 depth from cloud: descend computed so fingertips reach close_z
                      (mid-part height), gated against the table plane.
                      Requires --palm_tip_dz (measure once, see --help).
  L3 slow close     : 3.5 s multi-point position ramp, THEN effort-hold via
                      the grasp action goal topic (proven working 14 Jul).

GATES (validated): G1 base-settled, G2 palm_err vs FK(q*), G3 lift+hold.
B* applied RELATIVE to a stored reference odom (--ref_file) -> idempotent.
STAGES: --stage base | arm | grasp | all     --dry (publish nothing)
"""
import argparse, csv, sys, os, numpy as np, xml.etree.ElementTree as ET

ARM=["arm_lift_joint","arm_flex_joint","arm_roll_joint","wrist_flex_joint","wrist_roll_joint"]
COLS=["q_lift","q_flex","q_roll","q_wflex","q_wroll"]; BASEJ=None  # FIXED: use /hsrb/odom only
def Rx(a):c,s=np.cos(a),np.sin(a);return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a):c,s=np.cos(a),np.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def Rz(a):c,s=np.cos(a),np.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def rpyR(r):return Rz(r[2])@Ry(r[1])@Rx(r[0])
def aaR(ax,th):
    ax=ax/(np.linalg.norm(ax) or 1);x,y,z=ax;c,s,C=np.cos(th),np.sin(th),1-np.cos(th)
    return np.array([[c+x*x*C,x*y*C-z*s,x*z*C+y*s],[y*x*C+z*s,c+y*y*C,y*z*C-x*s],[z*x*C-y*s,z*y*C+x*s,c+z*z*C]])
def Tf(xyz,rpy):T=np.eye(4);T[:3,:3]=rpyR(rpy);T[:3,3]=xyz;return T
LOCKED={"wrist_ft_sensor_frame_joint"}
def load_chain(p,root,tip):
    r=ET.parse(p).getroot();J={}
    for j in r.findall("joint"):
        o=j.find("origin");xyz=[0,0,0];rpy=[0,0,0]
        if o is not None:xyz=[float(v) for v in o.get("xyz","0 0 0").split()];rpy=[float(v) for v in o.get("rpy","0 0 0").split()]
        ax=[1,0,0];aa=j.find("axis")
        if aa is not None:ax=[float(v) for v in aa.get("xyz","1 0 0").split()]
        J[j.get("name")]=dict(type=j.get("type"),parent=j.find("parent").get("link"),child=j.find("child").get("link"),xyz=xyz,rpy=rpy,axis=np.array(ax,float))
    bc={v["child"]:k for k,v in J.items()};seq=[];link=tip
    while link in bc and link!=root:jn=bc[link];seq.append(jn);link=J[jn]["parent"]
    return J,list(reversed(seq))
def fk(J,seq,qm):
    T=np.eye(4)
    for jn in seq:
        j=J[jn];T=T@Tf(j["xyz"],j["rpy"])
        if j["type"] in ("revolute","continuous","prismatic") and jn not in LOCKED:
            q=qm.get(jn,0.0);ax=j["axis"]/(np.linalg.norm(j["axis"]) or 1);M=np.eye(4)
            if j["type"]=="prismatic":M[:3,3]=ax*q
            else:M[:3,:3]=aaR(ax,q)
            T=T@M
    return T
def g_settled(cur,B,vel,pt=0.03,yt=3.0,vt=0.02):
    moved=np.hypot(cur[0]-B[0],cur[1]-B[1]);yaw=abs((np.degrees(cur[2]-B[2])+180)%360-180)
    return (moved<pt and yaw<yt and vel<vt),dict(arrived_xy=round(float(moved),4),arrived_yaw=round(float(yaw),2),speed=round(float(vel),4))
def g_palm(m,e,pt=0.02):
    pos=float(np.linalg.norm(m[:3,3]-e[:3,3]));Re=m[:3,:3].T@e[:3,:3];ang=float(np.degrees(np.arccos(np.clip((np.trace(Re)-1)/2,-1,1))))
    return (pos<pt and ang<15),dict(pos_err_m=round(pos,4),ori_err_deg=round(ang,2))
def g_lift(z0,z1,motor,lc,frac=0.5,eps=-0.885):  # calibrated 2026-07-06: empty=-0.8899, rim pinch=-0.877/-0.8834
    rose=z1-z0;held=motor>eps;return (rose>frac*lc and held),dict(z_rise_m=round(float(rose),4),hand_motor=round(float(motor),4),held=bool(held))
def load_row(csv_path,gi):
    r=next((x for x in csv.DictReader(open(csv_path)) if x["grasp"]==str(gi)),None)
    if r is None:sys.exit(f"grasp {gi} not in {csv_path}")
    if r["arm_only_ok"]!="1" or r.get("collision_free","1")=="0":sys.exit(f"grasp {gi} not safe")
    return (float(r["base_x"]),float(r["base_y"]),float(r["base_yaw_rad"])),{k:float(r[c]) for k,c in zip(ARM,COLS)},r
def load_funnel(path,gi):
    """close_params.csv row for this grasp (capture funnel), else None -> legacy."""
    if not os.path.exists(path):
        print(f"[funnel] {path} not found -> LEGACY close (open 1.2, --descend_extra, effort close)")
        return None
    fr=next((x for x in csv.DictReader(open(path)) if x.get("grasp_id")==str(gi)),None)
    if fr is None or fr.get("ok")!="1" or not fr.get("cage_motor_rad"):
        print(f"[funnel] grasp {gi} absent or ok=0 in {path} -> LEGACY close")
        return None
    f=dict(cage=float(fr["cage_motor_rad"]),close_z=float(fr["close_z"]),
           width=float(fr["part_width_m"]),plane=float(fr["plane_z"]))
    # P6 constraint-conditioned: policy columns (absent -> None -> legacy behaviour)
    def _num(k):
        v=fr.get(k,"")
        try: return float(v) if v not in ("",None) else None
        except ValueError: return None
    f["force_level"]=fr.get("force_level") or None
    f["effort"]=_num("effort"); f["hold_margin"]=_num("hold_margin_rad")
    f["lift"]=_num("lift_m")
    f["tilt"]=bool(_num("requires_controlled_tilt"))
    f["retreat"]=fr.get("retreat") or None
    print(f"[funnel] ACTIVE: cage_motor={f['cage']:.3f} (part_width={f['width']*1000:.0f}mm)  close_z={f['close_z']:.3f}  plane_z={f['plane']:.3f}")
    if f.get("force_level"):
        print(f"[policy] force={f['force_level']} effort={f['effort']} "
              f"hold_margin={f['hold_margin']} lift={f['lift']} "
              f"controlled_tilt={f['tilt']} retreat={f['retreat']}")
    else:
        print("[policy] no policy columns in close_params.csv -> legacy closure "
              "(re-run grasp_close_params.py with constraints.json present)")
    return f

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--urdf",default="hsrb.urdf");ap.add_argument("--csv",required=True);ap.add_argument("--grasp",type=int,required=True)
    ap.add_argument("--approach",type=float,default=0.07);ap.add_argument("--lift",type=float,default=0.10)
    ap.add_argument("--grip_effort",type=float,default=0.5)
    ap.add_argument("--descend_extra",type=float,default=0.025,help="LEGACY extra descent after G2 (m); ignored when funnel depth is active")
    ap.add_argument("--close_params",default="close_params.csv",help="per-grasp closing parameters from grasp_close_params.py; absent -> legacy close")
    ap.add_argument("--ignore_policy",action="store_true",help="ignore constraint-derived force/hold/lift columns in close_params.csv (P6)")
    ap.add_argument("--skip_base",action="store_true",help="hold the CURRENT base pose instead of re-driving to plan; use after hsr_final_center so servo alignment (x/y AND yaw) is not undone")
    ap.add_argument("--palm_tip_dz",type=float,default=None,help="vertical offset of hand_palm_link ABOVE fingertips at the grasp wrist pose (m). Measure once at hover: tf_echo base_link hand_palm_link vs base_link hand_l_finger_tip_frame, dz = palm_z - tip_z. Without it, funnel uses --descend_extra for depth (cage + slow close still active)")
    ap.add_argument("--close_time",type=float,default=3.5,help="slow-close position ramp duration (s)")
    ap.add_argument("--hold_backoff",type=float,default=0.005,help="rad to ease OPEN after contact before lifting; 0 = hold exactly at contact (lab_patch_0727_lift L2)")
    ap.add_argument("--lift_time",type=float,default=6.0,help="duration of the post-grasp lift ramp (s); 3.0 reproduces the old single-waypoint behaviour")
    ap.add_argument("--hold_margin",type=float,default=0.010,help="rad to close BEYOND the detected contact position when holding; 0.0 = hold exactly at contact (use 0.0 if over-current recurs)")
    ap.add_argument("--base_time",type=float,default=8.0);ap.add_argument("--arm_time",type=float,default=4.0)
    ap.add_argument("--settle",type=float,default=1.5,help="wait after a move before reading a gate")
    ap.add_argument("--ref_file",default=None,help="store/reuse reference odom for idempotent B*")
    ap.add_argument("--stage",choices=["base","arm","grasp","all"],default="all");ap.add_argument("--dry",action="store_true")
    a=ap.parse_args()
    J,seq=load_chain(a.urdf,"base_link","hand_palm_link")
    B,q,row=load_row(a.csv,a.grasp)
    q["wrist_flex_joint"]=max(q["wrist_flex_joint"],-1.90)  # incident #9: trajectories at the -1.92 URDF limit appear to be silently rejected
    exp=fk(J,seq,q)
    fun=load_funnel(a.close_params,a.grasp)
    # P6: constraint-derived parameters override defaults unless set on the CLI
    if fun is not None and not a.ignore_policy:
        _cli=set(x.split("=")[0] for x in sys.argv[1:] if x.startswith("--"))
        for _flag,_key,_attr in (("--grip_effort","effort","grip_effort"),
                                 ("--hold_margin","hold_margin","hold_margin"),
                                 ("--lift","lift","lift")):
            _v=fun.get(_key)
            if _v is not None and _flag not in _cli:
                print(f"[policy] {_attr}: {getattr(a,_attr)} -> {_v} (from constraints)")
                setattr(a,_attr,_v)
        if fun.get("tilt"):
            print("[policy] NOTE: requires_controlled_tilt -- post-grasp rotation "
                  "must clear the support before any wrist roll (not yet automated)")
        if fun.get("retreat") and fun["retreat"]!="none":
            print(f"[policy] NOTE: retreat plan '{fun['retreat']}' (not yet automated)")
    print(f"grasp {a.grasp}: B*_rel=({B[0]:.3f},{B[1]:.3f},{np.degrees(B[2]):.1f}deg)  manip={row.get('manip')}  clearance={row.get('clearance_m')}")
    print(f"expected palm (base_link): {np.round(exp[:3,3],3)}")

    import rospy
    from control_msgs.msg import FollowJointTrajectoryActionGoal, JointTrajectoryControllerState
    from trajectory_msgs.msg import JointTrajectoryPoint
    from sensor_msgs.msg import JointState
    from nav_msgs.msg import Odometry
    from geometry_msgs.msg import Twist
    try:
        from tmc_control_msgs.msg import GripperApplyEffortActionGoal; HAVE_GRIP=True
    except Exception: HAVE_GRIP=False
    from trajectory_msgs.msg import JointTrajectory
    from hsr_base_drive import BaseDriver

    rospy.init_node("place_grasp_raw",anonymous=True)
    st={"js":{},"odom":None}
    rospy.Subscriber("/hsrb/joint_states",JointState,lambda m:st.update(js=dict(zip(m.name,m.position))))
    rospy.Subscriber("/hsrb/odom",Odometry,lambda m:st.update(odom=m))
    pub_arm=rospy.Publisher("/hsrb/arm_trajectory_controller/command",JointTrajectory,queue_size=1)
    pub_grip_cmd=rospy.Publisher("/hsrb/gripper_controller/command",JointTrajectory,queue_size=1)
    pub_grip=rospy.Publisher("/hsrb/gripper_controller/grasp/goal",GripperApplyEffortActionGoal,queue_size=1) if HAVE_GRIP else None
    rospy.sleep(1.0)  # let publishers register with subscribers (latched-ish settle)
    t0=rospy.Time.now()
    while not st["js"] and (rospy.Time.now()-t0).to_sec()<5: rospy.sleep(0.1)
    if not st["js"]: sys.exit("ABORT: no /hsrb/joint_states")

    def wrap(a):
        return np.arctan2(np.sin(a), np.cos(a))

    def cur_base():
        o = st["odom"]
        if o is None:
            return None
        p = o.pose.pose.position
        q = o.pose.pose.orientation
        yaw = np.arctan2(
            2.0 * (q.w*q.z + q.x*q.y),
            1.0 - 2.0 * (q.y*q.y + q.z*q.z)
        )
        return (p.x, p.y, yaw)

    def speed():
        o=st["odom"]
        if o is None:return 0.0
        v=o.twist.twist
        return float(np.hypot(v.linear.x,v.linear.y)+abs(v.angular.z))

    def meas_T(): j=st["js"];return fk(J,seq,{k:j.get(k,0.0) for k in ARM})
    def publish_traj(pub,names,points,times):
        jt=JointTrajectory();jt.joint_names=names
        for p,t in zip(points,times):
            pt=JointTrajectoryPoint();pt.positions=list(p);pt.velocities=[0.0]*len(names);pt.time_from_start=rospy.Duration(t)
            jt.points.append(pt)
        jt.header.stamp=rospy.Time(0)
        pub.publish(jt)
    def wait(t): rospy.sleep(t)
    def grip_to(pos,dur):
        publish_traj(pub_grip_cmd,["hand_motor_joint"],[[pos]],[dur]);wait(dur+0.5)
    def grip_effort_hold():
        if not HAVE_GRIP: return
        gg=GripperApplyEffortActionGoal();gg.header.stamp=rospy.Time.now();gg.goal_id.stamp=rospy.Time.now()
        gg.goal_id.id=f"grip_{rospy.Time.now().to_nsec()}";gg.goal.effort=a.grip_effort
        for _ in range(3): pub_grip.publish(gg); rospy.sleep(0.05)
        wait(1.5)

    # reference odom (idempotent): stored once, reused
    ref=None
    if a.ref_file and os.path.exists(a.ref_file):
        ref=tuple(float(x) for x in open(a.ref_file).read().split(","))
    if ref is None:
        ref=cur_base()
        if a.ref_file: open(a.ref_file,"w").write("%f,%f,%f"%ref)
    rx,ry,rt=ref
    tx=rx+np.cos(rt)*B[0]-np.sin(rt)*B[1];ty=ry+np.sin(rt)*B[0]+np.cos(rt)*B[1];tt=rt+B[2]
    print(f"[plan] ref odom=({rx:.3f},{ry:.3f},{np.degrees(rt):.1f}deg) -> target odom=({tx:.3f},{ty:.3f},{np.degrees(tt):.1f}deg)")

    # funnel depth pre-computation + gate (BEFORE any motion, so --dry shows it)
    d_extra=a.descend_extra
    if fun is not None and a.palm_tip_dz is not None:
        d_extra=float(exp[2,3]-(fun["close_z"]+a.palm_tip_dz))
        tip_pred=exp[2,3]-d_extra-a.palm_tip_dz
        print(f"[funnel] computed descend={d_extra:.3f} m  predicted fingertip z={tip_pred:.3f} (close_z={fun['close_z']:.3f})")
        if d_extra<-0.005 or d_extra>0.08:
            sys.exit(f"ABORT: computed descend {d_extra:.3f} outside [0, 0.08] -- check --palm_tip_dz / close_z / grasp height")
        if tip_pred<fun["plane"]+0.020:
            sys.exit(f"ABORT: predicted fingertips {tip_pred:.3f} within 2 cm of table plane {fun['plane']:.3f}")
        d_extra=max(0.0,d_extra)
    elif fun is not None:
        print(f"[funnel] --palm_tip_dz not given -> depth via --descend_extra={a.descend_extra} (cage + slow close still ACTIVE)")
    if a.dry: print("[dry] publishing nothing."); return

    if a.skip_base:
        _c=cur_base()
        if _c is not None:
            tx,ty,tt=_c
            print(f"[skip_base] holding servo-aligned base pose ({tx:.3f},{ty:.3f},{np.degrees(tt):.1f}deg) -- NOT re-driving to plan")
    print("[1] base -> standoff (traj ctrl /hsrb/omni_base_controller/command)")
    if cur_base() is None:
        sys.exit("ABORT: no /hsrb/odom")
    # incident #10 guard: silent odom reset + stale ref -> drove into table.
    stfile = (a.ref_file + ".state") if a.ref_file else None
    cur0 = cur_base()
    if stfile and os.path.exists(stfile) and cur0 is not None:
        lx, ly, lt = [float(x) for x in open(stfile).read().split(",")]
        if abs(cur0[0]) < 0.003 and abs(cur0[1]) < 0.003 and np.hypot(lx, ly) > 0.15:
            sys.exit("ABORT: odom reads exactly ~(0,0,0) but the last stage ended at "
                     "(%.2f,%.2f) -- ODOM WAS RESET; the stored ref/plan is stale. "
                     "rm -f place_run.ref* and run a FULL fresh cycle (incident #10)." % (lx, ly))
    bd = BaseDriver()
    reached, binfo = bd.move_to(tx, ty, tt)
    print(f"    base driver: reached={reached} {binfo}")
    wait(a.settle)
    cur = cur_base()
    ok,info=g_settled(cur,(tx,ty,tt),speed())
    print(f"    base controller reached: {reached}")
    print(f"    G1 base-settled: {ok} {info}")
    if not ok: sys.exit("ABORT G1")
    if stfile:
        c=cur_base(); open(stfile,"w").write("%f,%f,%f"%c)
    if a.stage=="base": print("stage=base done."); return

    lift_max=0.69; ah=max(0.0,min(a.approach,lift_max-q["arm_lift_joint"]))
    pre=[q[k] for k in ARM]; pre[0]=q["arm_lift_joint"]+ah; grasp=[q[k] for k in ARM]
    open_pos=fun["cage"] if fun is not None else 1.2
    mode="CAGE" if fun is not None else "wide"
    print(f"[2] open gripper to {open_pos:.3f} ({mode}), then arm hover(+{ah:.3f}) and descend (topic-published)")
    grip_to(open_pos,1.5)
    # lift-first transit (incident #8, 16 Jul): raise lift while still tucked,
    # THEN extend at height, THEN descend -- simultaneous interpolation swept
    # the hand through tabletop space at increased table height.
    cur_arm=[st["js"].get(k,0.0) for k in ARM]
    tuck_up=list(cur_arm); tuck_up[0]=pre[0]
    publish_traj(pub_arm,ARM,[tuck_up,pre,grasp],[a.arm_time,2*a.arm_time,2*a.arm_time+3.0]); wait(2*a.arm_time+3.0+a.settle)
    ok,info=g_palm(meas_T(),exp); print(f"    G2 palm_err: {ok} {info}")
    if not ok:
        print("    measured arm:",{k:round(st['js'].get(k,0.0),3) for k in ARM})
        print("    commanded q*:",{k:round(q[k],3) for k in ARM})
        sys.exit("ABORT G2")
    if a.stage=="arm": print("stage=arm done."); return

    print(f"[3] extra descend {d_extra:.3f} m, then close")
    down=[q[k] for k in ARM]; down[0]=max(0.0,q["arm_lift_joint"]-d_extra)
    publish_traj(pub_arm,ARM,[down],[2.0]); wait(2.5)
    if abs(st["js"]["arm_lift_joint"]-down[0])>0.01:
        sys.exit(f"ABORT: descend NOT EXECUTED (lift at {st['js']['arm_lift_joint']:.3f}, commanded {down[0]:.3f}) -- trajectory dropped")
    z0=meas_T()[2,3]
    if fun is not None:
        # L3 slow close: quasi-static position ramp cage -> floor, then effort hold
        floor=max(fun["cage"]-1.15,-0.60)
        ramp=np.linspace(fun["cage"]-0.05,floor,4)
        times=np.linspace(a.close_time/4.0,a.close_time,4)
        print(f"[funnel] slow close: {fun['cage']:.3f} -> {floor:.3f} over {a.close_time:.1f}s, then effort hold {a.grip_effort}")
        # ---- incident #11 (v3): CONTACT-STOP close ----
        # Commanding a fixed endpoint stalls the motor against the object and
        # trips over-current. Step closed, watch hand_motor, stop at contact,
        # then hold at the MEASURED position (zero error -> minimal current).
        step = 0.04          # rad per increment
        dt   = 0.35          # s per increment
        cmd  = float(ramp[0])
        # INCIDENT #12 guard 1: confirm the gripper actually REACHED the cage
        # position before closing (publishing != moving).
        publish_traj(pub_grip_cmd,["hand_motor_joint"],[[cmd]],[0.4])
        _t0 = rospy.Time.now()
        while (rospy.Time.now()-_t0).to_sec() < 2.5:
            if abs(float(st["js"].get("hand_motor_joint", cmd)) - cmd) < 0.02: break
            rospy.sleep(0.1)
        wait(0.3)
        prev = float(st["js"].get("hand_motor_joint", cmd))
        start_pos = prev
        TRAVEL_ARM = 0.03      # rad of real travel before contact detection arms
        armed = False; latency_retries = 0
        print("    [close] start at %+.3f (cage %+.3f)" % (start_pos, cmd))
        stalled = 0; reason = "floor"
        while cmd > floor + 1e-6:
            cmd = max(cmd - step, floor)
            publish_traj(pub_grip_cmd,["hand_motor_joint"],[[cmd]],[dt]); wait(dt+0.15)
            meas  = float(st["js"].get("hand_motor_joint", cmd))
            moved = prev - meas          # how far the fingers actually closed
            lag   = meas - cmd           # >0 => fingers behind command = resistance
            print("    [close] cmd %+.3f  meas %+.3f  moved %.3f  lag %+.3f"
                  % (cmd, meas, moved, lag))
            prev = meas
            # INCIDENT #12 guard 2: contact detection is armed only once the
            # fingers have demonstrably started moving; before that a stalled
            # reading is command latency, not an object.
            if not armed:
                if (start_pos - meas) > TRAVEL_ARM:
                    armed = True
                elif latency_retries < 4:
                    latency_retries += 1
                    print("    [close] fingers not moving yet (travel %.3f) -- "
                          "re-issuing, retry %d" % (start_pos - meas, latency_retries))
                    cmd += step          # undo this step; re-issue the same command
                    wait(dt)
                    continue
                else:
                    reason = "no_motion"; break
            # 22 Jul: break at the FIRST sign of resistance. Requiring two
            # consecutive stalled steps left the motor commanded ~0.09 rad
            # (~6 mm) past the stall point for ~1 s -> over-current fault ->
            # frozen joint -> lift never executes.
            # lab_patch_0727_lift L1: break at the FIRST sign of resistance.
            # The old thresholds let the close run two steps past contact
            # (trial 4: resistance at -0.302, stopped at -0.355), and the
            # extra compression is what the lift then trips over.
            if lag > 0.010 or moved < 0.80 * step:
                reason = "contact"; break
        hold = float(st["js"].get("hand_motor_joint", cmd))
        # lab_patch_0727_lift L2: ease off slightly after contact. The spring
        # fingers keep the object; relieving compression leaves current
        # headroom for the lift, which is where the fault occurs.
        hold = max(hold - a.hold_margin, floor)
        hold = min(hold + a.hold_backoff, float(ramp[0]))
        print("    [close] stop reason=%s -> holding at measured %+.3f (margin %.3f)"
              % (reason, hold, a.hold_margin))
        publish_traj(pub_grip_cmd,["hand_motor_joint"],[[hold]],[0.4]); wait(0.6)
        if reason == "floor":
            print("    NOTE: closed to floor without detecting contact -- likely EMPTY grasp")
        elif reason == "no_motion":
            sys.exit("ABORT: gripper never moved from the cage position -- "
                     "controller not accepting commands (check for a joint fault "
                     "on the touchscreen). No grasp attempted. (incident #12)")
    elif HAVE_GRIP:
        gg=GripperApplyEffortActionGoal();gg.header.stamp=rospy.Time.now();gg.goal_id.stamp=rospy.Time.now()
        gg.goal_id.id=f"grip_{rospy.Time.now().to_nsec()}";gg.goal.effort=a.grip_effort
        for _ in range(3): pub_grip.publish(gg); rospy.sleep(0.05)
        wait(3.0)
    else:
        jt=JointTrajectory();jt.joint_names=["hand_motor_joint"];p=JointTrajectoryPoint();p.positions=[-0.1];p.time_from_start=rospy.Duration(2);jt.points=[p];pub_grip_cmd.publish(jt);wait(2.5)
    lift_avail=min(a.lift,0.69-q["arm_lift_joint"]-0.005)
    if lift_avail<0.03: sys.exit(f"ABORT: only {lift_avail:.3f} m lift headroom -- cannot verify grasp (incident #9)")
    print(f"[4] lift {lift_avail:.3f} m + G3"); up=[q[k] for k in ARM]; up[0]=q["arm_lift_joint"]+lift_avail
    lift_pre=st["js"]["arm_lift_joint"]
    # lab_patch_0727_lift L3: ramp the lift over --lift_time through several
    # waypoints instead of one 3 s command. A hard start back-drives the
    # compliant fingers; halving the acceleration halves that disturbance.
    _n = 4
    _pts, _ts = [], []
    for _i in range(1, _n + 1):
        _p = [q[k] for k in ARM]
        _p[0] = q["arm_lift_joint"] + lift_avail * _i / float(_n)
        _pts.append(_p); _ts.append(a.lift_time * _i / float(_n))
    publish_traj(pub_arm, ARM, _pts, _ts); wait(a.lift_time + a.settle)
    lift_post=st["js"]["arm_lift_joint"]
    print(f"    lift execution: arm_lift {lift_pre:.3f} -> {lift_post:.3f} (commanded {up[0]:.3f})")
    if abs(lift_post-lift_pre)<0.01:
        print("    WARNING: LIFT NOT EXECUTED -- trajectory dropped/controller fault; G3 below reflects a non-lift, not a grasp verdict")
    z1=meas_T()[2,3]; motor=st["js"].get("hand_motor_joint",0.0)
    ok,info=g_lift(z0,z1,motor,lift_avail); print(f"    G3 lift-verify: {ok} {info}")
    print("RESULT:", "GRASP OK" if ok else "GRASP FAILED (no z-rise or empty gripper)")

if __name__=="__main__": main()
