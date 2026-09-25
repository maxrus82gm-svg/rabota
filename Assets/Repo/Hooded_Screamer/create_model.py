import bpy, math, os, json
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(n,c,r=.6):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=r; return m
cloth=mat('Charcoal woven shroud',(.045,.053,.065),.88); bone=mat('Aged ivory mask',(.72,.70,.58)); black=mat('Deep mouth and sockets',(.003,.004,.006),.97); hands=mat('Ash violet fingers',(.17,.18,.24))
n=cloth.node_tree.nodes; links=cloth.node_tree.links; tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=180; tex.inputs['Detail'].default_value=2; bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.22; bump.inputs['Distance'].default_value=.018; links.new(tex.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
parts=[]
def mesh(n,v,f,m):
 d=bpy.data.meshes.new(n); d.from_pydata(v,[],f); d.update(); o=bpy.data.objects.new(n,d); bpy.context.collection.objects.link(o); o.data.materials.append(m); parts.append(o)
 for p in d.polygons:p.use_smooth=True
 return o
def uv(n,loc,scale,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=24,location=loc); o=bpy.context.object; o.name=n; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m); parts.append(o)
 for p in o.data.polygons:p.use_smooth=True
 return o
def tube(n,points,r,m,radii=None):
 c=bpy.data.curves.new(n,'CURVE'); c.dimensions='3D'; c.resolution_u=16; c.bevel_depth=r; c.bevel_resolution=4; c.use_fill_caps=True; sp=c.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
 for i,(p,co) in enumerate(zip(sp.bezier_points,points)):
  p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'; p.radius=radii[i] if radii else 1
 o=bpy.data.objects.new(n,c); bpy.context.collection.objects.link(o); o.data.materials.append(m); parts.append(o); return o
# Closed draped silhouette with subtle long folds.
levels=[(0,.76),(.08,.78),(.5,.72),(1,.67),(1.5,.61),(2,.54),(2.45,.46),(2.8,.36),(3.03,.22),(3.13,.055),(3.14,.002)]
v=[]; f=[]; N=96
for z,r in levels:
 for j in range(N):
  a=2*math.pi*j/N; rr=r*(1+.018*math.cos(a*11)+.012*math.sin(a*17+z*1.7)); v.append((rr*math.cos(a),rr*.70*math.sin(a),z+.012*math.cos(a*5)*(1-z/3.14)))
for k in range(len(levels)-1):
 for j in range(N):a=k*N+j;b=k*N+(j+1)%N;f.append((a,b,b+N,a+N))
f.append(tuple(reversed(range(N)))); f.append(tuple(range((len(levels)-1)*N,len(levels)*N)))
o=mesh('Continuous hood and robe',v,f,cloth); mod=o.modifiers.new('Soft draped fabric','SUBSURF'); mod.levels=2
# Mask rests forward of hood: deep black cavity with an ivory sculpted rim.
outline=[(-.22,2.88),(-.34,2.70),(-.345,2.41),(-.35,2.11),(-.34,1.85),(-.28,1.72),(0,1.68),(.28,1.72),(.34,1.85),(.35,2.11),(.345,2.41),(.34,2.70),(.22,2.88),(0,2.98)]
def face_y(z):return -.385-(2.8-z)*.15
verts=[(0,face_y(2.35),2.35)]+[(x,face_y(z),z) for x,z in outline]; fs=[(0,i+1,(i+1)%len(outline)+1) for i in range(len(outline))]; mesh('Recessed open mouth darkness',verts,fs,black)
tube('Ivory mask perimeter',[(x,face_y(z)-.025,z) for x,z in outline+[outline[0]]],.035,bone)
uv('Mask forehead',(0,-.397,2.765),(.292,.062,.205),bone)
for s in [-1,1]:
 o=uv('Hollow black eye socket',(s*.145,-.458,2.765),(.093,.03,.093),black); o.rotation_euler[1]=s*-.24
tube('Upper mouth arch',[(-.29,-.453,2.62),(0,-.485,2.60),(.29,-.453,2.62)],.035,bone)
uv('Nose bridge',(0,-.477,2.658),(.047,.042,.081),bone)
for i,x in enumerate([-.21,-.12,-.025,.07,.17,.24]):
 height=[.105,.18,.14,.20,.135,.10][i]; z=1.735
 bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=.042,radius2=.006,depth=height,location=(x,face_y(z)-.038,z+height/2)); o=bpy.context.object; o.name='Lower fang %d'%i; o.rotation_euler[1]=(-.14 if i%2 else .12); o.data.materials.append(bone); parts.append(o)
# Two crooked arms, each with four curled fingers and an opposing thumb.
for s in [-1,1]:
 tube('Shrouded bent arm',[(s*.57,.0,1.05),(s*.82,-.04,1.02),(s*.94,-.22,1.23)],.115,cloth,[1.2,1,.65])
 uv('Bony palm',(s*.99,-.28,1.26),(.13,.075,.17),hands)
 for i in range(4):
  root=(s*(.93+i*.047),-.31,1.33-i*.038)
  pts=[root,(s*(1.12+i*.066),-.35,1.48-i*.092),(s*(1.27+i*.039),-.43,1.39-i*.116),(s*(1.23+i*.012),-.50,1.20-i*.099)]
  tube('Long curled finger %s %d'%(s,i),pts,.039,hands,[1.05,.95,.8,.30])
  uv('Knuckle',pts[1],(.042,.041,.042),hands)
 tube('Opposing hooked thumb',[(s*.95,-.32,1.17),(s*.81,-.43,1.20),(s*.80,-.50,1.36),(s*.88,-.50,1.40)],.045,hands,[1.1,1,.7,.25])
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]; bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'hooded_screamer.glb'),use_selection=True,export_apply=True)
floor=mat('Studio',(.021,.028,.036),.62); bpy.ops.mesh.primitive_plane_add(size=200); bpy.context.object.data.materials.append(floor)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.35,-7,3.0)); c=bpy.context.object; aim(c,(0,0,1.55)); c.data.type='ORTHO'; c.data.ortho_scale=3.9; bpy.context.scene.camera=c
for loc,power,color,size in [((-3,-4,5),380,(.63,.86,1),3),((3,-1,4),270,(1,.42,.30),3),((0,2,4),480,(.2,.9,1),2),((0,-4,2),65,(1,1,1),2)]:
 bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=power; l.data.color=color; l.data.shape='DISK'; l.data.size=size; aim(l,(0,0,1.5))
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.samples=48; s.cycles.use_denoising=True; s.world.color=(.10,.10,.10); s.render.resolution_x=1000; s.render.resolution_y=1100; s.render.resolution_percentage=100; s.render.filepath=os.path.join(OUT,'preview.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'hooded_screamer.blend')); bpy.ops.render.render(write_still=True)
