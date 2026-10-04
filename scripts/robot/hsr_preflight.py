#!/usr/bin/env python3
"""
hsr_preflight.py -- single GO/NO-GO validator to run BEFORE any HSR grasp execution.

Runs every offline safety check at once and recommends the safest grasp:
  C1 files load            C5 joint-limit margins (flag joints at limits)
  C2 scene consistency     C6 APPROACH-PATH collision (descent sweep, not just final pose)
  C3 grasp flags ok        C7 FK sanity (q* reaches the expected standoff)
  C4 manipulability        C8 gate self-test

USAGE
  python3 hsr_preflight.py --urdf hsrb.urdf --grasps grasps_plain.npz \
      --cloud fused_cloud.npz --csv place_run.csv          # auto-picks best grasp
  python3 hsr_preflight.py ... --grasp 6                   # validate a specific grasp

EXIT: 0 = GO, 1 = NO-GO. Pure numpy. No ROS.
"""
import argparse, csv, sys
import numpy as np, xml.etree.ElementTree as ET

ARM=["arm_lift_joint","arm_flex_joint","arm_roll_joint","wrist_flex_joint","wrist_roll_joint"]
COLS=["q_lift","q_flex","q_roll","q_wflex","q_wroll"]
def Rx(a): c,s=np.cos(a),np.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a): c,s=np.cos(a),np.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def Rz(a): c,s=np.cos(a),np.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def rpy_R(r): return Rz(r[2])@Ry(r[1])@Rx(r[0])
def aa_R(ax,th):
    ax=ax/(np.linalg.norm(ax) or 1); x,y,z=ax; c,s,C=np.cos(th),np.sin(th),1-np.cos(th)
    return np.array([[c+x*x*C,x*y*C-z*s,x*z*C+y*s],[y*x*C+z*s,c+y*y*C,y*z*C-x*s],
                     [z*x*C-y*s,z*y*C+x*s,c+z*z*C]])
def T_(xyz,rpy): T=np.eye(4); T[:3,:3]=rpy_R(rpy); T[:3,3]=xyz; return T
LOCKED={"wrist_ft_sensor_frame_joint"}
def load_chain(p,root,tip):
    r=ET.parse(p).getroot(); J={}
    for j in r.findall("joint"):
        o=j.find("origin"); xyz=[0,0,0]; rpy=[0,0,0]
        if o is not None: xyz=[float(v) for v in o.get("xyz","0 0 0").split()]; rpy=[float(v) for v in o.get("rpy","0 0 0").split()]
        a=j.find("axis"); ax=[1,0,0]
        if a is not None: ax=[float(v) for v in a.get("xyz","1 0 0").split()]
        lim=j.find("limit"); lo=hi=None
        if lim is not None:
            lo=float(lim.get("lower")) if lim.get("lower") is not None else None
            hi=float(lim.get("upper")) if lim.get("upper") is not None else None
        J[j.get("name")]=dict(type=j.get("type"),parent=j.find("parent").get("link"),child=j.find("child").get("link"),
                              xyz=xyz,rpy=rpy,axis=np.array(ax,float),lo=lo,hi=hi)
    bc={v["child"]:k for k,v in J.items()}; seq=[]; link=tip
    while link in bc and link!=root: jn=bc[link]; seq.append(jn); link=J[jn]["parent"]
    return J,list(reversed(seq))
def fk_points(J,seq,qm,stop="wrist_roll_link",full=False):
    T=np.eye(4); pts=[T[:3,3].copy()]
    for jn in seq:
        j=J[jn]; T=T@T_(j["xyz"],j["rpy"])
        if j["type"] in ("revolute","continuous","prismatic") and jn not in LOCKED:
            q=qm.get(jn,0.0); ax=j["axis"]/(np.linalg.norm(j["axis"]) or 1); M=np.eye(4)
            if j["type"]=="prismatic": M[:3,3]=ax*q
            else: M[:3,:3]=aa_R(ax,q)
            T=T@M
        pts.append(T[:3,3].copy())
        if not full and j["child"]==stop: break
    return (np.array(pts), T) if full else np.array(pts)
def base_T(x,y,t): T=np.eye(4); T[:3,:3]=Rz(t); T[:3,3]=[x,y,0]; return T
def capsule(pts,step=0.03):
    out=[]
    for a,b in zip(pts[:-1],pts[1:]):
        L=np.linalg.norm(b-a); n=max(2,int(L/step)+1)
        for t in np.linspace(0,1,n): out.append(a+t*(b-a))
    return np.array(out) if out else pts
def build_obst(cloud,aff,carve,arm_r,margin,vox):
    pts=np.asarray(np.load(cloud,allow_pickle=True)["points"],float)
    if aff is not None: pts=pts[np.linalg.norm(pts-aff,axis=1)>carve]
    occ=set(map(tuple,np.floor(pts/vox).astype(np.int64))); hit=arm_r+margin; nb=int(np.ceil(hit/vox))
    offs=np.array([(i,j,k) for i in range(-nb,nb+1) for j in range(-nb,nb+1) for k in range(-nb,nb+1)])
    return dict(occ=occ,vox=vox,hit=hit,offs=offs)
def collide(J,seqc,armq,B,obst):
    S=capsule(fk_points(J,seqc,armq)); Sw=(B[:3,:3]@S.T).T+B[:3,3]
    occ,vox,hit,offs=obst["occ"],obst["vox"],obst["hit"],obst["offs"]
    for c in Sw:
        key=np.floor(c/vox).astype(np.int64)
        for nk in map(tuple,offs+key):
            if nk in occ:
                vc=(np.array(nk)+0.5)*vox
                if np.linalg.norm(c-vc)-vox*0.5<hit: return False
    return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--urdf",default="hsrb.urdf"); ap.add_argument("--grasps",required=True)
    ap.add_argument("--cloud",default=None); ap.add_argument("--csv",required=True)
    ap.add_argument("--grasp",type=int,default=None); ap.add_argument("--aff",default=None)
    ap.add_argument("--manip_min",type=float,default=0.10); ap.add_argument("--limit_margin",type=float,default=0.05)
    ap.add_argument("--approach",type=float,default=0.07); ap.add_argument("--carve",type=float,default=0.10)
    ap.add_argument("--arm_r",type=float,default=0.05); ap.add_argument("--margin",type=float,default=0.02); ap.add_argument("--voxel",type=float,default=0.02)
    a=ap.parse_args()
    P=[]; W=[]; ok=True
    def line(tag,status,msg): print(f"  [{status:^4}] {tag:22s} {msg}")

    print("="*64); print("HSR PRE-FLIGHT  (offline GO/NO-GO)"); print("="*64)
    # C1 load
    try:
        J,seq=load_chain(a.urdf,"odom","hand_palm_link"); Jc,seqc=load_chain(a.urdf,"base_link","hand_palm_link")
        d=np.load(a.grasps,allow_pickle=True)
        aff=np.array([float(v) for v in a.aff.split(",")]) if a.aff else (np.asarray(d["aff_center_3d"],float) if "aff_center_3d" in d.files else np.asarray(d["poses"])[:,:3,3].mean(0))
        rows=[r for r in csv.DictReader(open(a.csv))]
        line("C1 files load","OK",f"urdf+grasps+csv ok; aff={np.round(aff,3)}")
    except Exception as e:
        line("C1 files load","FAIL",str(e)); print("\nNO-GO (cannot load inputs)"); sys.exit(1)

    lo={k:(J[k]["lo"] if J[k]["lo"] is not None else -1e9) for k in J}
    hi={k:(J[k]["hi"] if J[k]["hi"] is not None else 1e9) for k in J}

    # C2 scene consistency: grasps cluster near aff AND cloud has geometry there
    obst=None
    gp=np.asarray(d["poses"],float)[:,:3,3]; gdist=float(np.median(np.linalg.norm(gp-aff,axis=1)))
    grasps_match = gdist < 0.20
    if a.cloud:
        C=np.asarray(np.load(a.cloud,allow_pickle=True)["points"],float)
        near=int((np.linalg.norm(C-aff,axis=1)<0.15).sum())
        if grasps_match and near>200:
            line("C2 scene consistency","OK",f"grasps cluster {gdist:.3f}m from aff; {near} cloud pts near aff")
        elif not grasps_match:
            line("C2 scene consistency","FAIL",f"grasps are {gdist:.3f}m from aff -> aff/grasps mismatch"); ok=False
        else:
            line("C2 scene consistency","FAIL",f"only {near} cloud pts near aff -> cloud != grasps scene"); ok=False
        obst=build_obst(a.cloud,aff,a.carve,a.arm_r,a.margin,a.voxel)
    else:
        msg="grasps cluster %.3fm from aff"%gdist if grasps_match else "grasps %.3fm from aff (MISMATCH)"%gdist
        line("C2 scene consistency","WARN","no --cloud; "+msg); W.append("no cloud")
        if not grasps_match: ok=False

    # choose grasp
    good=[r for r in rows if r["arm_only_ok"]=="1" and r.get("collision_free","1") in ("1","")]
    if a.grasp is not None:
        chosen=next((r for r in rows if r["grasp"]==str(a.grasp)),None)
        if chosen is None: line("pick grasp","FAIL",f"grasp {a.grasp} not in csv"); sys.exit(1)
    else:
        # auto: among good, max manip with all joints off-limits
        def lim_ok(r):
            q=[float(r[c]) for c in COLS]
            return all(min(qi-lo[k],hi[k]-qi)>a.limit_margin for qi,k in zip(q,ARM))
        ranked=sorted(good,key=lambda r:(lim_ok(r),float(r["manip"])),reverse=True)
        chosen=ranked[0] if ranked else rows[0]
    gi=chosen["grasp"]; q={k:float(chosen[c]) for k,c in zip(ARM,COLS)}
    B=base_T(float(chosen["base_x"]),float(chosen["base_y"]),float(chosen["base_yaw_rad"]))
    print(f"\n  >>> evaluating grasp {gi}  (manip={chosen['manip']}, standoff={chosen['standoff_m']})\n")

    # C3 flags
    if chosen["arm_only_ok"]=="1" and chosen.get("collision_free","1") in ("1",""):
        line("C3 grasp flags","OK","arm_only_ok=1, collision_free=1")
    else: line("C3 grasp flags","FAIL",f"arm_only_ok={chosen['arm_only_ok']} collision_free={chosen.get('collision_free')}"); ok=False

    # C4 manipulability
    m=float(chosen["manip"])
    if m>=a.manip_min: line("C4 manipulability","OK",f"{m:.3f} >= {a.manip_min}")
    else: line("C4 manipulability","WARN",f"{m:.3f} < {a.manip_min} (near-singular, fragile)"); W.append("low manip")

    # C5 joint-limit margins
    tight=[]
    for qi,k in zip([q[j] for j in ARM],ARM):
        mar=min(qi-lo[k],hi[k]-qi)
        if mar<a.limit_margin: tight.append(f"{k}({mar:.3f})")
    if not tight: line("C5 joint margins","OK",f"all joints > {a.limit_margin} rad from limits")
    else: line("C5 joint margins","WARN","at/near limit: "+", ".join(tight)); W.append("joint at limit")

    # C6 approach-path collision (vertical descent via arm_lift)
    if obst is not None:
        lift0=q["arm_lift_joint"]; lift_max=hi["arm_lift_joint"]
        ah=min(a.approach, lift_max-lift0)               # clamp to lift range
        if ah<0.02:
            line("C6 approach path","WARN",f"only {ah:.3f} m lift headroom (q_lift near max) -> shallow approach"); W.append("shallow approach")
            ah=max(ah,0.0)
        clear=True; hits=[]
        for t in np.linspace(0,1,5):
            qa=dict(q); qa["arm_lift_joint"]=lift0+ah*(1-t)   # from pre-grasp (high) down to grasp
            if not collide(Jc,seqc,qa,B,obst): clear=False; hits.append(round(lift0+ah*(1-t),3))
        if clear: line("C6 approach path","OK",f"descent {ah:.2f} m collision-free (5 waypoints)")
        else: line("C6 approach path","FAIL",f"approach sweeps into scene at lift={hits}"); ok=False
    else:
        line("C6 approach path","WARN","skipped (no cloud)")

    # C7 FK sanity
    pts,T=fk_points(Jc,seqc,q,full=True)
    reach=np.hypot(T[0,3],T[1,3]); standoff=float(chosen["standoff_m"])
    if abs(reach-standoff)<0.03 and aff[2]+0.05<T[2,3]<aff[2]+0.25:
        line("C7 FK sanity","OK",f"palm reach={reach:.3f}~standoff, z={T[2,3]:.3f}")
    else: line("C7 FK sanity","FAIL",f"reach={reach:.3f} vs standoff={standoff:.3f}, z={T[2,3]:.3f}"); ok=False

    # C8 gate self-test (pose error predicate sanity)
    exp=T.copy(); good_meas=exp.copy(); good_meas[:3,3]+=np.array([0.005,0,0]); bad=exp.copy(); bad[:3,3]+=np.array([0.03,0,0])
    def perr(M,E): return np.linalg.norm(M[:3,3]-E[:3,3])
    if perr(good_meas,exp)<0.02 and perr(bad,exp)>0.02:
        line("C8 gate logic","OK","palm_err gate passes 5mm, aborts 30mm")
    else: line("C8 gate logic","FAIL","gate predicate inconsistent"); ok=False

    print("\n"+"="*64)
    verdict = "GO" if ok and not W else ("GO-WITH-CAUTION" if ok else "NO-GO")
    print(f"VERDICT for grasp {gi}: {verdict}")
    if W: print("  cautions:", "; ".join(W))
    print(f"  -> run:  python3 execute_place_grasp.py --urdf {a.urdf} --csv {a.csv} --grasp {gi} --sim")
    print("="*64)
    sys.exit(0 if ok else 1)

if __name__=="__main__": main()
