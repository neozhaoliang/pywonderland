#define PI 3.141592653

float sl;

const float palNum = 70.;

float sFract(float x, float sm) {
    const float sf = 1.;

    vec2 u = vec2(x, fwidth(x)*sf*sm);
    u.x = fract(u.x);
    u += (1. - 2.*u)*step(u.y, u.x);
    return clamp(1. - u.x/u.y, 0., 1.); // Cos term ommitted.
}

float sFloor(float x) {
    return x - sFract(x, 1.);
}

vec3 rotHue(vec3 p, float a) {
    vec2 cs = sin(vec2(1.570796, 0) + a);

    mat3 hr = mat3(0.299,  0.587,  0.114,  0.299,  0.587,  0.114,  0.299,  0.587,  0.114) +
              mat3(0.701, -0.587, -0.114, -0.299,  0.413, -0.114, -0.300, -0.588,  0.886) * cs.x +
              mat3(0.168,  0.330, -0.497, -0.328,  0.035,  0.292,  1.250, -1.050, -0.203) * cs.y;

    return clamp(p*hr, 0., 1.);
}

float msign(in float x) {
    return x < 0.0 ? -1.0 : 1.0;
}

mat2 rot2d(float a) {
    float c=cos(a), s=sin(a);
    return mat2(c, -s, s, c);
}

vec2 cmul(vec2 p, vec2 q) {
    return vec2(p.x*q.x-p.y*q.y, p.x*q.y+p.y*q.x);
}

vec2 csqrt(vec2 p) {
    float a = atan(p.y, p.x) / 2.;
    return vec2(cos(a), sin(a)) * sqrt(length(p));
}

// distance from a 2d point p to a 2d segment (a, b)
float dseg(vec2 p, vec2 a, vec2 b) {
    vec2 v = b - a;
    p -= a;
    float t = clamp(dot(p, v)/dot(v, v), 0., 1.);
    return length(p - t * v);
}

// iq's triangle signed distance function
float sdTriangle( in vec2 p, in vec2 p0, in vec2 p1, in vec2 p2 ) {
    vec2 e0 = p1 - p0;
    vec2 e1 = p2 - p1;
    vec2 e2 = p0 - p2;

    vec2 v0 = p - p0;
    vec2 v1 = p - p1;
    vec2 v2 = p - p2;

    vec2 pq0 = v0 - e0*clamp( dot(v0,e0)/dot(e0,e0), 0.0, 1.0 );
    vec2 pq1 = v1 - e1*clamp( dot(v1,e1)/dot(e1,e1), 0.0, 1.0 );
    vec2 pq2 = v2 - e2*clamp( dot(v2,e2)/dot(e2,e2), 0.0, 1.0 );

    float s = e0.x*e2.y - e0.y*e2.x;
    vec2 d = min( min( vec2( dot( pq0, pq0 ), s*(v0.x*e0.y-v0.y*e0.x) ),
                       vec2( dot( pq1, pq1 ), s*(v1.x*e1.y-v1.y*e1.x) )),
                       vec2( dot( pq2, pq2 ), s*(v2.x*e2.y-v2.y*e2.x) ));

    return -sqrt(d.x)*sign(d.y);
}

// ellipse signed distance function
float sdEllipse( vec2 p, vec2 cen, float theta, in vec2 ab ) {
    p -= cen;
    float c = cos(theta), s = sin(theta);
    p *= mat2(c, s, -s, c);
    vec2 pab = p / (ab * ab);
    return (0.5 * dot(pab, p) - 0.5) / length(pab);
}

float sdEllipseFromTriangle(vec2 p, vec2 p0, vec2 p1, vec2 p2, out vec2 f1, out vec2 f2) {
    vec2 m = (p0 + p1 + p2) / 3.;
    vec2 n = (cmul(p0, p1) + cmul(p1, p2) + cmul(p2, p0)) / 3.;
    f1 = m + csqrt(cmul(m, m) - n);
    f2 = m - csqrt(cmul(m, m) - n);
    vec2 mid = (p0 + p1) / 2.;
    float a = (length(mid - f1) + length(mid - f2)) / 2.;
    vec2 cen = (f1 + f2) / 2.;
    vec2 dir = (f1 - f2) / 2.;
    float b = sqrt(a*a -dot(dir, dir));
    float theta = atan(dir.y, dir.x);
    return sdEllipse(p, cen, theta, vec2(a, b));
}

float getVoltage( vec2 p, vec2 p0, vec2 p1, vec2 p2 ) {
    float c = length(p - p0) * length(p - p1) * length(p - p2);
    c = log(max(c, 0.001));
    c = c / 10. + 0.5;
    c = clamp(c, 0., 1.);
    float level = sFloor(c*(palNum - .001));
    sl = level;
    return clamp(level/(palNum - 1.), 0., 1.) * .85 + .15 * c;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
    vec2 uv = (2.0*fragCoord - iResolution.xy) / iResolution.y;
    float sf = 2. / iResolution.y;
    vec2 p = uv * 2.;

    // triangle vertices
    vec2 A = vec2(1.5*sin(iTime), 1.5);
    vec2 B = vec2(-2.+0.4*cos(iTime*0.7), -1.+0.6*cos(iTime*0.7));
    vec2 C = vec2(1.8+cos(iTime), -1.6);

    // distance to the triangle
    float dtri = sdTriangle(p, A, B, C);

    // foci of the Steiner inscribed ellipse.
    vec2[2] foci;

    // solve the ellipse and foci
    vec2 m = (A + B + C) / 3.;
    vec2 n = (cmul(A, B) + cmul(B, C) + cmul(C, A)) / 3.;
    foci[0] = m + csqrt(cmul(m, m) - n);
    foci[1] = m - csqrt(cmul(m, m) - n);
    // the tangent point is the middle point of an edge.
    vec2 mid = (A + B) / 2.;
    // semi-axis
    float a = (length(mid - foci[0]) + length(mid - foci[1])) / 2.;
    vec2 cen = (foci[0] + foci[1]) / 2.;
    vec2 dir = (foci[0] - foci[1]) / 2.;
    float b = sqrt(a*a - dot(dir, dir));
    float theta = atan(dir.y, dir.x);
    // now we have the distance to the ellipse and the foci
    float dellipse = sdEllipse(p, cen, theta, vec2(a, b));
    float dfoci = min(length(p - foci[0]), length(p - foci[1])) - 0.04;

    // distance to the medians
    float dlines = 1e5;
    dlines = min(dlines, dseg(p, A, (B+C)/2.));
    dlines = min(dlines, dseg(p, B, (A+C)/2.));
    dlines = min(dlines, dseg(p, C, (B+A)/2.));

    // inside the ellipse/between ellipse and triangle/outside the triangle
    float sgn = dellipse < 0. ? -2. : (dtri < 0. ?  0. : 1.);

    // get voltage at this point
    float volt = getVoltage(p, A, B, C);
    float ssl = sl;

    vec2 e = vec2(8./clamp(iResolution.y, 300., 800.), 0);
    float fxl = getVoltage(p + e.xy, A, B, C);
    float fxr = getVoltage(p - e.xy, A, B, C);
    float fyt = getVoltage(p + e.yx, A, B, C);
    float fyb = getVoltage(p - e.yx, A, B, C);

    // color the region between voltage contours
    vec3 col = vec3(0.4, 0.7, 0.4) - sgn*vec3(0.2, 0., 0.2)*ssl/palNum;
    // dissipate the colors by doing some rotation
    col = rotHue(col, -(min(ssl/palNum, 0.85))*12.+1.);
    // darken the edges
    col *= max(1. - (abs(fxl - fxr) + abs(fyt - fyb))*10., 0.);
    // make some highlight
    fxl = getVoltage(p + e.xy*1.5, A, B, C);
    fyt = getVoltage(p + e.yx*1.5, A, B, C);
    col += vec3(.9, .7, 1.)*(max(volt - fyt, 0.) + max(volt - fxl, 0.)
                             + max(volt - fxr, 0.) + max(volt - fyb, 0.))*ssl;
    // draw the triangle
    col *= smoothstep(0.005, 0.005+2.0*sf, abs(dtri)-0.01);
    // draw the ellipse
    col *= smoothstep(0.005, 0.005+2.0*sf, abs(dellipse)-0.005);
    // draw the medians
    col *= smoothstep(0.005, 0.005+2.0*sf, abs(dlines)-0.002);
    // draw the segment connecting the foci
    col = mix(col, vec3(0.91, 0.1, 0.1), 1.-smoothstep(0., 0.005+2.*sf, dseg(p, foci[0], foci[1])-0.01));

    // decorate the vertices and foci
    vec2[3] verts; verts[0] = A; verts[1] = B; verts[2] = C;
    float lw = 0.02;
    for (int i=0; i<3; i++) {
        float dv = length(p - verts[i]) - .12;
        col = mix(col, vec3(0), (1. - smoothstep(0., sf*8., dv))*.5);
        col = mix(col, vec3(0), 1. - smoothstep(0., sf, dv));
        col = mix(col, vec3(1, .7, .6), 1. - smoothstep(0., sf, dv + lw*1.6));
        col = mix(col, vec3(0), 1. - smoothstep(0., sf, dv + .1 - lw));
    }
    for (int i=0; i<2; i++) {
        float dv = length(p - foci[i]) - .07;
        col = mix(col, vec3(0), (1. - smoothstep(0., sf*8., dv))*.5);
        col = mix(col, vec3(0), 1. - smoothstep(0., sf, dv));
        col = mix(col, vec3(.4, .6, 1.), 1. - smoothstep(0., sf, dv + lw*1.2));
        col = mix(col, vec3(0), 1. - smoothstep(0., sf, dv + .075 - lw));
    }

    col *= 1.25 - 0.2*length(p);

    fragColor = vec4(sqrt(max(col, 0.)), 1.0);
}
