#!/usr/bin/env python3
"""
hsr_collision_check.py -- offline scene-collision screen for HSR base-placement grasps.

Closes the last gap: the bio_ik check was collision-blind (empty planning scene).
This loads the fused scene cloud, carves out the target object, models the arm as a
capsule chain, and tests each placement's arm config for collision against the real
scene (desk, clutter, table edge, floor). Pure numpy (voxel occupancy) -- no scipy.

USAGE
  python3 hsr_collision_check.py --urdf hsrb.urdf --csv place_real.csv \
      --cloud fused_cloud.npz --aff 0.711,0.028,0.504

WHAT IT CHECKS
  Arm body links base_link..wrist_roll_link (the GRIPPER/fingers are excluded --
  they are meant to contact the object). Obstacles = cloud minus a carve sphere
  around the affordance (so the object being grasped isn't counted as a hit).
  A grasp is collision-free if every arm sphere clears obstacles by > margin.

CAVEATS (state in writeup)
  * Conservative arm-vs-scene screen, NOT full mesh collision. Sphere radii approximate.
  * The cloud is a snapshot of VISIBLE surfaces -> occluded geometry is unrepresented
    (the check can miss collisions behind visible surfaces). Strong, not perfect.
"""
import argparse, csv
import numpy as np, xml.etree.ElementTree as ET

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
        J[j.get("name")]=dict(type=j.get("type"),parent=j.find("parent").get("link"),
                              child=j.find("child").get("link"),xyz=xyz,rpy=rpy,axis=np.array(ax,float))
    bc={v["child"]:k for k,v in J.items()}; seq=[]; link=tip
    while link in bc and link!=root: jn=bc[link]; seq.append(jn); link=J[jn]["parent"]
    return J,list(reversed(seq))
def fk_link_points(J,seq,qm,stop_link="wrist_roll_link"):
    """Return list of link-frame origins (base_link frame) up to & incl stop_link's parent joint."""
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
def base_T(x,y,t): T=np.eye(4); T[:3,:3]=Rz(t); T[:3,3]=[x,y,0]; return T

def capsule_spheres(pts, step=0.03):
    """Sample sphere centers along the polyline through link origins."""
    out=[]
    for a,b in zip(pts[:-1],pts[1:]):
        L=np.linalg.norm(b-a); n=max(2,int(L/step)+1)
        for t in np.linspace(0,1,n): out.append(a+t*(b-a))
    return np.array(out) if out else pts

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--urdf",default="hsrb.urdf"); ap.add_argument("--csv",required=True)
    ap.add_argument("--cloud",required=True); ap.add_argument("--aff",default=None,help="x,y,z affordance center")
    ap.add_argument("--carve",type=float,default=0.10,help="object carve radius (m)")
    ap.add_argument("--arm_r",type=float,default=0.05,help="arm sphere radius (m)")
    ap.add_argument("--margin",type=float,default=0.02,help="extra clearance (m)")
    ap.add_argument("--voxel",type=float,default=0.02,help="obstacle voxel size (m)")
    ap.add_argument("--out_prefix",default="collision")
    a=ap.parse_args()

    J,seq=load_chain(a.urdf,"base_link","hand_palm_link")
    arm=["arm_lift_joint","arm_flex_joint","arm_roll_joint","wrist_flex_joint","wrist_roll_joint"]
    cols=["q_lift","q_flex","q_roll","q_wflex","q_wroll"]

    C=np.load(a.cloud,allow_pickle=True); pts=np.asarray(C["points"],float)
    if a.aff: aff=np.array([float(v) for v in a.aff.split(",")])
    else: aff=None
    # carve object
    if aff is not None:
        keep=np.linalg.norm(pts-aff,axis=1)>a.carve; pts=pts[keep]
    # voxelize obstacles -> occupied set + per-voxel representative for clearance
    vid=np.floor(pts/a.voxel).astype(np.int64)
    occ=set(map(tuple, vid))
    print(f"obstacle cloud: {len(pts)} pts -> {len(occ)} occupied voxels @ {a.voxel} m "
          f"(carved {a.carve} m around aff={aff})")
    hit_r=a.arm_r+a.margin
    nb=int(np.ceil(hit_r/a.voxel))
    offs=np.array([(i,j,k) for i in range(-nb,nb+1) for j in range(-nb,nb+1) for k in range(-nb,nb+1)])

    rows=[r for r in csv.DictReader(open(a.csv)) if r.get("arm_only_ok")=="1" and r.get("q_lift","")!=""]
    res=[]; print(f"\n{'g':>3} {'free':>5} {'clear_m':>8}  (arm vs scene, gripper excluded)")
    for r in rows:
        q={k:float(r[c]) for k,c in zip(arm,cols)}
        lp=fk_link_points(J,seq,q)                       # arm link origins in new base frame
        S=capsule_spheres(lp)                            # spheres along arm body
        B=base_T(float(r["base_x"]),float(r["base_y"]),float(r["base_yaw_rad"]))
        Sw=(B[:3,:3]@S.T).T + B[:3,3]                    # arm spheres in world (cloud) frame
        free=True; clr=9.0
        for c3 in Sw:
            key=np.floor(c3/a.voxel).astype(np.int64)
            # check occupied voxels in neighborhood
            near=offs+key
            for nk in map(tuple, near):
                if nk in occ:
                    # approx clearance = distance from sphere center to voxel center
                    vc=(np.array(nk)+0.5)*a.voxel
                    dd=np.linalg.norm(c3-vc)-a.voxel*0.5
                    clr=min(clr,dd)
                    if dd<hit_r: free=False
            if not free: break
        res.append((r["grasp"],free,clr))
        print(f"{r['grasp']:>3} {str(free):>5} {clr:8.3f}")
    nf=sum(1 for _,f,_ in res if f)
    print(f"\nCOLLISION-FREE (arm vs scene): {nf}/{len(res)} ({100*nf/len(res):.0f}%)")
    print(f"  params: arm_r={a.arm_r} margin={a.margin} carve={a.carve} voxel={a.voxel}")
    with open(f"{a.out_prefix}.csv","w",newline="") as fh:
        w=csv.writer(fh); w.writerow(["grasp","collision_free","clearance_m"])
        for g,f,c in res: w.writerow([g,int(f),round(c,4)])
    print(f"wrote {a.out_prefix}.csv")

if __name__=="__main__": main()
