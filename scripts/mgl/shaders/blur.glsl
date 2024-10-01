#version 330 core
out vec4 f_color;

in vec2 uv;

uniform sampler2D surface;
uniform bool horizontal;
uniform float weight[13] = float[] (
    0.136394, 0.125696, 0.102140, 
    0.072785, 0.046452, 0.026995, 
    0.013167, 0.005799, 0.002265, 
    0.000746, 0.000220, 0.000054, 
    0.000011
);

void main()
{             
    vec2 tex_offset = 1.0 / textureSize(surface, 0); // gets size of a single texel
    vec2 coords = uv;

    if (horizontal)
        coords.y = 1.0 - coords.y;


    vec3 result = texture(surface, coords).rgb * weight[0]; // current fragment's contribution
    if (horizontal) {
        for(int i = 1; i < 13; ++i) {
            result += texture(surface, coords + vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
            result += texture(surface, coords - vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
        }
    } else {
        for(int i = 1; i < 13; ++i) {
            result += texture(surface, coords + vec2(0.0, tex_offset.y * i)).rgb * weight[i];
            result += texture(surface, coords - vec2(0.0, tex_offset.y * i)).rgb * weight[i];
        }
    }
    f_color = vec4(result, 1.0);
}
