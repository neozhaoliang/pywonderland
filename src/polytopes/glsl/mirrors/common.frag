#version 130

uniform vec3          iResolution;
uniform float         iTime;
uniform vec4          iMouse;
uniform int           iFrame;
uniform samplerCube   iChannel0;
uniform sampler2D     iChannel1;

out vec4 fragColor;
