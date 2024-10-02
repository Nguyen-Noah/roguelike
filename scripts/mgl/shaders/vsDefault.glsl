#version 330 core

in vec2 vert;
in vec2 texcoord;

uniform mat4 projection;

out vec2 uv;

void main() {
    uv = texcoord;
    gl_Position = projection * vec4(vert, 0.0, 1.0);
}