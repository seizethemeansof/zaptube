let frag_shader = `
precision highp float;

// our texture
uniform sampler2D u_image;

uniform vec2 u_resolution;

// the texCoords passed in from the vertex shader.
varying vec2 v_texCoord;

uniform float u_time;

float scanline(vec2 uv) {
	return sin(uv.y * 200.0 - u_time * 10.0);
}

float slowscan(vec2 uv) {
	return sin(uv.y * 200.0 + u_time * 6.0);
}

vec2 colorShift(vec2 uv) {
	return vec2(
		uv.x,
		uv.y + sin(u_time)*0.02
	);
}

float noise(vec2 uv) {
	return clamp(texture2D(u_image, uv.xy + u_time*6.0).r +
		texture2D(u_image, uv.xy - u_time*4.0).g, 0.96, 1.0);
}

// from https://www.shadertoy.com/view/4sf3Dr
// Thanks, Jasper
vec2 crt(vec2 coord, float bend)
{
	// put in symmetrical coords
	coord = (coord - 0.5) * 2.0;

	coord *= 0.5;

	// deform coords
	coord.x *= 1.0 + pow((abs(coord.y) / bend), 2.0);
	coord.y *= 1.0 + pow((abs(coord.x) / bend), 2.0);

	// transform back to 0.0 - 1.0 space
	coord  = (coord / 1.0) + 0.5;

	return coord;
}

vec2 colorshift(vec2 uv, float amount, float rand) {

	return vec2(
		uv.x,
		uv.y + amount * rand // * sin(uv.y * u_resolution.y * 0.12 + u_time)
	);
}

vec2 scandistort(vec2 uv) {
	float scan1 = clamp(cos(uv.y * 2.0 + u_time), 0.0, 1.0);
	float scan2 = clamp(cos(uv.y * 2.0 + u_time + 4.0) * 10.0, 0.0, 1.0) ;
	float amount = scan1 * scan2 * uv.x;
    // Was channel1
	uv.x -= 0.05 * mix(texture2D(u_image, vec2(uv.x, amount)).r * amount, amount, 0.9);

	return uv;

}

float vignette(vec2 uv) {
	uv = (uv - 0.5) * 0.98;
	return clamp(pow(cos(uv.x * 3.1415), 1.2) * pow(cos(uv.y * 3.1415), 1.2) * 50.0, 0.0, 1.0);
}

void main()
{
	vec2 uv = v_texCoord;
	vec2 sd_uv = scandistort(uv);
	vec2 crt_uv = crt(sd_uv, 2.0);

	vec4 color;

	//float rand_r = sin(u_time * 3.0 + sin(u_time)) * sin(u_time * 0.2);
	//float rand_g = clamp(sin(u_time * 1.52 * uv.y + sin(u_time)) * sin(u_time* 1.2), 0.0, 1.0);
	// it was channel 1
	vec4 rand = texture2D(u_image, vec2(u_time * 0.01, u_time * 0.02));

	color.r = texture2D(u_image, crt(colorshift(sd_uv, 0.025, rand.r), 2.0)).r;
	color.g = texture2D(u_image, crt(colorshift(sd_uv, 0.01, rand.g), 2.0)).g;
	color.b = texture2D(u_image, crt(colorshift(sd_uv, 0.024, rand.b), 2.0)).b;
	color.a = 1.0;

	vec4 scanline_color = vec4(scanline(crt_uv));
	vec4 slowscan_color = vec4(slowscan(crt_uv));

	vec4 tex = mix(color, mix(scanline_color, slowscan_color, 0.5), 0.05) * vignette(uv)*noise(uv);
	gl_FragColor = vec4(tex.rgb, 1.0);
//	vec4 tex = mix(texture2D(u_image, uv), scanline_color, 0.05);
//    gl_FragColor = vec4(tex.rgb, 1.0);
	//fragColor = vec4(vignette(uv));
	//vec2 scan_dist = scandistort(uv);
	//fragColor = vec4(scan_dist.x, scan_dist.y,0.0, 1.0);
}
`