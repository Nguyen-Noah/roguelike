#version 330 core

uniform float u_time;
uniform vec2 u_resolution;
uniform vec2 u_mouse;

in vec2 uv;
out vec4 f_color;

void main() {
    vec2 pos = uv;

    // Aspect ratio correction
    vec2 aspect_ratio = vec2(u_resolution.x / u_resolution.y, 1.0);
    pos = (pos - 0.5) * aspect_ratio + 0.5;

    vec3 color = vec3(0.0);
    f_color = vec4(color, 1.0);
}