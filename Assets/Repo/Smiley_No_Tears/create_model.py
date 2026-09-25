import bpy, math, os, random, json
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,color,rough=.42):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough
 return m
gold=mat('Golden yellow',(1,.60,.008)); brown=mat('Warm brown brows',(.24,.085,.025)); rim=mat('Eye socket warm ochre',(.42,.145,.04)); dark=mat('Mouth interior',(.035,.012,.009)); gum=mat('Rose gums',(.48,.12,.14)); ivory=mat('Warm ivory teeth',(.86,.86,.59)); white=mat('Blue grey eyes',(.63,.78,.84),.25); black=mat('Pupils',(.009,.005,.003),.2)
parts=[]
def uv(name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,location=loc); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 parts.append(o); return o
def front(x,z):return -.72*math.sqrt(max(.015,1-x*x-z*z))
uv('Head',(0,0,0),(1,.72,1),gold)
def patch(name,coords,material,offset):
 cx=sum(x for x,z in coords)/len(coords); cz=sum(z for x,z in coords)/len(coords)
 verts=[(cx,front(cx,cz)-offset,cz)]+[(x,front(x,z)-offset,z) for x,z in coords]
 faces=[(0,i+1,(i+1)%len(coords)+1) for i in range(len(coords))]
 mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.data.materials.append(material); parts.append(o)
 bpy.context.view_layer.objects.active=o; o.select_set(True)
 mod=o.modifiers.new('Surface tessellation','SUBSURF'); mod.subdivision_type='SIMPLE'; mod.levels=5; bpy.ops.object.modifier_apply(modifier=mod.name)
 for v in mesh.vertices:v.co.y=front(v.co.x,v.co.z)-offset
 for p in mesh.polygons:p.use_smooth=True
 return o
def mouth_coords(w,top,bottom):
 return [(w*math.cos(t),top-(top-bottom)*math.sin(t)) for t in [math.pi*i/80 for i in range(81)]]
patch('Smile golden border',mouth_coords(.84,-.105,-.87),brown,.014)
patch('Mouth cavity',mouth_coords(.81,-.13,-.835),dark,.027)
patch('Gums',mouth_coords(.785,-.145,-.802),gum,.039)
patch('Space between tooth rows',mouth_coords(.755,-.32,-.70),dark,.051)
for side in [-1,1]:
 x=side*.435; z=.30
 uv('Eye socket', (x,front(x,z)-.014,z),(.335,.085,.295),rim)
 uv('Eye dark inset',(x,front(x,z)-.068,z),(.272,.065,.245),brown)
 uv('Eyeball',(x,front(x,z)-.14,z),(.205,.17,.222),white)
 uv('Pupil',(x-side*.013,front(x,z)-.306,z+.015),(.052,.025,.057),black)
 # Raised expressive eyebrow, tapered rounded curve
 curve=bpy.data.curves.new('Brow curve','CURVE'); curve.dimensions='3D'; curve.resolution_u=24; curve.bevel_depth=.061; curve.bevel_resolution=5
 spline=curve.splines.new('BEZIER'); spline.bezier_points.add(3)
 for p,(xx,zz,r) in zip(spline.bezier_points,[(side*.72,.65,.45),(side*.57,.73,1),(side*.39,.78,1.2),(side*.29,.82,.6)]):
  p.co=(xx,front(xx,zz)-.04,zz); p.radius=r; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
 o=bpy.data.objects.new('Raised eyebrow',curve); bpy.context.collection.objects.link(o); o.data.materials.append(brown); parts.append(o)
random.seed(8)
def tooth(name,x,z,width,height,angle):
 # Rounded bevelled individual teeth, slightly irregular like reference
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x,front(x,z)-.106,z)); o=bpy.context.object; o.name=name; o.dimensions=(width,.155,height); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.rotation_euler[1]=angle
 mod=o.modifiers.new('Rounded enamel','BEVEL'); mod.width=min(width*.32,.045); mod.segments=4
 mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); o.data.materials.append(ivory); parts.append(o)
for i,x in enumerate([-.695,-.565,-.42,-.255,-.085,.085,.255,.42,.565,.695]):
 z=-.33+.09*(abs(x)/.7)**1.8; h=.265-random.random()*.045
 tooth('Upper tooth %02d'%i,x,z,.142 if abs(x)<.5 else .119,h,random.uniform(-.15,.15))
for i,x in enumerate([-.64,-.50,-.34,-.17,0,.17,.34,.50,.64]):
 z=-.70+.22*(abs(x)/.67)**2
 tooth('Lower tooth %02d'%i,x,z,.14 if abs(x)<.4 else .115,.19+random.random()*.035,random.uniform(-.18,.18))
# Export only character geometry, keep presentation scene in Blender.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'smiley_no_tears.glb'),use_selection=True,export_apply=True)
floor=mat('Backdrop',(.78,.81,.85),.8)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-1.045)); bpy.context.object.name='Studio floor'; bpy.context.object.data.materials.append(floor)
def aim(o,point):o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.0,-6,1.05)); cam=bpy.context.object; aim(cam,(0,0,0)); cam.data.type='ORTHO'; cam.data.ortho_scale=2.65; bpy.context.scene.camera=cam
for name,loc,power,size in [('Key',(-3,-4,5),450,4),('Fill',(3,-3,2),250,3),('Rim',(0,2,4),500,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; aim(o,(0,0,0))
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.samples=48; s.cycles.use_denoising=True; s.world.color=(.25,.25,.25); s.render.resolution_x=1000; s.render.resolution_y=1000; s.render.resolution_percentage=100; s.view_settings.view_transform='AgX'
s.render.filepath=os.path.join(OUT,'preview.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'smiley_no_tears.blend')); bpy.ops.render.render(write_still=True)
with open(os.path.join(OUT,'asset_info.json'),'w') as f:json.dump({'name':'smiley_no_tears','source':'User supplied reference image; latest instruction: no tears','method':'Local procedural Blender modeling','parts':len(parts),'formats':['blend','glb'],'license':'User supplied reference; underlying reference rights not assessed'},f,indent=2)

