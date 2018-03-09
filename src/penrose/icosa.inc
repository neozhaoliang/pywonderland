#include "transforms.inc"
#include "colors.inc"


#declare Platonic_icosahedron_verts = array[12] {
    <0, 0, 1.175571>,
    <1.051462, 0, 0.5257311>,
    <0.3249197, 1., 0.5257311>,
    <-0.8506508, 0.618034, 0.5257311>,
    <-0.8506508, -0.618034, 0.5257311>,
    <0.3249197, -1., 0.5257311>,
    <0.8506508, 0.618034, -0.5257311>,
    <0.8506508, -0.618034, -0.5257311>,
    <-0.3249197, 1., -0.5257311>,
    <-1.051462, 0, -0.5257311>,
    <-0.3249197, -1., -0.5257311>,
    <0, 0, -1.175571>,
}

#local P0 = Platonic_icosahedron_verts[1];
#local P1 = Platonic_icosahedron_verts[2];
#local P2 = Platonic_icosahedron_verts[3];
#local V1 = P1 - P0;
#local V2 = P2 - P0;
#local Axis = vcross(V2, V1);
#local Tran1 = transform { Reorient_Trans(Axis, y) }
#local TV1 = vtransform(V1, Tran1);
#local The_Tran = transform {
    Reorient_Trans(Axis, y)
    Reorient_Trans(TV1, x) }
#local Num = 0;
#while (Num < 12)
    #declare Platonic_icosahedron_verts[Num] = vtransform(Platonic_icosahedron_verts[Num], The_Tran);
    #local Num = Num + 1;
#end

#macro Platonic_icosahedron_faces(OnPlane)
    #local Platonic_icosahedron_obj = mesh2 {
        vertex_vectors {
            12,
            Platonic_icosahedron_verts[0],
            Platonic_icosahedron_verts[1],
            Platonic_icosahedron_verts[2],
            Platonic_icosahedron_verts[3],
            Platonic_icosahedron_verts[4],
            Platonic_icosahedron_verts[5],
            Platonic_icosahedron_verts[6],
            Platonic_icosahedron_verts[7],
            Platonic_icosahedron_verts[8],
            Platonic_icosahedron_verts[9],
            Platonic_icosahedron_verts[10],
            Platonic_icosahedron_verts[11]
        }
        texture_list {
            5,
            texture{pigment{color Red}},
            texture{pigment{color Green}},
            texture{pigment{color Blue}},
            texture{pigment{color Yellow}},
            texture{pigment{color Cyan}}
        }
        face_indices {
            20,
            <0, 1, 2>, 0,
            <0, 2, 3>, 1,
            <0, 3, 4>, 2,
            <0, 4, 5>, 3,
            <0, 5, 1>, 4,
            <1, 5, 7>, 1,
            <1, 7, 6>, 2,
            <1, 6, 2>, 3,
            <2, 6, 8>, 2,
            <2, 8, 3>, 4,
            <3, 8, 9>, 3,
            <3, 9, 4>, 0,
            <4, 9, 10>, 1,
            <4, 10, 5>, 4,
            <5, 10, 7>, 0,
            <6, 7, 11>, 2,
            <6, 11, 8>, 0,
            <7, 10, 11>, 3,
            <8, 11, 9>, 1,
            <9, 11, 10>, 4
        }
        inside_vector y
        hollow 
    }
    #if (OnPlane)
        #local P0 = Platonic_icosahedron_verts[9];
        #local P1 = Platonic_icosahedron_verts[11];
        #local P2 = Platonic_icosahedron_verts[10];
        #local V1 = P1 - P0;
        #local V2 = P2 - P0;
        #local Axis = vcross(V2, V1);
        object {
            Platonic_icosahedron_obj
            translate -(P0+P1+P2)/3
            Reorient_Trans(Axis, y)
        }
    #else
        object { Platonic_icosahedron_obj }
    #end
#end

#macro Platonic_icosahedron_edges(RadEdg, RadVer, TexEdg, TexVer, OnPlane)
    union {
        union {
            sphere { Platonic_icosahedron_verts[0], RadVer }
            sphere { Platonic_icosahedron_verts[1], RadVer }
            sphere { Platonic_icosahedron_verts[2], RadVer }
            sphere { Platonic_icosahedron_verts[3], RadVer }
            sphere { Platonic_icosahedron_verts[4], RadVer }
            sphere { Platonic_icosahedron_verts[5], RadVer }
            sphere { Platonic_icosahedron_verts[6], RadVer }
            sphere { Platonic_icosahedron_verts[7], RadVer }
            sphere { Platonic_icosahedron_verts[8], RadVer }
            sphere { Platonic_icosahedron_verts[9], RadVer }
            sphere { Platonic_icosahedron_verts[10], RadVer }
            sphere { Platonic_icosahedron_verts[11], RadVer }
            texture { TexVer } }
        union {
            cylinder { Platonic_icosahedron_verts[0], Platonic_icosahedron_verts[1], RadEdg }
            cylinder { Platonic_icosahedron_verts[1], Platonic_icosahedron_verts[2], RadEdg }
            cylinder { Platonic_icosahedron_verts[2], Platonic_icosahedron_verts[0], RadEdg }
            cylinder { Platonic_icosahedron_verts[2], Platonic_icosahedron_verts[3], RadEdg }
            cylinder { Platonic_icosahedron_verts[3], Platonic_icosahedron_verts[0], RadEdg }
            cylinder { Platonic_icosahedron_verts[3], Platonic_icosahedron_verts[4], RadEdg }
            cylinder { Platonic_icosahedron_verts[4], Platonic_icosahedron_verts[0], RadEdg }
            cylinder { Platonic_icosahedron_verts[4], Platonic_icosahedron_verts[5], RadEdg }
            cylinder { Platonic_icosahedron_verts[5], Platonic_icosahedron_verts[0], RadEdg }
            cylinder { Platonic_icosahedron_verts[5], Platonic_icosahedron_verts[1], RadEdg }
            cylinder { Platonic_icosahedron_verts[5], Platonic_icosahedron_verts[7], RadEdg }
            cylinder { Platonic_icosahedron_verts[7], Platonic_icosahedron_verts[1], RadEdg }
            cylinder { Platonic_icosahedron_verts[7], Platonic_icosahedron_verts[6], RadEdg }
            cylinder { Platonic_icosahedron_verts[6], Platonic_icosahedron_verts[1], RadEdg }
            cylinder { Platonic_icosahedron_verts[6], Platonic_icosahedron_verts[2], RadEdg }
            cylinder { Platonic_icosahedron_verts[6], Platonic_icosahedron_verts[8], RadEdg }
            cylinder { Platonic_icosahedron_verts[8], Platonic_icosahedron_verts[2], RadEdg }
            cylinder { Platonic_icosahedron_verts[8], Platonic_icosahedron_verts[3], RadEdg }
            cylinder { Platonic_icosahedron_verts[8], Platonic_icosahedron_verts[9], RadEdg }
            cylinder { Platonic_icosahedron_verts[9], Platonic_icosahedron_verts[3], RadEdg }
            cylinder { Platonic_icosahedron_verts[9], Platonic_icosahedron_verts[4], RadEdg }
            cylinder { Platonic_icosahedron_verts[9], Platonic_icosahedron_verts[10], RadEdg }
            cylinder { Platonic_icosahedron_verts[10], Platonic_icosahedron_verts[4], RadEdg }
            cylinder { Platonic_icosahedron_verts[10], Platonic_icosahedron_verts[5], RadEdg }
            cylinder { Platonic_icosahedron_verts[10], Platonic_icosahedron_verts[7], RadEdg }
            cylinder { Platonic_icosahedron_verts[7], Platonic_icosahedron_verts[11], RadEdg }
            cylinder { Platonic_icosahedron_verts[11], Platonic_icosahedron_verts[6], RadEdg }
            cylinder { Platonic_icosahedron_verts[11], Platonic_icosahedron_verts[8], RadEdg }
            cylinder { Platonic_icosahedron_verts[10], Platonic_icosahedron_verts[11], RadEdg }
            cylinder { Platonic_icosahedron_verts[11], Platonic_icosahedron_verts[9], RadEdg }
            texture { TexEdg } }
        #if (OnPlane)
            #local P0 = Platonic_icosahedron_verts[9];
            #local P1 = Platonic_icosahedron_verts[11];
            #local P2 = Platonic_icosahedron_verts[10];
            #local V1 = P1 - P0;
            #local V2 = P2 - P0;
            #local Axis = vcross(V2, V1);
            translate -(P0+P1+P2)/3
            Reorient_Trans(Axis, y)
            translate y*max(RadEdg, RadVer)
        #end
    }
#end
