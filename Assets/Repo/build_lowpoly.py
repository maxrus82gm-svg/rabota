import bpy, bmesh, os, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def metrics(objects):
    rows=[]
    for o in objects:
        if o.type!='MESH': continue
        m=o.data; m.calc_loop_triangles()
        bm=bmesh.new(); bm.from_mesh(m)
        rows.append(dict(name=o.name,vertices=len(m.vertices),quads=sum(len(p.vertices)==4 for p in m.polygons),triangles=sum(len(p.vertices)==3 for p in m.polygons),ngons=sum(len(p.vertices)>4 for p in m.polygons),triangulated=len(m.loop_triangles),zero_area=sum(p.calc_area()<1e-12 for p in bm.faces),boundary_edges=sum(e.is_boundary for e in bm.edges),nonmanifold_interior=sum(not e.is_manifold and not e.is_boundary for e in bm.edges),loose_vertices=sum(not v.link_edges for v in bm.verts)))
        bm.free()
    return dict(totals={key:sum(r[key] for r in rows) for key in rows[0] if key!='name'},objects=rows)

def finalize(parts):
    for o in parts:
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
        if o.type=='CURVE': bpy.ops.object.convert(target='MESH')
        for mod in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=mod.name)
        bm=bmesh.new(); bm.from_mesh(o.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        # Retain authored quad strips; triangulate only caps with >4 corners.
        caps=[f for f in bm.faces if len(f.verts)>4]
        if caps:bmesh.ops.triangulate(bm,faces=caps,quad_method='BEAUTY',ngon_method='BEAUTY')
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(o.data); bm.free(); o.data.update()
    report=metrics(parts)
    assert report['totals']['ngons']==0 and report['totals']['zero_area']==0 and report['totals']['loose_vertices']==0, report['totals']
    coll=bpy.data.collections.new('CHARACTER_LOW_POLY'); bpy.context.scene.collection.children.link(coll)
    for o in parts:
        for c in list(o.users_collection):c.objects.unlink(o)
        coll.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    return report

patch_code='''def patch(name,coords,material,offset):
 w=max(x for x,z in coords); top=max(z for x,z in coords); bottom=min(z for x,z in coords)
 verts=[]; faces=[]; cols=32; rows=12
 for j in range(rows):
  u=j/rows; z=top+(bottom-top)*u; width=w*math.sqrt(1-u*u)
  for i in range(cols+1):
   x=width*(2*i/cols-1); verts.append((x,front(x,z)-offset,z))
 for j in range(rows-1):
  for i in range(cols):
   a=j*(cols+1)+i; faces.append((a,a+1,a+cols+2,a+cols+1))
 end=len(verts); verts.append((0,front(0,bottom)-offset,bottom))
 for i in range(cols):
  a=(rows-1)*(cols+1)+i; faces.append((a,a+1,end))
 mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.data.materials.append(material); parts.append(o)
 for p in mesh.polygons:p.use_smooth=True
 return o
'''

for folder,stem in [('Smiley_No_Tears','smiley_no_tears'),('Hooded_Screamer','hooded_screamer')]:
    out=ROOT/folder/'LowPoly'; out.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/folder/(stem+'.blend')))
    dg=bpy.context.evaluated_depsgraph_get(); baseline=0
    for o in bpy.context.scene.objects:
        if o.type not in {'MESH','CURVE'} or o.name in {'Studio floor','Plane'}:continue
        e=o.evaluated_get(dg); m=e.to_mesh(); m.calc_loop_triangles(); baseline+=len(m.loop_triangles); e.to_mesh_clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.world=bpy.data.worlds.new('World')
    src=(ROOT/folder/'create_model.py').read_text()
    src=src.replace('OUT=os.path.dirname(os.path.abspath(__file__))','OUT='+repr(str(out)))
    if folder=='Smiley_No_Tears':
        src=src.replace('segments=48,ring_count=32','segments=(32 if name=="Head" else 16),ring_count=(20 if name=="Head" else 10)')
        a=src.index('def patch('); b=src.index('def mouth_coords',a); src=src[:a]+patch_code+src[b:]
        src=src.replace('curve.resolution_u=24','curve.resolution_u=4').replace('curve.bevel_resolution=5','curve.bevel_resolution=1; curve.use_fill_caps=True')
        src=src.replace('mod.segments=4','mod.segments=2')
    else:
        src=src.replace('segments=32,ring_count=24','segments=(12 if n=="Knuckle" else 16),ring_count=(8 if n=="Knuckle" else 10)')
        src=src.replace('c.resolution_u=16','c.resolution_u=3').replace('c.bevel_resolution=4','c.bevel_resolution=1')
        src=src.replace('N=96','N=32').replace('mod.levels=2','mod.levels=1').replace('vertices=24','vertices=8')
        # Weld the mask rim seam by making it a cyclic curve, with no duplicate endpoint.
        src=src.replace("sp.bezier_points.add(len(points)-1)","closed=n=='Ivory mask perimeter'\n if closed:points=points[:-1]\n sp.bezier_points.add(len(points)-1); sp.use_cyclic_u=closed")
    src=src.replace("bpy.ops.export_scene.gltf(filepath=", "report=finalize(parts)\nbpy.ops.export_scene.gltf(filepath=")
    src=src.replace(stem+'.glb',stem+'_lowpoly.glb').replace(stem+'.blend',stem+'_lowpoly.blend')
    env={'__file__':str(ROOT/folder/'create_model.py'),'finalize':finalize}
    exec(compile(src,folder,'exec'),env)
    report=env['report']; report['baseline_evaluated_triangles']=baseline
    report['reduction_percent']=round(100*(1-report['totals']['triangulated']/baseline),2)
    (out/'topology_report.json').write_text(json.dumps(report,indent=2))
    print('TOPOLOGY',folder,json.dumps({k:v for k,v in report.items() if k!='objects'}),flush=True)
    # Save a wire overlay for visual inspection of the actual quad/triangle edges.
    ink=bpy.data.materials.new('Topology ink'); ink.diffuse_color=(.008,.012,.018,1)
    for o in env['parts']:
        w=o.copy(); w.data=o.data.copy(); bpy.context.collection.objects.link(w); w.name='Wire '+o.name; w.data.materials.clear(); w.data.materials.append(ink)
        mod=w.modifiers.new('Visible polygon edges','WIREFRAME'); mod.thickness=.0017 if folder=='Smiley_No_Tears' else .0025; mod.use_replace=True; mod.offset=1
    bpy.context.scene.render.filepath=str(out/'topology.png'); bpy.context.scene.cycles.samples=24; bpy.ops.render.render(write_still=True)
    # Test the exported bytes by importing them into an empty scene.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(out/(stem+'_lowpoly.glb')))
    imported=metrics(list(bpy.context.scene.objects))
    assert imported['totals']['triangulated']==report['totals']['triangulated'], (imported['totals'],report['totals'])
    (out/'glb_import_check.json').write_text(json.dumps(imported,indent=2))
