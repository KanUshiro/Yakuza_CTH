Unfinished Import/Export Blender addon for Yakuza Cloth Physics (CTH) and physics collision (HCB). 

Many thanks to theturboturnip for both helping me and letting me use GMD functions.
His tool is required: https://github.com/theturboturnip/yk_gmd_io

Thanks to SutandoTsukai181 for PyBinaryReader (already packed inside the tool).

Additional thanks to Evie.

Since I currently do not have a lot of time for this, I will only conditionally consider working on the tool:

**I will not respond to any general questions** about how to use it or topology. Be aware the format is complex to work with.

If you are certain you've found a bug with the tool itself, you can open an issue but please make it detailed.

My vertex-sorting algorithm is flawed and I do not have the level of math required to make a better one.
Unless someone gives me a better one for whatever reason, do not expect any improvement on that part

The HCB part is in a very raw state and globally untested, including the UI

Mesh grid requirement: https://i.imgur.com/q3uuLXs.png

___________________


CTH Cloth Physics format overview:
- Mesh shape allowed: **curved plane/surface only. This is a retro-ish/restrictive model format.** (no, you can't have modelled pockets unless they're their own cth)
- Several cth per model allowed: yes (naming convention v0_ v1_ ...)
- Backface culling: no
- Typical weights (attached to animated armature)
- Per-vertex physics slider (translated in blender by center/root bone weights)
- Stiffness (general physics value for the whole mesh)
- (Column) amount of normal/tangent
- Simplified armature from its gmd (animation weights)
- Simplified yakuza material (**one** per cth)
- Faces/edges: **none** (quad-like)
- Collision: vertex-based CTH, colliding with HCB object
- "Closed mesh": closed = skirts, etc. not closed = bottom of jackets, etc.

Tool options:
- Import/Batch Export for CTH & HCB
- Unstable-ish vertex autosort algorithm for automated face generation, on by default (workaround when it doesn't work on a specific mesh: sort vertices manually (good luck))
- Transferring a GMD material to a CTH: supported (not the other way around). General yakuza material rules apply.
- Transferring a GMD armature (or any armature, really) to a CTH: supported (unsure about the other way around)
- Cloth physics preview works with animations inside Blender.
    -> imported CTH armatures don't work with GMT plugin (bug)
    -> HCB Blender collision simulation inaccurate (tool's fault)

___________________

Faces buffer: (n, n+1, n+row, n+row+1) * row * column

Example of vertices sorted in the right order if *row = 6* and *column = 4* (-> expected vertices: 24):

0 6 12 18

1 7 13 19

2 8 14 20

3 9 15 21

4 10 16 22

5 11 17 23

Autosort picks (column) amount of what it sees as the highest vertices, then tries to follow the edges to trace the mesh.
It will be unable to properly write the mesh if it doesn't pick the right starting vertices. This is the tool's fault and not the format's fault.
In this case you can either sort them manually or try to make the geometry less curvy.

The tool bases itself on your faces to try to detect vertex order, but it **does not** save the faces. They are completely deleted at export. Save your blend file.
The faces generated at import are "fake", a blender simulation of what they would look like if they existed.
Use quads for better looking/more controlled results; it will always turn it into quads at export anyway.

Closest explanation to the model format I've found (we are in quads, not in tris, though): https://en.wikipedia.org/wiki/Triangle_strip

Good luck...

Mandatory shape object: https://docs.blender.org/manual/en/2.93/modeling/geometry_nodes/mesh_primitives/plane.html

You can curve it and subdivide it as long as the total amount of vertices is the area of a rectangle. Like a grid. (row * column)

HCB: Very dependent on the chosen armature. Size of collision = head/tail radius. Parent bone = "Bone Constraint" in the bone settings. The blender bone name in hcb doesn't matter.
