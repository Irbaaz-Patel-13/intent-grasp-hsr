#!/usr/bin/env python3
"""
hsr_base_placement.py -- reachability-aware base placement for HSR grasps (pure numpy).

WHY
  The HSR blocker is base PLACEMENT, not the wrist: targets at ~0.7 m are beyond
  the arm's ~0.63 m fixed-base reach, and folding a large base move INTO the grasp
  trajectory is what triggers "Failed to follow commanded trajectory". Fix: compute
  a base standoff that puts the target in the arm's comfortable envelope, NAVIGATE
  there first, then execute an ARM-ONLY grasp (short, trackable, fault-free).

WHAT IT OUTPUTS  (per grasp)
  base_x, base_y, base_yaw  : where to drive the base (same frame as the input grasps)
  arm joint solution         : the grasp config to run once parked (arm-only)
  arm_only_ok                : True => grasp reachable with base STATIONARY at the standoff
  standoff_m                 : final base->target distance (should sit ~comfort_reach)
  manip                      : Yoshikawa manipulability (higher = safer, away from singularity)

USAGE
  python3 hsr_base_placement.py --urdf hsrb.urdf --grasps candidates_mug.npz --topk 5
  python3 hsr_base_placement.py --urdf hsrb.urdf --grasps grasps_plain.npz --frame base_link

DEPS: numpy (+ matplotlib for the optional map). No scipy, no ROS.
CAVEATS: kinematic only -- NO collision/self-collision/table checks. "arm_only_ok"
  means kinematically reachable from the standoff, not collision-free.
"""
import argparse, glob, csv, os
import numpy as np, xml.etree.ElementTree as ET

# --- rotation / FK core (pure numpy, shared with the feasibility oracle) ---
def Rx(a): c,s=np.cos(a),np.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a): c,s=np.cos(a),np.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def Rz(a): c,s=np.cos(a),np.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def rpy_R(r): return Rz(r[2])@Ry(r[1])@Rx(r[0])
def aa_R(ax,th):
    ax=ax/(np.linalg.norm(ax) or 1); x,y,z=ax; c,s,C=np.cos(th),np.sin(th),1-np.cos(th)
    return np.array([[c+x*x*C,x*y*C-z*s,x*z*C+y*s],[y*x*C+z*s,c+y*y*C,y*z*C-x*s],
                     [z*x*C-y*s,z*y*C+x*s,c+z*z*C]])
def logSO3(R):
    tr=np.clip((np.trace(R)-1)/2,-1,1); ang=np.arccos(tr)
    if ang<1e-8: return np.zeros(3)
    if abs(np.pi-ang)<1e-6:
        k=int(np.argmax(np.diag(R))); v=np.zeros(3); v[k]=np.sqrt(max((R[k,k]+1)/2,0))
        if v[k]>1e-9:
            v[(k+1)%3]=R[(k+1)%3,k]/(2*v[k]); v[(k+2)%3]=R[(k+2)%3,k]/(2*v[k])
        return ang*v/(np.linalg.norm(v) or 1)
    w=np.array([R[2,1]-R[1,2],R[0,2]-R[2,0],R[1,0]-R[0,1]]); return ang*w/(2*np.sin(ang))
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
def fk(J,seq,qm):
    T=np.eye(4); cols={}
    for jn in seq:
        j=J[jn]; T=T@T_(j["xyz"],j["rpy"])
        if j["type"] in ("revolute","continuous","prismatic") and jn not in LOCKED:
            q=qm.get(jn,0.0); ax=j["axis"]/(np.linalg.norm(j["axis"]) or 1); axw=T[:3,:3]@ax; ow=T[:3,3].copy()
            M=np.eye(4)
            if j["type"]=="prismatic": M[:3,3]=ax*q; cols[jn]=("p",axw,ow)
            else: M[:3,:3]=aa_R(ax,q); cols[jn]=("r",axw,ow)
            T=T@M
    return T,cols
def errv(Tc,Tt): return np.concatenate([Tt[:3,3]-Tc[:3,3], Tc[:3,:3]@logSO3(Tc[:3,:3].T@Tt[:3,:3])])
def jac(cols,act,p):
    Jm=np.zeros((6,len(act)))
    for i,jn in enumerate(act):
        t,axw,ow=cols[jn]
        if t=="p": Jm[:3,i]=axw
        else: Jm[:3,i]=np.cross(axw,p-ow); Jm[3:,i]=axw
    return Jm
def ik(J,seq,Tt,act,lo,hi,rng,seed=None,iters=80,pos_tol=5e-3,ori_tol=np.deg2rad(5),lam=1e-2):
    if seed is not None: q=np.array([seed.get(k,0.0) for k in act],float)
    else: q=np.array([rng.uniform(max(lo[k],-np.pi),min(hi[k],np.pi)) if np.isfinite(lo[k]) else rng.uniform(-np.pi,np.pi) for k in act])
    for _ in range(iters):
        Tc,cols=fk(J,seq,dict(zip(act,q))); e=errv(Tc,Tt)
        if np.linalg.norm(e[:3])<pos_tol and np.linalg.norm(e[3:])<ori_tol: return True,q
        Jm=jac(cols,act,Tc[:3,3]); dq=np.clip(np.linalg.solve(Jm.T@Jm+lam*np.eye(len(act)),Jm.T@e),-0.4,0.4)
        q=np.array([np.clip(qi+dqi,lo[k],hi[k]) for qi,dqi,k in zip(q,dq,act)])
    Tc,_=fk(J,seq,dict(zip(act,q))); e=errv(Tc,Tt)
    return (np.linalg.norm(e[:3])<pos_tol and np.linalg.norm(e[3:])<ori_tol),q
def solve(J,seq,Tt,act,lo,hi,restarts=30,seed=None,**kw):
    rng=np.random.default_rng(11)
    if seed is not None:
        ok,q=ik(J,seq,Tt,act,lo,hi,rng,seed=seed,**kw)
        if ok: return True,q
    for _ in range(restarts):
        ok,q=ik(J,seq,Tt,act,lo,hi,rng,**kw)
        if ok: return True,q
    return False,q


# ---------------- grasp loading + base placement ----------------
def quatR(q):
    x,y,z,w=q/(np.linalg.norm(q) or 1)
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                     [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def toT(x):
    x=np.asarray(x,float)
    if x.shape==(4,4): return x
    if x.shape==(7,): T=np.eye(4); T[:3,:3]=quatR(x[3:]); T[:3,3]=x[:3]; return T
    if x.shape==(3,): T=np.eye(4); T[:3,3]=x; return T
    if x.ndim==3 and x.shape[1:]==(4,4): return x[0]
    raise ValueError(f"obj pose shape {x.shape}")
def load(path):
    d=np.load(path,allow_pickle=True)
    if "grasp_pose_world" in d:
        P=np.asarray(d["grasp_pose_world"],float)
        sc=np.asarray(d["quality_score"],float) if "quality_score" in d.files else np.ones(len(P))
        return P,sc,"world"
    if "poses" in d:
        P=np.asarray(d["poses"],float)
        sc=np.asarray(d["scores"],float) if "scores" in d.files else np.ones(len(P))
        return P,sc,"base_link"
    raise ValueError(f"{path}: no grasp_pose_world / poses")

def base_T(bx,by,byaw): T=np.eye(4); T[:3,:3]=Rz(byaw); T[:3,3]=[bx,by,0]; return T

def fk_link_points(J,seq,qm,stop_link="wrist_roll_link"):
    """Arm link-frame origins in base_link frame (for the collision capsule)."""
    T=np.eye(4); pts=[T[:3,3].copy()]
    for jn in seq:
        j=J[jn]; T=T@T_(j["xyz"],j["rpy"])
        if j["type"] in ("revolute","continuous","prismatic") and jn not in LOCKED:
            q=qm.get(jn,0.0); ax=j["axis"]/(np.linalg.norm(j["axis"]) or 1); M=np.eye(4)
            if j["type"]=="prismatic": M[:3,3]=ax*q
            else: M[:3,:3]=aa_R(ax,q)
            T=T@M
        pts.append(T[:3,3].copy())
        if j["child"]==stop_link: break
    return np.array(pts)

def capsule_spheres(pts, step=0.03):
    out=[]
    for a,b in zip(pts[:-1],pts[1:]):
        L=np.linalg.norm(b-a); n=max(2,int(L/step)+1)
        for t in np.linspace(0,1,n): out.append(a+t*(b-a))
    return np.array(out) if len(out) else pts

def collision_eval(Jc,seqc,arm,q_full,full,obst):
    """Return (collision_free, clearance_m) for a full-chain solution vs obstacle voxels."""
    bm=dict(zip(full,q_full)); B=base_T(bm["odom_x"],bm["odom_y"],bm["odom_t"])
    armq={k:q_full[i] for i,k in enumerate(arm)}
    S=capsule_spheres(fk_link_points(Jc,seqc,armq))
    Sw=(B[:3,:3]@S.T).T + B[:3,3]
    occ,vox,hit_r,offs=obst["occ"],obst["vox"],obst["hit_r"],obst["offs"]
    free=True; clr=9.0
    for c3 in Sw:
        key=np.floor(c3/vox).astype(np.int64)
        for nk in map(tuple, offs+key):
            if nk in occ:
                vc=(np.array(nk)+0.5)*vox; dd=np.linalg.norm(c3-vc)-vox*0.5
                clr=min(clr,dd)
                if dd<hit_r: free=False
        if not free: break
    return free,float(clr)

BASE_CLEAR=0.32  # base centre min distance to body-strike-height cloud (m)

def build_obstacles(cloud_path,aff,carve,arm_r,margin,vox):
    raw=np.asarray(np.load(cloud_path,allow_pickle=True)["points"],float)
    pts=raw
    if aff is not None: pts=pts[np.linalg.norm(pts-aff,axis=1)>carve]
    occ=set(map(tuple, np.floor(pts/vox).astype(np.int64)))
    hit_r=arm_r+margin; nb=int(np.ceil(hit_r/vox))
    offs=np.array([(i,j,k) for i in range(-nb,nb+1) for j in range(-nb,nb+1) for k in range(-nb,nb+1)])
    # base keep-out: anything at body-strike height is ground the base must not enter
    band=raw[(raw[:,2]>0.30)&(raw[:,2]<0.65)][:,:2]
    kv=(np.unique(np.floor(band/0.05).astype(np.int64),axis=0)*0.05+0.025) if len(band) else np.zeros((0,2))
    print(f"base keep-out: {len(kv)} cells at body-strike height (z 0.30-0.65 m)")
    return dict(occ=occ,vox=vox,hit_r=hit_r,offs=offs,n=len(occ),keepout=kv)

def manip(J,seq,act,q):
    T,cols=fk(J,seq,dict(zip(act,q))); Jm=jac(cols,act,T[:3,3])
    return float(np.sqrt(max(np.linalg.det(Jm.T@Jm),0)))   # sqrt(det(J^T J)) valid for m<6 DoF arm

def place_one(J,seq,arm,lo,hi,G,restarts=22,want=6,Jc=None,seqc=None,obst=None):
    """Free-base IK; collect feasible (base,arm) solutions; prefer a COLLISION-FREE
    one (if a scene is given), otherwise the most comfortable (max score)."""
    full=arm+["odom_x","odom_y","odom_t"]
    lo2=dict(lo); hi2=dict(hi); lo2["odom_t"],hi2["odom_t"]=-np.pi,np.pi
    for k in ("odom_x","odom_y"): lo2[k],hi2[k]=-1.2,1.2
    rng=np.random.default_rng(3); sols=[]
    cap = (28 if obst else restarts); target=(12 if obst else want)
    for _ in range(cap):
        ok,q=ik(J,seq,G,full,lo2,hi2,rng,iters=70)
        if ok:
            sols.append(q)
            if len(sols)>=target: break
    if not sols:
        return dict(ok=False,bx=0,by=0,byaw=0,q=None,standoff=0,manip=0,collision_free=None,clearance=None)
    p=G[:3,3]
    ko=obst.get("keepout") if obst is not None else None
    ko=ko if (ko is not None and len(ko)) else None
    def table_clear(q):
        if ko is None: return None
        bm=dict(zip(full,q))
        return float(np.min(np.linalg.norm(ko-np.array([bm["odom_x"],bm["odom_y"]]),axis=1)))
    if ko is not None:
        kept=[q for q in sols if table_clear(q)>=BASE_CLEAR]
        if not kept:
            return dict(ok=False,bx=0,by=0,byaw=0,q=None,standoff=0,manip=0,
                        collision_free=False,clearance=None,table_clear=None)
        sols=kept
    def score(q):
        bm=dict(zip(full,q)); bx,by=bm["odom_x"],bm["odom_y"]
        so=np.hypot(p[0]-bx,p[1]-by); disp=np.hypot(bx,by)
        return (manip(J,seq,arm,q[:5]) - 0.30*disp - 1.0*max(0,so-0.55) - 1.0*max(0,0.35-so))
    cfree=None; clr=None
    if obst is not None:
        ev=[(q,)+collision_eval(Jc,seqc,arm,q,full,obst) for q in sols]   # (q,free,clr)
        free=[e for e in ev if e[1]]
        if free:
            q,cfree,clr=max(free,key=lambda e:score(e[0]))[0], True, None
            best=q; clr=[e[2] for e in ev if e[0] is best][0]
        else:                                  # none clear -> least-bad (max clearance)
            e=max(ev,key=lambda e:e[2]); best=e[0]; cfree=False; clr=e[2]
    else:
        best=max(sols,key=score)
    bm=dict(zip(full,best)); bx,by,bt=bm["odom_x"],bm["odom_y"],bm["odom_t"]
    standoff=float(np.hypot(p[0]-bx,p[1]-by))
    return dict(ok=True,bx=float(bx),by=float(by),byaw=float(bt),q=best[:5],
                standoff=standoff,manip=manip(J,seq,arm,best[:5]),collision_free=cfree,clearance=clr,
                table_clear=table_clear(best))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--urdf",default="hsrb.urdf"); ap.add_argument("--grasps",required=True)
    ap.add_argument("--frame",choices=["auto","world","base_link"],default="auto")
    ap.add_argument("--d_fwd",type=float,default=0.40,help="comfortable base->target standoff (m)")
    ap.add_argument("--topk",type=int,default=0,help="only place the top-K by score (0=all)")
    ap.add_argument("--out_prefix",default="base_place")
    ap.add_argument("--cloud",default=None,help="fused scene npz -> enable collision-aware selection")
    ap.add_argument("--aff",default=None,help="object center x,y,z to carve from obstacles")
    ap.add_argument("--carve",type=float,default=0.10); ap.add_argument("--arm_r",type=float,default=0.05)
    ap.add_argument("--margin",type=float,default=0.02); ap.add_argument("--voxel",type=float,default=0.02)
    a=ap.parse_args()
    J,seq=load_chain(a.urdf,"odom","hand_palm_link")
    arm=["arm_lift_joint","arm_flex_joint","arm_roll_joint","wrist_flex_joint","wrist_roll_joint"]
    lo={k:(J[k]["lo"] if J[k]["lo"] is not None else -10.0) for k in J}
    hi={k:(J[k]["hi"] if J[k]["hi"] is not None else 10.0) for k in J}
    Jc,seqc=load_chain(a.urdf,"base_link","hand_palm_link")
    obst=None
    if a.cloud:
        aff=np.array([float(v) for v in a.aff.split(",")]) if a.aff else None
        obst=build_obstacles(a.cloud,aff,a.carve,a.arm_r,a.margin,a.voxel)
        print(f"collision scene: {obst['n']} voxels (carve {a.carve} m around aff={aff})")

    files=sorted(glob.glob(a.grasps)) or [a.grasps]
    P=[]; S=[]
    for f in files:
        Pi,Si,fr=load(f); P.append(Pi); S.append(Si)
    P=np.concatenate(P,0); S=np.concatenate(S,0)
    if a.topk>0:
        idx=np.argsort(-S)[:a.topk]; P=P[idx]; S=S[idx]
    print(f"placing {len(P)} grasp(s) from {len(files)} file(s); standoff={a.d_fwd} m")

    rows=[]; okc=0
    for i in range(len(P)):
        r=place_one(J,seq,arm,lo,hi,P[i],Jc=Jc,seqc=seqc,obst=obst); okc+=r["ok"]
        rows.append((i,float(S[i]),r))
    print(f"\narm-only reachable after placement: {okc}/{len(P)} ({100*okc/len(P):.0f}%)")
    if obst is not None:
        cf=[r["collision_free"] for *_,r in rows if r["ok"]]
        print(f"collision-free placements        : {sum(bool(x) for x in cf)}/{len(cf)} ({100*sum(bool(x) for x in cf)/max(len(cf),1):.0f}%)  <- after preferring clear standoffs")
        tc=[r.get("table_clear") for *_,r in rows if r["ok"] and r.get("table_clear") is not None]
        if tc: print(f"base keep-out clearance          : min {min(tc):.3f} m, median {float(np.median(tc)):.3f} m  (limit {BASE_CLEAR})")
    print(f"{'g':>3} {'score':>6} {'ok':>3} {'base_x':>7} {'base_y':>7} {'yaw_deg':>7} {'standoff':>8} {'manip':>7}")
    for i,sc,r in rows[:min(len(rows),12)]:
        print(f"{i:3d} {sc:6.2f} {str(r['ok']):>3} {r['bx']:7.3f} {r['by']:7.3f} "
              f"{np.degrees(r['byaw']):7.1f} {r['standoff']:8.3f} {r['manip']:7.4f}")
    if len(rows)>12: print(f"  ... ({len(rows)-12} more in CSV)")

    with open(f"{a.out_prefix}.csv","w",newline="") as fh:
        w=csv.writer(fh); w.writerow(["grasp","score","arm_only_ok","base_x","base_y","base_yaw_rad",
            "standoff_m","manip","collision_free","clearance_m"]+[f"q_{j}" for j in ["lift","flex","roll","wflex","wroll"]])
        for i,sc,r in rows:
            cf=("" if r["collision_free"] is None else int(bool(r["collision_free"])))
            cl=("" if r.get("clearance") is None else round(float(r["clearance"]),4))
            w.writerow([i,round(sc,3),int(r["ok"]),round(r["bx"],4),round(r["by"],4),round(r["byaw"],4),
                        round(r["standoff"],4),round(r["manip"],5),cf,cl]+
                       ([round(float(x),4) for x in r["q"]] if r["ok"] else [""]*5))
    print(f"wrote {a.out_prefix}.csv")

    # optional top-down map of the best grasp
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        best=max([r for *_,r in [(i,sc,r) for i,sc,r in rows]], key=lambda r:(r["ok"],r["manip"]))
        gi=[r for i,sc,r in rows].index(best); G=P[gi]; p=G[:3,3]
        fig,ax=plt.subplots(figsize=(5.5,5.5))
        ax.scatter([0],[0],c="k",marker="s",s=80,label="current base (origin)")
        ax.scatter([p[0]],[p[1]],c="#c0392b",s=90,label="grasp target")
        ax.scatter([best["bx"]],[best["by"]],c="#27ae60",marker="*",s=260,label="recommended base")
        th=np.linspace(0,2*np.pi,100); ax.plot(p[0]+0.633*np.cos(th),p[1]+0.633*np.sin(th),"--",c="grey",lw=.8,label="0.633 m reach of target")
        ax.annotate("",xy=(p[0],p[1]),xytext=(best["bx"],best["by"]),arrowprops=dict(arrowstyle="->",color="#27ae60"))
        ax.set_aspect("equal"); ax.legend(fontsize=8,loc="lower right"); ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
        ax.set_title(f"Base placement (best grasp #{gi}, standoff {best['standoff']:.2f} m)")
        plt.tight_layout(); plt.savefig(f"{a.out_prefix}_map.png",dpi=140); print(f"wrote {a.out_prefix}_map.png")
    except Exception as e: print("map skipped:",e)

if __name__=="__main__": main()
