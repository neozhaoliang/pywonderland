const float edge_thickness = 0.05;
const int   max_reflections = 10;
const float camera_distance_to_origin = 2.0;

struct Hit {
    float t;
    float ed;
    vec3 normal;
    vec3 bary;
};

const Hit NOHIT = Hit(1000.0, 0.0, vec3(0), vec3(0));

float orient(vec3 p, vec3 a, vec3 b, vec3 n) {
    vec3 z = cross(a - p, b - p);
    return dot(z, n);
}

Hit get_ray_intersection_facesA(vec3 ray_origin, vec3 ray_dir) {
    Hit hit = NOHIT;
    for (int m = 0; m < facesA.length() / facesAEnabled; m++) {
        vec3 v0 = facesA[m * facesAEnabled];
        vec3 v1 = facesA[m * facesAEnabled + 1];
        vec3 v2 = facesA[m * facesAEnabled + 2];

        vec3 v10 = v1 - v0;
        vec3 v20 = v2 - v0;
        vec3 q = ray_origin - v0;
        vec3 d20 = cross(ray_dir, v20);
        vec3 q10 = cross(q, v10);
        float det = dot(v10, d20);
        float h = dot(q10, v20);
        float t = h / det;

        if (t > 1e-3) {
            int count = 0;
            vec3 p = ray_origin + t * ray_dir;
            vec3 normal = normalize(cross(v10, v20));
            float ed2 = dot(p - v0, p - v0);
            for (int i = 0, j = facesAEnabled - 1; i < facesAEnabled; j = i, i++) {
                vec3 vj = facesA[m * facesAEnabled + j];
                vec3 vi = facesA[m * facesAEnabled + i];
                vec3 e = vj - vi;
                vec3 ip = p - vi;
                vec3 b = ip - e * clamp(dot(ip, e) / dot(e, e), 0., 1.);
                ed2 = min(ed2, dot(b, b));
                count += int(orient(p, vj, vi, normal) > 0.);
            }

            if ((count == facesAEnabled || count == -facesAEnabled) && t < hit.t) {
                float u = dot(q, d20) / det;
                float v = dot(ray_dir, q10) / det;
                float w = 1.0 - u - v;
                hit = Hit(t, sqrt(ed2), normal, vec3(u, v, w));
            }
        }
    }
    return hit;
}


#ifdef facesBEnabled

Hit get_ray_intersection_facesB(vec3 ray_origin, vec3 ray_dir) {
    Hit hit = NOHIT;
    for (int m = 0; m < facesB.length() / facesBEnabled; m++) {
        vec3 v0 = facesB[m * facesBEnabled];
        vec3 v1 = facesB[m * facesBEnabled + 1];
        vec3 v2 = facesB[m * facesBEnabled + 2];

        vec3 v10 = v1 - v0;
        vec3 v20 = v2 - v0;
        vec3 q = ray_origin - v0;
        vec3 d20 = cross(ray_dir, v20);
        vec3 q10 = cross(q, v10);
        float det = dot(v10, d20);
        float h = dot(q10, v20);
        float t = h / det;

        if (t > 1e-3) {
            int count = 0;
            vec3 p = ray_origin + t * ray_dir;
            vec3 normal = normalize(cross(v10, v20));
            float ed2 = dot(p - v0, p - v0);
            for (int i = 0, j = facesBEnabled - 1; i < facesBEnabled; j = i, i++) {
                vec3 vj = facesB[m * facesBEnabled + j];
                vec3 vi = facesB[m * facesBEnabled + i];
                vec3 e = vj - vi;
                vec3 ip = p - vi;
                vec3 b = ip - e * clamp(dot(ip, e) / dot(e, e), 0., 1.);
                ed2 = min(ed2, dot(b, b));
                count += int(orient(p, vj, vi, normal) > 0.);
            }

            if ((count == facesBEnabled || count == -facesBEnabled) && t < hit.t) {
                float u = dot(q, d20) / det;
                float v = dot(ray_dir, q10) / det;
                float w = 1.0 - u - v;
                hit = Hit(t, sqrt(ed2), normal, vec3(u, v, w));
            }
        }
    }
    return hit;
}

#endif


#ifdef facesCEnabled

Hit get_ray_intersection_facesC(vec3 ray_origin, vec3 ray_dir) {
    Hit hit = NOHIT;
    for (int m = 0; m < facesC.length() / facesCEnabled; m++) {
        vec3 v0 = facesC[m * facesCEnabled];
        vec3 v1 = facesC[m * facesCEnabled + 1];
        vec3 v2 = facesC[m * facesCEnabled + 2];

        vec3 v10 = v1 - v0;
        vec3 v20 = v2 - v0;
        vec3 q = ray_origin - v0;
        vec3 d20 = cross(ray_dir, v20);
        vec3 q10 = cross(q, v10);
        float det = dot(v10, d20);
        float h = dot(q10, v20);
        float t = h / det;

        if (t > 1e-3) {
            int count = 0;
            vec3 p = ray_origin + t * ray_dir;
            vec3 normal = normalize(cross(v10, v20));
            float ed2 = dot(p - v0, p - v0);
            for (int i = 0, j = facesCEnabled - 1; i < facesCEnabled; j = i, i++) {
                vec3 vj = facesC[m * facesCEnabled + j];
                vec3 vi = facesC[m * facesCEnabled + i];
                vec3 e = vj - vi;
                vec3 ip = p - vi;
                vec3 b = ip - e * clamp(dot(ip, e) / dot(e, e), 0., 1.);
                ed2 = min(ed2, dot(b, b));
                count += int(orient(p, vj, vi, normal) > 0.);
            }

            if ((count == facesCEnabled || count == -facesCEnabled) && t < hit.t) {
                float u = dot(q, d20) / det;
                float v = dot(ray_dir, q10) / det;
                float w = 1.0 - u - v;
                hit = Hit(t, sqrt(ed2), normal, vec3(u, v, w));
            }
        }
    }
    return hit;
}

#endif


Hit get_ray_intersection(vec3 ray_origin, vec3 ray_dir) {
    Hit result = get_ray_intersection_facesA(ray_origin, ray_dir);
    Hit hitB = NOHIT;
    Hit hitC = NOHIT;

#ifdef facesBEnabled
    hitB = get_ray_intersection_facesB(ray_origin, ray_dir);
#endif

#ifdef facesCEnabled
    hitC = get_ray_intersection_facesC(ray_origin, ray_dir);
#endif

    if (hitB.t < result.t)
        result = hitB;

    if (hitC.t < result.t)
        result = hitC;

    return result;
}


Hit hit_from_outside(vec3 ray_origin, vec3 ray_dir) {
    Hit hit = get_ray_intersection(ray_origin, ray_dir);
    if (hit.t <= 10.0 && dot(hit.normal, ray_dir) < 0.0)
        return hit;
    return NOHIT;
}


Hit hit_from_inside(vec3 ray_origin, vec3 ray_dir) {
    Hit hit = get_ray_intersection(ray_origin, ray_dir);
    if (hit.t <= 10.0)
        return hit;
    return NOHIT;
}

vec4 get_wall_color(vec3 ray_dir, Hit hit) {
    vec3 albedo = texture(iChannel1, vec2(hit.bary.yz) * 2.0).rgb;
    albedo = pow(albedo, vec3(2.2)) * 0.5;
    float lighting = 0.2 + max(dot(hit.normal, vec3(0.8, 0.5, 0.)), 0.);
    if (dot(ray_dir, hit.normal) < 0.) {
       float f = clamp(hit.ed * 1000. - 3., 0., 1.);
       albedo = mix(vec3(0.01), albedo, f);
       return vec4(albedo * lighting, f);
    }

    float m = max(max(hit.bary.x, hit.bary.y), hit.bary.z);
    vec2 a = fract(vec2(hit.ed, m) * 40.) - 0.5;
    float b = 0.2 / (dot(a, a) + 0.2);
    float light_shape = 1. - clamp(hit.ed * 100. - 2., 0., 1.);
    light_shape *= b;
    vec3 emissive = vec3(3.5, 1.8, 1.0);
    return vec4(mix(albedo * lighting, emissive, light_shape), 0.);
}


vec3 get_background_color(vec3 ray_dir) {
    vec3 col = texture(iChannel0, ray_dir).rgb;
    col = pow(col, vec3(2.2));
    float luma = dot(col, vec3(0.2126, 0.7152, 0.0722)) * 0.7;
    return 2.5 * col / (1.0 - luma);
}


vec3 get_ray_color(vec3 ray_origin, vec3 ray_dir) {
    vec3 color = vec3(0);

    Hit hit = hit_from_outside(ray_origin, ray_dir);
    if (hit.t > 10.0)
        return get_background_color(ray_dir);

    vec3 ref_dir = reflect(ray_dir, hit.normal);
    vec3 bg_color = pow(get_background_color(ref_dir), vec3(1.0));
    float fresnel = 0.05 + 0.95 * pow(1.0 - max(dot(ray_dir, -hit.normal), 0.0), 5.0);
    color += bg_color * fresnel;

    if (hit.ed < edge_thickness) {
        vec4 wc = get_wall_color(ray_dir, hit);
        return color * wc.a + wc.rgb;
    }

    ray_origin += hit.t * ray_dir;
    hit = hit_from_inside(ray_origin, ray_dir);
    vec3 transmit = vec3(1.0);

    for (int i = 0; i < max_reflections; i++) {
        if (hit.ed < edge_thickness) {
            return color + transmit * get_wall_color(ray_dir, hit).rgb;
        }

        ray_origin += hit.t * ray_dir;
        ray_dir = reflect(ray_dir, hit.normal);
        ray_origin += ray_dir * 0.001;
        transmit *= vec3(0.4, 0.7, 0.7);
        hit = hit_from_inside(ray_origin, ray_dir);
    }
    return color;
}

mat3 camera_matrix(vec3 eye, vec3 lookat, vec3 up) {
    vec3 forward = normalize(lookat - eye);
    vec3 right = normalize(cross(forward, up));
    up = normalize(cross(right, forward));
    return mat3(right, up, -forward);
}


mat3 rotateX(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat3(
        vec3(1, 0, 0),
        vec3(0, c, -s),
        vec3(0, s, c)
    );
}

// Rotation matrix around the Y axis.
mat3 rotateY(float theta) {
    float c = cos(theta);
    float s = sin(theta);
    return mat3(
        vec3(c, 0, s),
        vec3(0, 1, 0),
        vec3(-s, 0, c)
    );
}


void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (fragCoord.xy - iResolution.xy * 0.5) / iResolution.y;
    vec2 movement = vec2(iTime * 0.2, sin(iTime * 0.2) * 0.5);
    vec3 eye = camera_distance_to_origin * vec3(
        cos(movement.x) * cos(movement.y),
        sin(movement.y),
        sin(movement.x) * cos(movement.y));
    vec2 mouse = vec2(0);
    if (iMouse.x > 0.) {
        mouse = 2. * iMouse.xy / iResolution.y - 1.;
        eye = rotateY(mouse.x) * rotateX(-mouse.y) * eye;
    }
    mat3 M = camera_matrix(eye, vec3(0), vec3(0, 1, 0));
    vec3 camera_ray = normalize(M * vec3(uv, -1.0));
    vec3 color = get_ray_color(eye, camera_ray);
    color = color / (color * 0.5 + 0.5);
    color = pow(color, vec3(1.0 / 2.2));
    fragColor = vec4(color, 1.0);
}


void main() {
    mainImage(fragColor, gl_FragCoord.xy);
}
