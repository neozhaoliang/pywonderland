// Persistence of Vision Ray Tracer Scene Include File
// File: rubik.inc
// Vers: 3.7
// Date: 2018/02/08
// Auth: Zhao Liang mathzhaoliang@gmail.com
// Original work by John L. Bolt's work.

// Note: Bolt's original code was not so user-friendly, I changed the texture,
// added more comments and made the calling interface easier to use.

/*========================================================================*/
/* Settings for a subcube and its faces                                   */

#declare wCube = 0.750;       // Width of a subcube
#declare rCube = 0.050;       // Radius of subcube edges, it defines the roundness
                              // of the edges of a subcube
#declare lCube = wCube/2;     // Half-width of a subcube with edge radius
#declare hCube = lCube-rCube; // Half-width of a subcube face without edge radius

#declare tFace = 0.001;       // Thickness of faces
#declare rFace = 0.040;       // Radius of a label corner, this defines the roundness of
                              // the faces of the labels
#declare hFace = hCube-0.010; // Half-width of label with corner radius, here a little gap
                              // is added between the label and the edges of subcube
#declare dFace = hFace-rFace; // Half-width of label without corner radius

/*==========================================================================*/
/* Textures of the faces and edges                                          */

#declare FaceNormal = normal { bozo 0.005 scale 0.001 }

#declare FaceFinish = finish {
    specular 1
    roughness 0.003
    phong 0.9 phong_size 100
    diffuse 0.7
    reflection 0.1
}

#declare EdgeTexture = texture {
    pigment { color rgb 0.05 }
    finish { FaceFinish }
}

// Textures for the six labels on the faces of a subcube
#declare Top = texture { pigment { rgb <0, 1, 0> } normal { FaceNormal } finish{ FaceFinish } }
#declare Bot = texture { pigment { rgb <0, 0, .8> } normal { FaceNormal } finish{ FaceFinish } }
#declare Lef = texture { pigment { rgb <1, 1, 0> } normal { FaceNormal } finish{ FaceFinish } }
#declare Rig = texture { pigment { rgb <1, 1, 1> } normal { FaceNormal } finish{ FaceFinish } }
#declare For = texture { pigment { rgb <.8, 0, 0> } normal { FaceNormal } finish{ FaceFinish } }
#declare Aft = texture { pigment { rgb <1, .3, 0> } normal { FaceNormal } finish{ FaceFinish } }

/*------------------------------------------------------------------------*/
/* Undecorated subcube                                                    */

#declare Cube = union {
    // 12 cylinders for the edges (to make them rounded)
    cylinder { -hCube*x, hCube*x, rCube translate < 0, -1, -1>*hCube }
    cylinder { -hCube*x, hCube*x, rCube translate < 0,  1, -1>*hCube }
    cylinder { -hCube*x, hCube*x, rCube translate < 0,  1,  1>*hCube }
    cylinder { -hCube*x, hCube*x, rCube translate < 0, -1 , 1>*hCube }
    cylinder { -hCube*y, hCube*y, rCube translate <-1,  0, -1>*hCube }
    cylinder { -hCube*y, hCube*y, rCube translate < 1,  0, -1>*hCube }
    cylinder { -hCube*y, hCube*y, rCube translate <-1,  0,  1>*hCube }
    cylinder { -hCube*y, hCube*y, rCube translate < 1,  0,  1>*hCube }
    cylinder { -hCube*z, hCube*z, rCube translate < 1,  1,  0>*hCube }
    cylinder { -hCube*z, hCube*z, rCube translate < 1, -1,  0>*hCube }
    cylinder { -hCube*z, hCube*z, rCube translate <-1,  1,  0>*hCube }
    cylinder { -hCube*z, hCube*z, rCube translate <-1, -1,  0>*hCube }
    // eight spheres for the corners
    sphere { 0, rCube translate hCube*< 1,  1,  1> }
    sphere { 0, rCube translate hCube*<-1,  1,  1> }
    sphere { 0, rCube translate hCube*< 1, -1,  1> }
    sphere { 0, rCube translate hCube*< 1,  1, -1> }
    sphere { 0, rCube translate hCube*<-1, -1,  1> }
    sphere { 0, rCube translate hCube*<-1,  1, -1> }
    sphere { 0, rCube translate hCube*< 1, -1, -1> }
    sphere { 0, rCube translate hCube*<-1, -1, -1> }
    // six boxes for the faces
    box { <-lCube,-hCube,-hCube>, <-hCube, hCube, hCube> }
    box { < hCube,-hCube,-hCube>, < lCube, hCube, hCube> }
    box { <-hCube,-lCube,-hCube>, < hCube,-hCube, hCube> }
    box { <-hCube, hCube,-hCube>, < hCube, lCube, hCube> }
    box { <-hCube,-hCube,-lCube>, < hCube, hCube,-hCube> }
    box { <-hCube,-hCube, hCube>, < hCube, hCube, lCube> }

    texture { EdgeTexture }
}

/*========================================================================*/
/* Shapes for the labels                                                  */
/*
        ------------------------------
        |      <-dFace->             |
        |      ----------------      |
        |     /                \     |
        |    /                  \    |
        |   |                    |   |
        |   |                    |   |
        |   |                    |   |
        |   |                    |   |
        |    \                  /    |
        |     \                /     |
        |      ----------------      |
        |   <--hFace-->|             |
        |                            |
        -----------------------------|
        <----hCube----->
*/

#declare FaceLR = union {
    cylinder { -(lCube+tFace+0.001)*x, (lCube+tFace+0.001)*x, rFace translate < 0,-dFace, dFace> }
    cylinder { -(lCube+tFace+0.001)*x, (lCube+tFace+0.001)*x, rFace translate < 0,-dFace,-dFace> }
    cylinder { -(lCube+tFace+0.001)*x, (lCube+tFace+0.001)*x, rFace translate < 0, dFace,-dFace> }
    cylinder { -(lCube+tFace+0.001)*x, (lCube+tFace+0.001)*x, rFace translate < 0, dFace, dFace> }
    box { <-(lCube+tFace+0.001),-dFace,-hFace>, < (lCube+tFace+0.001), dFace, hFace> }
    box { <-(lCube+tFace+0.001),-hFace,-dFace>, < (lCube+tFace+0.001), hFace, dFace> }
}

#declare FaceBT = union {
    cylinder { -(lCube+tFace+0.001)*y, (lCube+tFace+0.001)*y, rFace translate <-dFace, 0, dFace> }
    cylinder { -(lCube+tFace+0.001)*y, (lCube+tFace+0.001)*y, rFace translate <-dFace, 0,-dFace> }
    cylinder { -(lCube+tFace+0.001)*y, (lCube+tFace+0.001)*y, rFace translate < dFace, 0,-dFace> }
    cylinder { -(lCube+tFace+0.001)*y, (lCube+tFace+0.001)*y, rFace translate < dFace, 0, dFace> }
    box { <-dFace,-(lCube+tFace+0.001),-hFace>, < dFace, (lCube+tFace+0.001), hFace> }
    box { <-hFace,-(lCube+tFace+0.001),-dFace>, < hFace, (lCube+tFace+0.001), dFace> }
}

#declare FaceFA = union {
    cylinder { -(lCube+tFace+0.001)*z, (lCube+tFace+0.001)*z, rFace translate <-dFace, dFace, 0> }
    cylinder { -(lCube+tFace+0.001)*z, (lCube+tFace+0.001)*z, rFace translate <-dFace,-dFace, 0> }
    cylinder { -(lCube+tFace+0.001)*z, (lCube+tFace+0.001)*z, rFace translate < dFace,-dFace, 0> }
    cylinder { -(lCube+tFace+0.001)*z, (lCube+tFace+0.001)*z, rFace translate < dFace, dFace, 0> }
    box { <-dFace,-hFace,-(lCube+tFace+0.001)>, < dFace, hFace, (lCube+tFace+0.001)> }
    box { <-hFace,-dFace,-(lCube+tFace+0.001)>, < hFace, dFace, (lCube+tFace+0.001)> }
}

/*========================================================================*/
/* Slice out LRBTFA labels                                                */

#declare FaceL = intersection {
    box { <-(lCube+tFace),-lCube,-lCube>, <-lCube, lCube, lCube> }
    object { FaceLR }
}

#declare FaceR = intersection {
    box { < lCube,-lCube,-lCube>, < (lCube+tFace), lCube, lCube> }
    object { FaceLR }
}

#declare FaceB = intersection {
    box { <-lCube,-(lCube+tFace),-lCube>, < lCube,-lCube, lCube> }
    object { FaceBT }
}

#declare FaceT = intersection {
    box { <-lCube, lCube,-lCube>, < lCube, (lCube+tFace), lCube> }
    object { FaceBT }
}

#declare FaceF = intersection {
    box { <-lCube,-lCube,-(lCube+tFace)>, < lCube, lCube,-lCube> }
    object { FaceFA }
}

#declare FaceA = intersection {
    box { <-lCube,-lCube, lCube>, < lCube, lCube, (lCube+tFace)> }
    object { FaceFA }
}

/*========================================================================*/
/* The 26 individual decorated subcubes                                   */

#declare CubeTLF = union {
    object { Cube }
    object { FaceT texture { Top } }
    object { FaceL texture { Lef } }
    object { FaceF texture { For } }
}

#declare CubeTF = union {
    object { Cube }
    object { FaceT texture { Top } }
    object { FaceF texture { For } }
}

#declare CubeTRF = union {
    object { Cube }
    object { FaceT texture { Top } }
    object { FaceR texture { Rig } }
    object { FaceF texture { For } }
}

#declare CubeTL = union {
    object { Cube }
    object { FaceT texture { Top } }
    object { FaceL texture { Lef } }
}

#declare CubeT = union {
    object { Cube }
    object { FaceT texture { Top } }
}

#declare CubeTR = union {
    object { Cube }
    object { FaceT texture { Top } }
    object { FaceR texture { Rig } }
}

#declare CubeTLA = union {
    object { Cube }
    object { FaceT texture { Top } }
    object { FaceL texture { Lef } }
    object { FaceA texture { Aft } }
}

#declare CubeTA = union {
    object { Cube }
    object { FaceT texture { Top } }
    object { FaceA texture { Aft } }
}

#declare CubeTRA = union {
    object { Cube }
    object { FaceT texture { Top } }
    object { FaceR texture { Rig } }
    object { FaceA texture { Aft } }
}

#declare CubeBLF = union {
    object { Cube }
    object { FaceB texture { Bot } }
    object { FaceL texture { Lef } }
    object { FaceF texture { For } }
}

#declare CubeBF = union {
    object { Cube }
    object { FaceB texture { Bot } }
    object { FaceF texture { For } }
}

#declare CubeBRF = union {
    object { Cube }
    object { FaceB texture { Bot } }
    object { FaceR texture { Rig } }
    object { FaceF texture { For } }
}

#declare CubeBL = union {
    object { Cube }
    object { FaceB texture { Bot } }
    object { FaceL texture { Lef } }
}

#declare CubeB = union {
    object { Cube }
    object { FaceB texture { Bot } }
}

#declare CubeBR = union {
    object { Cube }
    object { FaceB texture { Bot } }
    object { FaceR texture { Rig } }
}

#declare CubeBLA = union {
    object { Cube }
    object { FaceB texture { Bot } }
    object { FaceL texture { Lef } }
    object { FaceA texture { Aft } }
}

#declare CubeBA = union {
    object { Cube }
    object { FaceB texture { Bot } }
    object { FaceA texture { Aft } }
}

#declare CubeBRA = union {
    object { Cube }
    object { FaceB texture { Bot } }
    object { FaceR texture { Rig } }
    object { FaceA texture { Aft } }
}

#declare CubeLF = union {
    object { Cube }
    object { FaceL texture { Lef } }
    object { FaceF texture { For } }
}

#declare CubeF = union {
    object { Cube }
    object { FaceF texture { For } }
}

#declare CubeRF = union {
    object { Cube }
    object { FaceR texture { Rig } }
    object { FaceF texture { For } }
}

#declare CubeL = union {
    object { Cube }
    object { FaceL texture { Lef } }
}

#declare CubeR = union {
    object { Cube }
    object { FaceR texture { Rig } }
}

#declare CubeLA = union {
    object { Cube }
    object { FaceL texture { Lef } }
    object { FaceA texture { Aft } }
}

#declare CubeA = union {
    object { Cube }
    object { FaceA texture { Aft } }
}

#declare CubeRA = union {
    object { Cube }
    object { FaceR texture { Rig } }
    object { FaceA texture { Aft } }
}

/*========================================================================*/
/* The array of subcubes                                                  */

#declare Cubes = array[3][3][3] {
    {
        { object { CubeBLF }, object { CubeBL  }, object { CubeBLA } },
        { object { CubeLF  }, object { CubeL   }, object { CubeLA  } },
        { object { CubeTLF }, object { CubeTL  }, object { CubeTLA } }
    },
    {
        { object { CubeBF  }, object { CubeB   }, object { CubeBA  } },
        { object { CubeF   }, object { Cube    }, object { CubeA   } },
        { object { CubeTF  }, object { CubeT   }, object { CubeTA  } }
    },
    {
        { object { CubeBRF }, object { CubeBR  }, object { CubeBRA } },
        { object { CubeRF  }, object { CubeR   }, object { CubeRA  } },
        { object { CubeTRF }, object { CubeTR  }, object { CubeTRA } }
    }
}

/*------------------------------------------------------------------------*/
/* Translations of subcubes                                               */

#declare Tran = array[3][3][3] {
    {
        {transform{translate <-1,-1,-1>*wCube}, transform{translate <-1,-1, 0>*wCube}, transform{translate <-1,-1, 1>*wCube}},
        {transform{translate <-1, 0,-1>*wCube}, transform{translate <-1, 0, 0>*wCube}, transform{translate <-1, 0, 1>*wCube}},
        {transform{translate <-1, 1,-1>*wCube}, transform{translate <-1, 1, 0>*wCube}, transform{translate <-1, 1, 1>*wCube}}
    },
    {
        {transform{translate < 0,-1,-1>*wCube}, transform{translate < 0,-1, 0>*wCube}, transform{translate < 0,-1, 1>*wCube}},
        {transform{translate < 0, 0,-1>*wCube}, transform{translate < 0, 0, 0>*wCube}, transform{translate < 0, 0, 1>*wCube}},
        {transform{translate < 0, 1,-1>*wCube}, transform{translate < 0, 1, 0>*wCube}, transform{translate < 0, 1, 1>*wCube}}
    },
    {
        {transform{translate < 1,-1,-1>*wCube}, transform{translate < 1,-1, 0>*wCube}, transform{translate < 1,-1, 1>*wCube}},
        {transform{translate < 1, 0,-1>*wCube}, transform{translate < 1, 0, 0>*wCube}, transform{translate < 1, 0, 1>*wCube}},
        {transform{translate < 1, 1,-1>*wCube}, transform{translate < 1, 1, 0>*wCube}, transform{translate < 1, 1, 1>*wCube}}
    }
}

/*------------------------------------------------------------------------*/
/* Translation indirection array                                          */

#declare iTran = array[3][3][3] {
    {
        {<0, 0, 0>, <0, 0, 1>, <0, 0, 2>},
        {<0, 1, 0>, <0, 1, 1>, <0, 1, 2>},
        {<0, 2, 0>, <0, 2, 1>, <0, 2, 2>}
    },
    {
        {<1, 0, 0>, <1, 0, 1>, <1, 0, 2>},
        {<1, 1, 0>, <1, 1, 1>, <1, 1, 2>},
        {<1, 2, 0>, <1, 2, 1>, <1, 2, 2>}
    },
    {
        {<2, 0, 0>, <2, 0, 1>, <2, 0, 2>},
        {<2, 1, 0>, <2, 1, 1>, <2, 1, 2>},
        {<2, 2, 0>, <2, 2, 1>, <2, 2, 2>}
    }
}

/*========================================================================*/
/* Slice rotations                                                        */
/*   Rot_L(OT, IT, II, a) Rotate left slice around the X-axis             */
/*   Rot_I(OT, IT, II, a) Rotate middle slice around the X-axis           */
/*   Rot_R(OT, IT, II, a) Rotate right slice around the X-axis            */
/*   Rot_B(OT, IT, II, a) Rotate bottom slice around the Y-axis           */
/*   Rot_J(OT, IT, II, a) Rotate middle slice around the Y-axis           */
/*   Rot_T(OT, IT, II, a) Rotate top slice around the Y-axis              */
/*   Rot_F(OT, IT, II, a) Rotate forward slice around the Z-axis          */
/*   Rot_K(OT, IT, II, a) Rotate middle slice around the Z-axis           */
/*   Rot_A(OT, IT, II, a) Rotate aft slice around the Z-axis              */
/*   Rot_X(OT, IT, II, a) Rotate entire cube around the X-axis            */
/*   Rot_Y(OT, IT, II, a) Rotate entire cube around the Y-axis            */
/*   Rot_Z(OT, IT, II, a) Rotate entire cube around the Z-axis            */
/*     OT is Output translation array                                     */
/*     IT is Input translation array                                      */
/*     II is Translation indirection array                                */
/*     a  is number of steps to turn (fractional allowed)                 */

/*------------------------------------------------------------------------*/
/* Rotate left slice around the X-axis.                                   */

#macro Rot_L(OT, IT, II, a)
    #local iX = 0;
    #while (iX < 3)
        #local iY = 0;
        #while (iY < 3)
            #local iZ = 0;
            #while (iZ < 3)
                #if (iX = 0)
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = transform { IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] rotate 90*a*x }
                #else
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z]
                #end
                #local iZ = iZ + 1;
            #end
            #local iY = iY + 1;
        #end
        #local iX = iX + 1;
    #end
#end

/*------------------------------------------------------------------------*/
/* Rotate middle slice around the X-axis.                                 */

#macro Rot_I(OT, IT, II, a)
    #local iX = 0;
    #while (iX < 3)
        #local iY = 0;
        #while (iY < 3)
            #local iZ = 0;
            #while (iZ < 3)
                #if (iX = 1)
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = transform { IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] rotate 90*a*x }
                #else
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z]
                #end
                #local iZ = iZ + 1;
            #end
            #local iY = iY + 1;
        #end
        #local iX = iX + 1;
    #end
#end

/*------------------------------------------------------------------------*/
/* Rotate right slice around the X-axis.                                  */

#macro Rot_R(OT, IT, II, a)
    #local iX = 0;
    #while (iX < 3)
        #local iY = 0;
        #while (iY < 3)
            #local iZ = 0;
            #while (iZ < 3)
                #if (iX = 2)
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = transform { IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] rotate 90*a*x }
                #else
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z]
                #end
                #local iZ = iZ + 1;
            #end
            #local iY = iY + 1;
        #end
        #local iX = iX + 1;
    #end
#end

/*------------------------------------------------------------------------*/
/* Rotate bottom slice around the Y-axis.                                 */

#macro Rot_B(OT, IT, II, a)
    #local iX = 0;
    #while (iX < 3)
        #local iY = 0;
        #while (iY < 3)
            #local iZ = 0;
            #while (iZ < 3)
                #if (iY = 0)
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = transform { IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] rotate 90*a*y }
                #else
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z]
                #end
                #local iZ = iZ + 1;
            #end
            #local iY = iY + 1;
        #end
        #local iX = iX + 1;
    #end
#end

/*------------------------------------------------------------------------*/
/* Rotate middle slice around the Y-axis.                                 */

#macro Rot_J(OT, IT, II, a)
    #local iX = 0;
    #while (iX < 3)
        #local iY = 0;
        #while (iY < 3)
            #local iZ = 0;
            #while (iZ < 3)
                #if (iY = 1)
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = transform { IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] rotate 90*a*y }
                #else
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z]
                #end
                #local iZ = iZ + 1;
            #end
            #local iY = iY + 1;
        #end
        #local iX = iX + 1;
    #end
#end

/*------------------------------------------------------------------------*/
/* Rotate top slice around the Y-axis.                                    */

#macro Rot_T(OT, IT, II, a)
    #local iX = 0;
    #while (iX < 3)
        #local iY = 0;
        #while (iY < 3)
            #local iZ = 0;
            #while (iZ < 3)
                #if (iY = 2)
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = transform { IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] rotate 90*a*y }
                #else
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z]
                #end
                #local iZ = iZ + 1;
            #end
            #local iY = iY + 1;
        #end
        #local iX = iX + 1;
    #end
#end

/*------------------------------------------------------------------------*/
/* Rotate forward slice around the Z-axis.                                */

#macro Rot_F(OT, IT, II, a)
    #local iX = 0;
    #while (iX < 3)
        #local iY = 0;
        #while (iY < 3)
            #local iZ = 0;
            #while (iZ < 3)
                #if (iZ = 0)
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = transform { IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] rotate 90*a*z }
                #else
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z]
                #end
                #local iZ = iZ + 1;
            #end
            #local iY = iY + 1;
        #end
        #local iX = iX + 1;
    #end
#end

/*------------------------------------------------------------------------*/
/* Rotate middle slice around the Z-axis.                                 */

#macro Rot_K(OT, IT, II, a)
    #local iX = 0;
    #while (iX < 3)
        #local iY = 0;
        #while (iY < 3)
            #local iZ = 0;
            #while (iZ < 3)
                #if (iZ = 1)
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = transform { IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] rotate 90*a*z }
                #else
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z]
                #end
                #local iZ = iZ + 1;
            #end
            #local iY = iY + 1;
        #end
        #local iX = iX + 1;
    #end
#end

/*------------------------------------------------------------------------*/
/* Rotate aft slice around the Z-axis.                                    */

#macro Rot_A(OT, IT, II, a)
    #local iX = 0;
    #while (iX < 3)
        #local iY = 0;
        #while (iY < 3)
            #local iZ = 0;
            #while (iZ < 3)
                #if (iZ = 2)
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = transform { IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] rotate 90*a*z }
                #else
                    #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z]
                #end
                #local iZ = iZ + 1;
            #end
            #local iY = iY + 1;
        #end
        #local iX = iX + 1;
    #end
#end

/*------------------------------------------------------------------------*/
/* Rotate entire cube around the X-axis.                                    */

#macro Rot_X(OT, IT, II, a)
    #local iX = 0;
    #while (iX < 3)
        #local iY = 0;
        #while (iY < 3)
            #local iZ = 0;
            #while (iZ < 3)
                #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = transform { IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] rotate 90*a*x }
                #local iZ = iZ + 1;
            #end
            #local iY = iY + 1;
        #end
        #local iX = iX + 1;
    #end
#end

/*------------------------------------------------------------------------*/
/* Rotate entire cube around the Y-axis.                                    */

#macro Rot_Y(OT, IT, II, a)
    #local iX = 0;
    #while (iX < 3)
        #local iY = 0;
        #while (iY < 3)
            #local iZ = 0;
            #while (iZ < 3)
                #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = transform { IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] rotate 90*a*y }
                #local iZ = iZ + 1;
            #end
            #local iY = iY + 1;
        #end
        #local iX = iX + 1;
    #end
#end

/*------------------------------------------------------------------------*/
/* Rotate entire cube around the Z-axis.                                    */

#macro Rot_Z(OT, IT, II, a)
    #local iX = 0;
    #while (iX < 3)
        #local iY = 0;
        #while (iY < 3)
            #local iZ = 0;
            #while (iZ < 3)
                #declare OT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] = transform { IT[II[iX][iY][iZ].x][II[iX][iY][iZ].y][II[iX][iY][iZ].z] rotate 90*a*z }
                #local iZ = iZ + 1;
            #end
            #local iY = iY + 1;
        #end
        #local iX = iX + 1;
    #end
#end

/*------------------------------------------------------------------------*/
/* Select rotations by character code                                     */

#macro Rot(S, OT, IT, II, a)
    #switch(asc(S))
        #case (asc("L")) Rot_L(OT, IT, II,  a) #break
        #case (asc("I")) Rot_I(OT, IT, II,  a) #break
        #case (asc("R")) Rot_R(OT, IT, II,  a) #break
        #case (asc("B")) Rot_B(OT, IT, II,  a) #break
        #case (asc("J")) Rot_J(OT, IT, II,  a) #break
        #case (asc("T")) Rot_T(OT, IT, II,  a) #break
        #case (asc("F")) Rot_F(OT, IT, II,  a) #break
        #case (asc("K")) Rot_K(OT, IT, II,  a) #break
        #case (asc("A")) Rot_A(OT, IT, II,  a) #break
        #case (asc("X")) Rot_X(OT, IT, II,  a) #break
        #case (asc("Y")) Rot_Y(OT, IT, II,  a) #break
        #case (asc("Z")) Rot_Z(OT, IT, II,  a) #break

        #case (asc("l")) Rot_L(OT, IT, II, -a) #break
        #case (asc("i")) Rot_I(OT, IT, II, -a) #break
        #case (asc("r")) Rot_R(OT, IT, II, -a) #break
        #case (asc("b")) Rot_B(OT, IT, II, -a) #break
        #case (asc("j")) Rot_J(OT, IT, II, -a) #break
        #case (asc("t")) Rot_T(OT, IT, II, -a) #break
        #case (asc("f")) Rot_F(OT, IT, II, -a) #break
        #case (asc("k")) Rot_K(OT, IT, II, -a) #break
        #case (asc("a")) Rot_A(OT, IT, II, -a) #break
        #case (asc("x")) Rot_X(OT, IT, II, -a) #break
        #case (asc("y")) Rot_Y(OT, IT, II, -a) #break
        #case (asc("z")) Rot_Z(OT, IT, II, -a) #break
    #end
#end


/*========================================================================*/
/* Translation indirection array rotations                                */

/*------------------------------------------------------------------------*/
/*                                                                        */

#macro iRot_L(II)
    #local OI = II
    #local OI[0][0][0] = II[0][0][2];
    #local OI[0][0][1] = II[0][1][2];
    #local OI[0][0][2] = II[0][2][2];
    #local OI[0][1][0] = II[0][0][1];
    #local OI[0][1][1] = II[0][1][1];
    #local OI[0][1][2] = II[0][2][1];
    #local OI[0][2][0] = II[0][0][0];
    #local OI[0][2][1] = II[0][1][0];
    #local OI[0][2][2] = II[0][2][0];
    #declare II = OI
#end

/*------------------------------------------------------------------------*/
/*                                                                        */

#macro iRot_I(II)
    #local OI = II
    #local OI[1][0][0] = II[1][0][2];
    #local OI[1][0][1] = II[1][1][2];
    #local OI[1][0][2] = II[1][2][2];
    #local OI[1][1][0] = II[1][0][1];
    #local OI[1][1][1] = II[1][1][1];
    #local OI[1][1][2] = II[1][2][1];
    #local OI[1][2][0] = II[1][0][0];
    #local OI[1][2][1] = II[1][1][0];
    #local OI[1][2][2] = II[1][2][0];
    #declare II = OI
#end

/*------------------------------------------------------------------------*/
/*                                                                        */

#macro iRot_R(II)
    #local OI = II
    #local OI[2][0][0] = II[2][0][2];
    #local OI[2][0][1] = II[2][1][2];
    #local OI[2][0][2] = II[2][2][2];
    #local OI[2][1][0] = II[2][0][1];
    #local OI[2][1][1] = II[2][1][1];
    #local OI[2][1][2] = II[2][2][1];
    #local OI[2][2][0] = II[2][0][0];
    #local OI[2][2][1] = II[2][1][0];
    #local OI[2][2][2] = II[2][2][0];
    #declare II = OI
#end

/*------------------------------------------------------------------------*/
/*                                                                        */

#macro iRot_B(II)
    #local OI = II
    #local OI[0][0][0] = II[2][0][0];
    #local OI[0][0][1] = II[1][0][0];
    #local OI[0][0][2] = II[0][0][0];
    #local OI[1][0][0] = II[2][0][1];
    #local OI[1][0][1] = II[1][0][1];
    #local OI[1][0][2] = II[0][0][1];
    #local OI[2][0][0] = II[2][0][2];
    #local OI[2][0][1] = II[1][0][2];
    #local OI[2][0][2] = II[0][0][2];
    #declare II = OI
#end

/*------------------------------------------------------------------------*/
/*                                                                        */

#macro iRot_J(II)
    #local OI = II
    #local OI[0][1][0] = II[2][1][0];
    #local OI[0][1][1] = II[1][1][0];
    #local OI[0][1][2] = II[0][1][0];
    #local OI[1][1][0] = II[2][1][1];
    #local OI[1][1][1] = II[1][1][1];
    #local OI[1][1][2] = II[0][1][1];
    #local OI[2][1][0] = II[2][1][2];
    #local OI[2][1][1] = II[1][1][2];
    #local OI[2][1][2] = II[0][1][2];
    #declare II = OI
#end

/*------------------------------------------------------------------------*/
/*                                                                        */

#macro iRot_T(II)
    #local OI = II
    #local OI[0][2][0] = II[2][2][0];
    #local OI[0][2][1] = II[1][2][0];
    #local OI[0][2][2] = II[0][2][0];
    #local OI[1][2][0] = II[2][2][1];
    #local OI[1][2][1] = II[1][2][1];
    #local OI[1][2][2] = II[0][2][1];
    #local OI[2][2][0] = II[2][2][2];
    #local OI[2][2][1] = II[1][2][2];
    #local OI[2][2][2] = II[0][2][2];
    #declare II = OI
#end

/*------------------------------------------------------------------------*/
/*                                                                        */

#macro iRot_F(II)
    #local OI = II
    #local OI[0][0][0] = II[0][2][0];
    #local OI[0][1][0] = II[1][2][0];
    #local OI[0][2][0] = II[2][2][0];
    #local OI[1][0][0] = II[0][1][0];
    #local OI[1][1][0] = II[1][1][0];
    #local OI[1][2][0] = II[2][1][0];
    #local OI[2][0][0] = II[0][0][0];
    #local OI[2][1][0] = II[1][0][0];
    #local OI[2][2][0] = II[2][0][0];
    #declare II = OI
#end

/*------------------------------------------------------------------------*/
/*                                                                        */

#macro iRot_K(II)
    #local OI = II
    #local OI[0][0][1] = II[0][2][1];
    #local OI[0][1][1] = II[1][2][1];
    #local OI[0][2][1] = II[2][2][1];
    #local OI[1][0][1] = II[0][1][1];
    #local OI[1][1][1] = II[1][1][1];
    #local OI[1][2][1] = II[2][1][1];
    #local OI[2][0][1] = II[0][0][1];
    #local OI[2][1][1] = II[1][0][1];
    #local OI[2][2][1] = II[2][0][1];
    #declare II = OI
#end

/*------------------------------------------------------------------------*/
/*                                                                        */

#macro iRot_A(II)
    #local OI = II
    #local OI[0][0][2] = II[0][2][2];
    #local OI[0][1][2] = II[1][2][2];
    #local OI[0][2][2] = II[2][2][2];
    #local OI[1][0][2] = II[0][1][2];
    #local OI[1][1][2] = II[1][1][2];
    #local OI[1][2][2] = II[2][1][2];
    #local OI[2][0][2] = II[0][0][2];
    #local OI[2][1][2] = II[1][0][2];
    #local OI[2][2][2] = II[2][0][2];
    #declare II = OI
#end

/*------------------------------------------------------------------------*/
/*                                                                        */

#macro iRot_X(II)
    #local OI = II
    #local OI[0][0][0] = II[0][0][2];
    #local OI[0][0][1] = II[0][1][2];
    #local OI[0][0][2] = II[0][2][2];
    #local OI[0][1][0] = II[0][0][1];
    #local OI[0][1][1] = II[0][1][1];
    #local OI[0][1][2] = II[0][2][1];
    #local OI[0][2][0] = II[0][0][0];
    #local OI[0][2][1] = II[0][1][0];
    #local OI[0][2][2] = II[0][2][0];
    #local OI[1][0][0] = II[1][0][2];
    #local OI[1][0][1] = II[1][1][2];
    #local OI[1][0][2] = II[1][2][2];
    #local OI[1][1][0] = II[1][0][1];
    #local OI[1][1][1] = II[1][1][1];
    #local OI[1][1][2] = II[1][2][1];
    #local OI[1][2][0] = II[1][0][0];
    #local OI[1][2][1] = II[1][1][0];
    #local OI[1][2][2] = II[1][2][0];
    #local OI[2][0][0] = II[2][0][2];
    #local OI[2][0][1] = II[2][1][2];
    #local OI[2][0][2] = II[2][2][2];
    #local OI[2][1][0] = II[2][0][1];
    #local OI[2][1][1] = II[2][1][1];
    #local OI[2][1][2] = II[2][2][1];
    #local OI[2][2][0] = II[2][0][0];
    #local OI[2][2][1] = II[2][1][0];
    #local OI[2][2][2] = II[2][2][0];
    #declare II = OI
#end

/*------------------------------------------------------------------------*/
/*                                                                        */

#macro iRot_Y(II)
    #local OI = II
    #local OI[0][0][0] = II[2][0][0];
    #local OI[0][0][1] = II[1][0][0];
    #local OI[0][0][2] = II[0][0][0];
    #local OI[1][0][0] = II[2][0][1];
    #local OI[1][0][1] = II[1][0][1];
    #local OI[1][0][2] = II[0][0][1];
    #local OI[2][0][0] = II[2][0][2];
    #local OI[2][0][1] = II[1][0][2];
    #local OI[2][0][2] = II[0][0][2];
    #local OI[0][1][0] = II[2][1][0];
    #local OI[0][1][1] = II[1][1][0];
    #local OI[0][1][2] = II[0][1][0];
    #local OI[1][1][0] = II[2][1][1];
    #local OI[1][1][1] = II[1][1][1];
    #local OI[1][1][2] = II[0][1][1];
    #local OI[2][1][0] = II[2][1][2];
    #local OI[2][1][1] = II[1][1][2];
    #local OI[2][1][2] = II[0][1][2];
    #local OI[0][2][0] = II[2][2][0];
    #local OI[0][2][1] = II[1][2][0];
    #local OI[0][2][2] = II[0][2][0];
    #local OI[1][2][0] = II[2][2][1];
    #local OI[1][2][1] = II[1][2][1];
    #local OI[1][2][2] = II[0][2][1];
    #local OI[2][2][0] = II[2][2][2];
    #local OI[2][2][1] = II[1][2][2];
    #local OI[2][2][2] = II[0][2][2];
    #declare II = OI
#end

/*------------------------------------------------------------------------*/
/*                                                                        */

#macro iRot_Z(II)
    #local OI = II
    #local OI[0][0][0] = II[0][2][0];
    #local OI[0][1][0] = II[1][2][0];
    #local OI[0][2][0] = II[2][2][0];
    #local OI[1][0][0] = II[0][1][0];
    #local OI[1][1][0] = II[1][1][0];
    #local OI[1][2][0] = II[2][1][0];
    #local OI[2][0][0] = II[0][0][0];
    #local OI[2][1][0] = II[1][0][0];
    #local OI[2][2][0] = II[2][0][0];
    #local OI[0][0][1] = II[0][2][1];
    #local OI[0][1][1] = II[1][2][1];
    #local OI[0][2][1] = II[2][2][1];
    #local OI[1][0][1] = II[0][1][1];
    #local OI[1][1][1] = II[1][1][1];
    #local OI[1][2][1] = II[2][1][1];
    #local OI[2][0][1] = II[0][0][1];
    #local OI[2][1][1] = II[1][0][1];
    #local OI[2][2][1] = II[2][0][1];
    #local OI[0][0][2] = II[0][2][2];
    #local OI[0][1][2] = II[1][2][2];
    #local OI[0][2][2] = II[2][2][2];
    #local OI[1][0][2] = II[0][1][2];
    #local OI[1][1][2] = II[1][1][2];
    #local OI[1][2][2] = II[2][1][2];
    #local OI[2][0][2] = II[0][0][2];
    #local OI[2][1][2] = II[1][0][2];
    #local OI[2][2][2] = II[2][0][2];
    #declare II = OI
#end

/*------------------------------------------------------------------------*/
/*                                                                        */

#macro iRot(S, II)
    #switch(asc(S))
        #case (asc("L")) iRot_L(II) #break
        #case (asc("I")) iRot_I(II) #break
        #case (asc("R")) iRot_R(II) #break
        #case (asc("B")) iRot_B(II) #break
        #case (asc("J")) iRot_J(II) #break
        #case (asc("T")) iRot_T(II) #break
        #case (asc("F")) iRot_F(II) #break
        #case (asc("K")) iRot_K(II) #break
        #case (asc("A")) iRot_A(II) #break
        #case (asc("X")) iRot_X(II) #break
        #case (asc("Y")) iRot_Y(II) #break
        #case (asc("Z")) iRot_Z(II) #break
    #end
#end

/*========================================================================*/
/*                                                                        */

#macro iRotn(S, II, a)
    #local ta =  (strcmp(S, strupr(S))?-a:a);
    #local ta = mod(ta, 4);
    #if (ta != 0)
        #local ta = ((ta>0)?ta:4+ta);
        #local n = 0;
        #while (n < ta)
            iRot(strupr(S), II)
            #local n = n + 1;
        #end
    #end
#end

/*========================================================================*/
/* Manip(IT, II, s) - Manipulate the cube.                                */
/*   IT - Translation array                                               */
/*   II - Translation indirection array                                   */
/*   s  - Move string to be applied. Can contain the following            */
/*        characters (use lower case for reverse)                         */
/*          "L" - Rotate left slice around X-axis                         */
/*          "I" - Rotate middle slice around X-axis                       */
/*          "R" - Rotate right slice around X-axis                        */
/*          "X" - Rotate cube around X-axis                               */
/*          "B" - Rotate bottom slice around Y-axis                       */
/*          "J" - Rotate middle slice around Y-axis                       */
/*          "T" - Rotate top slice around Y-axis                          */
/*          "Y" - Rotate cube around Y-axis                               */
/*          "F" - Rotate forward slice around Z-axis                      */
/*          "K" - Rotate middle slice around Z-axis                       */
/*          "A" - Rotate aft slice around Z-axis                          */
/*          "Z" - Rotate cube around Z-axis                               */

#macro Manip(IT, II, s)
    #local Ttmp = array[3][3][3] // Temporary translation array
    #local sLen = strlen(s);     // Move string length
    #local idx = 0;              // Index of current move in move string
    #while (idx < sLen)
        Rot(substr(s, idx+1, 1), Ttmp, IT, II, 1) // Rotate slice
        #local IT = Ttmp
        iRotn(substr(s, idx+1, 1), II, 1) // Update translation indirection array
        #local idx = idx + 1;
    #end
#end

/*========================================================================*/
/* Rubik(C, T) - Put the subcubes together according to the translation   */
/*               array.                                                   */
/*   C - array of subcube objects                                         */
/*   T - translation array                                                */

#macro Rubik(C, T)
    union {
        #local iX = 0;
        #while (iX < 3)
            #local iY = 0;
            #while (iY < 3)
                #local iZ = 0;
                #while (iZ < 3)
                    object { C[iX][iY][iZ] transform T[iX][iY][iZ] }
                    #local iZ = iZ + 1;
                #end
                #local iY = iY + 1;
            #end
            #local iX = iX + 1;
        #end
    }
#end

#macro RubikCube(Movstr, s, a)
    #local Ttmp = array[3][3][3];
    Manip(Tran, iTran, Movstr)
    Rot(s, Ttmp, Tran, iTran, a)
    object {
        Rubik(Cubes, Ttmp)
        translate <0, 1.5*wCube+3*tFace, 0>
    }
#end
