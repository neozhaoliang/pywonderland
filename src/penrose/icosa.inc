// Persistence of Vision Ray Tracer Scene Include File
// File: icosa.inc
// Vers: 3.7
// Date: 2018/02/08
// Auth: Zhao Liang mathzhaoliang@gmail.com

#ifndef (Reorient_Trans)
    #include "transforms.inc"
#end

/*======================================================================*/
/* Settings for the edges, vertices and faces                           */

#declare icosa_edge_rad = 0.05;
#declare icosa_vert_rad = 0.1;
#declare phi = (1 + sqrt(5)) / 2;

#declare IcosaFaceFinish = finish {
    specular 1
    roughness 0.003
    phong 0.9 phong_size 100
    diffuse 0.7
    reflection 0.1
}

#declare IcosaFaceNormal = normal { bozo 0.005 scale 0.001 }

#declare IcosaEdgeTexture = texture {
    pigment { color rgb 0.05 }
    finish { IcosaFaceFinish }
}

/*======================================================================*/
/* Vertices of the icosahedron                                          */

#declare Icosa_Vertices = array[12] {
    <  0,  1,  phi>, <  1, phi,  0 >, < phi, 0,   1 >,
    <  0, -1,  phi>, < -1, phi,  0 >, < phi, 0,  -1 >,
    <  0,  1, -phi>, <  1,-phi,  0 >, <-phi, 0,   1 >,
    <  0, -1, -phi>, < -1,-phi,  0 >, <-phi, 0,  -1 >,
}

/*======================================================================*/
/* Edges of the icosahedron                                             */

#declare Icosa_Edges = array[30] {
    < 0,  1>, < 0,  2>, < 0,  3>, < 0,  4>, < 0,  8>,
    < 1,  2>, < 1,  4>, < 1,  5>, < 1,  6>, < 2,  3>,
    < 2,  5>, < 2,  7>, < 3,  7>, < 3,  8>, < 3, 10>,
    < 4,  6>, < 4,  8>, < 4, 11>, < 5,  6>, < 5,  7>,
    < 5,  9>, < 6,  9>, < 6, 11>, < 7,  9>, < 7, 10>,
    < 8, 10>, < 8, 11>, < 9, 10>, < 9, 11>, <10, 11>
}
/*======================================================================*/
/* Transform the vertices so that the bottom face lies horizontally     */

#local P0 = Icosa_Vertices[0];
#local P1 = Icosa_Vertices[1];
#local P2 = Icosa_Vertices[2];
#local V1 = P1 - P0;
#local V2 = P2 - P0;
#local Axis = vcross(V2, V1);
#local Tran1 = transform { Reorient_Trans(Axis, y) }
#local TV1 = vtransform(V1, Tran1);
#local The_Tran = transform {
    Reorient_Trans(Axis, y)
    Reorient_Trans(TV1, x)
}
#local ind = 0;
#while (ind<12)
    #declare Icosa_Vertices[ind] = vtransform(Icosa_Vertices[ind], The_Tran);
    #local ind = ind + 1;
#end

/*======================================================================*/
/* Icosahedron object                                                   */

// some prelimnary computations to make the bottom face lie on the xz plane
#local P0 = Icosa_Vertices[9];
#local P1 = Icosa_Vertices[10];
#local P2 = Icosa_Vertices[11];
#local V1 = P1 - P0;
#local V2 = P2 - P0;
#local Axis = vcross(V2, V1);

#declare Icosahedron = union {
    // edges and vertices
    union {
        #local i=0;
        #while (i<12)
            sphere { Icosa_Vertices[i], icosa_vert_rad }
            #local i = i+1;
        #end

        #local i=0;
        #while (i<30)
            cylinder { Icosa_Vertices[Icosa_Edges[i].x], Icosa_Vertices[Icosa_Edges[i].y], icosa_edge_rad }
            #local i=i+1;
        #end

        texture { IcosaEdgeTexture }
    }
    // faces
    mesh2 {
        vertex_vectors {
            12,
            Icosa_Vertices[0],
            Icosa_Vertices[1],
            Icosa_Vertices[2],
            Icosa_Vertices[3],
            Icosa_Vertices[4],
            Icosa_Vertices[5],
            Icosa_Vertices[6],
            Icosa_Vertices[7],
            Icosa_Vertices[8],
            Icosa_Vertices[9],
            Icosa_Vertices[10],
            Icosa_Vertices[11],
            }
        texture_list {
            5,
            texture { pigment { rgb <.8,  0,  0> } finish { IcosaFaceFinish } normal { IcosaFaceNormal } }
            texture { pigment { rgb < 1,  1,  1> } finish { IcosaFaceFinish } normal { IcosaFaceNormal } }
            texture { pigment { rgb < 1,  1,  0> } finish { IcosaFaceFinish } normal { IcosaFaceNormal } }
            texture { pigment { rgb < 0,  0, .8> } finish { IcosaFaceFinish } normal { IcosaFaceNormal } }
            texture { pigment { rgb < 0, .8,  0> } finish { IcosaFaceFinish } normal { IcosaFaceNormal } }
            }
        face_indices {
            20,
            <0,  1,  2>, 0,
            <0,  1,  4>, 1,
            <0,  2,  3>, 2,
            <0,  3,  8>, 3,
            <0,  4,  8>, 4,
            <1,  2,  5>, 4,
            <1,  4,  6>, 3,
            <1,  5,  6>, 2,
            <2,  3,  7>, 1,
            <2,  5,  7>, 3,
            <3,  7, 10>, 0
            <3,  8, 10>, 4,
            <4,  6, 11>, 0,
            <4,  8, 11>, 2,
            <5,  6,  9>, 1,
            <5,  7,  9>, 0,
            <6,  9, 11>, 4,
            <7,  9, 10>, 2,
            <8, 10, 11>, 1,
            <9, 10, 11>, 3
            }
        inside_vector y
        hollow
    }
    translate -(P0+P1+P2)/3
    Reorient_Trans(Axis, y)
    translate y*max(icosa_edge_rad, icosa_vert_rad)
}
