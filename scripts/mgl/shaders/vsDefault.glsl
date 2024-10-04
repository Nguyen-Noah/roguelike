#version 330 core

in vec2 vert;
in vec2 texcoord;

uniform vec2 tile_pos;

out vec2 uv;

void main() {
    uv = texcoord;

    vec4 world_pos = vec4(vert + tile_pos, 0.0, 1.0);
    //gl_Position = projection * world_pos;
    gl_Position = world_pos;
}
